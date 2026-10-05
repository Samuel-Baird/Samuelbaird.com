#!/usr/bin/env python3
"""Renders the five Clery Act reported-rape charts from the JSON written by
analyze.py (docs/datasets/clery-campus-safety-2025/). No number is typed here.

Bar charts reuse flagship-charts/common.render_magnitude_bar; the scatter and
histogram are drawn directly with the same canvas, fonts, and caption helper.
BYU is the one --accent bar/point; everything else is context gray.

Usage:
  python scripts/clery-campus-safety-2025/render.py \
    --out-dir public/data-explorer/clery-campus-safety-2025
"""
import argparse
import json
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "flagship-charts"))
sys.path.insert(0, str(HERE.parent))
from common import (  # noqa: E402
    ACCENT, CONTEXT_GRAY, DPI, FIG_H_IN, FIG_W_IN, INK, MUTED, PAPER,
    _draw_title, load_fonts, render_magnitude_bar,
)
from chart_style import BORDER, draw_caption_bottom  # noqa: E402

DATA = HERE.parent.parent / "docs" / "datasets" / "clery-campus-safety-2025"
HANDLE = "@ithinkisam | data: U.S. Dept. of Education, Clery Act 2025"
BYU_ID = "230038"
BYU_LABEL = "Brigham Young University"

SHORT = [
    (r"^Louisiana State University and Agricultural & Mechanical College$", "Louisiana State University"),
    (r"^California State Polytechnic University-Humboldt$", "Cal Poly Humboldt"),
    (r"^Pennsylvania State University-Main Campus$", "Penn State (Main Campus)"),
    (r"^Pennsylvania State University-Penn State (.*)$", r"Penn State \1"),
    (r"^Ohio State University-Main Campus$", "Ohio State University"),
    (r"^University of Cincinnati-Main Campus$", "University of Cincinnati"),
    (r"^University of New Hampshire-Main Campus$", "Univ. of New Hampshire"),
    (r"^Mayo Clinic College of Medicine and Science$", "Mayo Clinic Coll. of Medicine"),
    (r"^Arizona State University Campus Immersion$", "Arizona State University"),
    (r"^University of California-", "UC "),
    (r"^Indiana University-", "Indiana University "),
    (r"^Brigham Young University$", BYU_LABEL),
    (r"^The ", ""),
    (r"^State University of New York at ", "SUNY "),
    (r"^SUNY ", "SUNY "),
    (r"^Hobart William Smith Colleges$", "Hobart & William Smith"),
]


def short(name: str) -> str:
    for pat, rep in SHORT:
        name = re.sub(pat, rep, name)
    return name


def uniq_labels(rows):
    """Short label per row, de-duplicated (two institutions can shorten alike)."""
    seen, out = {}, []
    for r in rows:
        lab = short(r["name"])
        seen[lab] = seen.get(lab, 0) + 1
        out.append(lab if seen[lab] == 1 else f"{lab} ({r['state']})")
    return out


def bar_chart(*, rows, byu, value_key, title, subtitle, out, fonts, decimals, extra_rows=(), rank_key):
    """rows: top-30 records; byu appended if not already present."""
    ids = [r["unitid"] for r in rows]
    labels = uniq_labels(rows)
    values = {l: r[value_key] for l, r in zip(labels, rows)}
    order = list(labels)
    colors = {l: (ACCENT if r["unitid"] == BYU_ID else CONTEXT_GRAY) for l, r in zip(labels, rows)}
    if BYU_ID not in ids:
        lab = f"{BYU_LABEL} (#{byu[rank_key]:,})"
        order.append(lab)
        values[lab] = byu[value_key]
        colors[lab] = ACCENT
    for lab, val, col in extra_rows:  # (label, value, color) inserted by value
        values[lab] = val
        colors[lab] = col
        idx = next((i for i, l in enumerate(order) if values[l] < val), len(order))
        order.insert(idx, lab)
    render_magnitude_bar(
        rows=order, values=values, highlight_rows=None, row_colors=colors,
        title=title, subtitle=subtitle, caption_paragraphs=[], handle=HANDLE, out_path=out, fonts=fonts,
        value_suffix="", value_decimals=decimals, axes_left=0.40,
        row_label_fontsize=12.5, value_label_fontsize=12.5, bar_h_override=0.72, margin_frac_override=0.015,
    )


FONTS = {}


def stat_box(ax, lines, x=0.97, y=0.97):
    ax.text(x, y, "\n".join(lines), transform=ax.transAxes, ha="right", va="top", linespacing=1.45,
            fontproperties=FONTS["regular"], fontsize=15, color=INK, bbox=dict(boxstyle="square,pad=0.6", fc=PAPER, ec=BORDER, lw=1))


def scatter_chart(out, fonts):
    d = json.loads((DATA / "scatter-2024.json").read_text(encoding="utf-8"))
    pts = d["points"]
    XCAP = 85000
    n_off = sum(p["enrollment"] > XCAP for p in pts)
    pts_all, pts = pts, [p for p in pts if p["enrollment"] <= XCAP]
    x = np.array([p["enrollment"] for p in pts])
    y = np.array([p["rape24"] for p in pts])
    z = np.array([p["resid_z"] for p in pts])
    rate = d["pooled_rate_per_10k"]

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    sub_bottom = _draw_title(fig, fonts, "Campus Size and Reported Rapes at U.S. Universities",
                             "2024 Clery Act reports. One dot per four-year institution with\n"
                             f"at least {d['min_enrollment']:,} students ({len(pts):,} institutions).")
    cap_top = draw_caption_bottom(
        fig, fonts,
        [f"Line = expected reports if every campus reported at the pooled national rate "
         f"({rate:.1f} per 10,000 students); shaded band = 95% Poisson range around it. "
         "Labeled dots are the largest departures above the line, plus BYU and Cornell for comparison. "
         f"{n_off} very large, mostly online, institutions (enrollment above {XCAP:,}) are off the right edge; each reported 13 or fewer."],
        handle=HANDLE, fontsize=14, color=INK, wrap_width=80, line_step=0.0185)
    ax = fig.add_axes([0.14, cap_top + 0.075, 0.82, sub_bottom - cap_top - 0.105])
    ax.set_facecolor(PAPER)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.grid(color=BORDER, lw=0.8)
    ax.set_axisbelow(True)

    xs = np.linspace(0, XCAP, 200)
    exp = rate / 1e4 * xs
    ax.fill_between(xs, np.maximum(exp - 1.96 * np.sqrt(exp), 0), exp + 1.96 * np.sqrt(exp) + 1,
                    color=CONTEXT_GRAY, alpha=0.18, lw=0)
    ax.plot(xs, exp, color=INK, lw=2)
    ax.scatter(x, y, s=22, color=CONTEXT_GRAY, alpha=0.65, lw=0, zorder=3)

    byu = next(p for p in pts if p["unitid"] == BYU_ID)
    cornell = next(p for p in pts if p["unitid"] == "190415")
    ax.scatter([byu["enrollment"]], [byu["rape24"]], s=170, color=ACCENT, ec=PAPER, lw=1.5, zorder=5)
    ax.scatter([cornell["enrollment"]], [cornell["rape24"]], s=90, color=INK, ec=PAPER, lw=1.2, zorder=4)

    top = sorted(pts, key=lambda p: -abs(p["resid_z"]))
    over = [p for p in top if p["resid_z"] > 0][:6]
    under = []
    # (label, dx, dy in points, ha) hand-placed to avoid collisions
    place = {
        "230764": (9, -3, "left"), "126614": (9, -3, "left"), "151111": (9, -3, "left"),
        "173957": (9, 66, "left"), "182670": (9, 8, "left"), "115755": (9, 6, "left"),
        "110714": (9, 6, "left"), "190415": (12, -16, "left"), BYU_ID: (12, -6, "left"),
    }
    done = set()
    for p in over + under + [byu, cornell]:
        if p["unitid"] in done:
            continue
        done.add(p["unitid"])
        dx, dy, ha = place.get(p["unitid"], (8, 4, "left"))
        lab = short(p["name"]) if p["unitid"] != BYU_ID else "BYU"
        if p["unitid"] == "190415":
            lab = "Cornell"
        ax.annotate(f"{lab} ({p['rape24']})", (p["enrollment"], p["rape24"]), xytext=(dx, dy),
                    textcoords="offset points", ha=ha, fontsize=12.5,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkA=2, shrinkB=4),
                    fontproperties=fonts["bold" if p["unitid"] in (BYU_ID, "190415") else "regular"],
                    color=ACCENT if p["unitid"] == BYU_ID else INK, zorder=6)
    ax.set_xlim(0, XCAP)
    ax.set_ylim(0, y.max() * 1.08)
    ax.xaxis.set_major_formatter(lambda v, _: f"{int(v/1000)}k" if v else "0")
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontproperties(fonts["regular"])
        lab.set_fontsize(13)
    ax.set_xlabel("Total enrollment", fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.set_ylabel("Reported on-campus rapes, 2024", fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.text(xs.max() * 0.98, rate / 1e4 * xs.max() * 0.98 + 6, "Expected at national rate", ha="right", va="bottom",
            fontproperties=fonts["bold"], fontsize=13, color=INK)
    fig.savefig(out, dpi=DPI, facecolor=PAPER)
    plt.close(fig)


def hist_chart(out, fonts):
    h = json.loads((DATA / "histogram-2024.json").read_text(encoding="utf-8"))
    s = json.loads((DATA / "stats.json").read_text(encoding="utf-8"))
    rates = np.array(h["rates"])
    b = s["byu"]
    dist = s["distribution_ge_5000_2024"]

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    sub_bottom = _draw_title(fig, fonts, "Where BYU Falls Among U.S. Universities",
                             "Reported on-campus rapes per 10,000 students, 2024.\n"
                             f"{len(rates)} four-year institutions with at least {h['min_enrollment']:,} students.")
    cap_top = draw_caption_bottom(
        fig, fonts,
        [f"Percentile = share of institutions reporting a lower rate than BYU. {dist['share_zero']:.0f}% of institutions "
         "reported zero. Rates above 20 per 10,000 are grouped in the last bar. Clery counts are reports made, "
         "not a measure of how much assault occurs."],
        handle=HANDLE, fontsize=14, color=INK, wrap_width=80, line_step=0.0185)
    ax = fig.add_axes([0.13, cap_top + 0.07, 0.82, sub_bottom - cap_top - 0.10])
    ax.set_facecolor(PAPER)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(MUTED)
    ax.grid(axis="y", color=BORDER, lw=0.8)
    ax.set_axisbelow(True)

    cap = 20
    edges = np.arange(0, cap + 1, 1.0)
    clipped = np.minimum(rates, cap - 1e-6)
    counts, _ = np.histogram(clipped, bins=edges)
    cols = [ACCENT if (e <= b["rate_2024"] < e + 1) else CONTEXT_GRAY for e in edges[:-1]]
    ax.bar(edges[:-1], counts, width=1.0, align="edge", color=cols, ec=PAPER, lw=1.2, zorder=3)
    ymax = counts.max() * 1.18
    ax.axvline(b["rate_2024"], color=ACCENT, lw=3, zorder=5)
    ax.plot([dist["median"]] * 2, [0, ymax * 0.86], color=INK, lw=2, ls=(0, (5, 3)), zorder=4)
    ax.annotate(f"BYU: {b['rate_2024']:.2f}", (b["rate_2024"], ymax * 0.99), xytext=(8, 0), textcoords="offset points",
                ha="left", va="top", fontproperties=fonts["bold"], fontsize=16, color=ACCENT)
    ax.annotate(f"Median: {dist['median']:.2f}", (dist["median"], ymax * 0.86), xytext=(8, 0),
                textcoords="offset points", ha="left", va="top", fontproperties=fonts["bold"], fontsize=16, color=INK)
    ax.set_xlim(0, cap)
    ax.set_ylim(0, ymax)
    ax.set_xticks(range(0, cap + 1, 4))
    ax.set_xticklabels([str(v) if v < cap else f"{cap}+" for v in range(0, cap + 1, 4)])
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontproperties(fonts["regular"])
        lab.set_fontsize(13)
    ax.set_xlabel("Reported on-campus rapes per 10,000 students", fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.set_ylabel("Number of institutions", fontproperties=fonts["bold"], fontsize=14, color=INK)
    stat_box(ax, [
        f"BYU reports: {b['rapes_2024']}",
        f"BYU enrollment: {b['enrollment']:,}",
        f"BYU rate: {b['rate_2024']:.2f} per 10,000",
        f"National median: {dist['median']:.2f}",
        f"National mean: {dist['mean']:.2f}",
        f"BYU percentile: {b['percentile_ge_5000']:.0f}th",
    ], y=0.80)
    fig.savefig(out, dpi=DPI, facecolor=PAPER)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    fonts = load_fonts()
    FONTS.update(fonts)
    s = json.loads((DATA / "stats.json").read_text(encoding="utf-8"))

    raw = json.loads((DATA / "raw-rapes-2024-top30.json").read_text(encoding="utf-8"))
    bar_chart(rows=raw["rows"], byu=raw["byu"], value_key="rape24", rank_key="rank_raw", decimals=0,
              title="Reported On-Campus Rapes by University, 2024",
              subtitle="Raw number of incidents reported under the Clery Act.\n"
                       f"Top 30 of {raw['n']:,} four-year institutions, plus BYU.",
              out=args.out_dir / "reported-rapes-by-university-2024.png", fonts=fonts)

    rt = json.loads((DATA / "rate-2024-top30.json").read_text(encoding="utf-8"))
    bar_chart(rows=rt["rows"], byu=rt["byu"], value_key="rate24", rank_key="rank_rate", decimals=1,
              title="Reported On-Campus Rapes per 10,000 Students, 2024",
              subtitle="Clery Act reports adjusted for university enrollment.\n"
                       f"Top 30 of {rt['n']:,} four-year institutions with 1,000+ students, plus BYU.",
              out=args.out_dir / "reported-rapes-per-10k-students-2024.png", fonts=fonts)

    scatter_chart(args.out_dir / "campus-size-vs-reported-rapes-2024.png", fonts)
    hist_chart(args.out_dir / "byu-vs-national-distribution-2024.png", fonts)

    m = json.loads((DATA / "rate-2022-24-top30.json").read_text(encoding="utf-8"))
    bar_chart(rows=m["rows"], byu=m["byu"], value_key="rate3", rank_key="rank3", decimals=1,
              extra_rows=[(f"National median", m["median"], INK)],
              title="Average Reported On-Campus Rape Rate, 2022–2024",
              subtitle="Three-year Clery Act average per 10,000 students.\n"
                       f"Top 30 of {m['n']:,} institutions with 5,000+ students, plus BYU and the median.",
              out=args.out_dir / "reported-rapes-per-10k-3yr-average-2022-24.png", fonts=fonts)


if __name__ == "__main__":
    main()
