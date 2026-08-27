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

render_timeseries (added for the "mixed data" us-membership-growth-2000-2025
entry) is the first line chart in this pipeline: a single --accent line
over years, solid where every underlying figure is a real reported (or
Church-published round-estimate) number, dashed wherever a segment touches
a linearly-interpolated year (no source has that year's figure - see
scripts/us-membership-growth-2000-2025/build_data.py). Unlike the bar
shapes above, the y-axis does NOT start at zero: a line's slope reads as
the trend, not as a bar's length-as-magnitude, so truncating the axis to
the data's own range is standard practice for a line chart and isn't
misleading as long as the gridline values are labeled plainly, which they
are here.
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


BORDER = "#D9D5CC"


def render_timeseries(
    *,
    years: list[int],
    values: dict[int, float],
    statuses: dict[int, str],
    title: str,
    subtitle: str,
    caption_paragraphs: list[str],
    out_path: Path,
    fonts: dict[str, fm.FontProperties] | None = None,
    y_step: float = 500_000,
    y_label_divisor: float = 1_000_000,
    y_label_suffix: str = "M",
    label_years: list[int] | None = None,
    x_tick_step: int = 5,
    show_markers: bool = True,
) -> None:
    """A single line over `years` (evenly spaced, e.g. one per calendar
    year). `statuses[year]` is one of:
      - "reported"/"rounded": a real figure - solid --accent, filled marker.
      - "interpolated": linearly filled across a historical gap with no
        source - dashed --accent, hollow accent-outlined marker.
      - "projected": a forward trend projection, not a historical figure
        at all - dashed CONTEXT_GRAY, hollow gray-outlined marker. Kept
        visually distinct from "interpolated" so a reader can't mistake
        "we don't have this year's report" for "this hasn't happened yet."
    A segment between two adjacent years takes the "worse" status of its
    two endpoints (projected > interpolated > reported) for its line
    style. The legend only lists statuses actually present in `statuses`.
    `label_years` (default: first and last) get a bold value callout.

    `x_tick_step` spaces out year labels on the x-axis (raise it above the
    5-year default for a long span - e.g. 25 for an 1830-2025 series,
    where every-5-years would crowd ~40 labels together). `show_markers`
    turns off the per-year dot entirely (leaving just the line) for a
    dense multi-century series, where a dot every single year is visual
    noise rather than signal - the line's own shape already carries the
    same information.
    """
    import math

    STATUS_RANK = {"reported": 0, "rounded": 0, "interpolated": 1, "projected": 2}
    STATUS_COLOR = {"reported": ACCENT, "rounded": ACCENT, "interpolated": ACCENT, "projected": CONTEXT_GRAY}
    STATUS_LEGEND_LABEL = {
        "reported": "Reported figure", "rounded": "Reported figure",
        "interpolated": "Interpolated (no source found)",
        "projected": "Projected (linear trend)",
    }

    fonts = fonts or load_fonts()
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = _draw_title(fig, fonts, title, subtitle)
    caption_top = draw_caption_bottom(fig, fonts, caption_paragraphs)
    legend_top_y = caption_top + 0.02 + LEGEND_ROW_HEIGHT
    ax_top = subtitle_bottom - 0.03
    ax_bottom = legend_top_y + 0.03

    AXES_LEFT, AXES_WIDTH = 0.13, 0.80
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    for spine in ax.spines.values():
        spine.set_visible(False)

    vals = [values[y] for y in years]
    y_floor = math.floor(min(vals) / y_step) * y_step
    y_ceil = math.ceil(max(vals) / y_step) * y_step
    if y_ceil == y_floor:
        y_ceil += y_step

    y_ticks = []
    t = y_floor
    while t <= y_ceil:
        y_ticks.append(t)
        t += y_step
    ax.set_ylim(y_floor, y_ceil)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{t / y_label_divisor:g}{y_label_suffix}" for t in y_ticks])
    ax.tick_params(axis="y", length=0, pad=8, labelsize=MIN.AXIS_LABEL)
    for label in ax.get_yticklabels():
        label.set_fontproperties(fonts["regular"])
        label.set_color(MUTED)
    ax.grid(axis="y", color=BORDER, linewidth=1, zorder=1)

    x_ticks = [y for y in years if y % x_tick_step == 0] or years
    if years[0] not in x_ticks:
        x_ticks.insert(0, years[0])
    if years[-1] not in x_ticks:
        x_ticks.append(years[-1])
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([str(y) for y in x_ticks])
    ax.tick_params(axis="x", length=0, pad=10, labelsize=MIN.AXIS_LABEL)
    for label in ax.get_xticklabels():
        label.set_fontproperties(fonts["bold"])
        label.set_color(INK)
    ax.set_xlim(years[0] - 0.5, years[-1] + 0.5)

    for y0, y1 in zip(years[:-1], years[1:]):
        seg_status = max(statuses[y0], statuses[y1], key=lambda s: STATUS_RANK[s])
        color = STATUS_COLOR[seg_status]
        ax.plot(
            [y0, y1], [values[y0], values[y1]], color=color,
            linewidth=2.75, linestyle="solid" if STATUS_RANK[seg_status] == 0 else (0, (5, 3)),
            solid_capstyle="round", zorder=3,
        )
    marker_years = years if show_markers else (label_years or [years[0], years[-1]])
    for y in marker_years:
        color = STATUS_COLOR[statuses[y]]
        real = STATUS_RANK[statuses[y]] == 0
        ax.plot(
            y, values[y], marker="o",
            markersize=6 if real else 5.5,
            markerfacecolor=color if real else PAPER,
            markeredgecolor=color, markeredgewidth=1.8, zorder=4,
        )

    # A fixed pixel offset (not a fraction of the y-range) so a label never
    # overshoots the floor/ceiling regardless of how wide that range is -
    # a range-relative offset (e.g. "3.5% of the axis span") looks fine on
    # a 2M-wide axis but pushes a near-floor point's label past the bottom
    # spine on a wider one (e.g. this shape's own 2000-2050 projection,
    # which spans 4M). Direction still leans away from whichever boundary
    # (floor or ceiling) the point sits closer to.
    label_years = label_years or [years[0], years[-1]]
    for y in label_years:
        # The series' own first/last point has nothing to its left/right
        # in x, so floating its label sideways (vertically centered, no
        # vertical push at all) is always clear of the line - unlike a
        # vertical push, which for an interior or endpoint value close to
        # the floor/ceiling can either cross the axis spine (wide y-range)
        # or land back on the line's own steep climb (narrow one).
        # matplotlib doesn't clip an annotation that extends past the axes
        # box, so this is safe even though it's technically off the
        # plotted x-range.
        if y == years[0]:
            ax.annotate(
                f"{values[y]:,.0f}", xy=(y, values[y]), xytext=(-10, 0),
                textcoords="offset points", ha="right", va="center",
                color=STATUS_COLOR[statuses[y]], fontproperties=fonts["bold"],
                fontsize=MIN.DATA_LABEL + 2, zorder=5,
            )
            continue
        if y == years[-1]:
            # Unlike the first point, floating this one further right risks
            # running past the canvas edge entirely (there's much less
            # right-margin reserved than the left margin the y-axis labels
            # already claim) - so this one floats LEFT instead, back over
            # the plot, with a small upward nudge: sweeping left at exactly
            # this height is normally collision-free (the series' own
            # maximum only occurs at x = years[-1]), except when growth has
            # flattened right at the end (e.g. the last two years of the
            # U.S. 2000-2025 series are within 200 of each other) and a
            # second point sits at nearly the same height just before it.
            ax.annotate(
                f"{values[y]:,.0f}", xy=(y, values[y]), xytext=(-10, 12),
                textcoords="offset points", ha="right", va="center",
                color=STATUS_COLOR[statuses[y]], fontproperties=fonts["bold"],
                fontsize=MIN.DATA_LABEL + 2, zorder=5,
            )
            continue
        dist_to_floor = values[y] - y_floor
        dist_to_ceil = y_ceil - values[y]
        va = "bottom" if dist_to_floor < dist_to_ceil else "top"
        ax.annotate(
            f"{values[y]:,.0f}", xy=(y, values[y]), xytext=(0, 18 if va == "bottom" else -18),
            textcoords="offset points", ha="center", va=va,
            color=STATUS_COLOR[statuses[y]], fontproperties=fonts["bold"],
            fontsize=MIN.DATA_LABEL + 2, zorder=5,
        )

    from matplotlib.lines import Line2D
    # Dedupe by legend label, not raw status - "reported" and "rounded"
    # share one legend entry ("Reported figure") despite being distinct
    # statuses (see membership-by-year.json's own per-year `status`).
    present_ranks = sorted({STATUS_RANK[statuses[y]] for y in years})
    rank_to_status = {rank: s for s, rank in STATUS_RANK.items() if rank in present_ranks}
    handles = [
        Line2D(
            [0], [0], color=STATUS_COLOR[rank_to_status[rank]], linewidth=2.75,
            linestyle="solid" if rank == 0 else (0, (5, 3)),
            label=STATUS_LEGEND_LABEL[rank_to_status[rank]],
        )
        for rank in present_ranks
    ]
    legend = ax.legend(
        handles=handles, loc="upper left", bbox_to_anchor=(0.065, legend_top_y),
        bbox_transform=fig.transFigure,
        ncol=len(handles), frameon=False, handlelength=2.2, columnspacing=1.4,
        fontsize=MIN.LEGEND, prop=fonts["bold"],
    )
    for text in legend.get_texts():
        text.set_color(INK)
        text.set_fontsize(MIN.LEGEND)

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
