#!/usr/bin/env python3
"""Renders the eight "CCES 2016 by religion" PNGs for the Ryan Burge Data
Explorer page: four immigration items, two abortion items, one same-sex
marriage item (all select/support/favor magnitude bars), and religious
attendance (a full-distribution stack).

Reads only docs/datasets/ryan-burge/cces2016-by-religion.json (produced by
scripts/ryan-burge/cces2016_by_religion.py) - no number here is hand-typed.
Same canvas/fonts/highlight-vs-gray convention as the Pew RLS pipeline (see
scripts/pew-rls/STYLE.md) - this dataset doesn't have its own STYLE.md
since it borrows that one wholesale, per this backlog's own header.

Vertical layout follows scripts/pew-rls/STYLE.md's "Vertical layout"
rule from the start (not retrofitted): axes are sized to the real gap
between the subtitle and the caption, not a fixed guess.

Usage: see the eight --*-out flags below; run with --help for the full list.
"""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"

ACCENT = "#1f4f7a"
CONTEXT_GRAY = "#8f8b82"
HIGHLIGHT_GROUP = "Mormon"

# --chart-ordinal-1..7, light-mode values (src/app/globals.css) - the same
# official ordinal ramp scripts/pew-rls/render_practice_charts.py reuses
# for its own frequency scales, evenly resampled to however many segments
# a given scale has.
ORDINAL_RAMP_7 = ["#e8eff6", "#c3d7e8", "#96b9d6", "#5e8db8", "#1f4f7a", "#163a5c", "#0d2740"]
LABEL_INK_FOR_STEP_7 = [INK, INK, INK, INK, "#FFFFFF", "#FFFFFF", "#FFFFFF"]

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120

GROUP_ORDER = [
    "Mormon", "Protestant", "Catholic", "Orthodox", "Jewish", "Muslim",
    "Buddhist", "Hindu", "Atheist", "Agnostic", "Nothing in particular",
    "Something else",
]

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge" / "cces2016-by-religion.json"
).resolve()
DEFAULT_FONTS_DIR = (
    Path(__file__).parent / ".." / "state-of-theology-graphics" / "fonts"
).resolve()

CAPTION_TOP = 0.145


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
    """Returns the y-fraction where the subtitle block actually ends - see
    scripts/pew-rls/STYLE.md's "Vertical layout" section."""
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


def draw_caption(fig, fonts, total_n: int, note: str) -> None:
    source_paragraphs = [
        note,
        f"Ryan Burge (github.com/ryanburge), CCES 2016 common content extract · N = {total_n:,}",
        "Unweighted - this extract carries no survey weight column; good for shape/direction, "
        "not exact figures.",
    ]
    caption_lines = [line for para in source_paragraphs for line in textwrap.wrap(para, width=98)]
    for i, line in enumerate(caption_lines):
        fig.text(
            0.065, CAPTION_TOP - i * 0.0165, line, fontproperties=fonts["regular"],
            fontsize=10, color=MUTED, ha="left", va="top",
        )


def render_magnitude_bar(
    results: dict, title: str, subtitle: str, note: str, total_n: int,
    out_path: Path, fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = draw_title(fig, fonts, title, subtitle)
    ax_top = subtitle_bottom - 0.03
    ax_bottom = CAPTION_TOP + 0.03

    AXES_LEFT, AXES_WIDTH = 0.36, 0.58
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    rows = GROUP_ORDER[::-1]
    values = [results[g]["pct"] for g in rows]
    colors = [ACCENT if g == HIGHLIGHT_GROUP else CONTEXT_GRAY for g in rows]

    ax.barh(rows, values, height=0.68, color=colors, zorder=3)
    ax.set_xlim(0, max(values) * 1.2)
    ax.margins(y=0.05)

    for tick_label, g in zip(ax.get_yticklabels(), rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(12.5)
        tick_label.set_color(ACCENT if g == HIGHLIGHT_GROUP else INK)

    for g, v, c in zip(rows, values, colors):
        ax.text(v + max(values) * 0.02, g, f"{v:.0f}%", va="center", ha="left",
                 color=c, fontproperties=fonts["bold"], fontsize=13, zorder=4)

    draw_caption(fig, fonts, total_n, note)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def render_distribution_stack(
    results: dict, seg_order: list[str], title: str, subtitle: str, note: str,
    total_n: int, out_path: Path, fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = draw_title(fig, fonts, title, subtitle)
    ax_top = subtitle_bottom - 0.03
    ax_bottom = CAPTION_TOP + 0.03 + 0.05  # extra room for the legend below the axes

    n_segs = len(seg_order)
    step_idxs = [round(i * (len(ORDINAL_RAMP_7) - 1) / (n_segs - 1)) for i in range(n_segs)]
    colors = [ORDINAL_RAMP_7[i] for i in step_idxs]
    text_colors = [LABEL_INK_FOR_STEP_7[i] for i in step_idxs]

    AXES_LEFT, AXES_WIDTH = 0.36, 0.58
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    rows = GROUP_ORDER[::-1]
    bar_h = 0.68

    left = [0.0] * len(rows)
    for seg_label, color, text_color in zip(seg_order, colors, text_colors):
        vals = [results[g]["shares_pct"][seg_label] for g in rows]
        ax.barh(rows, vals, left=left, height=bar_h, color=color,
                edgecolor=PAPER, linewidth=1.2, zorder=3)
        for g, v, l in zip(rows, vals, left):
            if v >= 7:
                ax.text(l + v / 2, g, f"{v:.0f}%", va="center", ha="center",
                        color=text_color, fontproperties=fonts["bold"], fontsize=10.5, zorder=4)
        left = [l + v for l, v in zip(left, vals)]

    ax.set_xlim(0, 100)
    ax.margins(y=0.05)
    for tick_label, g in zip(ax.get_yticklabels(), rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(12)
        tick_label.set_color(ACCENT if g == HIGHLIGHT_GROUP else INK)

    handles = [mpatches.Patch(facecolor=c, edgecolor=PAPER, label=l)
               for l, c in zip(seg_order, colors)]
    legend = ax.legend(
        handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.045),
        ncol=3, frameon=False, handlelength=1.2, handleheight=1.2,
        fontsize=10.5, prop=fonts["bold"], columnspacing=1.2,
    )
    for text in legend.get_texts():
        text.set_color(INK)

    draw_caption(fig, fonts, total_n, note)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pathway-out", type=Path, required=True)
    ap.add_argument("--border-out", type=Path, required=True)
    ap.add_argument("--dreamer-out", type=Path, required=True)
    ap.add_argument("--deport-out", type=Path, required=True)
    ap.add_argument("--prochoice-out", type=Path, required=True)
    ap.add_argument("--prolife-out", type=Path, required=True)
    ap.add_argument("--gaym-out", type=Path, required=True)
    ap.add_argument("--attend-out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    total_n = data["total_n"]
    note = "Population: all 12 religpew categories, shown individually (not collapsed)."

    render_magnitude_bar(
        data["pathway_selected"],
        title="Grant legal status: 3+ years worked, no felonies",
        subtitle="Share who selected this option in a multi-select\nimmigration-policy battery.",
        note=note, total_n=total_n, out_path=args.pathway_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["border_selected"],
        title="Increase border patrols",
        subtitle="Share who selected this option in a multi-select\nimmigration-policy battery.",
        note=note, total_n=total_n, out_path=args.border_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["dreamer_selected"],
        title="Grant legal status to Dreamers",
        subtitle="Share who selected this option in a multi-select\nimmigration-policy battery.",
        note=note, total_n=total_n, out_path=args.dreamer_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["deport_selected"],
        title="Identify and deport illegal immigrants",
        subtitle="Share who selected this option in a multi-select\nimmigration-policy battery.",
        note=note, total_n=total_n, out_path=args.deport_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["prochoice_support"],
        title="Always allow abortion as a matter of choice",
        subtitle="Share who support always allowing a woman to obtain\nan abortion as a matter of choice.",
        note=note, total_n=total_n, out_path=args.prochoice_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["prolife_support"],
        title="Make abortion illegal in all circumstances",
        subtitle="Share who support making abortion illegal in all\ncircumstances.",
        note=note, total_n=total_n, out_path=args.prolife_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["gaym_favor"],
        title="Favor same-sex marriage",
        subtitle="Share who favor allowing gays and lesbians to marry\nlegally.",
        note=note, total_n=total_n, out_path=args.gaym_out, fonts=fonts,
    )
    render_distribution_stack(
        data["attend_distribution"], data["attend_order"],
        title="Religious attendance, full distribution",
        subtitle="How often each religion group attends religious\nservices.",
        note=note, total_n=total_n, out_path=args.attend_out, fonts=fonts,
    )


if __name__ == "__main__":
    main()
