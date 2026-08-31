#!/usr/bin/env python3
"""Renders the two "family and household" PNGs for the Pew RLS Data
Explorer page: share with children under 18 at home, and share of parents
who pray or read scripture with their kids.

Reads only docs/datasets/pew-rls-2023-24/family-household.json (produced by
scripts/pew-rls/family_household.py) - no number here is hand-typed. Same
canvas/fonts/per-group identity color palette as
render_childhood_formation_charts.py; see STYLE.md in this folder. The two
charts intentionally use different group sets (six Christian traditions +
Christian average for the first; those six + "Other religions" + a
religiously-affiliated average for the second), per the backlog item's own
note that the second item's population is explicitly wider - the render
script takes the group order as an argument rather than hardcoding one
list, so each chart draws exactly the rows its own JSON has.

Usage:
    python render_family_household_charts.py \
        --children-out ../../public/data-explorer/pew-religious-landscape-study/family-children-at-home.png \
        --kidact-out ../../public/data-explorer/pew-religious-landscape-study/family-kidact-prayer.png
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
from chart_style import MIN, color_for_group, draw_caption_bottom, sort_groups  # noqa: E402

# ---------------------------------------------------------------------------
# House style tokens - see STYLE.md. Keep this block and STYLE.md in sync.
# ---------------------------------------------------------------------------

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120  # 1080x1350 - matches every other Data Explorer graphic

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2023-24" / "family-household.json"
).resolve()
DEFAULT_FONTS_DIR = (
    Path(__file__).parent / ".." / "state-of-theology-graphics" / "fonts"
).resolve()

# Bottom-to-top plot order for each chart (top row is drawn last in a barh
# call using this reversed) - LDS first so it plots at the top, same
# convention as every other chart in this pipeline.
CHILDREN_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
    "Jehovah's Witness",
]
KIDACT_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
    "Jehovah's Witness", "Other religions",
    "Religiously affiliated average",
]


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


def draw_title(fig, fonts, title: str, subtitle: str, width: int = 26,
                subtitle_fontsize: float = 14) -> float:
    """Dynamic wrap + spacing; returns the y-fraction where the subtitle
    block actually ends, so the caller can size its axes to the real
    available band instead of a fixed guess - see STYLE.md's "Vertical
    layout" section."""
    title_fontsize = 27
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


def render_magnitude_bar(
    results: dict, group_order: list[str], title: str, subtitle: str, note: str,
    total_n: int, out_path: Path, fonts: dict[str, fm.FontProperties],
    axes_left: float = 0.34,
) -> None:
    """axes_left: left edge of the plot axes (figure-fraction) - also the
    right boundary the row (y-axis tick) labels are drawn leftward from.
    Default matches every chart in this pipeline; widen it on a chart-by-
    chart basis when a row label is long enough to clip past the canvas's
    left edge at MIN.LEGEND size - see STYLE.md's "Vertical layout" section
    for the general pattern this follows. KIDACT_ORDER's "Religiously
    affiliated average" row needed this (2026-08-31): at the default 0.34
    that label's text ran past x=0 and was clipped by the figure boundary."""
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    # Vertical centering: size the axes to the real gap between the
    # subtitle and the caption, not a fixed guess - see STYLE.md. Caption is
    # drawn first (bottom-anchored) so its real top edge is known.
    subtitle_bottom = draw_title(fig, fonts, title, subtitle)
    caption_top = draw_caption_bottom(fig, fonts, [], handle="@ithinkisam | data: Pew 2023-24 RLS")
    ax_top = subtitle_bottom - 0.035
    ax_bottom = caption_top + 0.035

    AXES_LEFT, AXES_WIDTH = axes_left, 0.94 - axes_left
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)

    sorted_order = sort_groups(group_order, lambda g: results[g]["pct"])
    rows = sorted_order[::-1]
    values = [results[g]["pct"] for g in rows]
    colors = [color_for_group(g) for g in rows]

    ax.barh(rows, values, height=0.6, color=colors, zorder=3)
    ax.set_xlim(0, max(values) * 1.2)
    ax.margins(y=0.11)

    for tick_label, g in zip(ax.get_yticklabels(), rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(MIN.LEGEND)
        tick_label.set_color(INK)

    for g, v, c in zip(rows, values, colors):
        ax.text(v + max(values) * 0.02, g, f"{v:.0f}%", va="center", ha="left",
                 color=c, fontproperties=fonts["bold"], fontsize=15, zorder=4)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--children-out", type=Path, required=True)
    ap.add_argument("--kidact-out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)

    render_magnitude_bar(
        data["children_with_kids_at_home"], CHILDREN_ORDER,
        title="Share with children under 18 at home",
        subtitle="Of each current tradition's members, share who are a\nparent or guardian of a child under 18 living with them.",
        note="Population: current tradition (CURREL); excludes don't know/refused.",
        total_n=data["total_unweighted_n"],
        out_path=args.children_out,
        fonts=fonts,
    )
    render_magnitude_bar(
        data["pray_or_read_scripture_with_kids"], KIDACT_ORDER,
        title="Of parents, who pray or read scripture with their kids",
        subtitle="Share of each tradition's parents who pray or read\nscripture with their children.",
        note="Population: parents of children under 18 (CHILDREN=Yes) in each current "
             "tradition (CURREL); excludes don't know/refused.",
        total_n=data["total_unweighted_n"],
        out_path=args.kidact_out,
        fonts=fonts,
        # KIDACT_ORDER's "Religiously affiliated average" row is long enough
        # at MIN.LEGEND size to clip past the canvas's left edge at the
        # default axes_left - see render_magnitude_bar's docstring.
        axes_left=0.46,
    )


if __name__ == "__main__":
    main()
