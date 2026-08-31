#!/usr/bin/env python3
"""Renders the five "beliefs" PNGs for the Pew RLS Data Explorer page:
belief in a soul, heaven, hell, a paired heaven-vs-hell comparison, and
evolution guided by God.

Reads only docs/datasets/pew-rls-2023-24/beliefs.json (produced by
scripts/pew-rls/beliefs.py) - no number here is hand-typed. Same
canvas/fonts as every other chart in this pipeline; see STYLE.md in this
folder. Four items reuse the magnitude-bar shape from
render_practice_charts.py; the heaven-vs-hell item is a new shape - a
paired bar, two bars per group sharing one baseline - since no existing
chart in this pipeline compares two independent binary items side by side
per group (StackedBars in the old in-app kit stacked one variable into
100%; this pairs two separate variables that don't sum to anything).

Usage: see the five --*-out flags below; run with --help for the full list.
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
from chart_style import (  # noqa: E402
    LEGEND_ROW_HEIGHT, MIN, color_for_group, draw_caption_bottom, sort_groups,
    split_title_qualifier,
)

# ---------------------------------------------------------------------------
# House style tokens - see STYLE.md. Keep this block and STYLE.md in sync.
# ---------------------------------------------------------------------------

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"

ACCENT = "#1f4f7a"
HONEY = "#8a5a06"

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120

# All twelve religiously-affiliated traditions individually, a weighted
# average, and the unaffiliated as their own row - see beliefs.py's
# docstring for why this section's open population question was resolved
# this way rather than defaulting to Christian-only.
GROUP_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Jehovah's Witness",
    "Muslim", "Hindu", "Orthodox Christian", "Buddhist",
    "Jewish", "Other world religions", "Other faiths",
    "All religious average", "Religiously unaffiliated",
]

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2023-24" / "beliefs.json"
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


def _draw_title(fig, fonts, title: str, subtitle: str) -> float:
    """Returns the y-fraction where the subtitle block actually ends, so
    the caller can size its axes to the real available band instead of a
    fixed guess - see STYLE.md's "Vertical layout" section."""
    title_fontsize = 32
    subtitle_fontsize = 16
    main_title, qualifier = split_title_qualifier(title)
    title_lines = textwrap.wrap(main_title, width=42)
    line_spacing = title_fontsize / 650
    title_top = 0.965
    for i, line in enumerate(title_lines):
        fig.text(
            0.065, title_top - i * line_spacing, line,
            fontproperties=fonts["title"], fontsize=title_fontsize, color=INK, ha="left", va="top",
        )
    n_title_lines = len(title_lines)
    if qualifier:
        qualifier_fontsize = title_fontsize * 0.55
        fig.text(
            0.065, title_top - n_title_lines * line_spacing, qualifier,
            fontproperties=fonts["title"], fontsize=qualifier_fontsize, color=INK, ha="left", va="top",
        )
        n_title_lines += qualifier_fontsize / title_fontsize
    subtitle_y = title_top - n_title_lines * line_spacing - 0.015
    fig.text(
        0.065, subtitle_y, subtitle,
        fontproperties=fonts["regular"], fontsize=subtitle_fontsize, color=INK, ha="left", va="top",
    )
    subtitle_lines = subtitle.count("\n") + 1
    subtitle_line_height = subtitle_fontsize * 1.2 / 72 / FIG_H_IN
    return subtitle_y - subtitle_lines * subtitle_line_height


def _draw_caption(fig, fonts, total_n: int, note: str) -> float:
    """Bottom-anchored caption - see STYLE.md's "Footnotes: bottom-anchored"
    section. Returns caption_top for the vertical-centering contract."""
    return draw_caption_bottom(
        fig, fonts, [], handle="@ithinkisam | data: Pew 2023-24 RLS",
        fontsize=16, color=INK,
    )


def render_magnitude_bar(
    results: dict, title: str, subtitle: str, note: str, total_n: int,
    out_path: Path, fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    # Vertical centering: size the axes to the real gap between the
    # subtitle and the caption, not a fixed guess - see STYLE.md. Caption is
    # drawn first (bottom-anchored) so its real top edge is known.
    subtitle_bottom = _draw_title(fig, fonts, title, subtitle)
    caption_top = _draw_caption(fig, fonts, total_n, note)
    ax_top = subtitle_bottom - 0.03
    ax_bottom = caption_top + 0.03

    AXES_LEFT, AXES_WIDTH = 0.36, 0.58
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    sorted_order = sort_groups(GROUP_ORDER, lambda g: results[g]["pct"])
    rows = sorted_order[::-1]
    values = [results[g]["pct"] for g in rows]
    colors = [color_for_group(g) for g in rows]

    ax.barh(rows, values, height=0.68, color=colors, zorder=3)
    ax.set_xlim(0, max(values) * 1.2)
    ax.margins(y=0.045)

    for tick_label, g in zip(ax.get_yticklabels(), rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(MIN.LEGEND)
        tick_label.set_color(INK)

    for g, v, c in zip(rows, values, colors):
        ax.text(v + max(values) * 0.02, g, f"{v:.0f}%", va="center", ha="left",
                 color=c, fontproperties=fonts["bold"], fontsize=MIN.DATA_LABEL, zorder=4)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def render_paired_bar(
    heaven: dict, hell: dict, title: str, subtitle: str, note: str, total_n: int,
    out_path: Path, fonts: dict[str, fm.FontProperties],
) -> None:
    """Two bars per group sharing one zero baseline - heaven above, hell
    below, within one row band - rather than the 100%-stacked treatment
    used elsewhere, since these are two independent yes/no items that
    don't sum to anything."""
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    # Vertical centering, same approach as render_magnitude_bar above, with
    # room reserved for the legend row above the axes (exact, via
    # LEGEND_ROW_HEIGHT - not a guessed constant, see chart_style.py).
    # Caption is drawn first (bottom-anchored) so its real top edge is known.
    subtitle_bottom = _draw_title(fig, fonts, title, subtitle)
    caption_top = _draw_caption(fig, fonts, total_n, note)
    legend_top_y = subtitle_bottom - 0.02
    legend_bottom_y = legend_top_y - LEGEND_ROW_HEIGHT  # 2 items, 1 row
    ax_top = legend_bottom_y - 0.02
    ax_bottom = caption_top + 0.03

    AXES_LEFT, AXES_WIDTH = 0.36, 0.58
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    sorted_order = sort_groups(GROUP_ORDER, lambda g: heaven[g]["pct"])
    rows = sorted_order[::-1]
    y_positions = list(range(len(rows)))
    ax.set_ylim(-0.7, len(rows) - 0.3)

    max_val = max(max(heaven[g]["pct"] for g in rows), max(hell[g]["pct"] for g in rows))
    ax.set_xlim(0, max_val * 1.22)

    bar_h = 0.34
    for y, g in zip(y_positions, rows):
        hv = heaven[g]["pct"]
        hl = hell[g]["pct"]
        ax.barh(y + bar_h / 2 + 0.02, hv, height=bar_h, color=ACCENT, zorder=3)
        ax.barh(y - bar_h / 2 - 0.02, hl, height=bar_h, color=HONEY, zorder=3)
        ax.text(hv + max_val * 0.02, y + bar_h / 2 + 0.02, f"{hv:.0f}%", va="center", ha="left",
                 color=ACCENT, fontproperties=fonts["bold"], fontsize=MIN.DATA_LABEL, zorder=4)
        ax.text(hl + max_val * 0.02, y - bar_h / 2 - 0.02, f"{hl:.0f}%", va="center", ha="left",
                 color=HONEY, fontproperties=fonts["bold"], fontsize=MIN.DATA_LABEL, zorder=4)
        ax.text(-max_val * 0.02, y, g, va="center", ha="right",
                 color=INK, fontproperties=fonts["bold"], fontsize=MIN.LEGEND, zorder=4)

    handles = [mpatches.Patch(facecolor=ACCENT, edgecolor=INK, label="Heaven"),
               mpatches.Patch(facecolor=HONEY, edgecolor=INK, label="Hell")]
    legend = ax.legend(
        handles=handles, loc="upper left", bbox_to_anchor=(0.36, legend_top_y),
        bbox_transform=fig.transFigure,
        ncol=2, frameon=False, handlelength=1.6, handleheight=1.6,
        fontsize=MIN.LEGEND, prop=fonts["bold"], columnspacing=1.5,
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
    ap.add_argument("--soul-out", type=Path, required=True)
    ap.add_argument("--heaven-out", type=Path, required=True)
    ap.add_argument("--hell-out", type=Path, required=True)
    ap.add_argument("--heaven-hell-out", type=Path, required=True)
    ap.add_argument("--evolution-out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    total_n = data["total_unweighted_n"]
    note = "Population: all religiously affiliated traditions individually, plus the " \
           "religiously unaffiliated as their own row."

    render_magnitude_bar(
        data["soul_belief"],
        title="Believe people have a soul or spirit",
        subtitle="Share who believe people have a soul or spirit in\naddition to their physical body.",
        note=note, total_n=total_n, out_path=args.soul_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["heaven_belief"],
        title="Believe in heaven",
        subtitle="Share who believe there is a heaven where people who\nled good lives are eternally rewarded.",
        note=note, total_n=total_n, out_path=args.heaven_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["hell_belief"],
        title="Believe in hell",
        subtitle="Share who believe there is a hell where people who led\nbad lives are eternally punished.",
        note=note, total_n=total_n, out_path=args.hell_out, fonts=fonts,
    )
    render_paired_bar(
        data["heaven_belief"], data["hell_belief"],
        title="Belief in heaven vs. hell",
        subtitle="The same two questions, compared side by side per\ntradition.",
        note=note, total_n=total_n, out_path=args.heaven_hell_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["evolution_guided_by_god"],
        title="Evolution guided by God",
        subtitle="Share who say humans evolved over time due to\nprocesses guided or allowed by God.",
        note=note, total_n=total_n, out_path=args.evolution_out, fonts=fonts,
    )


if __name__ == "__main__":
    main()
