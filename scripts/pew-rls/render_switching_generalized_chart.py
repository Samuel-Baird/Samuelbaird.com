#!/usr/bin/env python3
"""Renders the two "switching, generalized" 100%-stacked composition PNGs
for the Pew RLS Data Explorer page: of today's members, raised in it or
converted in? and of those raised in it, stayed or left?

Reads only docs/datasets/pew-rls-2023-24/switching-generalized.json
(produced by scripts/pew-rls/switching_generalized.py) - no number here is
hand-typed. Same canvas/fonts as render_switching_chart.py; see STYLE.md in
this folder for the shared palette this implements.

Usage:
    python render_switching_generalized_chart.py \
        --composition-out ../../public/data-explorer/pew-religious-landscape-study/switching-current-composition.png \
        --raised-cohort-out ../../public/data-explorer/pew-religious-landscape-study/switching-raised-cohort.png
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
from chart_style import LEGEND_ROW_HEIGHT, MIN, draw_caption_bottom, sort_groups  # noqa: E402

# ---------------------------------------------------------------------------
# House style tokens - see STYLE.md. Keep this block and STYLE.md in sync.
# ---------------------------------------------------------------------------

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"
GRID = "#D9D5CC"

ACCENT = "#1f4f7a"  # --accent - "raised in it" / "stayed", the same weighted
                    # headcount read against two different denominators
HONEY = "#8a5a06"   # --honey - "converted in"
OXBLOOD = "#7c2d2d"  # --oxblood - "left", the site's decline/negative token
TEXT_ON_FILL = "#FFFFFF"  # every segment fill here is dark enough for white text

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120  # 1080x1350 - matches every other Data Explorer graphic

# Same order the two companion interactive figures used, kept here so a
# reader comparing this PNG against the old screenshots still recognizes it.
GROUP_ORDER = [
    "Latter-day Saint",
    "Catholic",
    "Protestant",
    "Orthodox Christian",
    "Jehovah's Witness",
]

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2023-24" / "switching-generalized.json"
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


def render_panel(
    switching: dict,
    total_unweighted_n: int,
    seg_keys: tuple[str, str],
    seg_labels: tuple[str, str],
    seg_colors: tuple[str, str],
    n_key: str,
    title: str,
    subtitle_lines: list[str],
    denominator_note: str,
    out_path: Path,
    fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    # Caption drawn first (bottom-anchored) so its real top edge is known
    # before the axes/legend/denominator-note stack above it is placed - see
    # STYLE.md's "Footnotes: bottom-anchored" section. The relative spacing
    # between caption -> denominator note -> axes bottom is preserved from
    # the old fixed layout; only the anchor point moved.
    caption_top = draw_caption_bottom(fig, fonts, [], handle="@ithinkisam | data: Pew 2023-24 RLS")
    denom_note_y = caption_top + 0.06
    legend_bottom_y = denom_note_y + 0.02
    legend_top_y = legend_bottom_y + LEGEND_ROW_HEIGHT  # 2 items, 1 row
    ax_bottom = legend_top_y + 0.02

    AXES_LEFT, AXES_WIDTH = 0.30, 0.64
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, 0.32 + 0.48 - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)

    # Sorted by each panel's own primary/first-listed segment (retained_in_pct
    # for the composition panel, stayed_pct for the raised-cohort panel).
    sorted_order = sort_groups(GROUP_ORDER, lambda g: switching[g][seg_keys[0]])
    rows = sorted_order[::-1]  # bottom-to-top, so the highest-sorted group plots at top
    bar_height = 0.6

    left = [0.0] * len(rows)
    for key, label, color in zip(seg_keys, seg_labels, seg_colors):
        vals = [switching[g][key] for g in rows]
        ax.barh(rows, vals, left=left, height=bar_height, color=color,
                edgecolor=INK, linewidth=1.5, zorder=3)
        for g, v, l in zip(rows, vals, left):
            if v >= 8:  # suppress a label that can't clear the mobile floor cleanly
                ax.text(
                    l + v / 2, g, f"{v:.0f}%", va="center", ha="center",
                    color=TEXT_ON_FILL, fontproperties=fonts["bold"], fontsize=MIN.DATA_LABEL, zorder=4,
                )
        left = [l + v for l, v in zip(left, vals)]

    ax.set_xlim(0, 100)
    ax.margins(y=0.11)

    for tick_label in ax.get_yticklabels():
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(MIN.LEGEND)
        tick_label.set_color(INK)

    handles = [mpatches.Patch(facecolor=c, edgecolor=INK, label=l) for l, c in zip(seg_labels, seg_colors)]
    legend = ax.legend(
        handles=handles, loc="upper left", bbox_to_anchor=(AXES_LEFT, legend_top_y),
        bbox_transform=fig.transFigure,
        ncol=len(handles), frameon=False, handlelength=1.6, handleheight=1.6,
        fontsize=MIN.LEGEND, prop=fonts["bold"], columnspacing=1.4, labelspacing=0.9,
    )
    for text in legend.get_texts():
        text.set_color(INK)
        text.set_fontsize(MIN.LEGEND)  # legend()'s fontsize= is ignored when prop= is also passed

    fig.text(
        AXES_LEFT, denom_note_y, denominator_note,
        fontproperties=fonts["regular"], fontsize=10, color=MUTED, ha="left", va="top",
    )

    # --- Title / subtitle -------------------------------------------------
    # Dynamic wrap + spacing, same approach as
    # scripts/state-of-theology-graphics/render_chart.py's long-statement
    # titles: line_spacing scales with fontsize so title/subtitle never
    # collide regardless of how many lines the title wraps to.
    title_fontsize = 26
    title_lines = textwrap.wrap(title, width=24)
    line_spacing = title_fontsize / 650
    title_top = 0.965
    for i, line in enumerate(title_lines):
        fig.text(
            0.065, title_top - i * line_spacing, line,
            fontproperties=fonts["title"], fontsize=title_fontsize, color=INK, ha="left", va="top",
        )
    subtitle_y = title_top - len(title_lines) * line_spacing - 0.015
    fig.text(
        0.065, subtitle_y, "\n".join(subtitle_lines),
        fontproperties=fonts["regular"], fontsize=14, color=MUTED, ha="left", va="top",
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--composition-out", type=Path, required=True)
    ap.add_argument("--raised-cohort-out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    switching = data["switching_generalized"]
    total_n = data["total_unweighted_n"]

    render_panel(
        switching, total_n,
        seg_keys=("retained_in_pct", "converted_in_pct"),
        seg_labels=("Raised in it", "Converted in"),
        seg_colors=(ACCENT, HONEY),
        n_key="current_unweighted_n",
        title="Of today's members: raised in it, or converted in?",
        subtitle_lines=[
            "Each tradition's current membership, split by whether they",
            "were raised in it or joined from elsewhere.",
        ],
        denominator_note="Denominator: each tradition's current (2023-24) membership.",
        out_path=args.composition_out,
        fonts=fonts,
    )
    render_panel(
        switching, total_n,
        seg_keys=("stayed_pct", "left_pct"),
        seg_labels=("Stayed", "Left"),
        seg_colors=(ACCENT, OXBLOOD),
        n_key="raised_unweighted_n",
        title="Of those raised in it: still in it, or left?",
        subtitle_lines=[
            "People raised in each tradition, split by whether they're",
            "still in it today.",
        ],
        denominator_note="Denominator: each tradition's raised-in-it cohort (FRMREL).",
        out_path=args.raised_cohort_out,
        fonts=fonts,
    )


if __name__ == "__main__":
    main()
