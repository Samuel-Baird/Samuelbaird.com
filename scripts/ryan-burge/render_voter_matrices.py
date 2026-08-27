#!/usr/bin/env python3
"""Renders the three VOTER Survey Panel "matrix" PNGs for the Ryan Burge
Data Explorer page: feeling thermometers (racial/religious and
political/social) and issue importance, all by religion (2017 wave).

Reads only the three docs/datasets/ryan-burge/voter-*.json files (produced
by scripts/ryan-burge/voter_matrices.py) - no number here is hand-typed.
This is a heatmap/small-multiples matrix shape - one row per target (the
7/9/23 things being rated), one column per religion group, each cell colored
by a tri-color diverging ramp (low -> white -> high, semantically anchored
per chart - see scripts/ryan-burge/STYLE.md) and printing its own value -
matching this pipeline's "every mark carries its own printed label" rule
even in a heatmap. Same vertical-centering layout rule as the rest of the
pipeline (see scripts/pew-rls/STYLE.md), captions bottom-anchored via
scripts/chart_style.py.

Usage: see the three --*-out flags below; run with --help for the full list.
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import (  # noqa: E402
    BORDER,
    DIV_COOL_BLUE,
    DIV_WARM_RED,
    MIN,
    diverging_color,
    draw_caption_bottom,
    label_ink,
)

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"
HIGHLIGHT_GROUP = "Mormon"

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120

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


def draw_title(fig, fonts, title: str, subtitle: str, width: int = 34,
                title_fontsize: float = MIN.TITLE, subtitle_fontsize: float = MIN.SUBTITLE) -> float:
    title_lines = textwrap.wrap(title, width=width)
    line_spacing = title_fontsize / 650
    title_top = 0.975
    for i, line in enumerate(title_lines):
        fig.text(
            0.045, title_top - i * line_spacing, line,
            fontproperties=fonts["title"], fontsize=title_fontsize, color=INK, ha="left", va="top",
        )
    subtitle_y = title_top - len(title_lines) * line_spacing - 0.012
    fig.text(
        0.045, subtitle_y, subtitle,
        fontproperties=fonts["regular"], fontsize=subtitle_fontsize, color=MUTED, ha="left", va="top",
    )
    subtitle_lines = subtitle.count("\n") + 1
    subtitle_line_height = subtitle_fontsize * 1.2 / 72 / FIG_H_IN
    return subtitle_y - subtitle_lines * subtitle_line_height


def render_heatmap(
    matrix: dict, row_order: list[str], col_order: list[str], value_min: float, value_max: float,
    unit: str, title: str, subtitle: str, note: str, out_path: Path,
    fonts: dict[str, fm.FontProperties],
    low_color: str = DIV_COOL_BLUE, high_color: str = DIV_WARM_RED, mid_value: float | None = None,
) -> None:
    """mid_value defaults to the scale's own midpoint ((value_min + value_max)
    / 2) - the ramp's white point should be the scale's substantive midpoint,
    not the data's median. See scripts/ryan-burge/STYLE.md for anchor-color
    choice per chart."""
    if mid_value is None:
        mid_value = (value_min + value_max) / 2

    def cell_color(val: float) -> str:
        t = (val - value_min) / (value_max - value_min)
        # Re-scale so mid_value lands exactly at t=0.5 on the diverging ramp,
        # even when it isn't the arithmetic midpoint of [value_min, value_max].
        mid_t = (mid_value - value_min) / (value_max - value_min)
        if mid_t <= 0:
            t = 0.5 + 0.5 * t
        elif mid_t >= 1:
            t = 0.5 * t
        elif t <= mid_t:
            t = 0.5 * (t / mid_t) if mid_t else 0.5
        else:
            t = 0.5 + 0.5 * (t - mid_t) / (1 - mid_t)
        return diverging_color(t, low_color, high_color)

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = draw_title(fig, fonts, title, subtitle)

    source_paragraphs = [
        note,
        "Democracy Fund Voter Study Group / YouGov, VOTER Survey Panel, via "
        "Ryan Burge (github.com/ryanburge).",
    ]
    caption_top = draw_caption_bottom(
        fig, fonts, source_paragraphs, left=0.045, wrap_width=118, fontsize=9, line_step=0.0145,
    )

    ax_top = subtitle_bottom - 0.025
    ax_bottom = caption_top + 0.02

    ROW_LABEL_W = 0.34
    AXES_LEFT, AXES_RIGHT = 0.045, 0.975
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_RIGHT - AXES_LEFT, ax_top - ax_bottom])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    n_rows = len(row_order)
    n_cols = len(col_order)
    grid_left = ROW_LABEL_W
    grid_w = 1.0 - grid_left
    col_w = grid_w / n_cols

    # Stacked top-down, each band given real separation from its neighbor:
    # legend strip, then rotated column headers (which need room to extend
    # upward from their anchor), then the grid itself.
    legend_h = 0.035
    legend_y0, legend_y1 = 1.0 - legend_h, 1.0
    header_h = min(0.13, (1.0 - legend_h) / n_rows * 1.8)
    header_gap = 0.018
    plot_top = legend_y0 - header_gap - header_h

    n_steps = 40
    for k in range(n_steps):
        x0 = grid_left + k * (grid_w / n_steps)
        t = k / (n_steps - 1)
        val = value_min + t * (value_max - value_min)
        ax.add_patch(Rectangle((x0, legend_y0), grid_w / n_steps + 0.001, legend_y1 - legend_y0,
                                facecolor=cell_color(val), edgecolor="none", zorder=2))
    ax.text(grid_left, legend_y1 + 0.006, f"{value_min:.0f}{unit}", ha="left", va="bottom",
            fontproperties=fonts["regular"], fontsize=MIN.LEGEND, color=MUTED)
    ax.text(grid_left + grid_w / 2, legend_y1 + 0.006, f"{mid_value:.0f}{unit}", ha="center", va="bottom",
            fontproperties=fonts["regular"], fontsize=MIN.LEGEND, color=MUTED)
    ax.text(grid_left + grid_w, legend_y1 + 0.006, f"{value_max:.0f}{unit}", ha="right", va="bottom",
            fontproperties=fonts["regular"], fontsize=MIN.LEGEND, color=MUTED)

    # Column headers (religion group names), rotated for narrow columns.
    for j, group in enumerate(col_order):
        cx = grid_left + (j + 0.5) * col_w
        color = "#1f4f7a" if group == HIGHLIGHT_GROUP else INK
        ax.text(cx, plot_top + header_h, group, ha="right", va="top",
                rotation=38, rotation_mode="anchor",
                fontproperties=fonts["bold"], fontsize=MIN.HEATMAP_HEADER, color=color)

    for i, row_label in enumerate(row_order):
        y0 = plot_top - (i + 1) * (plot_top / n_rows)
        y1 = plot_top - i * (plot_top / n_rows)
        cell_h = y1 - y0
        ax.text(grid_left - 0.012, (y0 + y1) / 2, row_label, ha="right", va="center",
                fontproperties=fonts["bold"], fontsize=MIN.HEATMAP_HEADER, color=INK)
        for j, group in enumerate(col_order):
            x0 = grid_left + j * col_w
            val = matrix[group][row_label]
            if val is None:
                fig_color = PAPER
                label = "n/a"
                text_color = MUTED
            else:
                fig_color = cell_color(val)
                label = f"{val:.0f}{unit}"
                text_color = label_ink(fig_color)
            ax.add_patch(Rectangle((x0, y0), col_w, cell_h, facecolor=fig_color,
                                    edgecolor=BORDER, linewidth=1.2, zorder=2))
            ax.text(x0 + col_w / 2, (y0 + y1) / 2, label, ha="center", va="center",
                    fontproperties=fonts["bold"], fontsize=MIN.HEATMAP_CELL, color=text_color, zorder=3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--racial-out", type=Path, required=True)
    ap.add_argument("--political-out", type=Path, required=True)
    ap.add_argument("--imiss-out", type=Path, required=True)
    ap.add_argument(
        "--data-dir", type=Path,
        default=(Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge").resolve(),
    )
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()
    fonts = load_fonts(args.fonts_dir)

    with open(args.data_dir / "voter-ft-racial-religious.json", encoding="utf-8") as f:
        racial = json.load(f)
    with open(args.data_dir / "voter-ft-political-social.json", encoding="utf-8") as f:
        political = json.load(f)
    with open(args.data_dir / "voter-issue-importance.json", encoding="utf-8") as f:
        imiss = json.load(f)

    excluded_note = "Too thin to show individually: " + ", ".join(racial["excluded_too_thin"].values()) + "."

    # Feeling thermometers: the thermometer's own cold/warm metaphor - fully
    # colorblind-safe since it doesn't depend on red/green discrimination.
    render_heatmap(
        racial["matrix"], racial["target_order"], racial["group_order"], 0, 100, "",
        title="Feeling thermometers: racial and religious groups, by religion",
        subtitle="0 = coldest/most unfavorable, 100 = warmest/most favorable. Weighted means.",
        note=f"Population: religpew_2017, weighted by weight_2017. {excluded_note}",
        out_path=args.racial_out, fonts=fonts,
        low_color=DIV_COOL_BLUE, high_color=DIV_WARM_RED,
    )
    render_heatmap(
        political["matrix"], political["target_order"], political["group_order"], 0, 100, "",
        title="Feeling thermometers: political and social groups, by religion",
        subtitle="0 = coldest/most unfavorable, 100 = warmest/most favorable. Weighted means.",
        note=f"Population: religpew_2017, weighted by weight_2017. {excluded_note}",
        out_path=args.political_out, fonts=fonts,
        low_color=DIV_COOL_BLUE, high_color=DIV_WARM_RED,
    )
    # Issue importance: non-valenced intensity ("how much"), not a value
    # judgment - stays on the neutral blue-red ramp rather than green/red.
    render_heatmap(
        imiss["matrix"], imiss["target_order"], imiss["group_order"], 0, 100, "%",
        title="Issue importance, by religion",
        subtitle="Share saying very or somewhat important (top-two-box).",
        note=f"Population: religpew_2017, weighted by weight_2017. {excluded_note}",
        out_path=args.imiss_out, fonts=fonts,
        low_color=DIV_COOL_BLUE, high_color=DIV_WARM_RED,
    )


if __name__ == "__main__":
    main()
