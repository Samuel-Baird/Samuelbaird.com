#!/usr/bin/env python3
"""Renders the "switching, generalized" graphic for the Pew RLS Data
Explorer page: a fuller composition view than the shipped net-change chart,
split into the two questions GRAPHICS_TODO.md's "Switching, generalized"
item asks for, each its own 100%-stacked small-multiples panel (see
switching_generalized.py's docstring for why one merged bar isn't used).

Reads only docs/datasets/pew-rls-2023-24/switching-generalized.json
(produced by switching_generalized.py from the microdata) - no number here
is hand-typed.

Color: the "stayed" segment (raised in a tradition AND still in it) is the
same weighted headcount in both panels, just read against two different
denominators - current members in panel 1, the raised cohort in panel 2 -
so it gets one shared color (--accent) across both rather than four
unrelated hues. "Converted in" (panel 1) takes --honey, the site's single
deliberate-highlight token, since a convert is the notable/non-default case
for a tradition's current composition. "Left" (panel 2) takes --oxblood,
BRANDING_AND_DESIGN.md's decline/negative token, since leaving a tradition
one was raised in is exactly the decline signal that token is reserved for.

Usage:
    python render_switching_generalized_chart.py \
        --out ../../public/data-explorer/pew-religious-landscape-study/switching-generalized.png
"""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"

ACCENT = "#1f4f7a"    # --accent: shared "stayed" segment, both panels
HONEY = "#8a5a06"     # --honey: single deliberate highlight -> "converted in"
OXBLOOD = "#7c2d2d"   # --oxblood: decline/negative token -> "left"

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120  # 1080x1350 - matches every other Data Explorer graphic

# Same six-group order as switching_rates.py's GROUP_ORDER, Christian
# average appended as a reference row - matching the birth-decade chart's
# own precedent for where the reference row sits.
GROUP_ORDER = [
    "Christian average",
    "Other Christian",
    "Jehovah's Witness",
    "Orthodox Christian",
    "Latter-day Saint",
    "Protestant",
    "Catholic",
]

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2023-24"
    / "switching-generalized.json"
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


def draw_panel(fig, ax, groups, left_vals, right_vals, left_color, right_color,
                left_label, right_label, fonts, show_ylabels: bool) -> None:
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)
    ax.set_xlim(0, 100)
    ax.margins(y=0.10)

    bar_height = 0.6
    ax.barh(groups, left_vals, height=bar_height, color=left_color, zorder=3)
    ax.barh(groups, right_vals, left=left_vals, height=bar_height, color=right_color, zorder=3)

    for g, lv, rv in zip(groups, left_vals, right_vals):
        if lv >= 8:
            ax.text(lv / 2, g, f"{lv:.0f}", va="center", ha="center",
                     color=PAPER, fontproperties=fonts["bold"], fontsize=11)
        if rv >= 8:
            ax.text(lv + rv / 2, g, f"{rv:.0f}", va="center", ha="center",
                     color=PAPER, fontproperties=fonts["bold"], fontsize=11)

    if show_ylabels:
        for label in ax.get_yticklabels():
            label.set_fontproperties(fonts["bold"])
            label.set_fontsize(14)
            label.set_color(INK)
    else:
        ax.set_yticklabels([])


def render(data: dict, out_path: Path, fonts: dict[str, fm.FontProperties]) -> None:
    switching = data["switching_generalized"]
    total_n = data["total_unweighted_n"]
    groups = GROUP_ORDER

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    AXES_LEFT, AXES_WIDTH = 0.30, 0.64
    ax_current = fig.add_axes([AXES_LEFT, 0.605, AXES_WIDTH, 0.235])
    ax_raised = fig.add_axes([AXES_LEFT, 0.285, AXES_WIDTH, 0.235])

    retained = [switching[g]["retained_in_pct"] for g in groups]
    converted = [switching[g]["converted_in_pct"] for g in groups]
    stayed = [switching[g]["stayed_pct"] for g in groups]
    left = [switching[g]["left_pct"] for g in groups]

    fig.text(AXES_LEFT, 0.858, "Of today's members: raised in it, or converted in?",
              fontproperties=fonts["bold"], fontsize=15, color=INK, ha="left", va="top")
    draw_panel(fig, ax_current, groups, retained, converted, ACCENT, HONEY,
               "Raised in it", "Converted in", fonts, show_ylabels=True)

    fig.text(AXES_LEFT, 0.538, "Of those raised in it: still in it, or left?",
              fontproperties=fonts["bold"], fontsize=15, color=INK, ha="left", va="top")
    draw_panel(fig, ax_raised, groups, stayed, left, ACCENT, OXBLOOD,
               "Stayed", "Left", fonts, show_ylabels=True)

    # --- Shared legend, one per panel, directly under each --------------
    def legend_row(y, left_label, left_color, right_label, right_color):
        x = AXES_LEFT
        swatch_w, swatch_h = 0.022, 0.014
        for label, color in ((left_label, left_color), (right_label, right_color)):
            fig.patches.append(plt.Rectangle((x, y), swatch_w, swatch_h,
                                              transform=fig.transFigure,
                                              facecolor=color, edgecolor="none"))
            fig.text(x + swatch_w + 0.006, y + swatch_h / 2, label,
                      fontproperties=fonts["regular"], fontsize=10, color=MUTED,
                      ha="left", va="center")
            x += swatch_w + 0.006 + 0.012 * len(label) + 0.03

    legend_row(0.585, "Raised in it", ACCENT, "Converted in", HONEY)
    legend_row(0.265, "Stayed", ACCENT, "Left", OXBLOOD)

    # --- Title / subtitle ---------------------------------------------------
    fig.text(
        0.065, 0.965, "Switching, generalized",
        fontproperties=fonts["title"], fontsize=28, color=INK, ha="left", va="top",
    )
    fig.text(
        0.065, 0.912,
        "Two views of the same raised-vs-current cross-tab behind \"Net change\n"
        "since childhood\" — composition, not one net number. 2023-24 Religious\n"
        "Landscape Study.",
        fontproperties=fonts["regular"], fontsize=13, color=MUTED, ha="left", va="top",
    )

    # --- Caption --------------------------------------------------------------
    source_paragraphs = [
        f"Pew Research Center's Religious Landscape Study (RLS), 2023-24 wave · "
        f"N = {total_n:,} U.S. adults",
        "Top panel's base is each tradition's current (CURREL) membership; bottom panel's "
        "base is people raised (FRMREL) in it — different denominators, so the two panels' "
        "bars aren't directly comparable in absolute headcount, only within their own panel.",
        "Pew Research Center. 2025. “2023-24 Religious Landscape Study (RLS) Dataset.” "
        "doi: 10.58094/3kwb-bf52.",
    ]
    caption_lines = [line for para in source_paragraphs for line in textwrap.wrap(para, width=98)]
    caption_y = 0.20
    for i, line in enumerate(caption_lines):
        fig.text(
            0.065, caption_y - i * 0.0165, line, fontproperties=fonts["regular"],
            fontsize=10, color=MUTED, ha="left", va="top",
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True, help="output PNG path")
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    render(data, args.out, fonts)


if __name__ == "__main__":
    main()
