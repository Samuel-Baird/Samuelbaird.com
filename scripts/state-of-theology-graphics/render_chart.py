#!/usr/bin/env python3
"""Render State of Theology comparison-by-tradition graphics.

Python port of the house style established by the social-media R scripts
(scripts/social-graphics/state_of_theology_groups.R) -
same palette and typography, adapted per STYLE.md for the website (white
background, neutral titles) - for use where R/ggplot2/ragg aren't available.
Those R scripts are the canonical generator for social posts;
this exists so a Claude Code session (or anyone without an R toolchain) can
produce a website-style chart without installing one.

Reads directly from the quiz's own data.json (produced by
scripts/evangelical-quiz/build_data.py) rather than hand-entered numbers, so
a chart here can never drift from what the quiz itself shows.

See STYLE.md for the full spec this implements - colors, fonts, layout
rules - so a chart made here and a chart made in R stay visually identical
on every point except the two documented, deliberate departures.

Usage:
    # One item:
    python render_chart.py --item arian --out ../../public/data-explorer/state-of-theology/nicaea-lost.png

    # Every item in data.json, written as <item_id>.png:
    python render_chart.py --all --out-dir ../../public/data-explorer/state-of-theology

Fonts: needs Roboto Condensed (regular/bold/italic/bold-italic) and Roboto
Slab (bold) as local .ttf files - point --fonts-dir at a folder containing
them, or place them next to this script in a `fonts/` subdirectory.
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import MIN, draw_caption_bottom  # noqa: E402

# ---------------------------------------------------------------------------
# House style tokens - see STYLE.md. Keep this block and STYLE.md in sync.
# ---------------------------------------------------------------------------

INK = "#1A1A1A"
# White, not the Instagram scripts' cream (#F7F5F0) - the website's graphics
# spec calls for a white background specifically. Everything else in the
# palette (ink/muted/grid/group colors) is shared with the social style.
PAPER = "#FFFFFF"
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

SPONSOR_LINE = (
    "The State of Theology survey · sponsored by Ligonier Ministries, "
    "conducted by Lifeway Research"
)
GROUP_MEANING_LINE = "Groups are religious tradition (denomination and church association)."
# Sample size / margin of error is wave-specific - never state a number for
# a wave it wasn't measured in. See scripts/evangelical-quiz/survey-meta.ts,
# the source of truth for these figures.
WAVE_METHODOLOGY = {
    2025: "National online panel · 3,001 U.S. adults · margin of error ±1.9%",
    2022: "National online panel · sample size and margin of error not yet on file for this wave",
}
HANDLE = "@ithinkisam"

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "src" / "lib" / "evangelical-quiz" / "data.json"
).resolve()


def load_data(data_json: Path) -> dict:
    with open(data_json, encoding="utf-8") as f:
        return json.load(f)


def item_agree_pcts(item: dict) -> dict[str, int]:
    """Whole-number "agree" percent (strongly + somewhat) per group that has
    data for this item, from the item's raw_pct (aligned to item['scale']).
    """
    scale = item["scale"]
    i_swa = scale.index("somewhat_agree") if "somewhat_agree" in scale else None
    i_sa = scale.index("strongly_agree")
    out = {}
    for group, pcts in item["raw_pct"].items():
        agree = pcts[i_sa] + (pcts[i_swa] if i_swa is not None else 0)
        out[group] = round(agree)
    return out


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


def render(item: dict, out_path: Path, fonts: dict[str, fm.FontProperties]) -> None:
    statement = item["statement"]
    year = item["year"]
    values = item_agree_pcts(item)

    groups = [g for g in GROUP_ORDER if g in values][::-1]  # bottom-to-top
    pcts = [values[g] for g in groups]
    colors = [PALETTE[g] for g in groups]

    fig, ax = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)

    # Caption drawn first (bottom-anchored) - see STYLE.md's "Footnotes:
    # bottom-anchored" section - so subplots_adjust's `bottom` below can use
    # its real top edge instead of a fixed guess.
    source_lines = [
        SPONSOR_LINE,
        GROUP_MEANING_LINE,
        WAVE_METHODOLOGY.get(year, "National online panel · methodology not yet on file for this wave"),
    ]
    caption_top = draw_caption_bottom(
        fig, fonts, source_lines, left=0.065, fontsize=10.5, line_step=0.021,
        handle=HANDLE, handle_color=PALETTE["Evangelical"],
    )

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

    # Title IS the survey statement, verbatim, in quotes - no editorial
    # headline above it. Wrapped by hand (matplotlib's fig-level wrap= is
    # unreliable) at a width tuned for this font/size/canvas combination.
    # Long statements get a smaller title size so they still fit above the
    # chart without colliding with it.
    title_fontsize = 34
    title_lines = textwrap.wrap(f"“{statement}”", width=26)
    if len(title_lines) > 4:
        title_fontsize = 27
        title_lines = textwrap.wrap(f"“{statement}”", width=33)

    line_spacing = title_fontsize / 650
    title_top = 0.965

    subtitle_y = title_top - len(title_lines) * line_spacing - 0.01

    fig.subplots_adjust(left=0.30, right=0.94, top=subtitle_y - 0.055, bottom=caption_top + 0.045)

    for i, line in enumerate(title_lines):
        fig.text(
            0.065, title_top - i * line_spacing, line,
            fontproperties=fonts["title"], fontsize=title_fontsize,
            color=INK, ha="left", va="top",
        )

    fig.text(
        0.065, subtitle_y,
        f"Share who strongly agree or somewhat agree, {year}",
        fontproperties=fonts["regular"], fontsize=15, color=MUTED,
        ha="left", va="top",
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--item", help="item_id from data.json, e.g. arian")
    ap.add_argument("--all", action="store_true", help="render every item in data.json")
    ap.add_argument("--out", type=Path, help="output PNG path (with --item)")
    ap.add_argument("--out-dir", type=Path, help="output directory (with --all); files named <item_id>.png")
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON, help="path to data.json")
    ap.add_argument("--fonts-dir", type=Path, default=Path(__file__).parent / "fonts")
    args = ap.parse_args()

    if bool(args.item) == bool(args.all):
        raise SystemExit("pass exactly one of --item or --all")
    if args.item and not args.out:
        raise SystemExit("--item requires --out")
    if args.all and not args.out_dir:
        raise SystemExit("--all requires --out-dir")

    data = load_data(args.data)
    items_by_id = {item["id"]: item for item in data["items"]}
    fonts = load_fonts(args.fonts_dir)

    if args.item:
        if args.item not in items_by_id:
            raise SystemExit(f"item {args.item!r} not found in {args.data}")
        render(items_by_id[args.item], args.out, fonts)
    else:
        for item_id, item in items_by_id.items():
            render(item, args.out_dir / f"{item_id}.png", fonts)


if __name__ == "__main__":
    main()
