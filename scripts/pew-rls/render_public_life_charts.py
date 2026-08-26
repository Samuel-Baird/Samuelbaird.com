#!/usr/bin/env python3
"""Renders the eleven "public life and society" PNGs for the Pew RLS Data
Explorer page - GRAPHICS_TODO.md's final backlog section.

Reads only docs/datasets/pew-rls-2023-24/public-life.json (produced by
scripts/pew-rls/public_life.py) - no number here is hand-typed. Reuses the
magnitude-bar shape from render_practice_charts.py/render_beliefs_charts.py
across all eleven items, at whichever group-order width each item's own
population calls for (7, 8, or 14 rows); see STYLE.md in this folder.

Usage: see the eleven --*-out flags below; run with --help for the full list.
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

CHRISTIAN_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
    "Jehovah's Witness", "Other Christian", "Christian average",
]
CHRISTIAN_PLUS_OTHER_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
    "Jehovah's Witness", "Other Christian", "Other religions",
    "Religiously affiliated average",
]
WIDEST_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Jehovah's Witness",
    "Muslim", "Hindu", "Orthodox Christian", "Other Christian", "Buddhist",
    "Jewish", "Other world religions", "Other faiths",
    "All religious average", "Religiously unaffiliated",
]

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2023-24" / "public-life.json"
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
    """Returns the y-fraction where the subtitle block actually ends, so
    the caller can size its axes to the real available band instead of a
    fixed guess - see STYLE.md's "Vertical layout" section."""
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


CAPTION_TOP = 0.145


def render_magnitude_bar(
    results: dict, group_order: list[str], title: str, subtitle: str, note: str,
    total_n: int, out_path: Path, fonts: dict[str, fm.FontProperties],
) -> None:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    # Vertical centering: size the axes to the real gap between the
    # subtitle and the caption, not a fixed guess - see STYLE.md.
    subtitle_bottom = draw_title(fig, fonts, title, subtitle)
    ax_top = subtitle_bottom - 0.03
    ax_bottom = CAPTION_TOP + 0.03

    n_rows = len(group_order)
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

    bar_h = 0.62 if n_rows <= 8 else 0.68
    ax.barh(rows, values, height=bar_h, color=colors, zorder=3)
    ax.set_xlim(0, max(values) * 1.22)
    ax.margins(y=0.06 if n_rows > 8 else 0.11)

    for tick_label, g in zip(ax.get_yticklabels(), rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(12.5 if n_rows > 8 else 14)
        tick_label.set_color(ACCENT if g == HIGHLIGHT_GROUP else INK)

    for g, v, c in zip(rows, values, colors):
        ax.text(v + max(values) * 0.02, g, f"{v:.0f}%", va="center", ha="left",
                 color=c, fontproperties=fonts["bold"], fontsize=13 if n_rows > 8 else 15, zorder=4)

    source_paragraphs = [
        note,
        f"Pew Research Center's Religious Landscape Study (RLS), 2023-24 wave · "
        f"N = {total_n:,} U.S. adults",
        "Pew Research Center. 2025. “2023-24 Religious Landscape Study (RLS) Dataset.” "
        "doi: 10.58094/3kwb-bf52.",
    ]
    caption_lines = [line for para in source_paragraphs for line in textwrap.wrap(para, width=98)]
    for i, line in enumerate(caption_lines):
        fig.text(
            0.065, CAPTION_TOP - i * 0.0165, line, fontproperties=fonts["regular"],
            fontsize=10, color=MUTED, ha="left", va="top",
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--openiden-out", type=Path, required=True)
    ap.add_argument("--chng-a-out", type=Path, required=True)
    ap.add_argument("--divracpop-out", type=Path, required=True)
    ap.add_argument("--divrelpop-out", type=Path, required=True)
    ap.add_argument("--humntr-out", type=Path, required=True)
    ap.add_argument("--relimpact-out", type=Path, required=True)
    ap.add_argument("--relinst-f-out", type=Path, required=True)
    ap.add_argument("--relinst-g-out", type=Path, required=True)
    ap.add_argument("--relinst-e-out", type=Path, required=True)
    ap.add_argument("--scimpact-out", type=Path, required=True)
    ap.add_argument("--vol12-out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    total_n = data["total_unweighted_n"]
    christian_note = "Population: Christian only."

    render_magnitude_bar(
        data["openiden_openness_essential"], CHRISTIAN_ORDER,
        title="America's openness to the world is essential",
        subtitle="Share who say America's openness to people from all\nover the world is essential to who we are as a nation.",
        note=christian_note, total_n=total_n, out_path=args.openiden_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["chng_a_immigration_better"], CHRISTIAN_ORDER,
        title="Immigration is a change for the better",
        subtitle="Share who say a growing population of immigrants is a\nchange for the better.",
        note=christian_note, total_n=total_n, out_path=args.chng_a_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["divracpop_strengthens"], CHRISTIAN_ORDER,
        title="Racial/ethnic diversity strengthens society",
        subtitle="Share who say people of many different races/\nethnicities strengthens American society.",
        note=christian_note, total_n=total_n, out_path=args.divracpop_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["divrelpop_strengthens"], CHRISTIAN_ORDER,
        title="Religious diversity strengthens society",
        subtitle="Share who say people of many different religions (and\nno religion) strengthens American society.",
        note=christian_note, total_n=total_n, out_path=args.divrelpop_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["humntr_b_completely"], CHRISTIAN_PLUS_OTHER_ORDER,
        title="God gave humans a duty to protect the Earth",
        subtitle="Of God-believers, share who say this completely\ndescribes their view.",
        note="Population: Christian + other religions, filtered to respondents who believe "
             "in God (GOD=Yes); cutpoint is \"Completely\" alone (top box).",
        total_n=total_n, out_path=args.humntr_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["relimpact_more_good"], WIDEST_ORDER,
        title="Religion does more good than harm",
        subtitle="Share who say religion's overall impact on American\nsociety is more good than harm.",
        note="Population: all religiously affiliated traditions individually, plus the "
             "religiously unaffiliated as their own row - the widest population in this section.",
        total_n=total_n, out_path=args.relimpact_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["relinst_f_bring_together"], CHRISTIAN_ORDER,
        title="Religious orgs bring people together",
        subtitle="Share who agree churches and other religious\norganizations strengthen community bonds.",
        note=christian_note, total_n=total_n, out_path=args.relinst_f_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["relinst_g_help_poor"], CHRISTIAN_ORDER,
        title="Religious orgs help the poor and needy",
        subtitle="Share who agree churches and other religious\norganizations play an important role helping the poor.",
        note=christian_note, total_n=total_n, out_path=args.relinst_g_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["relinst_e_strengthen_morality"], CHRISTIAN_ORDER,
        title="Religious orgs protect and strengthen morality",
        subtitle="Share who agree churches and other religious\norganizations protect and strengthen morality in society.",
        note=christian_note, total_n=total_n, out_path=args.relinst_e_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["scimpact_more_harm"], CHRISTIAN_ORDER,
        title="Science does more harm than good",
        subtitle="Share who say science's overall impact on American\nsociety is more harm than good.",
        note=christian_note, total_n=total_n, out_path=args.scimpact_out, fonts=fonts,
    )
    render_magnitude_bar(
        data["vol12_volunteered"], WIDEST_ORDER,
        title="Volunteered in the past 12 months",
        subtitle="Share who spent any time volunteering in the past 12\nmonths.",
        note="Population: all religiously affiliated traditions individually, plus the "
             "religiously unaffiliated as their own row.",
        total_n=total_n, out_path=args.vol12_out, fonts=fonts,
    )


if __name__ == "__main__":
    main()
