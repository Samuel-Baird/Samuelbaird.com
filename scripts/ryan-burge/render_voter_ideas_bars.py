#!/usr/bin/env python3
"""Renders the eight VOTER Panel "magnitude bar" idea graphics
(docs/datasets/ryan-burge/VOTER_PANEL_IDEAS.md, ideas 4/6/10/13/15/19).

Reads only docs/datasets/ryan-burge/voter-ideas-bars.json (produced by
scripts/ryan-burge/voter_ideas_bars.py) - no number here is hand-typed.
Same canvas/fonts/vertical-centering rule as the rest of this pipeline
(see scripts/pew-rls/STYLE.md).

Usage: see the eight --*-out flags below; run with --help for the full list.
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

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"
ACCENT = "#1f4f7a"
CONTEXT_GRAY = "#8f8b82"
HIGHLIGHT_GROUP = "Mormon"

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge" / "voter-ideas-bars.json"
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
    results: dict, group_order: list[str], title: str, subtitle: str, note: str,
    out_path: Path, fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = draw_title(fig, fonts, title, subtitle)
    source_paragraphs = [
        note,
        "Democracy Fund Voter Study Group / YouGov, VOTER Survey Panel (2016 wave), via Ryan "
        "Burge (github.com/ryanburge).",
    ]
    caption_top = draw_caption_bottom(fig, fonts, source_paragraphs)
    ax_top = subtitle_bottom - 0.03
    ax_bottom = caption_top + 0.03

    AXES_LEFT, AXES_WIDTH = 0.36, 0.58
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    rows = group_order[::-1]
    values = [results[g]["pct"] for g in rows]
    colors = [ACCENT if g == HIGHLIGHT_GROUP else CONTEXT_GRAY for g in rows]

    ax.barh(rows, values, height=0.68, color=colors, zorder=3)
    ax.set_xlim(0, max(values) * 1.2)
    ax.margins(y=0.05)

    for tick_label, g in zip(ax.get_yticklabels(), rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(MIN.AXIS_LABEL)
        tick_label.set_color(ACCENT if g == HIGHLIGHT_GROUP else INK)

    for g, v, c in zip(rows, values, colors):
        ax.text(v + max(values) * 0.02, g, f"{v:.0f}%", va="center", ha="left",
                 color=c, fontproperties=fonts["bold"], fontsize=14, zorder=4)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wished-voted-out", type=Path, required=True)
    ap.add_argument("--vote-regrets-out", type=Path, required=True)
    ap.add_argument("--self-reliance-out", type=Path, required=True)
    ap.add_argument("--race-slave-out", type=Path, required=True)
    ap.add_argument("--reverse-discrimination-out", type=Path, required=True)
    ap.add_argument("--trust-people-out", type=Path, required=True)
    ap.add_argument("--rigged-elites-out", type=Path, required=True)
    ap.add_argument("--military-out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    group_order = data["group_order"]
    note = "Population: religpew_2016, unweighted."

    render_magnitude_bar(
        data["wished_voted"], group_order,
        title="Wished they had voted in 2016",
        subtitle="Of those who didn't vote, share who wish they had.",
        note=note, out_path=args.wished_voted_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["vote_regrets"], group_order,
        title="Regret their 2016 presidential vote",
        subtitle="Share who regret who they voted for president in 2016.",
        note=note, out_path=args.vote_regrets_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["self_reliance"], group_order,
        title="Value self-reliance over obedience in children",
        subtitle="Forced choice: which quality matters more for a child\nto have - obedience, or self-reliance.",
        note=note, out_path=args.self_reliance_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["race_slave_agree"], group_order,
        title="Slavery's legacy still disadvantages Black Americans",
        subtitle="Share who agree generations of slavery and\ndiscrimination have made it hard for Black people to succeed.",
        note=note, out_path=args.race_slave_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["reverse_discrimination_agree"], group_order,
        title="Discrimination against whites is a serious problem",
        subtitle="Share who agree discrimination against white people\nis as big a problem as discrimination against minorities.",
        note=note, out_path=args.reverse_discrimination_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["trust_people"], group_order,
        title="Most people can be trusted",
        subtitle="Generalized social trust - can't be too careful vs.\nmost people can be trusted.",
        note=note, out_path=args.trust_people_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["rigged_elites_agree"], group_order,
        title="Elites don't understand people like me",
        subtitle="Share who agree elites in this country don't\nunderstand the problems they're facing.",
        note=note, out_path=args.rigged_elites_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["military_household"], group_order,
        title="Military household connection",
        subtitle="Share who or whose family currently serve or\npreviously served in the military.",
        note=note, out_path=args.military_out, fonts=fonts,
    )


if __name__ == "__main__":
    main()
