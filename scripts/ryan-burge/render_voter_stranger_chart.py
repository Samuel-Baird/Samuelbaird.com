#!/usr/bin/env python3
"""Renders "Feel like a stranger in my own country," by religion (2017
wave), for the VOTER Survey Panel Data Explorer page.

Reads only docs/datasets/ryan-burge/voter-stranger.json (produced by
scripts/ryan-burge/voter_stranger.py) - no number here is hand-typed. Same
canvas/fonts/vertical-centering rule as the rest of this pipeline (see
scripts/pew-rls/STYLE.md).

Usage:
    python render_voter_stranger_chart.py \
        --out ../../public/data-explorer/voter-survey-panel/stranger-2017.png
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
from chart_style import LEGEND_ROW_HEIGHT, MIN, draw_caption_bottom  # noqa: E402

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"

# --chart-ordinal-1..7, light-mode values, resampled to 4 steps for extra
# contrast between adjacent segments - same approach as the Pew RLS
# pipeline's own frequency-scale stacks.
ORDINAL_RAMP_7 = ["#e8eff6", "#c3d7e8", "#96b9d6", "#5e8db8", "#1f4f7a", "#163a5c", "#0d2740"]
LABEL_INK_FOR_STEP_7 = [INK, INK, INK, INK, "#FFFFFF", "#FFFFFF", "#FFFFFF"]

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge" / "voter-stranger.json"
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


def draw_title(fig, fonts, title: str, subtitle: str, width: int = 27,
                title_fontsize: float = 26, subtitle_fontsize: float = 13.5) -> float:
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


def render(data: dict, out_path: Path, fonts: dict[str, fm.FontProperties]) -> None:
    results = data["results"]
    group_order = data["group_order"]
    seg_order = data["stranger_order"]

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    title = "“These days I feel like a stranger in my own country”"
    subtitle = "Agreement with this statement, by religion (2017 wave)."
    subtitle_bottom = draw_title(fig, fonts, title, subtitle)

    caption_top = draw_caption_bottom(fig, fonts, [], handle="@ithinkisam | data: Ryan Burge, Voter Study Group")
    ax_top = subtitle_bottom - 0.03

    legend_ncol = 2
    legend_rows = -(-len(seg_order) // legend_ncol)  # ceil division
    legend_bottom_y = caption_top + 0.02
    legend_top_y = legend_bottom_y + LEGEND_ROW_HEIGHT * legend_rows
    ax_bottom = legend_top_y + 0.02

    AXES_LEFT, AXES_WIDTH = 0.34, 0.60
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    rows = group_order[::-1]
    n_segs = len(seg_order)
    step_idxs = [round(i * (len(ORDINAL_RAMP_7) - 1) / (n_segs - 1)) for i in range(n_segs)]
    colors = [ORDINAL_RAMP_7[i] for i in step_idxs]
    text_colors = [LABEL_INK_FOR_STEP_7[i] for i in step_idxs]

    left = [0.0] * len(rows)
    for seg_label, color, text_color in zip(seg_order, colors, text_colors):
        vals = [results[g]["shares_pct"][seg_label] for g in rows]
        ax.barh(rows, vals, left=left, height=0.65, color=color,
                edgecolor=PAPER, linewidth=1.2, zorder=3)
        for g, v, l in zip(rows, vals, left):
            if v >= 8:  # suppress a label that can't clear the mobile floor cleanly
                ax.text(l + v / 2, g, f"{v:.0f}%", va="center", ha="center",
                        color=text_color, fontproperties=fonts["bold"], fontsize=MIN.DATA_LABEL, zorder=4)
        left = [l + v for l, v in zip(left, vals)]

    ax.set_xlim(0, 100)
    ax.margins(y=0.06)
    for tick_label, g in zip(ax.get_yticklabels(), rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(13)
        tick_label.set_color(INK)

    handles = [mpatches.Patch(facecolor=c, edgecolor=PAPER, label=l)
               for l, c in zip(seg_order, colors)]
    legend = ax.legend(
        handles=handles, loc="upper left", bbox_to_anchor=(0.065, legend_top_y),
        bbox_transform=fig.transFigure,
        ncol=legend_ncol, frameon=False, handlelength=1.6, handleheight=1.6,
        fontsize=MIN.LEGEND, prop=fonts["bold"], columnspacing=1.4, labelspacing=0.9,
    )
    for text in legend.get_texts():
        text.set_color(INK)
        text.set_fontsize(MIN.LEGEND)  # legend()'s fontsize= is ignored when prop= is also passed

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    render(data, args.out, fonts)


if __name__ == "__main__":
    main()
