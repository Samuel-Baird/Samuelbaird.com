"""
Shared render helper for the eight "flagship graphic" charts added when the
raw Pew datasets in data/pew-mormon-survey-2011/, pew-religious-knowledge-2010/,
pew-rls-2007/, pew-rls-2014/, pew-rls-2014-recontact/, pew-latin-america-2014/,
pew-faith-in-flux-2008/, and pew-atp-w70-2020/ were first registered in the
Data Explorer (each shipped with graphics: [] - see each dataset's own
docs/datasets/<slug>/README.md).

Unlike scripts/pew-rls/ or scripts/ryan-burge/, which accumulate many charts
per dataset family and so duplicate their own render_magnitude_bar per file
(see those folders' STYLE.md), each of these eight datasets gets exactly one
flagship chart. Duplicating the same ~150-line matplotlib function eight
times for a single call site each would just be copy-paste, not the
"family evolves independently" reason the other folders duplicate - so this
one shared module holds the single chart shape all eight need: a horizontal
magnitude bar, one row per category, with one or more rows optionally
highlighted in --accent and the rest in a bar-safe gray. Same canvas, fonts,
and caption/title layout as every other chart in the Data Explorer pipeline
(scripts/chart_style.py, scripts/state-of-theology-graphics/STYLE.md) - only
the compute step differs per dataset, in that dataset's own
scripts/<slug>/*.py analysis script.

If an eighth-plus one-off chart appears here later needing a genuinely new
shape (a stack, a heatmap), add it as its own function in this file rather
than forking a new per-dataset copy - the "one shape per module" pattern
still holds, there's just one module for all one-off flagship charts.

render_100_stack (added for pew-mormon-survey-2011's second chart, "Is
Mormonism a Christian religion?") is the first such addition: a small
100%-stacked horizontal bar for a handful of rows (here, two - "U.S.
Mormons" vs. "U.S. general public") each broken into the same few
segments (Yes/No/Don't know). Segment colors are fixed at Yes=--accent
(blue), No=--oxblood (red, the site's own decline/negative token), Don't
know=Muted (gray) - not a caller-supplied palette - since this shape only
exists for yes/no/don't-know-style items where that mapping is always the
right one.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import LEGEND_ROW_HEIGHT, MIN, draw_caption_bottom  # noqa: E402

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"

ACCENT = "#1f4f7a"
OXBLOOD = "#7c2d2d"
CONTEXT_GRAY = "#8f8b82"

# Fixed segment palette for render_100_stack's yes/no/don't-know shape.
YES_NO_DK_COLORS = {"Yes": ACCENT, "No": OXBLOOD, "Don't know": MUTED}
YES_NO_DK_TEXT_ON = {"Yes": PAPER, "No": PAPER, "Don't know": PAPER}

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120

FONTS_DIR = (Path(__file__).parent / ".." / "state-of-theology-graphics" / "fonts").resolve()


def load_fonts(fonts_dir: Path = FONTS_DIR) -> dict[str, fm.FontProperties]:
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
    title_fontsize = 26
    subtitle_fontsize = 13.5
    title_lines = textwrap.wrap(title, width=27)
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
    *,
    rows: list[str],
    values: dict[str, float],
    highlight_rows: set[str] | None,
    title: str,
    subtitle: str,
    caption_paragraphs: list[str],
    out_path: Path,
    fonts: dict[str, fm.FontProperties] | None = None,
    value_suffix: str = "%",
    axes_left: float = 0.36,
) -> None:
    """One horizontal bar per `rows` entry (already in top-to-bottom display
    order), reading its value from `values[row]`. Rows in `highlight_rows`
    (or every row, if None - a single-population "which of these items
    mattered" chart rather than a by-group comparison) are drawn in
    --accent; everything else in a bar-safe gray. `caption_paragraphs` are
    passed straight to chart_style.draw_caption_bottom - put the
    population/method note first, then the source line(s) with N and the
    recommended citation, matching every other chart in this pipeline.

    `axes_left` reserves that figure-fraction for the row labels before the
    bars start; raise it above the 0.36 default when a row label is long
    prose (e.g. a survey-item sentence) rather than a short group name -
    the default clips long labels past the canvas's left edge, since
    matplotlib doesn't wrap or shrink y-tick labels on its own.
    """
    fonts = fonts or load_fonts()
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = _draw_title(fig, fonts, title, subtitle)
    caption_top = draw_caption_bottom(fig, fonts, caption_paragraphs)
    ax_top = subtitle_bottom - 0.03
    ax_bottom = caption_top + 0.03

    n_rows = len(rows)
    AXES_LEFT, AXES_WIDTH = axes_left, 0.94 - axes_left
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    display_rows = rows[::-1]
    vals = [values[r] for r in display_rows]
    colors = [
        ACCENT if (highlight_rows is None or r in highlight_rows) else CONTEXT_GRAY
        for r in display_rows
    ]

    bar_h = 0.62 if n_rows <= 8 else 0.68
    ax.barh(display_rows, vals, height=bar_h, color=colors, zorder=3)
    ax.set_xlim(0, max(vals) * 1.22)
    ax.margins(y=0.06 if n_rows > 8 else 0.11)

    for tick_label, r in zip(ax.get_yticklabels(), display_rows):
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(MIN.AXIS_LABEL if n_rows > 8 else 14)
        tick_label.set_color(ACCENT if (highlight_rows is None or r in highlight_rows) else INK)

    for r, v, c in zip(display_rows, vals, colors):
        ax.text(
            v + max(vals) * 0.02, r, f"{v:.0f}{value_suffix}", va="center", ha="left",
            color=c, fontproperties=fonts["bold"],
            fontsize=MIN.DATA_LABEL if n_rows > 8 else 15, zorder=4,
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def render_100_stack(
    *,
    rows: list[str],
    segment_order: list[str],
    values: dict[str, dict[str, float]],
    title: str,
    subtitle: str,
    caption_paragraphs: list[str],
    out_path: Path,
    fonts: dict[str, fm.FontProperties] | None = None,
) -> None:
    """A handful of rows, each a 100%-stacked bar over the fixed Yes/No/
    Don't know palette (YES_NO_DK_COLORS) - see this module's docstring.
    `values[row][segment]` is that segment's share of that row, 0-100.
    `caption_paragraphs` are passed straight to
    chart_style.draw_caption_bottom, same convention as render_magnitude_bar.
    """
    fonts = fonts or load_fonts()
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = _draw_title(fig, fonts, title, subtitle)
    caption_top = draw_caption_bottom(fig, fonts, caption_paragraphs)
    ax_top = subtitle_bottom - 0.03

    n_rows = len(rows)
    n_segs = len(segment_order)
    legend_ncol = n_segs
    legend_bottom_y = caption_top + 0.02
    legend_top_y = legend_bottom_y + LEGEND_ROW_HEIGHT
    ax_bottom = legend_top_y + 0.02

    AXES_LEFT, AXES_WIDTH = 0.30, 0.64
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    display_rows = rows[::-1]
    bar_h = 0.42

    left = [0.0] * len(display_rows)
    for seg in segment_order:
        color = YES_NO_DK_COLORS[seg]
        text_color = YES_NO_DK_TEXT_ON[seg]
        vals = [values[r][seg] for r in display_rows]
        ax.barh(display_rows, vals, left=left, height=bar_h, color=color,
                 edgecolor=PAPER, linewidth=1.5, zorder=3)
        for r, v, l in zip(display_rows, vals, left):
            if v >= 5:
                ax.text(l + v / 2, r, f"{v:.0f}%", va="center", ha="center",
                        color=text_color, fontproperties=fonts["bold"],
                        fontsize=MIN.DATA_LABEL + 3, zorder=4)
        left = [l + v for l, v in zip(left, vals)]

    ax.set_xlim(0, 100)
    ax.margins(y=0.35)
    for tick_label in ax.get_yticklabels():
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(16)
        tick_label.set_color(INK)

    import matplotlib.patches as mpatches
    handles = [mpatches.Patch(facecolor=YES_NO_DK_COLORS[s], edgecolor=PAPER, label=s)
               for s in segment_order]
    legend = ax.legend(
        handles=handles, loc="upper left", bbox_to_anchor=(0.065, legend_top_y),
        bbox_transform=fig.transFigure,
        ncol=legend_ncol, frameon=False, handlelength=1.6, handleheight=1.6,
        fontsize=MIN.LEGEND, prop=fonts["bold"], columnspacing=1.4, labelspacing=0.9,
    )
    for text in legend.get_texts():
        text.set_color(INK)
        text.set_fontsize(MIN.LEGEND)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")
