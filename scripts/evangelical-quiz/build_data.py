#!/usr/bin/env python3
"""Build the probability blob for the "How Evangelical Are You?" quiz.

Reads the State of Theology workbook, validates it, derives the
NOT-Evangelical distribution, smooths, computes per-answer log-likelihood
weights, simulates a synthetic national population, and emits a JSON blob
for the client-side scorer.

Standard library only, on purpose - no openpyxl, no pandas - so this runs
anywhere Python 3.9+ does with nothing installed.

Usage:
    python build_data.py --xlsx workbook.xlsx --out ../../src/data/quiz.json
    python build_data.py --xlsx workbook.xlsx --report-only
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from bisect import bisect_left
from pathlib import Path

# ---------------------------------------------------------------------------
# Tunable constants. Mirrored into the emitted blob so the client, the README
# and whatever produced the numbers can never silently disagree.
# ---------------------------------------------------------------------------

EVANGELICAL_SHARE = 0.25   # w: evangelical share of the U.S. adult population
PROB_FLOOR = 0.02          # floor applied to every probability before logs
NEG_FLOOR = 0.005          # floor for negative cells when backing out not-E
SHRINKAGE = 2.5            # divides the summed score; the items correlate
SIM_N = 20_000             # synthetic respondents drawn from the All-U.S. dist
SIM_SEED = 20250825        # fixed so builds are reproducible
TIE_MARGIN = 0.25          # nats; top-two traditions closer than this = a tie
PCTL_STEPS = 200           # breakpoints stored: 0, 0.5, 1.0 ... 100

DATA_VERSION = "2"         # bump when the workbook or this math changes
                           # (2: arian moved into the christology block,
                           # which also reshuffles the simulation's RNG
                           # sequence and thus the percentile breakpoints)

# Question order follows the workbook's row order, except for explicit
# placements here: item -> the item it should appear immediately before.
# arian (2022 wave - dropped from the 2025 instrument but kept because it
# is theologically interesting) belongs with the deity-of-Christ items
# rather than tacked on at the end where the workbook appends it.
PLACE_BEFORE = {
    "arian": "jesus_not_god",
}

# ---------------------------------------------------------------------------

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

RESPONSES = [
    "strongly_disagree",
    "somewhat_disagree",
    "not_sure",
    "somewhat_agree",
    "strongly_agree",
]
# Collapsed 3-option scale, used when a wave only published agree/disagree.
RESPONSES_3 = ["strongly_disagree", "not_sure", "strongly_agree"]

EVANGELICAL = "Evangelical"
BASELINE = "All U.S. adults"
TRADITIONS = ["Evangelical", "Black Protestant", "Mainline", "Roman Catholic"]
REQUIRED_GROUPS = TRADITIONS + [BASELINE]

SUM_LO, SUM_HI = 98.0, 102.0


# ---------------------------------------------------------------------------
# Minimal .xlsx reader
# ---------------------------------------------------------------------------

def _col_index(ref: str) -> int:
    letters = re.match(r"([A-Z]+)", ref).group(1)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read_sheet(xlsx_path: Path, sheet_name: str = "Sheet1") -> list:
    """Return the sheet as a list of rows, each a list of cell values.

    Formula cells yield their cached value (or None). We never evaluate
    formulas - the total_check column is ignored by name anyway.
    """
    with zipfile.ZipFile(xlsx_path) as z:
        names = z.namelist()

        shared = []
        if "xl/sharedStrings.xml" in names:
            sst = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in sst.iter(NS + "si"):
                shared.append("".join(t.text or "" for t in si.iter(NS + "t")))

        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rel_target = {r.get("Id"): r.get("Target") for r in rels}

        target = None
        for sheet in wb.iter(NS + "sheet"):
            if sheet.get("name") == sheet_name:
                target = rel_target.get(sheet.get(R_NS + "id"))
                break
        if target is None:
            raise SystemExit("sheet %r not found in %s" % (sheet_name, xlsx_path))

        path = target.lstrip("/")
        if not path.startswith("xl/"):
            path = "xl/" + path
        root = ET.fromstring(z.read(path))

    rows = []
    for r in root.iter(NS + "row"):
        cells = {}
        for c in r.iter(NS + "c"):
            t = c.get("t")
            v = c.find(NS + "v")
            if t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter(NS + "t"))
            elif v is None or v.text is None or v.text == "":
                val = None
            elif t == "s":
                val = shared[int(v.text)]
            else:
                val = v.text
            cells[_col_index(c.get("r"))] = val
        width = (max(cells) + 1) if cells else 0
        rows.append([cells.get(i) for i in range(width)])
    return rows


def parse_percent(raw):
    if raw is None:
        return None
    s = str(raw).strip().replace("%", "").replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Load + validate
# ---------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.notes = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.notes.append(msg)


def load_rows(xlsx_path: Path):
    rows = read_sheet(xlsx_path)
    if not rows:
        raise SystemExit("workbook is empty")

    header = [str(h).strip() if h is not None else "" for h in rows[0]]
    idx = {name: i for i, name in enumerate(header)}
    for required in ["item_id", "statement", "year", "group"] + RESPONSES:
        if required not in idx:
            raise SystemExit(
                "missing required column %r. Found: %s" % (required, header)
            )
    # total_check is deliberately never read.

    items = {}
    order = []

    for rownum, row in enumerate(rows[1:], start=2):
        def cell(name):
            i = idx[name]
            return row[i] if i < len(row) else None

        item_id = cell("item_id")
        if item_id is None or not str(item_id).strip():
            continue
        item_id = str(item_id).strip()

        group = str(cell("group")).strip() if cell("group") is not None else ""
        statement = str(cell("statement") or "").strip()
        year_raw = cell("year")
        try:
            year = int(float(year_raw)) if year_raw is not None else None
        except (TypeError, ValueError):
            year = None

        if item_id not in items:
            items[item_id] = {
                "id": item_id,
                "statement": statement,
                "year": year,
                "rows": {},
            }
            order.append(item_id)

        items[item_id]["rows"][group] = {
            "rownum": rownum,
            "values": {r: parse_percent(cell(r)) for r in RESPONSES},
            "year": year,
        }

    return order, items


def classify(order, items, rep: Report):
    """Split items into usable / unusable, validating every filled row."""
    usable, unusable = [], []
    groups_seen = set()

    for item_id in order:
        item = items[item_id]
        problems = []
        filled, blank = [], []

        for group, row in item["rows"].items():
            groups_seen.add(group)
            vals = row["values"]
            present = [v for v in vals.values() if v is not None]
            if not present:
                blank.append(group)
                continue
            if len(present) != len(RESPONSES):
                missing = [k for k, v in vals.items() if v is None]
                problems.append(
                    "row %d (%s): partial row, missing %s"
                    % (row["rownum"], group, ", ".join(missing))
                )
                continue
            total = sum(present)
            if not (SUM_LO <= total <= SUM_HI):
                problems.append(
                    "row %d (%s): percentages sum to %g, outside %g-%g"
                    % (row["rownum"], group, total, SUM_LO, SUM_HI)
                )
                continue
            filled.append(group)

        missing_groups = [g for g in REQUIRED_GROUPS if g not in filled]
        if missing_groups:
            if len(blank) == len(item["rows"]):
                reason = "no data yet (all %d rows blank)" % len(blank)
            else:
                reason = "missing " + ", ".join(missing_groups)
            unusable.append((item_id, reason, problems))
            for p in problems:
                rep.error("%s: %s" % (item_id, p))
            continue

        for p in problems:
            rep.warn("%s: %s (extra group, ignored)" % (item_id, p))
        usable.append(item_id)

    return apply_placements(usable), unusable, groups_seen


def apply_placements(usable):
    """Relocate items per PLACE_BEFORE, preserving workbook order otherwise."""
    result = list(usable)
    for item_id, before_id in PLACE_BEFORE.items():
        if item_id in result and before_id in result:
            result.remove(item_id)
            result.insert(result.index(before_id), item_id)
    return result


# ---------------------------------------------------------------------------
# Scoring math (pure functions - mirrored in the client)
# ---------------------------------------------------------------------------

def normalize(v):
    total = sum(v)
    if total <= 0:
        return [1.0 / len(v)] * len(v)
    return [x / total for x in v]


def is_three_option(dists):
    """True when every group left both somewhat_ columns at 0.

    Per the workbook README that means the wave only published collapsed
    agree/disagree totals, so the item degrades to 3 options rather than us
    inventing a split.
    """
    i_sd = RESPONSES.index("somewhat_disagree")
    i_sa = RESPONSES.index("somewhat_agree")
    return all(d[i_sd] == 0 and d[i_sa] == 0 for d in dists.values())


def to_three(v):
    i = RESPONSES.index
    return [
        v[i("strongly_disagree")] + v[i("somewhat_disagree")],
        v[i("not_sure")],
        v[i("strongly_agree")] + v[i("somewhat_agree")],
    ]


def back_out_not_evangelical(p_all, p_e, w=EVANGELICAL_SHARE, floor=NEG_FLOOR):
    """P(r|notE) = (P(r|all) - w*P(r|E)) / (1-w), clamped and renormalized.

    "All U.S. adults" includes evangelicals, which drags every likelihood
    ratio toward 1. This removes them.
    """
    raw = [(a - w * e) / (1.0 - w) for a, e in zip(p_all, p_e)]
    clamped = [x if x > floor else floor for x in raw]
    return normalize(clamped), any(x <= floor for x in raw)


def smooth(p, floor=PROB_FLOOR):
    """Floor every probability, then renormalize. Keeps the logs finite."""
    return normalize([x if x > floor else floor for x in p])


def weights(p_e, p_note):
    return [math.log(e / n) for e, n in zip(p_e, p_note)]


def round_pct(fractions):
    """Fractions (sum to 1) -> whole percentages that sum to exactly 100.

    Plain rounding, then the rounding error is dumped on whichever bucket
    was rounded the least accurately - keeps the display total exact
    without distorting any one bucket more than necessary.
    """
    pct = [x * 100 for x in fractions]
    r = [round(x) for x in pct]
    diff = 100 - sum(r)
    if diff != 0:
        idx = (max if diff > 0 else min)(
            range(len(pct)), key=lambda i: pct[i] - r[i]
        )
        r[idx] += diff
    return r


def score_answers(answers, item_weights, shrinkage=SHRINKAGE):
    """answers: {item_id: response_index}. Unanswered items are skipped."""
    total = 0.0
    for item_id, r in answers.items():
        w = item_weights.get(item_id)
        if w is None or r is None:
            continue
        total += w[r]
    return total / shrinkage


def percentile_of(score, breakpoints):
    """Percent of the synthetic national population scoring below `score`."""
    if not breakpoints:
        return 50.0
    i = bisect_left(breakpoints, score)
    return 100.0 * i / (len(breakpoints) - 1)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build(items, usable, unusable, order, rep: Report):
    out_items = []
    item_weights = {}
    baseline_dists = {}
    three_option_ids = []

    for item_id in usable:
        item = items[item_id]
        raw = {
            g: normalize([item["rows"][g]["values"][r] for r in RESPONSES])
            for g in REQUIRED_GROUPS
        }

        three = is_three_option(raw)
        scale = RESPONSES_3 if three else RESPONSES
        if three:
            raw = {g: to_three(v) for g, v in raw.items()}
            three_option_ids.append(item_id)

        p_e = smooth(raw[EVANGELICAL])
        p_all = smooth(raw[BASELINE])
        p_note, clamped = back_out_not_evangelical(p_all, p_e)
        p_note = smooth(p_note)
        if clamped:
            rep.note(
                "%s: a not-Evangelical cell went negative and was clamped "
                "to %g" % (item_id, NEG_FLOOR)
            )

        w = weights(p_e, p_note)
        if not all(math.isfinite(x) for x in w):
            rep.error("%s: non-finite weight, item dropped" % item_id)
            continue

        item_weights[item_id] = w
        baseline_dists[item_id] = p_all

        out_items.append({
            "id": item_id,
            "statement": item["statement"],
            "year": item["year"],
            "scale": scale,
            "three_option": three,
            "w": [round(x, 6) for x in w],
            "p": {g: [round(x, 6) for x in smooth(raw[g])] for g in TRADITIONS},
            "p_all": [round(x, 6) for x in p_all],
            "p_not_evangelical": [round(x, 6) for x in p_note],
            # Unsmoothed, as-entered percentages for every group (0-2% floor
            # from `smooth()` never applied) - for the per-question group
            # breakdown chart, which shows the real numbers, not the
            # log-friendly ones the scoring math uses.
            "raw_pct": {g: round_pct(raw[g]) for g in REQUIRED_GROUPS},
        })

    if three_option_ids:
        rep.note("3-option items (collapsed in the source): "
                 + ", ".join(three_option_ids))

    kept = [it["id"] for it in out_items]
    breakpoints = simulate(kept, item_weights, baseline_dists, rep)
    years = sorted({it["year"] for it in out_items if it["year"]})

    return {
        "data_version": DATA_VERSION,
        "responses": RESPONSES,
        "responses_3": RESPONSES_3,
        "traditions": TRADITIONS,
        "baseline_group": BASELINE,
        "constants": {
            "EVANGELICAL_SHARE": EVANGELICAL_SHARE,
            "PROB_FLOOR": PROB_FLOOR,
            "NEG_FLOOR": NEG_FLOOR,
            "SHRINKAGE": SHRINKAGE,
            "SIM_N": SIM_N,
            "SIM_SEED": SIM_SEED,
            "TIE_MARGIN": TIE_MARGIN,
        },
        "years": years,
        "items": out_items,
        # Every item_id the workbook defines, and the ones that had no usable
        # data at build time. The app reads these so it can say plainly that
        # it is asking fewer questions than the instrument contains, rather
        # than quietly presenting a short quiz as the whole thing.
        "expected_items": len(order),
        "pending_items": [
            {"id": item_id, "reason": reason} for item_id, reason, _ in unusable
        ],
        "percentile_breakpoints": [round(x, 6) for x in breakpoints],
    }


def simulate(usable, item_weights, baseline_dists, rep: Report):
    """Draw SIM_N synthetic respondents from the All-U.S. distribution.

    Each answer is drawn independently, which is exactly the naive-Bayes
    assumption the scorer makes - so the percentiles are self-consistent with
    the scoring, even though real answers correlate.
    """
    if not usable:
        return []

    rng = random.Random(SIM_SEED)
    cums = {}
    for item_id in usable:
        acc, run = [], 0.0
        for x in baseline_dists[item_id]:
            run += x
            acc.append(run)
        cums[item_id] = acc

    scores = []
    for _ in range(SIM_N):
        total = 0.0
        for item_id in usable:
            acc = cums[item_id]
            r = bisect_left(acc, rng.random())
            if r >= len(acc):
                r = len(acc) - 1
            total += item_weights[item_id][r]
        scores.append(total / SHRINKAGE)

    scores.sort()
    last = len(scores) - 1
    breakpoints = [
        scores[int(round(k / PCTL_STEPS * last))] for k in range(PCTL_STEPS + 1)
    ]
    for a, b in zip(breakpoints, breakpoints[1:]):
        if b < a:
            rep.error("percentile breakpoints are not monotonic")
            break
    return breakpoints


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_report(order, usable, unusable, groups_seen, rep, blob):
    print("=" * 68)
    print("STATE OF THEOLOGY WORKBOOK - PARSE REPORT")
    print("=" * 68)
    print("items found        : %d" % len(order))
    print("items usable       : %d" % len(usable))
    print("items unusable     : %d" % len(unusable))
    print("groups present     : %s" % ", ".join(sorted(groups_seen)))
    missing_groups = [g for g in REQUIRED_GROUPS if g not in groups_seen]
    if missing_groups:
        print("groups MISSING     : %s" % ", ".join(missing_groups))
    if blob:
        print("years in usable set: %s"
              % ", ".join(str(y) for y in blob["years"]))

    if unusable:
        print("\n--- unusable items ---")
        for item_id, reason, problems in unusable:
            print("  %-26s %s" % (item_id, reason))
            for p in problems:
                print("      ! %s" % p)

    for label, msgs in (("errors", rep.errors), ("warnings", rep.warnings),
                        ("notes", rep.notes)):
        if msgs:
            print("\n--- %s ---" % label)
            for m in msgs:
                print("  %s" % m)

    if blob and blob["items"]:
        print("\n--- per-item weights  ln P(r|E) / P(r|notE) ---")
        for it in blob["items"]:
            pairs = ", ".join(
                "%s=%+.2f" % (r.replace("strongly_", "s.")
                               .replace("somewhat_", "sw."), w)
                for r, w in zip(it["scale"], it["w"])
            )
            print("  %-26s %s" % (it["id"], pairs))
        bp = blob["percentile_breakpoints"]
        if bp:
            print("\n--- synthetic population (n=%d, seed=%d) ---"
                  % (SIM_N, SIM_SEED))
            for pct in (1, 10, 25, 50, 75, 90, 99):
                print("  p%-3d score %+.3f"
                      % (pct, bp[int(pct / 100 * PCTL_STEPS)]))
    print()


def main():
    ap = argparse.ArgumentParser(description="Build the quiz probability blob.")
    ap.add_argument("--xlsx", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="where to write the JSON blob")
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    rep = Report()
    order, items = load_rows(args.xlsx)
    usable, unusable, groups_seen = classify(order, items, rep)
    blob = build(items, usable, unusable, order, rep) if usable else None

    if not args.quiet:
        print_report(order, usable, unusable, groups_seen, rep, blob)

    if args.report_only:
        return 0 if not rep.errors else 1

    if not blob or not blob["items"]:
        sys.stderr.write("REFUSING TO EMIT: no usable items.\n")
        return 2

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(blob, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if not args.quiet:
            print("wrote %s (%d items, %d breakpoints)"
                  % (args.out, len(blob["items"]),
                     len(blob["percentile_breakpoints"])))
    else:
        sys.stdout.write(json.dumps(blob, ensure_ascii=False, indent=2))

    return 1 if rep.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
