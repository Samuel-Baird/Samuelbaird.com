#!/usr/bin/env python3
"""Renders the three "spiritual experience" PNGs for the Pew RLS Data
Explorer page: thinking about life's meaning/purpose weekly+, feeling
spiritual peace weekly+, and feeling the presence of something beyond this
world weekly+ - all Christian only.

Reads only docs/datasets/pew-rls-2023-24/spiritual-experience.json
(produced by scripts/pew-rls/spiritual_experience.py) - no number here is
hand-typed. Same canvas/fonts/highlight-vs-gray magnitude-bar shape as
render_childhood_formation_charts.py; see STYLE.md in this folder.

Usage:
    python render_spiritual_experience_charts.py \
        --meaning-out ../../public/data-explorer/pew-religious-landscape-study/spiritual-meaning.png \
        --peace-out ../../public/data-explorer/pew-religious-landscape-study/spiritual-peace.png \
        --presence-out ../../public/data-explorer/pew-religious-landscape-study/spiritual-presence.png
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

ACCENT = "#1f4f7a"
CONTEXT_GRAY = "#8f8b82"
HIGHLIGHT_GROUP = "Latter-day Saint"

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120

GROUP_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
    "Jehovah's Witness", "Other Christian", "Christian average",
]

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2023-24" / "spiritual-experience.json"
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
    results: dict, title: str, subtitle: str, total_n: int,
    out_path: Path, fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    # Vertical centering: size the axes to the real gap between the
    # subtitle and the caption, not a fixed guess - see STYLE.md.
    caption_top = 0.185
    subtitle_bottom = draw_title(fig, fonts, title, subtitle)
    ax_top = subtitle_bottom - 0.035
    ax_bottom = caption_top + 0.035

    AXES_LEFT, AXES_WIDTH = 0.34, 0.60
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)

    rows = GROUP_ORDER[::-1]
    values = [results[g]["pct"] for g in rows]
    colors = [ACCENT if g == HIGHLIGHT_GROUP else CONTEXT_GRAY for g in rows]

    ax.barh(rows, values, height=0.6, color=colors, zorder=3)
    ax.set_xlim(0, max(values) * 1.2)
    ax.margins(y=0.11)

    for tick_label, g in zip(ax.get_yticklabels(), rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(14)
        tick_label.set_color(ACCENT if g == HIGHLIGHT_GROUP else INK)

    for g, v, c in zip(rows, values, colors):
        ax.text(v + max(values) * 0.02, g, f"{v:.0f}%", va="center", ha="left",
                 color=c, fontproperties=fonts["bold"], fontsize=15, zorder=4)

    source_paragraphs = [
        "Population: Christian only.",
        f"Pew Research Center's Religious Landscape Study (RLS), 2023-24 wave · "
        f"N = {total_n:,} U.S. adults",
        "Pew Research Center. 2025. “2023-24 Religious Landscape Study (RLS) Dataset.” "
        "doi: 10.58094/3kwb-bf52.",
    ]
    caption_lines = [line for para in source_paragraphs for line in textwrap.wrap(para, width=98)]
    for i, line in enumerate(caption_lines):
        fig.text(
            0.065, caption_top - i * 0.0165, line, fontproperties=fonts["regular"],
            fontsize=10, color=MUTED, ha="left", va="top",
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--meaning-out", type=Path, required=True)
    ap.add_argument("--peace-out", type=Path, required=True)
    ap.add_argument("--presence-out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    total_n = data["total_unweighted_n"]

    render_magnitude_bar(
        data["meaning_purpose_weekly_plus"],
        title="Think about life's meaning and purpose, weekly+",
        subtitle="Share who think about the meaning and purpose of life\nat least once a week.",
        total_n=total_n, out_path=args.meaning_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["spiritual_peace_weekly_plus"],
        title="Feel spiritual peace and well-being, weekly+",
        subtitle="Share who feel a deep sense of spiritual peace and\nwell-being at least once a week.",
        total_n=total_n, out_path=args.peace_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["presence_beyond_weekly_plus"],
        title="Feel a presence beyond this world, weekly+",
        subtitle="Share who feel the presence of something from beyond\nthis world at least once a week.",
        total_n=total_n, out_path=args.presence_out, fonts=fonts,
    )


if __name__ == "__main__":
    main()
