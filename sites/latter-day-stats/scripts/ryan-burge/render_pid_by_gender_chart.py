#!/usr/bin/env python3
"""Renders "Party ID (pid7), LDS men vs. LDS women, over time" for the CES
Stacked 2006-2018 Data Explorer page.

Reads only docs/datasets/ryan-burge/pid-by-gender.json (produced by
scripts/ryan-burge/pid_by_gender.py) - no number here is hand-typed. Same
canvas/fonts as the Pew RLS pipeline (see scripts/pew-rls/STYLE.md), with
the same vertical-centering layout rule that STYLE.md documents. Sixteen
rows (8 waves x 2 genders), most-recent wave at top, men above women
within each wave. Three segments (Democrat/Independent/Republican, per
this item's own design-decision collapse) use `--accent` for Democrat and
`--honey` for Republican - not literal red/blue, and not `--oxblood`
(reserved sitewide for decline signals, not a party) - with a neutral gray
for Independent.

Usage:
    python render_pid_by_gender_chart.py \
        --out ../../public/data-explorer/ces-stacked-2006-2018/pid-by-gender.png
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

DEM_COLOR = "#1f4f7a"    # --accent
IND_COLOR = "#8f8b82"    # bar-fill-safe lighten of --muted
REP_COLOR = "#8a5a06"    # --honey
TEXT_ON_FILL = "#FFFFFF"

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge" / "pid-by-gender.json"
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


def draw_title(fig, fonts, title: str, subtitle: str, width: int = 35,
                title_fontsize: float = 32, subtitle_fontsize: float = 16) -> float:
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
        fontproperties=fonts["regular"], fontsize=subtitle_fontsize, color=INK, ha="left", va="top",
    )
    subtitle_lines = subtitle.count("\n") + 1
    subtitle_line_height = subtitle_fontsize * 1.2 / 72 / FIG_H_IN
    return subtitle_y - subtitle_lines * subtitle_line_height


def render(data: dict, out_path: Path, fonts: dict[str, fm.FontProperties]) -> None:
    by_year_gender = data["by_year_gender"]
    category_order = data["category_order"]
    waves = data["waves"]

    row_keys = []
    row_labels = []
    for year in reversed(waves):
        for gender, short in (("Male", "Men"), ("Female", "Women")):
            row_keys.append(f"{year}_{gender}")
            row_labels.append(f"{year} · {short}")

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    title = "Party ID, LDS men vs. LDS women, over time"
    subtitle = ("3-category party ID (Democrat/Independent/Republican,\n"
                "leaners folded in) among Latter-day Saints, by gender and wave.")
    subtitle_bottom = draw_title(fig, fonts, title, subtitle)
    caption_top = draw_caption_bottom(
        fig, fonts, [], handle="@ithinkisam | data: Ryan Burge, CES 2006-2018", fontsize=16, color=INK,
    )
    ax_top = subtitle_bottom - 0.03
    legend_bottom_y = caption_top + 0.02
    legend_top_y = legend_bottom_y + LEGEND_ROW_HEIGHT  # 3 items, 1 row
    ax_bottom = legend_top_y + 0.02

    AXES_LEFT, AXES_WIDTH = 0.30, 0.64
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)

    rows = row_labels[::-1]
    keys = row_keys[::-1]
    colors = {"Democrat": DEM_COLOR, "Independent": IND_COLOR, "Republican": REP_COLOR}

    left = [0.0] * len(rows)
    for cat in category_order:
        color = colors[cat]
        vals = [by_year_gender[k]["shares_pct"][cat] or 0 for k in keys]
        ax.barh(rows, vals, left=left, height=0.72, color=color,
                edgecolor=INK, linewidth=1.2, zorder=3)
        for r, v, l in zip(rows, vals, left):
            if v >= 9:  # suppress a label that can't clear the mobile floor cleanly
                ax.text(l + v / 2, r, f"{v:.0f}%", va="center", ha="center",
                        color=TEXT_ON_FILL, fontproperties=fonts["bold"], fontsize=MIN.DATA_LABEL, zorder=4)
        left = [l + v for l, v in zip(left, vals)]

    ax.set_xlim(0, 100)
    ax.margins(y=0.015)
    for tick_label, r, k in zip(ax.get_yticklabels(), rows, keys):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(MIN.LEGEND)
        tick_label.set_color(INK)

    # A thin divider between each year's two rows, drawn at the boundary
    # between adjacent wave blocks so the 16 rows read as 8 grouped pairs.
    for i in range(2, len(rows), 2):
        ax.axhline(i - 0.5, color="#D9D5CC", linewidth=1, zorder=1)

    handles = [mpatches.Patch(facecolor=colors[c], edgecolor=INK, label=c) for c in category_order]
    legend = ax.legend(
        handles=handles, loc="upper left", bbox_to_anchor=(AXES_LEFT, legend_top_y),
        bbox_transform=fig.transFigure,
        ncol=3, frameon=False, handlelength=1.6, handleheight=1.6,
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
