#!/usr/bin/env python3
"""Build the probability blob for the "How Evangelical Are You?" quiz.

Reads the State of Theology workbook, validates it, derives the
NOT-Evangelical distribution, smooths, computes per-answer log-likelihood
weights, scores the real 2025 respondent microdata with those weights to
build empirical (all-adults and per-tradition) percentile curves, and emits
a JSON blob for the client-side scorer.

Standard library only, on purpose - no openpyxl, no pandas - so this runs
anywhere Python 3.9+ does with nothing installed.

Usage:
    python build_data.py --xlsx workbook.xlsx --csv responses-2025.csv \
        --out ../../src/lib/evangelical-quiz/data.json
    python build_data.py --xlsx workbook.xlsx --csv responses-2025.csv \
        --report-only
    python build_data.py --xlsx workbook.xlsx --fetch --out ...   # fetches
        # the CSV to --csv's path (default data/state-of-theology/) if absent
"""

from __future__ import annotations

import argparse
import csv as csvlib
import json
import math
import re
import sys
import urllib.request
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
SHRINKAGE = 2.5            # divides the summed score; the items correlate.
                           # Rank-preserving, so it has no effect on any
                           # percentile - it only scales the stored score and
                           # the per-question breakdown display.
TIE_MARGIN = 0.25          # nats; top-two traditions closer than this = a tie
PCTL_STEPS = 200           # breakpoints stored per curve: 0, 0.5, 1.0 ... 100
CROSSCHECK_TOL = 1.5       # pct points; workbook cells are whole-number
                           # rounded (observed max rounding drift: 1.0 pt),
                           # so a real item/group mismatch (tens of points)
                           # is unmistakable against this tolerance

DATA_VERSION = "3"         # bump when the workbook or this math changes
                           # (2: arian moved into the christology block;
                           # 3: percentiles are now empirical - scored from
                           # the real 2025 respondent microdata instead of an
                           # independent-draw synthetic population, with a
                           # curve per religious tradition. arian is excluded
                           # from the percentile score, since the 2025 wave
                           # never asked it.)

# The 2025-wave respondent microdata this build scores for the empirical
# percentile curves. One row per respondent; Q21_1..Q30_4 are the 35
# statement columns (1=Strongly Agree .. 5=Not Sure), WT is the survey
# weight, RELTRAD is the report's religious-tradition code, EVB flags the
# survey's own belief-based "Evangelical by belief" (NAE definition) group.
CSV_URL = "https://thestateoftheology.com/assets/data/us/responses-2025.csv"
CSV_DEFAULT = Path(__file__).resolve().parents[2] / "data/state-of-theology/responses-2025.csv"

# CSV code (1=Strongly Agree .. 5=Not Sure) -> index into RESPONSES
# (strongly_disagree, somewhat_disagree, not_sure, somewhat_agree, strongly_agree)
CODE_TO_INDEX = {4: 0, 3: 1, 5: 2, 2: 3, 1: 4}

# The 35 2025-wave statement columns, in survey order. This is the order the
# workbook's rows were "pasted straight across" from (per the workbook
# README), i.e. the usable item list with `arian` removed - arian is the one
# 2022-wave item, dropped from the 2025 instrument, so no 2025 respondent
# has an answer for it. crosscheck_workbook() proves this mapping is right
# by reproducing the workbook's own published percentages from the CSV.
QCOLS = [
    col
    for screen, count in (
        (21, 4), (22, 4), (23, 3), (24, 4), (25, 3),
        (26, 3), (27, 3), (28, 4), (29, 3), (30, 4),
    )
    for col in (f"Q{screen}_{i}" for i in range(1, count + 1))
]

# Reference groups the empirical percentile is offered against. `member`
# takes a CSV row and returns whether it belongs. RELTRAD codes verified
# against the shipped workbook data itself (crosscheck_workbook): 1 =
# Evangelical, 2 = Black Protestant, 3 = Mainline, 4 = Roman Catholic, 5 =
# Other faiths & the unaffiliated - matching this build's own `Evangelical`
# / `Black Protestant` / `Mainline` / `Roman Catholic` workbook groups
# exactly, not the survey's separate belief-based EVB flag (see
# evangelical_by_belief below, which uses EVB and is kept distinct).
REFERENCE_GROUPS = [
    ("all", "All Americans", lambda r: True),
    ("evangelical", "Evangelicals", lambda r: r["RELTRAD"] == "1"),
    ("non_evangelical", "Non-evangelicals", lambda r: r["RELTRAD"] != "1"),
    ("black_protestant", "Black Protestants", lambda r: r["RELTRAD"] == "2"),
    ("mainline", "Mainline Protestants", lambda r: r["RELTRAD"] == "3"),
    ("catholic", "Roman Catholics", lambda r: r["RELTRAD"] == "4"),
    ("other_none", "Other faiths & the unaffiliated", lambda r: r["RELTRAD"] == "5"),
    ("evangelical_by_belief", "Evangelicals by belief (NAE definition)",
     lambda r: r["EVB"] == "1"),
]

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
    """Percent of the reference group scoring below `score`."""
    if not breakpoints:
        return 50.0
    i = bisect_left(breakpoints, score)
    return 100.0 * i / (len(breakpoints) - 1)


# ---------------------------------------------------------------------------
# Respondent microdata: empirical percentile curves
# ---------------------------------------------------------------------------

def load_microdata(csv_path: Path, rep: Report):
    """Load and validate the State of Theology respondent CSV.

    Every Q-column must be present with an integer 1-5 in every row (the
    2025 file has none blank; a future wave dropping items would need this
    revisited), and every WT must parse as a positive float.
    """
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csvlib.DictReader(f))

    if not rows:
        raise SystemExit("microdata CSV %s is empty" % csv_path)

    required = QCOLS + ["WT", "RELTRAD", "EVB"]
    missing = [c for c in required if c not in rows[0]]
    if missing:
        raise SystemExit(
            "microdata CSV missing required column(s): %s" % ", ".join(missing)
        )

    for i, row in enumerate(rows, start=2):
        for col in QCOLS:
            v = row.get(col, "").strip()
            if v not in {"1", "2", "3", "4", "5"}:
                raise SystemExit(
                    "microdata CSV row %d: %s=%r is not an integer 1-5"
                    % (i, col, row.get(col))
                )
        try:
            wt = float(row["WT"])
        except (TypeError, ValueError):
            wt = -1
        if wt <= 0:
            raise SystemExit("microdata CSV row %d: WT=%r is not > 0"
                              % (i, row.get("WT")))

    rep.note("microdata: %d respondents loaded from %s" % (len(rows), csv_path))
    return rows


def qcol_mapping(usable):
    """The 35 2025-wave item ids, in workbook/survey row order, paired with
    their CSV column. `usable` is build()'s post-placement item order;
    `arian` is the only item PLACE_BEFORE ever moves, so removing it here
    recovers the original per-row order for every other item.
    """
    ids_2025 = [item_id for item_id in usable if item_id != "arian"]
    if len(ids_2025) != len(QCOLS):
        raise SystemExit(
            "expected 35 2025-wave items to map onto the 35 QCOLS, got %d "
            "(%s) - has an item been added/removed from the 2025 wave?"
            % (len(ids_2025), ", ".join(ids_2025))
        )
    return dict(zip(ids_2025, QCOLS))


def weighted_group_dist(rows, col, member, scale_len):
    """WT-weighted response percentage distribution for `member` rows."""
    acc = [0.0] * scale_len
    total = 0.0
    for row in rows:
        if not member(row):
            continue
        idx = CODE_TO_INDEX[int(row[col])]
        w = float(row["WT"])
        acc[idx] += w
        total += w
    if total <= 0:
        return None
    return [100.0 * x / total for x in acc]


# Workbook group name -> REFERENCE_GROUPS predicate, for the crosscheck.
# Deliberately restricted to the four traditions + baseline the workbook
# itself carries; evangelical_by_belief and non_evangelical aren't workbook
# groups, so there's nothing to cross-check them against.
_CROSSCHECK_GROUPS = {
    "Evangelical": lambda r: r["RELTRAD"] == "1",
    "Black Protestant": lambda r: r["RELTRAD"] == "2",
    "Mainline": lambda r: r["RELTRAD"] == "3",
    "Roman Catholic": lambda r: r["RELTRAD"] == "4",
    "All U.S. adults": lambda r: True,
}


def crosscheck_workbook(out_items, rows, q_of, rep: Report):
    """Reproduce every 2025-wave item's workbook percentages from the CSV.

    This is what actually proves qcol_mapping() lines up the right survey
    column with the right item, and that RELTRAD really means what
    REFERENCE_GROUPS assumes it means - a wrong mapping would show up here
    as a wild (tens-of-points) mismatch, not the ~1pt rounding noise a
    correct mapping produces.
    """
    checked = 0
    max_dev = 0.0
    for item in out_items:
        item_id = item["id"]
        col = q_of.get(item_id)
        if col is None:  # arian: 2022-only, not in the 2025 microdata
            continue
        for group, member in _CROSSCHECK_GROUPS.items():
            expected = item["raw_pct"].get(group)
            if expected is None:
                continue
            computed = weighted_group_dist(rows, col, member, len(expected))
            if computed is None:
                rep.error("%s/%s: no CSV respondents matched" % (item_id, group))
                continue
            dev = max(abs(a - b) for a, b in zip(expected, computed))
            max_dev = max(max_dev, dev)
            checked += 1
            if dev > CROSSCHECK_TOL:
                rep.error(
                    "%s/%s: workbook says %s, CSV recomputes %s (%.2f pt off, "
                    "tolerance %.2f) - check qcol_mapping / RELTRAD coding"
                    % (item_id, group, expected,
                       [round(x, 1) for x in computed], dev, CROSSCHECK_TOL)
                )
    rep.note("crosscheck: %d item/group cells compared, max deviation %.2f pt"
              % (checked, max_dev))
    return checked, max_dev


def score_respondent(row, q_of, item_weights, three_option_ids, shrinkage=SHRINKAGE):
    """Score one CSV respondent with the same weights the app uses.

    Mirrors score_answers(): sum w[i][r] over every percentile item, divided
    by SHRINKAGE. `r` collapses to the 3-option scale for any item that
    degraded to one (none currently do, but this keeps the two scorers
    consistent if a future wave introduces one).
    """
    total = 0.0
    for item_id, col in q_of.items():
        w = item_weights.get(item_id)
        if w is None:
            continue
        idx = CODE_TO_INDEX[int(row[col])]
        if item_id in three_option_ids:
            idx = {0: 0, 1: 0, 2: 1, 3: 2, 4: 2}[idx]
        total += w[idx]
    return total / shrinkage


def weighted_quantile_curve(scored, steps=PCTL_STEPS):
    """PCTL_STEPS+1 evenly-spaced weighted-quantile breakpoints.

    Deterministic (no RNG): sort (score, weight) pairs and walk the
    cumulative weight, so identical input always produces byte-identical
    output.
    """
    pairs = sorted(scored)
    total = sum(w for _, w in pairs)
    if total <= 0 or not pairs:
        return []
    cum = 0.0
    cum_scores = []
    for score, w in pairs:
        cum += w
        cum_scores.append((cum, score))
    breakpoints = []
    for k in range(steps + 1):
        target = (k / steps) * total
        i = bisect_left(cum_scores, (target, float("-inf")))
        if i >= len(cum_scores):
            i = len(cum_scores) - 1
        breakpoints.append(cum_scores[i][1])
    return breakpoints


def empirical_curves(rows, q_of, item_weights, three_option_ids, rep: Report):
    """Score every respondent, once, and build each REFERENCE_GROUPS curve
    from the same scores - so every curve is self-consistent with the
    others (an Evangelical is also one of the "All Americans" respondents).
    """
    scored_all = [
        (score_respondent(row, q_of, item_weights, three_option_ids), float(row["WT"]))
        for row in rows
    ]

    groups = {}
    for key, label, member in REFERENCE_GROUPS:
        subset = [(s, w) for (s, w), row in zip(scored_all, rows) if member(row)]
        n = sum(1 for row in rows if member(row))
        if n == 0:
            rep.error("reference group %r matched zero respondents" % key)
            continue
        curve = weighted_quantile_curve(subset)
        for a, b in zip(curve, curve[1:]):
            if b < a:
                rep.error("%s: percentile curve is not monotonic" % key)
                break
        groups[key] = {"label": label, "n": n, "curve": [round(x, 6) for x in curve]}

    reltrad_n = sum(groups[k]["n"] for k in
                     ("evangelical", "black_protestant", "mainline", "catholic", "other_none")
                     if k in groups)
    if "all" in groups and reltrad_n != groups["all"]["n"]:
        rep.error("RELTRAD group counts (%d) don't sum to the All-Americans "
                  "count (%d)" % (reltrad_n, groups["all"]["n"]))

    return {
        "source": "State of Theology 2025 respondent microdata",
        "url": CSV_URL,
        "n": len(rows),
        "group_order": [key for key, _, _ in REFERENCE_GROUPS],
        "groups": groups,
    }


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build(items, usable, unusable, order, rep: Report, microdata_rows=None):
    out_items = []
    item_weights = {}
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

    years = sorted({it["year"] for it in out_items if it["year"]})

    percentile_items = [it["id"] for it in out_items if it["id"] != "arian"]

    reference = None
    if microdata_rows is not None:
        q_of = qcol_mapping(usable)
        crosscheck_workbook(out_items, microdata_rows, q_of, rep)
        percentile_item_weights = {k: v for k, v in item_weights.items() if k != "arian"}
        reference = empirical_curves(
            microdata_rows, q_of, percentile_item_weights, three_option_ids, rep
        )

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
        # The items counted in the percentile score - every usable item
        # except `arian` (2022-only; the 2025 respondents behind `reference`
        # below were never asked it, so it can't be scored against them).
        "percentile_items": percentile_items,
        "reference": reference,
    }


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
        ref = blob.get("reference")
        if ref:
            print("\n--- reference population (%s, n=%d) ---"
                  % (ref["source"], ref["n"]))
            for key in ref["group_order"]:
                g = ref["groups"].get(key)
                if not g:
                    continue
                curve = g["curve"]
                landmarks = ", ".join(
                    "p%d=%+.2f" % (pct, curve[int(pct / 100 * PCTL_STEPS)])
                    for pct in (1, 10, 25, 50, 75, 90, 99)
                )
                print("  %-24s n=%-5d %s" % (g["label"], g["n"], landmarks))
    print()


def main():
    ap = argparse.ArgumentParser(description="Build the quiz probability blob.")
    ap.add_argument("--xlsx", required=True, type=Path)
    ap.add_argument("--csv", type=Path, default=CSV_DEFAULT,
                     help="State of Theology 2025 respondent microdata, for "
                          "the empirical percentile curves (default: %s)"
                          % CSV_DEFAULT)
    ap.add_argument("--fetch", action="store_true",
                     help="download --csv from %s if the path doesn't "
                          "already exist" % CSV_URL)
    ap.add_argument("--out", type=Path, help="where to write the JSON blob")
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    rep = Report()
    order, items = load_rows(args.xlsx)
    usable, unusable, groups_seen = classify(order, items, rep)

    microdata_rows = None
    if usable:
        if args.fetch and not args.csv.exists():
            args.csv.parent.mkdir(parents=True, exist_ok=True)
            if not args.quiet:
                print("fetching %s -> %s" % (CSV_URL, args.csv))
            urllib.request.urlretrieve(CSV_URL, args.csv)
        if not args.csv.exists():
            raise SystemExit(
                "microdata CSV not found at %s (pass --csv, or --fetch to "
                "download it from %s)" % (args.csv, CSV_URL)
            )
        microdata_rows = load_microdata(args.csv, rep)

    blob = build(items, usable, unusable, order, rep, microdata_rows) if usable else None

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
            print("wrote %s (%d items, %d percentile items, %d reference groups)"
                  % (args.out, len(blob["items"]), len(blob["percentile_items"]),
                     len(blob["reference"]["groups"]) if blob["reference"] else 0))
    else:
        sys.stdout.write(json.dumps(blob, ensure_ascii=False, indent=2))

    return 1 if rep.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
