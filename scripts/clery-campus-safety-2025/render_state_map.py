#!/usr/bin/env python3
"""Renders the state heat maps of reported on-campus rapes per 10,000 students.

Geometry: docs/datasets/clery-campus-safety-2025/us-state-paths.json (written by
export-us-state-paths.mjs from the same Albers USA outlines as the site's state map).
Data: state-rates.json (written by analyze.py). Banding, ramp, zero/no-data swatches
follow src/components/map/classes.ts and docs/MAPS.md.

Usage:
  python scripts/clery-campus-safety-2025/render_state_map.py \
    --out-dir public/data-explorer/clery-campus-safety-2025
"""
import argparse
import json
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "flagship-charts"))
sys.path.insert(0, str(HERE.parent))
from common import FIG_H_IN, FIG_W_IN, DPI, INK, MUTED, PAPER, _draw_title, load_fonts  # noqa: E402
from chart_style import draw_caption_bottom  # noqa: E402

DATA = HERE.parent.parent / "docs" / "datasets" / "clery-campus-safety-2025"
HANDLE = "@ithinkisam | data: U.S. Dept. of Education, Clery Act 2025"
DISCLAIMER = ("These figures represent incidents reported under the Clery Act, not estimates of the actual "
              "prevalence of sexual assault. Differences may reflect both differences in victimization and "
              "differences in reporting practices.")

# docs/MAPS.md palette (same hex as src/components/map/classes.ts)
RAMP = ["#fde9a9", "#f6b95b", "#e4762f", "#b7372b", "#5b1230"]
ZERO_FILL = "#e4e1da"
ABBR = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
        "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA",
        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
        "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
        "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
        "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
        "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
        "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
        "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}
TINY = {"DC", "DE", "RI", "CT", "NJ", "MD", "MA", "NH", "VT"}  # no room for a label inside the shape

DIGITS = [1, 5, 2, 2.5, 3, 4, 6, 8, 1.5, 7.5]


def roundest(lo, hi):
    """Roundest number in (lo, hi] (port of roundest() in classes.ts, non-integer case)."""
    import math
    best = None
    top = math.ceil(math.log10(hi))
    for m in range(top, math.floor(math.log10(lo)) - 3, -1):
        for rank, d in enumerate(DIGITS):
            n = float(f"{d * 10 ** m:.12g}")
            if n <= lo or n > hi:
                continue
            if best is None or rank < best[1] or (rank == best[1] and n > best[0]):
                best = (n, rank)
    return best or (hi, len(DIGITS))


def classify_once(values, tol_frac):
    """Up to five bands with round cut-offs holding roughly equal numbers of states (classes.ts)."""
    positive = sorted(v for v in values if v > 0)
    n = len(RAMP)
    uniq, before = [], []
    for i, v in enumerate(positive):
        if not uniq or uniq[-1] != v:
            uniq.append(v)
            before.append(i)
    cut = []
    prev = 0
    for j in range(1, n):
        target = j * len(positive) / n
        tol = tol_frac * len(positive) / n
        max_idx = len(uniq) - (n - j)
        best_idx, best_score = prev + 1, float("inf")
        for idx in range(prev + 1, max_idx + 1):
            dev = abs(before[idx] - target)
            score = roundest(uniq[idx - 1], uniq[idx])[1] * 1e6 + dev if dev <= tol else 1e12 + dev
            if score < best_score:
                best_score, best_idx = score, idx
        cut.append(best_idx)
        prev = best_idx
    picks = [roundest(uniq[i - 1], uniq[i]) for i in cut]
    return [p[0] for p in picks], all(p[1] < len(DIGITS) for p in picks)


def classify(values):
    """classes.ts uses a 30% tolerance. With only 51 states a round cut-off sometimes isn't that close,
    so widen the tolerance (still five bands, still no value moved by rounding) until every cut is round."""
    for tol in (0.3, 0.45, 0.6, 0.8, 1.0):
        breaks, ok = classify_once(values, tol)
        if ok:
            return breaks
    return breaks


def fmt(v):
    return f"{v:g}"


def band_labels(breaks):
    k = len(breaks) + 1
    out = []
    for i in range(k):
        if i == 0:
            out.append(f"Under {fmt(breaks[0])}")
        elif i == k - 1:
            out.append(f"{fmt(breaks[-1])}+")
        else:
            out.append(f"{fmt(breaks[i - 1])}–{fmt(breaks[i])}")
    return out


def parse_path(d):
    """d3 geoPath output (M/L/Z only) -> (matplotlib Path, polygons)."""
    verts, codes, polys, cur = [], [], [], None
    for cmd, args in re.findall(r"([MLZ])([^MLZ]*)", d):
        if cmd == "Z":
            if cur:
                verts.append(cur[0])
                codes.append(MPath.CLOSEPOLY)
                polys.append(cur)
            cur = None
            continue
        for k, pair in enumerate(re.findall(r"-?[\d.]+(?:e-?\d+)?,-?[\d.]+(?:e-?\d+)?", args)):
            x, y = (float(t) for t in pair.split(","))
            verts.append((x, 600 - y))
            codes.append(MPath.MOVETO if cmd == "M" and k == 0 else MPath.LINETO)
            if cmd == "M" and k == 0:
                cur = []
            cur.append((x, 600 - y))
    return MPath(verts, codes), polys


def polygon_center(polys):
    big = max(polys, key=lambda p: (max(x for x, _ in p) - min(x for x, _ in p)) * (max(y for _, y in p) - min(y for _, y in p)))
    xs, ys = [x for x, _ in big], [y for _, y in big]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def render(rates, key, title, subtitle, out, fonts, circle=None):
    states = rates[key]
    by_name = {v["state"]: v for v in states.values()}
    geo = json.loads((DATA / "us-state-paths.json").read_text(encoding="utf-8"))
    values = [v["rate_per_10k"] for v in by_name.values()] + ([circle["rate"]] if circle else [])
    breaks = classify(values)
    labels = band_labels(breaks)

    def band(v):
        i = 0
        while i < len(breaks) and v >= breaks[i]:
            i += 1
        return i

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    sub_bottom = _draw_title(fig, fonts, title, subtitle)
    cap_top = draw_caption_bottom(fig, fonts, [DISCLAIMER], handle=HANDLE, fontsize=14, color=INK,
                                  wrap_width=80, line_step=0.0185)

    ranked = sorted(by_name.values(), key=lambda v: -v["rate_per_10k"])[:10]
    rank_h = 0.0225 * 5 + 0.02
    rank_bottom = cap_top + 0.02
    key_y = rank_bottom + rank_h + 0.012
    map_bottom = key_y + 0.04
    map_h = sub_bottom - 0.02 - map_bottom
    ax = fig.add_axes([0.03, map_bottom, 0.94, map_h])
    ax.set_xlim(0, geo["width"])
    ax.set_ylim(0, geo["height"])
    ax.set_aspect("equal")
    ax.axis("off")
    labels_to_draw = []
    for name, d in geo["shapes"].items():
        path, polys = parse_path(d)
        v = by_name[name]["rate_per_10k"]
        fill = ZERO_FILL if v <= 0 else RAMP[band(v)]
        ax.add_patch(PathPatch(path, facecolor=fill, edgecolor=PAPER, lw=1.1))
        ab = ABBR[name]
        if ab not in TINY:
            cx, cy = polygon_center(polys)
            cx += {"FL": 32, "LA": -6, "MI": 8}.get(ab, 0)
            dark = v > 0 and band(v) >= 3
            labels_to_draw.append((cx, cy, ab, PAPER if dark else INK))
    for cx, cy, ab, col in labels_to_draw:  # after every shape so no neighbor paints over a label
        ax.text(cx, cy, ab, ha="center", va="center", fontsize=10.5, fontproperties=fonts["bold"], color=col, zorder=5)

    if circle:  # a campus shown on its own, as a circle off the Atlantic coast
        from matplotlib.patches import Circle
        cx, cy, r = 905, 600 - 462, 36
        v = circle["rate"]
        ax.add_patch(Circle((cx, cy), r, facecolor=ZERO_FILL if v <= 0 else RAMP[band(v)], edgecolor=PAPER, lw=1.5, zorder=4))
        ax.text(cx, cy, f"{v:.1f}", ha="center", va="center", fontsize=15, fontproperties=fonts["bold"],
                color=PAPER if (v > 0 and band(v) >= 3) else INK, zorder=5)
        ax.text(cx, cy - r - 8, circle["label"], ha="center", va="top", fontsize=11.5, fontproperties=fonts["bold"],
                color=INK, zorder=5, linespacing=1.15)

    # key: five swatches in one row
    sw_w, sw_h, x = 0.025, 0.014, 0.065
    for i, lab in enumerate(labels):
        fig.patches.append(plt.Rectangle((x, key_y), sw_w, sw_h, transform=fig.transFigure, fc=RAMP[i], ec="none"))
        fig.text(x + sw_w + 0.008, key_y + sw_h / 2, lab, va="center", ha="left", fontproperties=fonts["regular"],
                 fontsize=15, color=INK)
        x += 0.175 if i < 4 else 0
    fig.text(0.065, key_y + 0.028, "Reported on-campus rapes per 10,000 students",
             fontproperties=fonts["bold"], fontsize=14, color=INK, va="center")

    # top 10, two columns
    fig.text(0.065, rank_bottom + rank_h - 0.002, "Highest ten states", fontproperties=fonts["bold"], fontsize=14,
             color=INK, va="top")
    for i, v in enumerate(ranked):
        col, row = divmod(i, 5)
        xx = 0.065 + col * 0.46
        yy = rank_bottom + rank_h - 0.026 - row * 0.0215
        fig.text(xx, yy, f"{i + 1}. {v['state']}", fontproperties=fonts["regular"], fontsize=15, color=INK, va="top")
        fig.text(xx + 0.40, yy, f"{v['rate_per_10k']:.1f}", fontproperties=fonts["bold"], fontsize=15, color=INK,
                 va="top", ha="right")
    fig.savefig(out, dpi=DPI, facecolor=PAPER)
    plt.close(fig)
    print("wrote", out, "bands", breaks)


def main_ex_uofu(rates, out_dir, fonts):
    u = rates["uofu"]
    for key, rkey, per, sub in (("rate_2022_24_ex_uofu", "rate_2022_24", "2022–2024", "Three-year Clery Act average."),
                                ("rate_2024_ex_uofu", "rate_2024", "2024", "Clery Act reports.")):
        render(rates, key, f"Reported On-Campus Rapes per 10,000 Students by State, {per}",
               "Utah excludes the University of Utah, shown as the circle." + chr(10) + sub + " All other four-year institutions pooled.",
               out_dir / f"state-map-reported-rapes-per-10k-{'2022-24' if '22' in rkey else '2024'}-without-university-of-utah.png",
               fonts, circle={"rate": u[rkey], "label": "University" + chr(10) + "of Utah"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    fonts = load_fonts()
    rates = json.loads((DATA / "state-rates.json").read_text(encoding="utf-8"))
    render(rates, "rate_2022_24", "Reported On-Campus Rapes per 10,000 Students by State, 2022–2024",
           "Three-year Clery Act average. All four-year institutions in each state, pooled.",
           args.out_dir / "state-map-reported-rapes-per-10k-2022-24.png", fonts)
    render(rates, "rate_2024", "Reported On-Campus Rapes per 10,000 Students by State, 2024",
           "Clery Act reports. All four-year institutions in each state, pooled.",
           args.out_dir / "state-map-reported-rapes-per-10k-2024.png", fonts)
    main_ex_uofu(rates, args.out_dir, fonts)


if __name__ == "__main__":
    main()
