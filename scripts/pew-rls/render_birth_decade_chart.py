#!/usr/bin/env python3
"""Renders the birth-decade-makeup 100%-stacked PNG for the Pew RLS Data
Explorer page: share of each tradition's current members born in each
decade.

Reads only docs/datasets/pew-rls-2023-24/birth-decade-distribution.json
(produced by scripts/pew-rls/birth_decade_distribution.py) - no number here
is hand-typed. Same canvas/fonts as render_switching_chart.py; see STYLE.md
in this folder. Colors are the single-hue ordinal ramp
(`--chart-ordinal-1..7`, light-mode values from src/app/globals.css) rather
than an identity palette - this is a "which decade" scale, not a second set
of tradition colors.

Usage:
    python render_birth_decade_chart.py \
        --out ../../public/data-explorer/pew-religious-landscape-study/birth-decade-distribution.png
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
from chart_style import MIN, draw_caption_bottom  # noqa: E402

# ---------------------------------------------------------------------------
# House style tokens - see STYLE.md. Keep this block and STYLE.md in sync.
# ---------------------------------------------------------------------------

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"

# --chart-ordinal-1..7, light-mode values (src/app/globals.css) - faintest
# to most intense. Steps 1-4 need dark (INK) label text, 5-7 need white -
# same split documented in src/components/charts/palette.ts's LABEL_ON.
ORDINAL_RAMP = ["#e8eff6", "#c3d7e8", "#96b9d6", "#5e8db8", "#1f4f7a", "#163a5c", "#0d2740"]
LABEL_INK_FOR_STEP = [INK, INK, INK, INK, "#FFFFFF", "#FFFFFF", "#FFFFFF"]

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

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2023-24" / "birth-decade-distribution.json"
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


def render(data: dict, out_path: Path, fonts: dict[str, fm.FontProperties]) -> None:
    distribution = data["distribution"]
    decade_order = data["decade_order"]
    total_n = data["total_unweighted_n"]

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    # Caption drawn first (bottom-anchored) - see STYLE.md's "Footnotes:
    # bottom-anchored" section - so the axes/legend/note stack above it can
    # be placed relative to its real top edge.
    source_paragraphs = [
        f"Pew Research Center's Religious Landscape Study (RLS), 2023-24 wave · "
        f"N = {total_n:,} U.S. adults",
        "Pew Research Center. 2025. “2023-24 Religious Landscape Study (RLS) Dataset.” "
        "doi: 10.58094/3kwb-bf52.",
    ]
    caption_top = draw_caption_bottom(fig, fonts, source_paragraphs)
    note_y = caption_top + 0.04
    ax_bottom = note_y + 0.16

    AXES_LEFT, AXES_WIDTH = 0.30, 0.64
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, 0.32 + 0.44 - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)

    rows = GROUP_ORDER[::-1]  # bottom-to-top, so LDS plots at top
    bar_height = 0.6

    left = [0.0] * len(rows)
    for step, decade in enumerate(decade_order):
        color = ORDINAL_RAMP[step]
        text_color = LABEL_INK_FOR_STEP[step]
        vals = [distribution[g]["shares_pct"][decade] for g in rows]
        ax.barh(rows, vals, left=left, height=bar_height, color=color,
                edgecolor=PAPER, linewidth=1.5, zorder=3)
        for g, v, l in zip(rows, vals, left):
            if v >= 8:  # suppress a label that can't clear the mobile floor cleanly
                ax.text(
                    l + v / 2, g, f"{v:.0f}%", va="center", ha="center",
                    color=text_color, fontproperties=fonts["bold"], fontsize=MIN.DATA_LABEL, zorder=4,
                )
        left = [l + v for l, v in zip(left, vals)]

    ax.set_xlim(0, 100)
    ax.margins(y=0.11)

    for tick_label in ax.get_yticklabels():
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(15)
        tick_label.set_color(INK)

    handles = [
        mpatches.Patch(facecolor=c, edgecolor=PAPER, label=d)
        for d, c in zip(decade_order, ORDINAL_RAMP)
    ]
    legend = ax.legend(
        handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.09),
        ncol=4, frameon=False, handlelength=1.2, handleheight=1.2,
        fontsize=MIN.LEGEND, prop=fonts["bold"], columnspacing=1.2,
    )
    for text in legend.get_texts():
        text.set_color(INK)

    fig.text(
        AXES_LEFT, note_y,
        "The finest age measure the public-use file offers - no numeric median age.",
        fontproperties=fonts["regular"], fontsize=10, color=MUTED, ha="left", va="top",
    )

    # --- Title / subtitle -------------------------------------------------
    title_fontsize = 27
    title = "Birth-decade makeup, by tradition"
    title_lines = textwrap.wrap(title, width=26)
    line_spacing = title_fontsize / 650
    title_top = 0.965
    for i, line in enumerate(title_lines):
        fig.text(
            0.065, title_top - i * line_spacing, line,
            fontproperties=fonts["title"], fontsize=title_fontsize, color=INK, ha="left", va="top",
        )
    subtitle_y = title_top - len(title_lines) * line_spacing - 0.015
    fig.text(
        0.065, subtitle_y,
        "Share of each tradition's current members born in each decade.",
        fontproperties=fonts["regular"], fontsize=14, color=MUTED, ha="left", va="top",
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
