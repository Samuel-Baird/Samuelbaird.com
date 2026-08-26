#!/usr/bin/env python3
"""Renders the ten "practice" PNGs for the Pew RLS Data Explorer page -
GRAPHICS_TODO.md's "Practice" section.

Reads only docs/datasets/pew-rls-2023-24/practice.json (produced by
scripts/pew-rls/practice.py) - no number here is hand-typed. Same
canvas/fonts as every other chart in this pipeline; see STYLE.md in this
folder. Two chart shapes, reused across all ten items:

- Magnitude bar (highlight-vs-gray, Latter-day Saint in --accent, every
  other group in a bar-safe gray) - for the eight single-percentage items.
- 100%-stacked bar (single-hue ordinal ramp, the official
  --chart-ordinal-1..7 tokens' light-mode hex) - for the two full-
  distribution items (attendance, prayer frequency).

Group sets vary by item's own population rule (see practice.py's
docstring) - CHRISTIAN_ORDER (7 rows), CHRISTIAN_PLUS_OTHER_ORDER (8 rows),
or ALL_RELIGIOUS_ORDER (13 rows) - so every render call passes its own
order list rather than a single hardcoded one.

Usage: see the ten --*-out flags below; run with --help for the full list.
"""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# House style tokens - see STYLE.md. Keep this block and STYLE.md in sync.
# ---------------------------------------------------------------------------

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"

ACCENT = "#1f4f7a"
CONTEXT_GRAY = "#8f8b82"
HIGHLIGHT_GROUP = "Latter-day Saint"

# --chart-ordinal-1..7, light-mode values (src/app/globals.css) - the site's
# one official ordinal ramp, reused here for two different frequency scales
# (attendance, prayer) rather than inventing a new ramp per chart; distinct
# from childhood-education's own tan ramp so "years of education" doesn't
# read as the same kind of scale as "how often."
ORDINAL_RAMP_7 = ["#e8eff6", "#c3d7e8", "#96b9d6", "#5e8db8", "#1f4f7a", "#163a5c", "#0d2740"]
LABEL_INK_FOR_STEP_7 = [INK, INK, INK, INK, "#FFFFFF", "#FFFFFF", "#FFFFFF"]

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120

CHRISTIAN_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
    "Jehovah's Witness", "Other Christian", "Christian average",
]
CHRISTIAN_PLUS_OTHER_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
    "Jehovah's Witness", "Other Christian", "Other religions",
    "Religiously affiliated average",
]
ALL_RELIGIOUS_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Jehovah's Witness",
    "Muslim", "Hindu", "Orthodox Christian", "Other Christian", "Buddhist",
    "Jewish", "Other world religions", "Other faiths", "All religious average",
]

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2023-24" / "practice.json"
).resolve()
DEFAULT_FONTS_DIR = (
    Path(__file__).parent / ".." / "state-of-theology-graphics" / "fonts"
).resolve()


def load_fonts(fonts_dir: Path) -> dict[str, fm.FontProperties]:
    files = {
        "regular": "RobotoCondensed-Regular.ttf",
        "bold": "RobotoCondensed-Bold.ttf",
        "title": "RobotoSlab-Bold.ttf",
    }
    props = {}
    for key, filename in files.items():
        path = fonts_dir / filename
        if not path.exists():
            raise SystemExit(f"missing font file: {path}")
        fm.fontManager.addfont(str(path))
        props[key] = fm.FontProperties(fname=str(path))
    return props


def _draw_title(fig, fonts, title: str, subtitle: str) -> None:
    title_fontsize = 26
    title_lines = textwrap.wrap(title, width=27)
    line_spacing = title_fontsize / 650
    title_top = 0.965
    for i, line in enumerate(title_lines):
        fig.text(
            0.065, title_top - i * line_spacing, line,
            fontproperties=fonts["title"], fontsize=title_fontsize, color=INK, ha="left", va="top",
        )
    subtitle_y = title_top - len(title_lines) * line_spacing - 0.015
    fig.text(
        0.065, subtitle_y, subtitle,
        fontproperties=fonts["regular"], fontsize=13.5, color=MUTED, ha="left", va="top",
    )


def _draw_caption(fig, fonts, total_n: int, note: str) -> None:
    source_paragraphs = [
        note,
        f"Pew Research Center's Religious Landscape Study (RLS), 2023-24 wave · "
        f"N = {total_n:,} U.S. adults",
        "Pew Research Center. 2025. “2023-24 Religious Landscape Study (RLS) Dataset.” "
        "doi: 10.58094/3kwb-bf52.",
    ]
    caption_lines = [line for para in source_paragraphs for line in textwrap.wrap(para, width=98)]
    caption_y = 0.145
    for i, line in enumerate(caption_lines):
        fig.text(
            0.065, caption_y - i * 0.0165, line, fontproperties=fonts["regular"],
            fontsize=10, color=MUTED, ha="left", va="top",
        )


def render_magnitude_bar(
    results: dict, group_order: list[str], title: str, subtitle: str, note: str,
    total_n: int, out_path: Path, fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    n_rows = len(group_order)
    axes_height = min(0.62, 0.052 * n_rows + 0.08)
    AXES_LEFT, AXES_WIDTH = 0.36, 0.58
    ax = fig.add_axes([AXES_LEFT, 0.20, AXES_WIDTH, axes_height])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    rows = group_order[::-1]
    values = [results[g]["pct"] for g in rows]
    colors = [ACCENT if g == HIGHLIGHT_GROUP else CONTEXT_GRAY for g in rows]

    bar_h = 0.62 if n_rows <= 8 else 0.68
    ax.barh(rows, values, height=bar_h, color=colors, zorder=3)
    ax.set_xlim(0, max(values) * 1.22)
    ax.margins(y=0.06 if n_rows > 8 else 0.11)

    for tick_label, g in zip(ax.get_yticklabels(), rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(12.5 if n_rows > 8 else 14)
        tick_label.set_color(ACCENT if g == HIGHLIGHT_GROUP else INK)

    for g, v, c in zip(rows, values, colors):
        ax.text(v + max(values) * 0.02, g, f"{v:.0f}%", va="center", ha="left",
                 color=c, fontproperties=fonts["bold"], fontsize=13 if n_rows > 8 else 15, zorder=4)

    _draw_title(fig, fonts, title, subtitle)
    _draw_caption(fig, fonts, total_n, note)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def render_distribution_stack(
    results: dict, group_order: list[str], seg_order: list[str], title: str, subtitle: str,
    note: str, total_n: int, out_path: Path, fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    n_rows = len(group_order)
    n_segs = len(seg_order)
    # Evenly spaced picks from the 7-step ramp so a 4-segment scale (prayer)
    # gets more contrast between adjacent steps than a naive first-4 slice.
    step_idxs = [round(i * (len(ORDINAL_RAMP_7) - 1) / (n_segs - 1)) for i in range(n_segs)]
    colors = [ORDINAL_RAMP_7[i] for i in step_idxs]
    text_colors = [LABEL_INK_FOR_STEP_7[i] for i in step_idxs]

    axes_height = min(0.56, 0.048 * n_rows + 0.08)
    AXES_LEFT, AXES_WIDTH = 0.36, 0.58
    ax = fig.add_axes([AXES_LEFT, 0.28, AXES_WIDTH, axes_height])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    rows = group_order[::-1]
    bar_h = 0.62 if n_rows <= 8 else 0.68

    left = [0.0] * len(rows)
    for seg_label, color, text_color in zip(seg_order, colors, text_colors):
        vals = [results[g]["shares_pct"][seg_label] for g in rows]
        ax.barh(rows, vals, left=left, height=bar_h, color=color,
                edgecolor=PAPER, linewidth=1.2, zorder=3)
        for g, v, l in zip(rows, vals, left):
            if v >= 7:
                ax.text(l + v / 2, g, f"{v:.0f}%", va="center", ha="center",
                        color=text_color, fontproperties=fonts["bold"],
                        fontsize=10.5 if n_rows > 8 else 12, zorder=4)
        left = [l + v for l, v in zip(left, vals)]

    ax.set_xlim(0, 100)
    ax.margins(y=0.06 if n_rows > 8 else 0.11)
    for tick_label, g in zip(ax.get_yticklabels(), rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(12 if n_rows > 8 else 14)
        tick_label.set_color(ACCENT if g == HIGHLIGHT_GROUP else INK)

    handles = [mpatches.Patch(facecolor=c, edgecolor=PAPER, label=l)
               for l, c in zip(seg_order, colors)]
    legend = ax.legend(
        handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.055),
        ncol=min(4, n_segs), frameon=False, handlelength=1.2, handleheight=1.2,
        fontsize=11, prop=fonts["bold"], columnspacing=1.2,
    )
    for text in legend.get_texts():
        text.set_color(INK)

    _draw_title(fig, fonts, title, subtitle)
    _draw_caption(fig, fonts, total_n, note)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--relimp-out", type=Path, required=True)
    ap.add_argument("--bibimp-out", type=Path, required=True)
    ap.add_argument("--attend-out", type=Path, required=True)
    ap.add_argument("--attend-monthly-out", type=Path, required=True)
    ap.add_argument("--memb-out", type=Path, required=True)
    ap.add_argument("--pray-out", type=Path, required=True)
    ap.add_argument("--pracb-out", type=Path, required=True)
    ap.add_argument("--pracc-out", type=Path, required=True)
    ap.add_argument("--grace-out", type=Path, required=True)
    ap.add_argument("--praca-out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    total_n = data["total_unweighted_n"]

    render_magnitude_bar(
        data["relimp_important"], CHRISTIAN_PLUS_OTHER_ORDER,
        title="Religion is important in their life",
        subtitle="Share who say religion is very or somewhat important\nin their life.",
        note="Population: Christian + other religions, excluding the unaffiliated; "
             "cutpoint is very+somewhat important (top-two-box).",
        total_n=total_n, out_path=args.relimp_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["bibimp_important"], CHRISTIAN_ORDER,
        title="The Bible is important in their life",
        subtitle="Share who say the Bible is extremely or very important\nin their life.",
        note="Population: Christian only; cutpoint is extremely+very important, as asked.",
        total_n=total_n, out_path=args.bibimp_out, fonts=fonts,
    )
    render_distribution_stack(
        data["attend_distribution"], ALL_RELIGIOUS_ORDER, data["attend_order"],
        title="Attendance frequency, full distribution",
        subtitle="How often each tradition's members attend religious\nservices in person.",
        note="Population: all religiously affiliated traditions, individually.",
        total_n=total_n, out_path=args.attend_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["attend_monthly_plus_either"], ALL_RELIGIOUS_ORDER,
        title="Attend in-person and/or online, monthly or more",
        subtitle="Share attending religious services monthly+ either\nin person or online/on TV.",
        note="Population: all religiously affiliated traditions, individually. Derived: "
             "monthly+ on ATTNDPERRLS or ATTNDONRLS.",
        total_n=total_n, out_path=args.attend_monthly_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["memb_member"], ALL_RELIGIOUS_ORDER,
        title="Member of a house of worship",
        subtitle="Share who are personally a member of a church,\nsynagogue, mosque, temple, or other house of worship.",
        note="Population: all religiously affiliated traditions, individually.",
        total_n=total_n, out_path=args.memb_out, fonts=fonts,
    )
    render_distribution_stack(
        data["pray_distribution"], ALL_RELIGIOUS_ORDER, data["pray_order"],
        title="Prayer frequency",
        subtitle="How often each tradition's members pray, outside of\nattending religious services.",
        note="Population: all religiously affiliated traditions, individually. Collapsed "
             "from Pew's 7-category scale to 4 (see practice.py's design_decisions).",
        total_n=total_n, out_path=args.pray_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["pracb_weekly_plus"], ALL_RELIGIOUS_ORDER,
        title="Read scripture outside of services, weekly+",
        subtitle="Share reading scripture at least once a week, outside\nof religious services.",
        note="Population: all religiously affiliated traditions, individually.",
        total_n=total_n, out_path=args.pracb_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["pracc_weekly_plus"], CHRISTIAN_ORDER,
        title="Read other holy texts or devotions, weekly+",
        subtitle="Share reading other holy texts, devotions, or\ninspirational literature at least once a week.",
        note="Population: Christian only.",
        total_n=total_n, out_path=args.pracc_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["grace_always"], CHRISTIAN_ORDER,
        title="Always say grace before meals",
        subtitle="Share who always pray or say grace before meals.",
        note="Population: Christian only; cutpoint is \"Always\" alone (top box).",
        total_n=total_n, out_path=args.grace_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["praca_weekly_plus"], CHRISTIAN_ORDER,
        title="Prayer or scripture study groups, weekly+",
        subtitle="Share participating in prayer groups, scripture study,\nor religious education programs weekly+.",
        note="Population: Christian only; \"at least once a week\" (the scale's own top category).",
        total_n=total_n, out_path=args.praca_out, fonts=fonts,
    )


if __name__ == "__main__":
    main()
