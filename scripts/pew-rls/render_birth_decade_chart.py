#!/usr/bin/env python3
"""Renders the birth-decade distribution graphic for the Pew RLS Data
Explorer page: a 100%-stacked bar per Christian tradition, showing what
share of today's members were born in each decade.

Reads only docs/datasets/pew-rls-2023-24/birth-decade-distribution.json
(produced by birth_decade_distribution.py from the microdata) - no number
here is hand-typed. Palette is a single-hue sequential ramp (light->dark,
oldest->newest decade) on the site's --accent hue (#1f4f7a), generated and
validated per the dataviz skill's ordinal-ramp rule (one hue, monotone
lightness, light end >=2:1 vs. the white paper surface) - see the
validate_palette.js run this ramp was built from, recorded here rather than
in STYLE.md since this is this graphic's only ordinal ramp so far.

Usage:
    python render_birth_decade_chart.py \
        --out ../../public/data-explorer/pew-religious-landscape-study/birth-decade-distribution.png
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

# Single-hue sequential ramp on --accent (#1f4f7a, hue 248.7deg in OKLCH),
# oldest decade lightest -> newest decade darkest. Validated with:
#   node validate_palette.js "#7ebaf4,#68a4dd,#538ec6,#3e79af,#296499,#105083,#003c6e" \
#     --ordinal --mode light
# -> ALL CHECKS PASS (monotone L, adjacent dL>=0.06, light-end contrast 2.00:1, single hue).
DECADE_COLORS = {
    "1940s or earlier": "#7ebaf4",
    "1950s": "#68a4dd",
    "1960s": "#538ec6",
    "1970s": "#3e79af",
    "1980s": "#296499",
    "1990s": "#105083",
    "2000s": "#003c6e",
}

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120  # 1080x1350 - matches every other Data Explorer graphic

# Bottom-to-top plot order: Christian average as the reference row at the
# bottom (consistent with how the switching chart treats its own reference
# elements last/lowest), LDS placed with its sibling traditions rather than
# curated to a particular position - data-driven, not curated, same rule
# the switching chart's GROUP_ORDER comment states for itself.
GROUP_ORDER = [
    "Christian average",
    "Other Christian",
    "Jehovah's Witness",
    "Orthodox Christian",
    "Latter-day Saint",
    "Catholic",
    "Protestant",
]

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2023-24"
    / "birth-decade-distribution.json"
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

    AXES_LEFT, AXES_WIDTH = 0.30, 0.64
    ax = fig.add_axes([AXES_LEFT, 0.40, AXES_WIDTH, 0.44])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)

    groups = GROUP_ORDER
    ax.set_xlim(0, 100)
    ax.margins(y=0.06)

    bar_height = 0.62
    left = [0.0] * len(groups)
    for decade in decade_order:
        values = [distribution[g]["shares_pct"][decade] for g in groups]
        ax.barh(groups, values, left=left, height=bar_height,
                color=DECADE_COLORS[decade], zorder=3)
        # Direct value labels only where a segment is wide enough to hold one
        # legibly (>=8% of the 100-point axis) - narrow segments rely on the
        # legend instead, same "selective direct labels" rule as any other
        # chart in this house style.
        for g, v, l in zip(groups, values, left):
            if v >= 8:
                # Dark decades get a white label (readable on navy); the two
                # lightest decades keep dark ink instead.
                label_color = PAPER if decade in ("1980s", "1990s", "2000s") else INK
                ax.text(l + v / 2, g, f"{v:.0f}", va="center", ha="center",
                        color=label_color, fontproperties=fonts["bold"], fontsize=11)
        left = [l + v for l, v in zip(left, values)]

    for label in ax.get_yticklabels():
        label.set_fontproperties(fonts["bold"])
        label.set_fontsize(15)
        label.set_color(INK)

    # --- Legend: one swatch + label per decade, two rows of 4/3, since ------
    # --- color order alone (light->dark) isn't self-explanatory without a --
    # --- key, and all 7 in one row runs past the right margin at this -----
    # --- point size. Fixed column width (not text-length-based) so columns
    # --- align cleanly across the two rows.
    legend_top, row_h, col_w = 0.355, 0.026, AXES_WIDTH / 4
    swatch_w, swatch_h = 0.022, 0.014
    for i, decade in enumerate(decade_order):
        row, col = divmod(i, 4)
        x = AXES_LEFT + col * col_w
        y = legend_top - row * row_h
        fig.patches.append(plt.Rectangle((x, y), swatch_w, swatch_h,
                                          transform=fig.transFigure,
                                          facecolor=DECADE_COLORS[decade],
                                          edgecolor="none"))
        fig.text(x + swatch_w + 0.006, y + swatch_h / 2, decade,
                  fontproperties=fonts["regular"], fontsize=9.5, color=MUTED,
                  ha="left", va="center")

    # --- Title / subtitle ---------------------------------------------------
    fig.text(
        0.065, 0.965, "Birth-decade makeup, by tradition",
        fontproperties=fonts["title"], fontsize=27, color=INK, ha="left", va="top",
    )
    fig.text(
        0.065, 0.912,
        "Share of each tradition's current members born in each decade — 2023-24\n"
        "Religious Landscape Study. No single-year age variable exists in the public\n"
        "file, so decade is the finest age measure available (no numeric median age).",
        fontproperties=fonts["regular"], fontsize=13, color=MUTED, ha="left", va="top",
    )

    # --- Caption --------------------------------------------------------------
    source_paragraphs = [
        f"Pew Research Center's Religious Landscape Study (RLS), 2023-24 wave · "
        f"N = {total_n:,} U.S. adults",
        "Groups are current religion (CURREL), not childhood religion. Respondents who "
        "declined to state their birth decade are excluded from that group's base.",
        "Pew Research Center. 2025. “2023-24 Religious Landscape Study (RLS) Dataset.” "
        "doi: 10.58094/3kwb-bf52.",
    ]
    caption_lines = [line for para in source_paragraphs for line in textwrap.wrap(para, width=98)]
    caption_y = 0.185
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
