#!/usr/bin/env python3
"""Renders two VOTER Survey Panel "volunteering" summary PNGs (baseline
wave, ~2011): average non-religious causes volunteered for per person,
and share who volunteer for a religious organization specifically.

Reads only docs/datasets/ryan-burge/voter-volunteering-summary.json
(produced by scripts/ryan-burge/voter_volunteering_summary.py) - no number
here is hand-typed. Same canvas/fonts/vertical-centering rule as the rest
of this pipeline (see scripts/pew-rls/STYLE.md), same highlight-vs-gray
(Mormon in --accent, everyone else gray) convention as this family's other
magnitude-bar charts (render_voter_ideas_bars.py, render_voter_stranger_chart.py)
- narrower than that convention's sitewide replacement in the Pew RLS
pipeline, but kept for consistency with this dataset's sibling charts
rather than migrating this one file ahead of the rest of ryan-burge/.

Unlike every other magnitude bar in this pipeline, the "average causes"
chart's value is a per-person COUNT (0-16), not a percentage - so its bars
use a 2-decimal value label with no "%" suffix, and its own x-axis scale
(the group max is under 2, not under 100).

Usage:
    python render_voter_volunteering_summary_chart.py \
        --nonreligious-out ../../public/data-explorer/voter-survey-panel/volunteer-nonreligious-avg.png \
        --religious-org-out ../../public/data-explorer/voter-survey-panel/volunteer-religious-org.png
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

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge" / "voter-volunteering-summary.json"
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


def render_magnitude_bar(
    results: dict, value_key: str, group_order: list[str], title: str, subtitle: str,
    out_path: Path, fonts: dict[str, fm.FontProperties],
    value_fmt: str = "{:.0f}%",
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = draw_title(fig, fonts, title, subtitle)
    caption_top = draw_caption_bottom(fig, fonts, [], handle="@ithinkisam | data: Ryan Burge, Voter Study Group")
    ax_top = subtitle_bottom - 0.03
    ax_bottom = caption_top + 0.03

    AXES_LEFT, AXES_WIDTH = 0.36, 0.58
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    sorted_order = sort_groups(group_order, lambda g: results[g][value_key])
    rows = sorted_order[::-1]
    values = [results[g][value_key] for g in rows]
    colors = [color_for_group(g) for g in rows]

    ax.barh(rows, values, height=0.68, color=colors, zorder=3)
    ax.set_xlim(0, max(values) * 1.22)
    ax.margins(y=0.06)

    for tick_label, g in zip(ax.get_yticklabels(), rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(MIN.LEGEND)
        tick_label.set_color(INK)

    for g, v, c in zip(rows, values, colors):
        ax.text(v + max(values) * 0.02, g, value_fmt.format(v), va="center", ha="left",
                 color=c, fontproperties=fonts["bold"], fontsize=15, zorder=4)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nonreligious-out", type=Path, required=True)
    ap.add_argument("--religious-org-out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    group_order = data["group_order"]

    render_magnitude_bar(
        data["nonreligious_causes_avg"], "avg_causes", group_order,
        title="Average non-religious causes volunteered for",
        subtitle="Of 16 non-religious cause types, average number each\nperson volunteered for in the past 12 months.",
        out_path=args.nonreligious_out, fonts=fonts, value_fmt="{:.2f}",
    )
    render_magnitude_bar(
        data["religious_org_pct"], "pct", group_order,
        title="Volunteer for a religious organization",
        subtitle="Share who volunteered for a religious organization in\nthe past 12 months.",
        out_path=args.religious_org_out, fonts=fonts, value_fmt="{:.0f}%",
    )


if __name__ == "__main__":
    main()
