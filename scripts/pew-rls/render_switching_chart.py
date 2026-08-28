#!/usr/bin/env python3
"""Renders the "raised vs. current" net-change graphic for the Pew RLS
Data Explorer page: how much each tradition's share of U.S. adults has
grown or shrunk relative to the share raised in it, LDS included.

Reads only docs/datasets/pew-rls-2023-24/switching-rates.json (produced by
switching_rates.py from the microdata) - no number here is hand-typed. See
STYLE.md in this folder for the palette and layout this implements, and why
it departs from state-of-theology-graphics/STYLE.md's identity palette.

Usage:
    python render_switching_chart.py \
        --out ../../public/data-explorer/pew-religious-landscape-study/switching-rates.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import MIN, draw_caption_bottom, sort_groups  # noqa: E402

# ---------------------------------------------------------------------------
# House style tokens - see STYLE.md. Keep this block and STYLE.md in sync.
# ---------------------------------------------------------------------------

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"
GRID = "#D9D5CC"

DECLINE_CONFIDENT = "#7c2d2d"  # --oxblood: BRANDING_AND_DESIGN.md's decline/negative token
DECLINE_UNCERTAIN = "#b08181"  # 60% tint - lightest that still clears WCAG's 3:1 non-text floor

# The Protestant-composition inset reuses state-of-theology's own locked
# identity palette directly - these ARE the same categories, so they get
# the same colors, no exceptions (same rule that palette states for itself).
PROTESTANT_PALETTE = {
    "Evangelical Protestant": "#C9721C",
    "Mainline Protestant": "#4E5D80",
    "Historically Black Protestant": "#5B7553",
}

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120  # 1080x1350 - matches every other Data Explorer graphic

# Set of rows for the main chart - which groups belong, not what order they
# plot in. Order now comes from chart_style.sort_groups at render time
# (descending by |net change|, largest decline first), with the site-wide
# tiering rule applied on top: "Other Christian" sinks below every
# substantive row regardless of its own |net change|, since it's a
# catch-all/aggregate row, not a distinct tradition. LDS still lands
# wherever its own number puts it among the substantive rows, same as every
# other non-pinned group.
GROUP_ORDER = [
    "Catholic",
    "Jehovah's Witness",
    "Latter-day Saint",
    "Protestant",
    "Other Christian",
    "Orthodox Christian",
]

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2023-24" / "switching-rates.json"
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


def ci_excludes_zero(net_change_pct: float, se: float) -> bool:
    margin = 1.96 * se
    lo, hi = net_change_pct - margin, net_change_pct + margin
    return lo > 0 or hi < 0


def render(data: dict, out_path: Path, fonts: dict[str, fm.FontProperties]) -> None:
    switching = data["switching"]
    protestant = data["protestant_current_composition"]
    total_n = data["total_unweighted_n"]

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    # Caption drawn first (bottom-anchored) so its actual top edge is known
    # before the inset axes' bottom is chosen - see STYLE.md's "Footnotes:
    # bottom-anchored" / "Vertical layout" sections.
    source_paragraphs = [
        f"Pew Research Center's Religious Landscape Study (RLS), 2023-24 wave · "
        f"N = {total_n:,} U.S. adults",
        "Net change = share currently in a tradition vs. the share raised in it, as % of "
        "the raised share. Confidence intervals from Pew's own 500 bootstrap replicate weights.",
        "Pew Research Center. 2025. “2023-24 Religious Landscape Study (RLS) Dataset.” "
        "doi: 10.58094/3kwb-bf52.",
    ]
    caption_top = draw_caption_bottom(fig, fonts, source_paragraphs, left=0.065)

    # Explicit rectangles ([left, bottom, width, height], figure fraction, 0
    # at the bottom) rather than gridspec: this chart mixes two axes with
    # hand-placed text between and around them, and gridspec's height_ratios
    # + hspace interact in ways that are hard to predict by eye. Explicit
    # coordinates make every element's vertical budget an intentional,
    # visible number here rather than an emergent one.
    AXES_LEFT, AXES_WIDTH = 0.30, 0.64
    INSET_TOP = 0.370
    inset_bottom = caption_top + 0.03
    ax_main = fig.add_axes([AXES_LEFT, 0.485, AXES_WIDTH, 0.30])
    ax_inset = fig.add_axes([AXES_LEFT, inset_bottom, AXES_WIDTH, INSET_TOP - inset_bottom])
    for ax in (ax_main, ax_inset):
        ax.set_facecolor(PAPER)
        ax.set_xticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(axis="y", length=0, pad=10)

    # --- Main chart: net change, diverging from a zero baseline ----------
    sorted_groups = sort_groups(GROUP_ORDER, lambda g: abs(switching[g]["net_change_pct"]))
    groups = sorted_groups[::-1]  # bottom-to-top, so the largest decline plots at top
    values = [switching[g]["net_change_pct"] for g in groups]
    ses = [switching[g]["net_change_se"] for g in groups]
    margins = [1.96 * se for se in ses]
    confident = [ci_excludes_zero(v, se) for v, se in zip(values, ses)]
    colors = [DECLINE_CONFIDENT if c else DECLINE_UNCERTAIN for c in confident]

    bar_height = 0.58
    ax_main.barh(groups, values, height=bar_height, color=colors, zorder=3)
    ax_main.margins(y=0.10)

    # xlim has to fit the widest whisker, not just the longest bar - a small
    # group's margin of error can extend well past its own point estimate
    # (Jehovah's Witness: -35.6% ± 15.0). Leave extra room on the left for
    # the value label itself, sized as a fraction of the final span so it
    # scales with the data instead of a fixed unit count that only works for
    # one particular set of numbers.
    leftmost = min(v - m for v, m in zip(values, margins))
    xmin, xmax = leftmost * 1.22, 4
    ax_main.set_xlim(xmin, xmax)
    span = xmax - xmin
    label_offset = span * 0.028
    ax_main.axvline(0, color=GRID, linewidth=1.4, zorder=2)

    for g, v, m, c in zip(groups, values, margins, confident):
        # CI whisker: drawn in Muted (a structural element, not the bar's
        # own decline/uncertain tone) so it reads the same regardless of
        # which fill tone the bar itself has.
        ax_main.plot(
            [v - m, v + m], [g, g],
            color=MUTED, linewidth=1.5, zorder=4, solid_capstyle="butt",
        )
        for edge in (v - m, v + m):
            ax_main.plot([edge, edge], [g, g], marker="|", markersize=9,
                         markeredgewidth=1.5, color=MUTED, zorder=4)

        label_color = DECLINE_CONFIDENT if c else MUTED
        ax_main.text(
            v - m - label_offset, g, f"{v:+.0f}%",
            va="center", ha="right", color=label_color,
            fontproperties=fonts["bold"], fontsize=18,
        )

    for label in ax_main.get_yticklabels():
        label.set_fontproperties(fonts["bold"])
        label.set_fontsize(16)
        label.set_color(INK)

    fig.text(
        AXES_LEFT, 0.465,
        "Faded bars: 95% confidence interval includes zero — not statistically "
        "distinguishable from no change.",
        fontproperties=fonts["regular"], fontsize=10, color=MUTED, ha="left", va="top",
    )

    # --- Inset: current Protestant-tradition composition (a snapshot, ----
    # --- not a rate - FRMREL can't split this finely in the public file) -
    fig.text(
        AXES_LEFT, 0.415, "Protestant tradition today",
        fontproperties=fonts["bold"], fontsize=15, color=INK, ha="left", va="top",
    )
    fig.text(
        AXES_LEFT, 0.392,
        "Share of U.S. adults, 2023-24 — a snapshot, not a change rate (see note above).",
        fontproperties=fonts["regular"], fontsize=10, color=MUTED, ha="left", va="top",
    )

    inset_groups = list(PROTESTANT_PALETTE.keys())[::-1]
    inset_values = [protestant[g]["current_pct"] for g in inset_groups]
    inset_colors = [PROTESTANT_PALETTE[g] for g in inset_groups]
    short_labels = {
        "Evangelical Protestant": "Evangelical",
        "Mainline Protestant": "Mainline",
        "Historically Black Protestant": "Hist. Black",
    }

    ax_inset.barh(inset_groups, inset_values, height=0.55, color=inset_colors, zorder=3)
    ax_inset.margins(y=0.20)
    xtop_inset = max(inset_values) * 1.3
    ax_inset.set_xlim(0, xtop_inset)
    ax_inset.set_yticks(inset_groups)
    ax_inset.set_yticklabels([short_labels[g] for g in inset_groups])
    for label in ax_inset.get_yticklabels():
        label.set_fontproperties(fonts["bold"])
        label.set_fontsize(14)
        label.set_color(INK)

    for g, v, color in zip(inset_groups, inset_values, inset_colors):
        ax_inset.text(
            v + xtop_inset * 0.02, g, f"{v:.0f}%",
            va="center", ha="left", color=color,
            fontproperties=fonts["bold"], fontsize=14,
        )

    # --- Title / subtitle -------------------------------------------------
    # Short enough to fit one line at this size - render_chart.py's titles
    # can run long because they must quote a survey statement verbatim; this
    # chart has no such statement to quote, so the title stays short and the
    # subtitle carries the fuller description.
    fig.text(
        0.065, 0.965, "Net change since childhood",
        fontproperties=fonts["title"], fontsize=28, color=INK, ha="left", va="top",
    )
    fig.text(
        0.065, 0.912,
        "Each tradition's share of U.S. adults today, compared with the share\n"
        "raised in it — 2023-24 Religious Landscape Study.",
        fontproperties=fonts["regular"], fontsize=14, color=MUTED, ha="left", va="top",
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
