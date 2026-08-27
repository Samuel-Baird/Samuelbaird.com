#!/usr/bin/env python3
"""Renders the three "childhood formation" PNGs for the Pew RLS Data
Explorer page: grew up attending church monthly+, religion very important
to family growing up, and religious education received.

Reads only docs/datasets/pew-rls-2023-24/childhood-formation.json
(produced by scripts/pew-rls/childhood_formation.py) - no number here is
hand-typed. Same canvas/fonts as render_switching_chart.py; see STYLE.md in
this folder. The first two items are single-value magnitude comparisons,
so they use the highlight-vs-gray convention (Latter-day Saint in
--accent, every other group in muted gray) rather than the diverging or
100%-stacked treatments used elsewhere on this page. The third item is a
real 4-category distribution, so it's a 100%-stacked bar like
render_switching_generalized_chart.py.

Usage:
    python render_childhood_formation_charts.py \
        --attendance-out ../../public/data-explorer/pew-religious-landscape-study/childhood-attendance.png \
        --importance-out ../../public/data-explorer/pew-religious-landscape-study/childhood-importance.png \
        --education-out ../../public/data-explorer/pew-religious-landscape-study/childhood-education.png
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import draw_caption_bottom  # noqa: E402

# ---------------------------------------------------------------------------
# House style tokens - see STYLE.md. Keep this block and STYLE.md in sync.
# ---------------------------------------------------------------------------

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"

ACCENT = "#1f4f7a"       # --accent - the one highlighted series (Latter-day Saint)
CONTEXT_GRAY = "#8f8b82"  # a bar-fill-safe lighten of --muted - readable at full
                          # opacity as a fill (unlike the line chart's stroke use)
TEXT_ON_FILL = "#FFFFFF"

# Same two colors render_switching_generalized_chart.py uses for the
# comparable "raised in it" / "converted in"-style split.
EDU_RAMP = ["#d9d2c2", "#b3a487", "#8a7550", "#5c4a26"]  # None -> 7+ years, light to dark

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120  # 1080x1350 - matches every other Data Explorer graphic

GROUP_ORDER = [
    "Latter-day Saint",
    "Catholic",
    "Protestant",
    "Orthodox Christian",
    "Jehovah's Witness",
    "Other Christian",
    "Christian average",
]
HIGHLIGHT_GROUP = "Latter-day Saint"

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2023-24" / "childhood-formation.json"
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


def draw_title(fig, fonts, title: str, subtitle: str, width: int = 26,
                subtitle_fontsize: float = 14) -> float:
    """Dynamic wrap + spacing, same approach as render_switching_generalized_chart.py.
    Returns the y-fraction where the subtitle block actually ends (not just
    where it starts) - see STYLE.md's "Vertical layout" section - so the
    caller can size its axes to the real available band instead of a fixed
    guess. Title lines are placed one at a time so their bottom is exact;
    the subtitle is one fig.text() call with an embedded newline, so its
    height is matplotlib's default linespacing (1.2x fontsize) times its
    line count, converted from points to figure-fraction units."""
    title_fontsize = 27
    title_lines = textwrap.wrap(title, width=width)
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
        fontproperties=fonts["regular"], fontsize=subtitle_fontsize, color=MUTED, ha="left", va="top",
    )
    subtitle_lines = subtitle.count("\n") + 1
    subtitle_line_height = subtitle_fontsize * 1.2 / 72 / FIG_H_IN
    return subtitle_y - subtitle_lines * subtitle_line_height


def draw_caption(fig, fonts, total_n: int, extra_note: str | None) -> float:
    """Bottom-anchored caption - see STYLE.md's "Footnotes: bottom-anchored"
    section. Returns caption_top for the vertical-centering contract."""
    source_paragraphs = [
        f"Pew Research Center's Religious Landscape Study (RLS), 2023-24 wave · "
        f"N = {total_n:,} U.S. adults raised Christian",
        "Pew Research Center. 2025. “2023-24 Religious Landscape Study (RLS) Dataset.” "
        "doi: 10.58094/3kwb-bf52.",
    ]
    if extra_note:
        source_paragraphs.insert(0, extra_note)
    return draw_caption_bottom(fig, fonts, source_paragraphs)


def render_magnitude_bar(
    results: dict, title: str, subtitle: str, note: str, out_path: Path,
    fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    # Vertical centering: size the axes to the real gap between the
    # subtitle and the caption, not a fixed guess - see STYLE.md. Caption is
    # drawn first (bottom-anchored) so its real top edge is known.
    subtitle_bottom = draw_title(fig, fonts, title, subtitle)
    caption_top = draw_caption(fig, fonts, results["Christian average"]["group_unweighted_n"], note)
    ax_top = subtitle_bottom - 0.035
    ax_bottom = caption_top + 0.035

    AXES_LEFT, AXES_WIDTH = 0.30, 0.64
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)

    rows = GROUP_ORDER[::-1]
    values = [results[g]["pct"] for g in rows]
    colors = [ACCENT if g == HIGHLIGHT_GROUP else CONTEXT_GRAY for g in rows]

    ax.barh(rows, values, height=0.6, color=colors, zorder=3)
    ax.set_xlim(0, max(values) * 1.18)
    ax.margins(y=0.11)

    for tick_label, g in zip(ax.get_yticklabels(), rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(15)
        tick_label.set_color(ACCENT if g == HIGHLIGHT_GROUP else INK)

    for g, v, c in zip(rows, values, colors):
        ax.text(v + max(values) * 0.02, g, f"{v:.0f}%", va="center", ha="left",
                 color=c, fontproperties=fonts["bold"], fontsize=15, zorder=4)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def render_education_stack(
    results: dict, decade_order: list[str], title: str, subtitle: str, note: str,
    out_path: Path, fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    # Vertical centering, same approach as render_magnitude_bar above, with
    # extra bottom room reserved for the legend row below the axes.
    subtitle_bottom = draw_title(fig, fonts, title, subtitle)
    caption_top = draw_caption(fig, fonts, results["Christian average"]["group_unweighted_n"], note)
    ax_top = subtitle_bottom - 0.035
    ax_bottom = caption_top + 0.035 + 0.05

    AXES_LEFT, AXES_WIDTH = 0.30, 0.64
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)

    rows = GROUP_ORDER[::-1]
    bar_height = 0.6

    left = [0.0] * len(rows)
    for step, seg_label in enumerate(decade_order):
        color = EDU_RAMP[step]
        text_color = INK if step < 2 else TEXT_ON_FILL
        vals = [results[g]["shares_pct"][seg_label] for g in rows]
        ax.barh(rows, vals, left=left, height=bar_height, color=color,
                edgecolor=PAPER, linewidth=1.5, zorder=3)
        for g, v, l in zip(rows, vals, left):
            if v >= 6:
                ax.text(l + v / 2, g, f"{v:.0f}%", va="center", ha="center",
                        color=text_color, fontproperties=fonts["bold"], fontsize=12, zorder=4)
        left = [l + v for l, v in zip(left, vals)]

    ax.set_xlim(0, 100)
    ax.margins(y=0.11)
    for tick_label in ax.get_yticklabels():
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(15)
        tick_label.set_color(INK)

    handles = [mpatches.Patch(facecolor=c, edgecolor=PAPER, label=l)
               for l, c in zip(decade_order, EDU_RAMP)]
    legend = ax.legend(
        handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.09),
        ncol=4, frameon=False, handlelength=1.2, handleheight=1.2,
        fontsize=11.5, prop=fonts["bold"], columnspacing=1.2,
    )
    for text in legend.get_texts():
        text.set_color(INK)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--attendance-out", type=Path, required=True)
    ap.add_argument("--importance-out", type=Path, required=True)
    ap.add_argument("--education-out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)

    render_magnitude_bar(
        data["chattend_monthly_plus"],
        title="Grew up attending church monthly or more",
        subtitle="Share of each Christian tradition's raised-in-it population, by\nchildhood attendance frequency.",
        note="Population: respondents raised in each Christian tradition (FRMREL); "
             "excludes don't know/refused.",
        out_path=args.attendance_out,
        fonts=fonts,
    )
    render_magnitude_bar(
        data["chimprel_very_important"],
        title="Religion was very important to their family growing up",
        subtitle="Share of each Christian tradition's raised-in-it population who\nsay religion was \"very important\" to their family.",
        note="Population: respondents raised in each Christian tradition (FRMREL); "
             "excludes don't know/refused.",
        out_path=args.importance_out,
        fonts=fonts,
    )
    render_education_stack(
        data["chedu2_distribution"], data["chedu2_order"],
        title="Religious education received growing up",
        subtitle="Years of Sunday School, CCD, or similar religious education, by\ntradition raised in.",
        note="Population: respondents raised in each Christian tradition (FRMREL); "
             "excludes don't know/refused.",
        out_path=args.education_out,
        fonts=fonts,
    )


if __name__ == "__main__":
    main()
