#!/usr/bin/env python3
"""Render a State of Theology comparison-by-tradition graphic.

Python port of the house style established in
github.com/Samuel-Baird/ithinksam_statistics (state_of_theology_groups.R) -
same palette, typography, and composition, for use where R/ggplot2/ragg
aren't available. The R scripts in that repo are the canonical generator;
this exists so Claude Code sessions (and anyone else without an R toolchain)
can produce a chart in the same house style without installing one.

See scripts/state-of-theology-graphics/STYLE.md for the full spec this
implements - colors, fonts, layout rules - so a chart made here and a chart
made in R stay visually identical.

Usage:
    python render_chart.py --item arian --out ../../public/data-explorer/state-of-theology/nicaea-lost.png

Fonts: needs Roboto Condensed (regular/bold/italic/bold-italic) and Roboto
Slab (bold) as local .ttf files - point --fonts-dir at a folder containing
them, or place them next to this script in a `fonts/` subdirectory.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# House style tokens - see STYLE.md. Keep this block and STYLE.md in sync.
# ---------------------------------------------------------------------------

INK = "#1A1A1A"
PAPER = "#F7F5F0"
MUTED = "#6E6A63"
GRID = "#D9D5CC"

PALETTE = {
    "Evangelical": "#C9721C",       # amber
    "Black Protestant": "#5B7553",  # moss
    "Mainline": "#4E5D80",          # slate
    "Roman Catholic": "#8C4A5F",    # wine
    "All U.S. adults": "#2C7B8C",   # teal
}
GROUP_ORDER = list(PALETTE.keys())

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120  # 1080x1350 - Instagram 4:5

SOURCE_LINES = [
    "The State of Theology survey · sponsored by Ligonier Ministries, conducted by Lifeway Research",
    "Groups are religious tradition (denomination and church association).",
    "National online panel · 3,001 U.S. adults · margin of error ±1.9%",
]
HANDLE = "@ithinkisam"

# item_id -> (chart title, statement quote, direction word, survey year,
# {group: whole-number percent})
ITEMS = {
    "arian": (
        "A majority also deny the Trinity",
        "Jesus is the first and greatest being created by God.",
        "agree",
        "2022",
        {
            "Evangelical": 61,
            "Black Protestant": 78,
            "Mainline": 61,
            "Roman Catholic": 71,
            "All U.S. adults": 55,
        },
    ),
}


def load_fonts(fonts_dir: Path) -> dict[str, fm.FontProperties]:
    files = {
        "regular": "RobotoCondensed-Regular.ttf",
        "bold": "RobotoCondensed-Bold.ttf",
        "italic": "RobotoCondensed-Italic.ttf",
        "bold_italic": "RobotoCondensed-BoldItalic.ttf",
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


def render(item_id: str, out_path: Path, fonts_dir: Path) -> None:
    title, quote, direction, year, values = ITEMS[item_id]
    fonts = load_fonts(fonts_dir)

    groups = [g for g in GROUP_ORDER if g in values][::-1]  # bottom-to-top
    pcts = [values[g] for g in groups]
    colors = [PALETTE[g] for g in groups]

    fig, ax = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)

    bar_height = 0.62
    ax.barh(groups, pcts, height=bar_height, color=colors, zorder=3)
    ax.margins(y=0.06)

    xtop = ((max(pcts) // 10) + 1) * 10
    if xtop - max(pcts) < 6:
        xtop += 10
    ax.set_xlim(0, xtop * 1.14)

    for g, pct, color in zip(groups, pcts, colors):
        ax.text(
            pct + xtop * 0.015, g, f"{pct}%",
            va="center", ha="left", color=color,
            fontproperties=fonts["bold"], fontsize=21,
        )

    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)
    for label in ax.get_yticklabels():
        label.set_fontproperties(fonts["bold"])
        label.set_fontsize(19)
        label.set_color(INK)

    fig.subplots_adjust(left=0.30, right=0.94, top=0.62, bottom=0.28)

    # Title (Roboto Slab Bold), plot-level so it aligns with the caption.
    fig.text(
        0.065, 0.965, title, fontproperties=fonts["title"], fontsize=30,
        color=INK, ha="left", va="top", wrap=True,
    )

    # Subtitle: italic quote line, then the share/year line.
    fig.text(
        0.065, 0.895, f"“{quote}”", fontproperties=fonts["italic"],
        fontsize=15, color=MUTED, ha="left", va="top",
    )
    fig.text(
        0.065, 0.86,
        f"Share who strongly {direction} or somewhat {direction}, {year}",
        fontproperties=fonts["regular"], fontsize=15, color=MUTED,
        ha="left", va="top",
    )

    # Caption block: source lines (muted) + handle (amber bold), bottom-left.
    caption_y = 0.105
    for i, line in enumerate(SOURCE_LINES):
        fig.text(
            0.065, caption_y - i * 0.021, line, fontproperties=fonts["regular"],
            fontsize=10.5, color=MUTED, ha="left", va="top",
        )
    fig.text(
        0.065, caption_y - len(SOURCE_LINES) * 0.021 - 0.01, HANDLE,
        fontproperties=fonts["bold"], fontsize=10.5,
        color=PALETTE["Evangelical"], ha="left", va="top",
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--item", required=True, choices=sorted(ITEMS))
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument(
        "--fonts-dir", type=Path, default=Path(__file__).parent / "fonts",
    )
    args = ap.parse_args()
    render(args.item, args.out, args.fonts_dir)


if __name__ == "__main__":
    main()
