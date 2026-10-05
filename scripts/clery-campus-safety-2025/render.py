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

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.text
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
OFFENSE = "rape"  # --offense fondling swaps DATA to its fondling/ folder and rewrites every chart's wording


def T(text):
    """Rewrites chart wording for the selected offense (the JSON field names still say 'rape')."""
    if OFFENSE == "rape":
        return text
    for a, b in (("Rapes", "Fondling Offenses"), ("rapes", "fondling offenses"), ("Rape", "Fondling"), ("rape", "fondling")):
        text = text.replace(a, b)
    return text


_draw_title_base = _draw_title


def _draw_title(fig, fonts, title, subtitle):  # noqa: F811 - reword before the title is wrapped to fit
    return _draw_title_base(fig, fonts, T(title), T(subtitle))


def fname(name):
    return name if OFFENSE == "rape" else name.replace("rapes", "fondling").replace("rape", "fondling")


def save(fig, out):
    if OFFENSE != "rape":
        for t in fig.findobj(matplotlib.text.Text):
            t.set_text(T(t.get_text()))
    fig.savefig(out, dpi=DPI, facecolor=PAPER)
HANDLE = "@ithinkisam | data: U.S. Dept. of Education, Clery Act 2025"
BYU_ID = "230038"
UTAH_ID = "230764"
# School colors for the Utah-only charts (primary color of each school; schools not listed stay gray).
SCHOOL_COLORS = {"230038": "#002E5D",  # BYU royal blue
                 "230764": "#9C2B2B",  # University of Utah red (site-wide Utah red)
                 "230728": "#0F2439",  # Utah State navy
                 "230782": "#4B2E83",  # Weber State purple
                 "230737": "#275D38",  # Utah Valley green
                 "230603": "#C8102E",  # Southern Utah cardinal
                 "230171": "#E03C31"}  # Utah Tech red
CORNELL_ID = "190415"
CORNELL_RED = "#B31B1B"  # Cornell carnelian red
UVU_ID = "230737"
UVU_GREEN = "#275D38"
UTAH_RED = "#9C2B2B"  # crimson from chart_style; the University of Utah is red on every chart
BYU_LABEL = "Brigham Young University"
DISCLAIMER = ("These figures represent incidents reported under the Clery Act, not estimates of the actual "
              "prevalence of sexual assault. Differences may reflect both differences in victimization and "
              "differences in reporting practices.")

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


def bar_chart(*, rows, byu, value_key, title, subtitle, out, fonts, decimals, extra_rows=(), rank_key, accent_ids=(BYU_ID,), label_key=None, red_ids=(UTAH_ID,), color_map=None):
    """rows: top-30 records; byu appended if not already present."""
    ids = [r["unitid"] for r in rows]
    labels = [r[label_key] for r in rows] if label_key else uniq_labels(rows)
    values = {l: r[value_key] for l, r in zip(labels, rows)}
    order = list(labels)
    colors = {l: (ACCENT if r["unitid"] in accent_ids else UTAH_RED if r["unitid"] in red_ids else CONTEXT_GRAY)
              for l, r in zip(labels, rows)}
    if color_map:
        colors = {l: color_map.get(r["unitid"], CONTEXT_GRAY) for l, r in zip(labels, rows)}
    if not any(i in ids for i in accent_ids) and BYU_ID not in ids:
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
        title=T(title), subtitle=T(subtitle), caption_paragraphs=[DISCLAIMER], caption_wrap_width=80, caption_line_step=0.0215, handle=HANDLE, out_path=out, fonts=fonts,
        value_suffix="", value_decimals=decimals, axes_left=0.40,
        row_label_fontsize=12.5, value_label_fontsize=12.5, bar_h_override=0.72, margin_frac_override=0.015,
    )


FONTS = {}


def stat_box(ax, lines, x=0.97, y=0.97):
    ax.text(x, y, "\n".join(lines), transform=ax.transAxes, ha="right", va="top", linespacing=1.45,
            fontproperties=FONTS["regular"], fontsize=15, color=INK, bbox=dict(boxstyle="square,pad=0.6", fc=PAPER, ec=BORDER, lw=1))


def scatter_chart(out, fonts, hide=(), period="2024"):
    """Counts vs enrollment. period "3yr" plots the 2022-24 average annual count (rape24 holds the average)."""
    three = period == "3yr"
    if three:
        d = json.loads((DATA / "scatter-2022-24.json").read_text(encoding="utf-8"))
        pts = [{**q, "rape24": q["avg_rapes"], "resid_z": (q["avg_rapes"] - q["expected"]) / np.sqrt(q["expected"] / 3)}
               for q in d["points"]]
    else:
        d = json.loads((DATA / "scatter-2024.json").read_text(encoding="utf-8"))
        pts = d["points"]
    vdiv = 3 if three else 1  # variance of the three-year mean is the single-year variance / 3

    def cnt(v):
        return f"{v:.1f}" if three else f"{v:g}"
    XCAP = 85000
    n_off = sum(p["enrollment"] > XCAP for p in pts)
    off_max = max(p["rape24"] for p in pts if p["enrollment"] > XCAP)
    pts_all, pts = pts, [p for p in pts if p["enrollment"] <= XCAP]
    hidden = [p for p in pts if p["unitid"] in hide]
    pts = [p for p in pts if p["unitid"] not in hide]
    x = np.array([p["enrollment"] for p in pts])
    y = np.array([p["rape24"] for p in pts])
    z = np.array([p["resid_z"] for p in pts])
    rate = d["pooled_rate_per_10k"]

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    title = ("Campus Size and Reported Rapes at U.S. Universities" if not hide
             else "Campus Size and Reported Rapes, Without the Three Largest Outliers")
    if three:
        title = "Campus Size and Average Reported Rapes at U.S. Universities, 2022" + chr(0x2013) + "2024"
    sub_bottom = _draw_title(fig, fonts, title,
                             ("2022" + chr(0x2013) + "2024 average annual Clery Act reports. One dot per four-year institution with" if three
                              else "2024 Clery Act reports. One dot per four-year institution with") + chr(10) +
                             f"at least {d['min_enrollment']:,} students ({len(pts):,} institutions).")
    cap_top = draw_caption_bottom(
        fig, fonts,
        [f"Line = expected reports if every campus reported at the pooled national rate "
         f"({rate:.1f} per 10,000 students); shaded band = 95% Poisson range around it. "
         "Labeled dots are the largest departures above the line, plus BYU and Cornell for comparison. "
         f"{n_off} very large, mostly online, institutions (enrollment above {XCAP:,}) are off the right edge; each reported {cnt(off_max)} or fewer."
         + (" The three highest-count institutions are removed to improve the scale; arrows give their values." if hide else ""),
         DISCLAIMER],
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
    ax.fill_between(xs, np.maximum(exp - 1.96 * np.sqrt(exp / vdiv), 0), exp + 1.96 * np.sqrt(exp / vdiv) + 1 / vdiv,
                    color=CONTEXT_GRAY, alpha=0.18, lw=0)
    ax.plot(xs, exp, color=INK, lw=2)
    ax.scatter(x, y, s=22, color=CONTEXT_GRAY, alpha=0.65, lw=0, zorder=3)

    byu = next(p for p in pts if p["unitid"] == BYU_ID)
    cornell = next(p for p in pts if p["unitid"] == "190415")
    ax.scatter([byu["enrollment"]], [byu["rape24"]], s=170, color=ACCENT, ec=PAPER, lw=1.5, zorder=5)
    ax.scatter([cornell["enrollment"]], [cornell["rape24"]], s=90, color=CORNELL_RED, ec=PAPER, lw=1.2, zorder=4)
    for u in (p for p in pts if p["unitid"] == UTAH_ID):
        ax.scatter([u["enrollment"]], [u["rape24"]], s=110, color=UTAH_RED, ec=PAPER, lw=1.2, zorder=4)
    uvu = next(p for p in pts if p["unitid"] == UVU_ID)
    ax.scatter([uvu["enrollment"]], [uvu["rape24"]], s=110, color=UVU_GREEN, ec=PAPER, lw=1.2, zorder=4)

    top = sorted(pts, key=lambda p: -abs(p["resid_z"]))
    over = [p for p in top if p["resid_z"] > 0][:6]
    if not hide:  # Mayo Clinic, Dartmouth and Lycoming labels removed from the main scatter
        over = [p for p in over if p["unitid"] not in ("173957", "182670", "213668")]
    if hide:
        over = [p for p in over if p["unitid"] in ("173957", "182670", "115755", "110714")]
    under = []
    if three:  # keep the crowded low-count cluster unlabeled, but always label the University of Utah
        over = [p for p in over if p["rape24"] > 25]
        over += [p for p in pts if p["unitid"] == UTAH_ID and p not in over]
    # (label, dx, dy in points, ha) hand-placed to avoid collisions
    place = {
        "230764": (9, -3, "left"), "126614": (9, -3, "left"), "151111": (9, -3, "left"),
        "173957": (9, 66 if not hide else 86, "left"), "182670": (12, 26 if hide else 8, "left"),
        "115755": (12, -26 if hide else 6, "left"),
        "110714": (9, 6, "left"), "190415": (12, -16, "left"), BYU_ID: (12, -6, "left"), UVU_ID: (26, -8, "left"),
    }
    if three:
        place["190415"] = (-12, 12, "right")
        place["151111"] = (8, -6, "left")
        place["133881"] = (8, -12, "left")
    done = set()
    for p in over + under + [byu, cornell, uvu]:
        if p["unitid"] in done:
            continue
        done.add(p["unitid"])
        dx, dy, ha = place.get(p["unitid"], (8, 4, "left"))
        if p["unitid"] == UVU_ID and p["rape24"] < 5:
            dy = 14  # low count: keep the label off the axis
        lab = short(p["name"]) if p["unitid"] != BYU_ID else "BYU"
        if p["unitid"] == UVU_ID:
            lab = "Utah Valley"
        if p["unitid"] == "190415":
            lab = "Cornell"
        ax.annotate(f"{lab} ({cnt(p['rape24'])})", (p["enrollment"], p["rape24"]), xytext=(dx, dy),
                    textcoords="offset points", ha=ha, fontsize=12.5,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkA=2, shrinkB=4),
                    fontproperties=fonts["bold" if p["unitid"] in (BYU_ID, "190415", UVU_ID) else "regular"],
                    color=ACCENT if p["unitid"] == BYU_ID else UTAH_RED if p["unitid"] == UTAH_ID
                    else UVU_GREEN if p["unitid"] == UVU_ID else CORNELL_RED if p["unitid"] == CORNELL_ID else INK, zorder=6)
    ylim = y.max() * (1.30 if hidden else 1.08)
    for k, p in enumerate(sorted(hidden, key=lambda q: q["enrollment"])):
        lab = {"126614": "CU Boulder", "151111": "IU Indianapolis"}.get(p["unitid"]) or short(p["name"])
        left = p["unitid"] != "126614"
        ytxt = ylim * (0.84 if p["unitid"] == UTAH_ID else 0.93)
        ax.annotate("", xy=(p["enrollment"], ylim * 0.995), xytext=(p["enrollment"], ytxt - ylim * 0.012),
                    arrowprops=dict(arrowstyle="-|>", color=UTAH_RED if p["unitid"] == UTAH_ID else INK, lw=1.8))
        ax.text(p["enrollment"] + (-900 if left else 900), ytxt, f"{lab}: {cnt(p['rape24'])}", ha="right" if left else "left",
                va="center", fontproperties=fonts["bold"], fontsize=13,
                color=UTAH_RED if p["unitid"] == UTAH_ID else INK)
    ax.set_xlim(0, XCAP)
    ax.set_ylim(0, ylim)
    ax.xaxis.set_major_formatter(lambda v, _: f"{int(v/1000)}k" if v else "0")
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontproperties(fonts["regular"])
        lab.set_fontsize(13)
    ax.set_xlabel("Total enrollment", fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.set_ylabel("Avg. annual reported on-campus rapes, 2022" + chr(0x2013) + "2024" if three else "Reported on-campus rapes, 2024",
                  fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.text(xs.max() * 0.98, rate / 1e4 * xs.max() * 0.98 + 6, "Expected at national rate", ha="right", va="bottom",
            fontproperties=fonts["bold"], fontsize=13, color=INK)
    save(fig, out)
    plt.close(fig)

def rate_scatter_chart(out, fonts):
    d = json.loads((DATA / "scatter-2024.json").read_text(encoding="utf-8"))
    pts = d["points"]
    rate = d["pooled_rate_per_10k"]
    for p in pts:
        p["rate"] = p["rape24"] / p["enrollment"] * 1e4
    YCAP = 50
    n_off = sum(p["rate"] > YCAP for p in pts)
    off_max = max(p["rate"] for p in pts)

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    sub_bottom = _draw_title(fig, fonts, "Campus Size and Reported Rape Rates at U.S. Universities",
                             "2024 Clery Act reports per 10,000 students. One dot per four-year\n"
                             f"institution with at least {d['min_enrollment']:,} students ({len(pts):,} institutions).")
    cap_top = draw_caption_bottom(
        fig, fonts,
        [f"Line = U.S. national rate ({rate:.1f} per 10,000 students); shaded band = 95% Poisson range around it, "
         "which narrows as campuses get larger, so small campuses swing widely by chance. Enrollment is on a log scale. "
         f"{n_off} small institutions with rates above {YCAP} (up to {off_max:.0f}) are off the top edge.", DISCLAIMER],
        handle=HANDLE, fontsize=14, color=INK, wrap_width=80, line_step=0.0185)
    ax = fig.add_axes([0.14, cap_top + 0.075, 0.82, sub_bottom - cap_top - 0.105])
    ax.set_facecolor(PAPER)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(MUTED)
    ax.grid(color=BORDER, lw=0.8)
    ax.set_axisbelow(True)

    xmax = max(p["enrollment"] for p in pts) * 1.1
    xs = np.geomspace(1000, xmax, 300)
    exp = rate / 1e4 * xs
    lo = np.maximum(exp - 1.96 * np.sqrt(exp), 0) / xs * 1e4
    hi = (exp + 1.96 * np.sqrt(exp) + 1) / xs * 1e4
    ax.fill_between(xs, lo, hi, color=CONTEXT_GRAY, alpha=0.18, lw=0)
    ax.axhline(rate, color=INK, lw=2)
    shown = [p for p in pts if p["rate"] <= YCAP]
    ax.scatter([p["enrollment"] for p in shown], [p["rate"] for p in shown], s=22, color=CONTEXT_GRAY,
               alpha=0.65, lw=0, zorder=3)

    byu = next(p for p in pts if p["unitid"] == BYU_ID)
    cornell = next(p for p in pts if p["unitid"] == "190415")
    ax.scatter([byu["enrollment"]], [byu["rate"]], s=170, color=ACCENT, ec=PAPER, lw=1.5, zorder=5)
    ax.scatter([cornell["enrollment"]], [cornell["rate"]], s=90, color=INK, ec=PAPER, lw=1.2, zorder=4)

    ids = ["230764", "151111", "126614", "182670", "115755", "110714"]
    place = {"230764": (12, 10, "left"), "151111": (-12, -16, "right"), "126614": (-12, 12, "right"),
             "182670": (12, 14, "left"), "115755": (-14, 12, "right"), "110714": (-12, 6, "right"),
             "190415": (12, 22, "left"), BYU_ID: (16, -32, "left")}
    for p in [byu, cornell] + [next(q for q in pts if q["unitid"] == i) for i in ids]:
        dx, dy, ha = place[p["unitid"]]
        lab = ("BYU" if p["unitid"] == BYU_ID else "Cornell" if p["unitid"] == "190415"
               else "CU Boulder" if p["unitid"] == "126614" else short(p["name"]))
        bold = p["unitid"] in (BYU_ID, "190415")
        ax.annotate(f"{lab} ({p['rate']:.1f})", (p["enrollment"], p["rate"]), xytext=(dx, dy),
                    textcoords="offset points", ha=ha, fontsize=12.5,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkA=2, shrinkB=4),
                    fontproperties=fonts["bold" if bold else "regular"],
                    color=ACCENT if p["unitid"] == BYU_ID else INK, zorder=6)
    ax.set_xscale("log")
    ax.set_xlim(1000, xmax)
    ax.set_ylim(-4, YCAP)
    ticks = [1000, 2000, 5000, 10000, 20000, 50000, 100000]
    ax.set_xticks([t for t in ticks if t <= xmax])
    ax.xaxis.set_minor_locator(plt.NullLocator())
    ax.xaxis.set_major_formatter(lambda v, _: f"{int(v/1000)}k")
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontproperties(fonts["regular"])
        lab.set_fontsize(13)
    ax.set_xlabel("Total enrollment (log scale)", fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.set_ylabel("Reported on-campus rapes per 10,000 students, 2024", fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.text(xmax * 0.97, rate + 0.8, "National rate", ha="right", va="bottom",
            fontproperties=fonts["bold"], fontsize=13, color=INK)
    save(fig, out)
    plt.close(fig)

def rate_scatter_3yr_chart(out, fonts, period="3yr"):
    """Linear-x funnel plot of the rate per 10,000 (2022-24 average, or 2024 alone); BYU campuses blue, labeled."""
    three = period == "3yr"
    k = 3 if three else 1  # variance of the three-year mean is the single-year variance / 3
    if three:
        d = json.loads((DATA / "scatter-2022-24.json").read_text(encoding="utf-8"))
        pts = d["points"]
    else:
        d = json.loads((DATA / "scatter-2024.json").read_text(encoding="utf-8"))
        pts = [{**q, "rate3": q["rape24"] / q["enrollment"] * 1e4} for q in d["points"]]
    rate = d["pooled_rate_per_10k"]
    byu_ids = {"230038": "BYU–Provo", "142522": "BYU–Idaho", "230047": "BYU–Hawaii"}
    XCAP, YCAP = 85000, 50
    n_x = sum(p["enrollment"] > XCAP for p in pts)
    n_y = sum(p["rate3"] > YCAP and p["enrollment"] <= XCAP for p in pts)
    y_max = max(p["rate3"] for p in pts)

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    sub_bottom = _draw_title(fig, fonts, "Campus Size and Average Reported Rape Rates, 2022" + chr(0x2013) + "2024" if three
                             else "Campus Size and Reported Rape Rates, 2024",
                             ("Three-year Clery Act average per 10,000 students. One dot per" if three
                              else "2024 Clery Act reports per 10,000 students. One dot per") + chr(10) +
                             f"four-year institution with 1,000+ students ({len(pts):,} institutions).")
    cap_top = draw_caption_bottom(
        fig, fonts,
        [f"Line = U.S. national rate ({rate:.1f} per 10,000 students); shaded band = 95% Poisson range around it, "
         f"which narrows as campuses get larger. {n_x} very large institutions (enrollment above {XCAP:,}) and "
         f"{n_y} small ones with rates above {YCAP} (up to {y_max:.0f}) are off the edges.", DISCLAIMER],
        handle=HANDLE, fontsize=14, color=INK, wrap_width=80, line_step=0.0185)
    ax = fig.add_axes([0.14, cap_top + 0.075, 0.82, sub_bottom - cap_top - 0.105])
    ax.set_facecolor(PAPER)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(MUTED)
    ax.grid(color=BORDER, lw=0.8)
    ax.set_axisbelow(True)

    xs = np.linspace(500, XCAP, 400)
    exp = rate / 1e4 * xs
    half = 1.96 * np.sqrt(exp / k)
    ax.fill_between(xs, np.maximum(exp - half, 0) / xs * 1e4, (exp + half + 1 / k) / xs * 1e4,
                    color=CONTEXT_GRAY, alpha=0.18, lw=0)
    ax.axhline(rate, color=INK, lw=2)
    hi_ids = {"230038", "142522", UVU_ID}  # highlighted dots: BYU-Provo, BYU-Idaho (blue) and Utah Valley (green)
    shown = [p for p in pts if p["enrollment"] <= XCAP and p["rate3"] <= YCAP and p["unitid"] not in hi_ids]
    ax.scatter([p["enrollment"] for p in shown], [p["rate3"] for p in shown], s=22, color=CONTEXT_GRAY,
               alpha=0.65, lw=0, zorder=3)
    place = {"230038": (-16, 62, "right"), "142522": (16, 36, "left"),
             "230764": (-14, 8, "right")}
    byu_ids = {k: v for k, v in byu_ids.items() if k != "230047"}  # BYU-Hawaii is an ordinary gray dot
    place[UVU_ID] = (0, 80, "center")
    for p in pts:
        if p["unitid"] in byu_ids:
            ax.scatter([p["enrollment"]], [p["rate3"]], s=170, color=ACCENT, ec=PAPER, lw=1.5, zorder=5)
        elif p["unitid"] == UVU_ID:
            ax.scatter([p["enrollment"]], [p["rate3"]], s=110, color=UVU_GREEN, ec=PAPER, lw=1.5, zorder=5)
        elif p["unitid"] in place:
            ax.scatter([p["enrollment"]], [p["rate3"]], s=90 if p["unitid"] == UTAH_ID else 60,
                       color=UTAH_RED if p["unitid"] == UTAH_ID else INK, ec=PAPER, lw=1.2, zorder=4)
        else:
            continue
        isb = p["unitid"] in byu_ids
        lab = "Utah Valley" if p["unitid"] == UVU_ID else byu_ids.get(p["unitid"]) or short(p["name"])
        dx, dy, ha = place[p["unitid"]]
        ax.annotate(f"{lab} ({p['rate3']:.1f})", (p["enrollment"], p["rate3"]), xytext=(dx, dy),
                    textcoords="offset points", ha=ha, fontsize=13 if isb else 12.5,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkA=2, shrinkB=4),
                    fontproperties=fonts["bold" if (isb or p["unitid"] == UVU_ID) else "regular"],
                    color=ACCENT if isb else UTAH_RED if p["unitid"] == UTAH_ID
                    else UVU_GREEN if p["unitid"] == UVU_ID else INK, zorder=6)
    ax.set_xlim(0, XCAP)
    ax.set_ylim(-3, YCAP)
    ax.xaxis.set_major_formatter(lambda v, _: f"{int(v/1000)}k" if v else "0")
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontproperties(fonts["regular"])
        lab.set_fontsize(13)
    ax.set_xlabel("Total enrollment", fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.set_ylabel("Avg. annual reported rapes per 10,000 students" if three else "Reported rapes per 10,000 students, 2024",
                  fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.text(XCAP * 0.98, rate + 0.8, f"National rate: {rate:.1f}", ha="right", va="bottom",
            fontproperties=fonts["bold"], fontsize=13, color=INK)
    save(fig, out)
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
         "reported zero. Rates above 20 per 10,000 are grouped in the last bar.", DISCLAIMER],
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
    save(fig, out)
    plt.close(fig)


def utah_scatter(out, fonts):
    u = json.loads((DATA / "utah-2024.json").read_text(encoding="utf-8"))
    s = json.loads((DATA / "stats.json").read_text(encoding="utf-8"))
    rate = s["pooled_rate_per_10k_ge_1000"]
    pts = u["rows"]
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    sub_bottom = _draw_title(fig, fonts, "Campus Size and Reported Rapes at Utah Universities",
                             "2024 Clery Act reports. All four-year institutions in Utah\n"
                             f"with at least {u['min_enrollment']:,} students ({len(pts)} institutions).")
    cap_top = draw_caption_bottom(
        fig, fonts,
        [f"Line = expected reports at the U.S. national rate ({rate:.1f} per 10,000 students, "
         f"institutions with 1,000+ students).", DISCLAIMER],
        handle=HANDLE, fontsize=14, color=INK, wrap_width=80, line_step=0.0185)
    ax = fig.add_axes([0.14, cap_top + 0.075, 0.82, sub_bottom - cap_top - 0.105])
    ax.set_facecolor(PAPER)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(MUTED)
    ax.grid(color=BORDER, lw=0.8)
    ax.set_axisbelow(True)
    xmax = 50000
    xs = np.linspace(0, xmax, 100)
    ax.plot(xs, rate / 1e4 * xs, color=INK, lw=2)
    YTOP = 16
    place = {"Utah Valley University": (-8, 14, "right"), "Weber State University": (0, -30, "center"),
             "Utah State University": (14, 10, "left"), "Southern Utah University": (10, -16, "left"),
             "Brigham Young University": (14, -18, "left"), "Ensign College": (8, -16, "left"),
             "Snow College": (-6, 18, "right"), "Utah Tech University": (-10, 34, "right")}
    grouped = ("Westminster University", "Joyce University of Nursing and Health Sciences",
               "Rocky Mountain University of Health Professions")
    for p in pts:
        isb = p["unitid"] == BYU_ID
        off = p["rape24"] > YTOP
        y = YTOP - 0.9 if off else p["rape24"]
        isu = p["unitid"] == UTAH_ID
        ax.scatter([p["enrollment"]], [y], s=170 if isb else 90 if isu else 60, marker="^" if off else "o",
                   color=SCHOOL_COLORS.get(p["unitid"], CONTEXT_GRAY), ec=PAPER, lw=1.2, zorder=5 if isb else 4)
        if p["name"] in grouped:
            continue
        lab = "BYU" if isb else short(p["name"])
        txt = f"{lab} ({p['rape24']}, off chart)" if off else f"{lab} ({p['rape24']})"
        dx, dy, ha = (-12, -4, "right") if off else place.get(p["name"], (10, 6, "left"))
        ax.annotate(txt, (p["enrollment"], y), xytext=(dx, dy), textcoords="offset points",
                    ha=ha, fontsize=12.5, fontproperties=fonts["bold" if isb else "regular"],
                    color=SCHOOL_COLORS.get(p["unitid"], INK), zorder=6,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkA=2, shrinkB=4))
    gp = next(p for p in pts if p["name"] == grouped[1])
    ax.annotate("Westminster, Joyce, Rocky Mountain (0 each)", (gp["enrollment"], 0), xytext=(14, 70),
                textcoords="offset points", ha="left", fontsize=12.5, fontproperties=fonts["regular"], color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkA=2, shrinkB=4))
    ax.set_xlim(0, xmax)
    ax.set_ylim(-2.2, YTOP + 1.4)
    ax.xaxis.set_major_formatter(lambda v, _: f"{int(v/1000)}k" if v else "0")
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontproperties(fonts["regular"])
        lab.set_fontsize(13)
    ax.set_xlabel("Total enrollment", fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.set_ylabel("Reported on-campus rapes, 2024", fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.text(41000, YTOP + 0.4, "Expected at national rate", ha="right", va="bottom",
            fontproperties=fonts["bold"], fontsize=13, color=INK)
    save(fig, out)
    plt.close(fig)


def utah_rate_scatter(out, fonts):
    u = json.loads((DATA / "utah-2024.json").read_text(encoding="utf-8"))
    s = json.loads((DATA / "stats.json").read_text(encoding="utf-8"))
    rate = s["pooled_rate_per_10k_ge_1000"]
    pts = u["rows"]
    YTOP, xmax = 16, 50000
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    sub_bottom = _draw_title(fig, fonts, "Campus Size and Reported Rape Rates at Utah Universities",
                             "2024 Clery Act reports per 10,000 students. All four-year\n"
                             f"Utah institutions with at least {u['min_enrollment']:,} students ({len(pts)} institutions).")
    cap_top = draw_caption_bottom(
        fig, fonts,
        [f"Line = U.S. national rate ({rate:.1f} per 10,000 students); shaded band = 95% Poisson range around it, "
         "which narrows as campuses get larger. The University of Utah's rate is above the top edge.", DISCLAIMER],
        handle=HANDLE, fontsize=14, color=INK, wrap_width=80, line_step=0.0185)
    ax = fig.add_axes([0.14, cap_top + 0.075, 0.82, sub_bottom - cap_top - 0.105])
    ax.set_facecolor(PAPER)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(MUTED)
    ax.grid(color=BORDER, lw=0.8)
    ax.set_axisbelow(True)
    xs = np.linspace(1000, xmax, 300)
    exp = rate / 1e4 * xs
    ax.fill_between(xs, np.maximum(exp - 1.96 * np.sqrt(exp), 0) / xs * 1e4,
                    (exp + 1.96 * np.sqrt(exp) + 1) / xs * 1e4, color=CONTEXT_GRAY, alpha=0.18, lw=0)
    ax.axhline(rate, color=INK, lw=2)
    place = {"Snow College": (14, 8, "left"), "Utah Tech University": (14, 10, "left")}
    pos = {"Utah State University": (29000, 7.0, "center"), "Weber State University": (33000, 9.3, "center"),
           "Brigham Young University": (41500, 5.6, "center"), "Utah Valley University": (44500, 8.0, "center"),
           "Southern Utah University": (15400, 2.6, "center"), "Ensign College": (8500, -1.1, "left")}
    grouped = ("Westminster University", "Joyce University of Nursing and Health Sciences",
               "Rocky Mountain University of Health Professions")
    leader = dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkA=2, shrinkB=4)
    for p in pts:
        isb, isu = p["unitid"] == BYU_ID, p["unitid"] == UTAH_ID
        off = p["rate24"] > YTOP
        y = YTOP - 0.7 if off else p["rate24"]
        ax.scatter([p["enrollment"]], [y], s=170 if isb else 90 if isu else 60, marker="^" if off else "o",
                   color=SCHOOL_COLORS.get(p["unitid"], CONTEXT_GRAY), ec=PAPER, lw=1.2,
                   zorder=5 if (isb or isu) else 4)
        if p["name"] in grouped:
            continue
        lab = "BYU" if isb else short(p["name"])
        txt = f"{lab} ({p['rate24']:.1f}, off chart)" if off else f"{lab} ({p['rate24']:.1f})"
        kw = dict(ha="left", fontsize=12.5, fontproperties=fonts["bold" if (isb or isu) else "regular"],
                  color=SCHOOL_COLORS.get(p["unitid"], INK), zorder=6, arrowprops=leader)
        if p["name"] in pos:
            x0, y0, ha = pos[p["name"]]
            kw["ha"] = ha
            ax.annotate(txt, (p["enrollment"], y), xytext=(x0, y0), textcoords="data", **kw)
        else:
            dx, dy, ha = (-12, -4, "right") if off else place.get(p["name"], (10, 6, "left"))
            kw["ha"] = ha
            ax.annotate(txt, (p["enrollment"], y), xytext=(dx, dy), textcoords="offset points", **kw)
    gp = next(p for p in pts if p["name"] == grouped[1])
    ax.annotate("Westminster, Joyce, Rocky" + chr(10) + "Mountain (0 each)", (gp["enrollment"], 0), xytext=(1200, 6.3),
                textcoords="data", ha="left", va="center", fontsize=12.5, fontproperties=fonts["regular"], color=INK,
                arrowprops=leader)
    ax.set_xlim(0, xmax)
    ax.set_ylim(-2, YTOP + 1)
    ax.xaxis.set_major_formatter(lambda v, _: f"{int(v/1000)}k" if v else "0")
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontproperties(fonts["regular"])
        lab.set_fontsize(13)
    ax.set_xlabel("Total enrollment", fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.set_ylabel("Reported on-campus rapes per 10,000 students, 2024", fontproperties=fonts["bold"], fontsize=14, color=INK)
    ax.text(21000, rate + 0.2, "National rate", ha="left", va="bottom",
            fontproperties=fonts["bold"], fontsize=13, color=INK)
    save(fig, out)
    plt.close(fig)


def byu_campus_bars(args, fonts, include_raw=True):
    # ---- BYU's three campuses ----
    bc = json.loads((DATA / "byu-campuses.json").read_text(encoding="utf-8"))
    crow = bc["rows"]
    cmp_colors = {**{i: ACCENT for i in bc["byu_ids"]}, UTAH_ID: UTAH_RED, UVU_ID: UVU_GREEN, CORNELL_ID: CORNELL_RED}
    kw = dict(byu=None, rank_key=None, accent_ids=set(bc["byu_ids"]), label_key="label", fonts=fonts, color_map=cmp_colors)
    sub = "BYU's three campuses against the U.S. median and well-known schools."
    if include_raw:
        bar_chart(rows=sorted(crow, key=lambda r: (-r["rape24"], -r["enrollment"])), value_key="rape24", decimals=0,
                  title="Reported On-Campus Rapes at BYU's Campuses and Comparison Schools, 2024",
                  subtitle="Raw number of incidents reported under the Clery Act.\n" + "BYU's three campuses and well-known schools.",
                  out=args.out_dir / fname("byu-campuses-reported-rapes-2024.png"), **kw)
    no_hi = [r for r in crow if r["unitid"] != "230047"]  # per-10k charts omit BYU-Hawaii
    sub2 = "BYU"+chr(0x2013)+"Provo and BYU"+chr(0x2013)+"Idaho vs. the U.S. median and well-known schools."
    bar_chart(rows=sorted(no_hi, key=lambda r: -r["rate24"]), value_key="rate24", decimals=1,
              extra_rows=[("U.S. median", bc["median_rate_2024"], INK)],
              title="Reported On-Campus Rapes per 10,000 Students at BYU's Campuses and Comparison Schools, 2024",
              subtitle="Clery Act reports adjusted for enrollment.\n" + sub2,
              out=args.out_dir / fname("byu-campuses-reported-rapes-per-10k-2024.png"), **kw)
    bar_chart(rows=sorted(no_hi, key=lambda r: -r["rate3"]), value_key="rate3", decimals=1,
              extra_rows=[("U.S. median", bc["median_rate_3yr"], INK)],
              title="Average Reported On-Campus Rape Rate at BYU's Campuses and Comparison Schools, 2022–2024",
              subtitle="Three-year Clery Act average per 10,000 students.\n" + sub2,
              out=args.out_dir / fname("byu-campuses-reported-rapes-per-10k-3yr-average-2022-24.png"), **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--offense", choices=["rape", "fondling"], default="rape")
    args = ap.parse_args()
    global DATA, OFFENSE
    OFFENSE = args.offense
    if OFFENSE == "fondling":
        DATA = DATA / "fondling"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    fonts = load_fonts()
    FONTS.update(fonts)
    if OFFENSE == "fondling":  # the five charts that mirror the rape set we are comparing
        scatter_chart(args.out_dir / fname("campus-size-vs-reported-rapes-2024.png"), fonts)
        scatter_chart(args.out_dir / fname("campus-size-vs-reported-rapes-2022-24-average.png"), fonts, period="3yr")
        rate_scatter_3yr_chart(args.out_dir / fname("campus-size-vs-reported-rape-rate-3yr-2022-24.png"), fonts)
        rate_scatter_3yr_chart(args.out_dir / fname("campus-size-vs-reported-rape-rate-2024.png"), fonts, period="2024")
        byu_campus_bars(args, fonts, include_raw=False)
        return
    s = json.loads((DATA / "stats.json").read_text(encoding="utf-8"))

    scatter_chart(args.out_dir / "campus-size-vs-reported-rapes-2024.png", fonts)
    scatter_chart(args.out_dir / "campus-size-vs-reported-rapes-2024-without-outliers.png", fonts,
                  hide=(UTAH_ID, "126614", "151111"))
    rate_scatter_3yr_chart(args.out_dir / "campus-size-vs-reported-rape-rate-3yr-2022-24.png", fonts)

    # ---- Utah only ----
    ut = json.loads((DATA / "utah-2024.json").read_text(encoding="utf-8"))
    ub = next(r for r in ut["rows"] if r["unitid"] == BYU_ID)
    n_ut = ut["n"]
    sub_ut = f"All {n_ut} four-year Utah institutions with 1,000+ students"
    bar_chart(rows=ut["rows"], byu=ub, value_key="rape24", rank_key="rank_raw", decimals=0,
              title="Reported On-Campus Rapes at Utah Universities, 2024",
              subtitle=f"Raw number of incidents reported under the Clery Act.\n{sub_ut}.",
              out=args.out_dir / "utah-reported-rapes-by-university-2024.png", fonts=fonts, color_map=SCHOOL_COLORS)
    by_rate = sorted(ut["rows"], key=lambda r: -r["rate24"])
    bar_chart(rows=by_rate, byu=ub, value_key="rate24", rank_key="rank_rate", decimals=1,
              extra_rows=[("Utah median", ut["median_rate_2024"], INK)],
              title="Reported On-Campus Rapes per 10,000 Students at Utah Universities, 2024",
              subtitle=f"Clery Act reports adjusted for enrollment.\n{sub_ut}, plus the median.",
              out=args.out_dir / "utah-reported-rapes-per-10k-students-2024.png", fonts=fonts, color_map=SCHOOL_COLORS)
    u3 = json.loads((DATA / "utah-2022-24.json").read_text(encoding="utf-8"))
    b3 = next(r for r in u3["rows"] if r["unitid"] == BYU_ID)
    bar_chart(rows=u3["rows"], byu=b3, value_key="rate3", rank_key="rank3", decimals=1,
              extra_rows=[("Utah median", u3["median_rate_3yr"], INK),
                          ("U.S. median", json.loads((DATA / "byu-campuses.json").read_text(encoding="utf-8"))["median_rate_3yr"], INK)],
              title="Reported On-Campus Rapes per 10,000 Students at Utah Universities, 2022–2024",
              subtitle=f"Three-year Clery Act average per 10,000 students.\n{sub_ut}, plus the Utah and U.S. medians.",
              out=args.out_dir / "utah-reported-rapes-per-10k-3yr-average-2022-24.png", fonts=fonts, color_map=SCHOOL_COLORS)
    utah_scatter(args.out_dir / "utah-campus-size-vs-reported-rapes-2024.png", fonts)
    utah_rate_scatter(args.out_dir / "utah-campus-size-vs-reported-rape-rate-2024.png", fonts)

    byu_campus_bars(args, fonts)


if __name__ == "__main__":
    main()
