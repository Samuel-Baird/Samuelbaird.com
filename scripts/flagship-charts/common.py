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
one shared module holds the single chart shape all eight need (and every
other one-off dataset registered since - see this folder's STYLE.md for
the full list): a horizontal magnitude bar, one row per category, colored
either by per-group religious identity (`group_identity=True`, the
default for any group-comparison chart - see BRANDING_AND_DESIGN.md's
"Charts" section) or by a binary highlight of the chart's own subject
(`highlight_rows`, for a chart about a specific country/time-period/
category rather than a religious identity). Same canvas, fonts, and
caption/title layout as every other chart in the Data Explorer pipeline
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

render_range_projection (added for the us-membership-growth-2000-2025
dataset's 2050 chart, replacing an earlier single-line version) is a
history line plus a shaded low/high band for the projected years, not a
single projected line - a single trend line turned out not to be
defensible 25 years past the data (see
scripts/us-membership-growth-2000-2025/build_projection.py's own
docstring for why: a better-fitting quadratic reverses into an implausible
decline when extrapolated that far, and a mechanistically nicer
declining-growth-rate model fits the noisy underlying rate data poorly).
Showing a range communicates the real uncertainty instead of one
falsely-precise number.

render_timeseries_by_direction (added for a second worldwide-membership-
history chart) colors every segment by whether it rose or fell from the
prior year - --accent (blue) for an increase, --oxblood (red) for a
decrease - rather than by data-quality status the way render_timeseries
does. This is a different question a chart can answer ("when did it ever
go down?") and needed its own function rather than a mode flag on
render_timeseries, since the two are mutually exclusive ways to color the
same line (quality-of-source vs. direction-of-change) and a single
function trying to do both would need a confusing dual-legend.

render_dumbbell_log (added for the ten-largest-us-churches-2035 dataset,
comparing TEN denominations against each other rather than tracking one
body over time) is a log-scale dumbbell/slope chart: one row per
denomination, a gray dot at its own last-reported membership and a
triangle at its 2035 straight-line projection, connected by a line colored
--accent (growing) or --oxblood (declining). Log scale is required here,
not a style choice - these ten bodies span from ~400K to ~70M members, and
on a linear axis the nine smaller ones would collapse to indistinguishable
points against the Catholic Church's bar. This is the multi-entity
counterpart to render_timeseries's single-entity "solid vs. dashed"
distinction: here every entry gets its own real-vs-projected pair, so the
dashed/solid device doesn't apply and confidence is instead marked with an
asterisk on the row label (see `low_confidence_rows`) with the caption
explaining which bodies that covers and why.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import LEGEND_ROW_HEIGHT, MIN, color_for_group, draw_caption_bottom  # noqa: E402

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
    handle: str | None = None,
    handle_color: str | None = None,
    out_path: Path,
    fonts: dict[str, fm.FontProperties] | None = None,
    value_suffix: str = "%",
    axes_left: float = 0.36,
    group_identity: bool = False,
) -> None:
    """One horizontal bar per `rows` entry (already in top-to-bottom display
    order), reading its value from `values[row]`. `caption_paragraphs`,
    `handle`, and `handle_color` are passed straight to
    chart_style.draw_caption_bottom - per the site-wide caption convention
    (BRANDING_AND_DESIGN.md's "Charts" section), pass `caption_paragraphs=[]`
    and `handle="@ithinkisam | data: <short title>"` rather than building a
    multi-line citation block.

    Two coloring modes, chosen by `group_identity`:

    - `group_identity=True` (a by-religious-group comparison chart): every
      row is colored by `chart_style.color_for_group`, its own locked
      identity hex rather than a binary highlight. `highlight_rows` is
      ignored in this mode - pass `highlight_rows=None`. This is the
      site-wide rule for any chart whose rows are named religious groups
      (BRANDING_AND_DESIGN.md's "Charts" section): no single group,
      including Latter-day Saints, gets singled out in --accent against a
      gray field of everyone else.
    - `group_identity=False` (default): rows in `highlight_rows` (or every
      row, if `highlight_rows` is None - a single-population "which of
      these items mattered" chart with no group axis at all) are drawn in
      --accent, everything else in a bar-safe gray. This remains legitimate
      for a chart whose subject is a specific country/time-period/tracked
      category rather than a religious identity (e.g. highlighting "United
      States" among a list of countries) - it isn't the "gray out everyone
      but the one favored group" pattern this rule targets.

    In both modes the y-axis tick label itself is always plain ink, never
    colored to match its bar - a row's color lives on the bar, not the
    label.

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
    caption_top = draw_caption_bottom(
        fig, fonts, caption_paragraphs, handle=handle, handle_color=handle_color,
    )
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
    if group_identity:
        colors = [color_for_group(r) for r in display_rows]
    else:
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
        tick_label.set_color(INK)

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
    handle: str | None = None,
    handle_color: str | None = None,
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
    caption_top = draw_caption_bottom(
        fig, fonts, caption_paragraphs, handle=handle, handle_color=handle_color,
    )
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
        # in x, so floating its label sideways is normally clear of the
        # line - unlike a vertical push, which for an interior or endpoint
        # value close to the floor/ceiling can either cross the axis spine
        # (wide y-range) or land back on the line's own steep climb
        # (narrow one). A small upward nudge is still needed on top of the
        # sideways float when the first point sits at (or very near) the
        # y-axis floor itself, e.g. worldwide-membership-history's 1830
        # value of 280 on an 18M-tall axis - centered-on-the-point placement
        # there lands directly on top of the floor's own "0M" tick label,
        # since both are drawn at the same height in the same left margin.
        # matplotlib doesn't clip an annotation that extends past the axes
        # box, so floating left is safe even though it's technically off
        # the plotted x-range.
        if y == years[0]:
            ax.annotate(
                f"{values[y]:,.0f}", xy=(y, values[y]), xytext=(-10, 14),
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


def render_range_projection(
    *,
    history_years: list[int],
    history_values: dict[int, float],
    range_years: list[int],
    low_values: dict[int, float],
    high_values: dict[int, float],
    title: str,
    subtitle: str,
    caption_paragraphs: list[str],
    handle: str | None = None,
    handle_color: str | None = None,
    out_path: Path,
    fonts: dict[str, fm.FontProperties] | None = None,
    y_step: float = 500_000,
    y_label_divisor: float = 1_000_000,
    y_label_suffix: str = "M",
) -> None:
    """A solid --accent history line (`history_years`), then a shaded
    low/high band for `range_years` (which should start at the same year
    `history_years` ends on, so the band picks up exactly where the solid
    line stops) - see this module's docstring for why a range, not a
    single projected line. The high boundary is drawn --accent dashed (the
    "trend continues" reading), the low boundary CONTEXT_GRAY dashed (the
    "deceleration continues" reading); the fill between them is a light
    --accent tint. Value callouts: history's own first point, plus the
    range's final low and high figures.
    """
    import math

    fonts = fonts or load_fonts()
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = _draw_title(fig, fonts, title, subtitle)
    caption_top = draw_caption_bottom(
        fig, fonts, caption_paragraphs, handle=handle, handle_color=handle_color,
    )
    legend_top_y = caption_top + 0.02 + LEGEND_ROW_HEIGHT
    ax_top = subtitle_bottom - 0.03
    ax_bottom = legend_top_y + 0.03

    AXES_LEFT, AXES_WIDTH = 0.13, 0.80
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    for spine in ax.spines.values():
        spine.set_visible(False)

    all_years = history_years + range_years[1:]
    hist_vals = [history_values[y] for y in history_years]
    low_vals = [low_values[y] for y in range_years]
    high_vals = [high_values[y] for y in range_years]
    y_min = min(hist_vals + low_vals)
    y_max = max(hist_vals + high_vals)
    y_floor = math.floor(y_min / y_step) * y_step
    y_ceil = math.ceil(y_max / y_step) * y_step
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

    x_ticks = [y for y in all_years if y % 5 == 0] or all_years
    if all_years[0] not in x_ticks:
        x_ticks.insert(0, all_years[0])
    if all_years[-1] not in x_ticks:
        x_ticks.append(all_years[-1])
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([str(y) for y in x_ticks])
    ax.tick_params(axis="x", length=0, pad=10, labelsize=MIN.AXIS_LABEL)
    for label in ax.get_xticklabels():
        label.set_fontproperties(fonts["bold"])
        label.set_color(INK)
    ax.set_xlim(all_years[0] - 0.5, all_years[-1] + 0.5)

    ax.plot(history_years, hist_vals, color=ACCENT, linewidth=2.75,
            solid_capstyle="round", zorder=3)
    ax.fill_between(range_years, low_vals, high_vals, color=ACCENT, alpha=0.13,
                     linewidth=0, zorder=2)
    ax.plot(range_years, high_vals, color=ACCENT, linewidth=1.75,
            linestyle=(0, (5, 3)), zorder=3)
    ax.plot(range_years, low_vals, color=CONTEXT_GRAY, linewidth=1.75,
            linestyle=(0, (5, 3)), zorder=3)
    for x, y, c in ((history_years[-1], hist_vals[-1], ACCENT),):
        ax.plot(x, y, marker="o", markersize=6, markerfacecolor=c,
                markeredgecolor=c, markeredgewidth=1.8, zorder=4)

    # First history point floats left (see render_timeseries for why: it's
    # the one placement clear of both the axis floor and the line's own
    # early climb, regardless of axis range). Final high/low points float
    # left of the canvas's own right edge for the same reason a plain
    # rightward float would overflow it.
    def label(x, y, color, dx, dy, ha):
        ax.annotate(
            f"{y:,.0f}", xy=(x, y), xytext=(dx, dy), textcoords="offset points",
            ha=ha, va="center", color=color, fontproperties=fonts["bold"],
            fontsize=MIN.DATA_LABEL + 2, zorder=5,
        )

    label(history_years[0], hist_vals[0], ACCENT, -10, 14, "right")
    label(range_years[-1], high_vals[-1], ACCENT, -10, 0, "right")
    # The low bound flattens out (hits its 0%-growth floor) well before
    # 2050, so its own line runs dead flat under this label - nudge down
    # so the line passes below the text rather than straight through it.
    label(range_years[-1], low_vals[-1], CONTEXT_GRAY, -10, -14, "right")

    from matplotlib.lines import Line2D
    import matplotlib.patches as mpatches
    handles = [
        Line2D([0], [0], color=ACCENT, linewidth=2.75, linestyle="solid", label="Reported figure"),
        mpatches.Patch(facecolor=ACCENT, alpha=0.13, edgecolor="none",
                        label=f"Projected range, {range_years[0] + 1}-{range_years[-1]}"),
    ]
    legend = ax.legend(
        handles=handles, loc="upper left", bbox_to_anchor=(0.065, legend_top_y),
        bbox_transform=fig.transFigure,
        ncol=2, frameon=False, handlelength=2.2, columnspacing=1.4,
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
    handle: str | None = None,
    handle_color: str | None = None,
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
    caption_top = draw_caption_bottom(
        fig, fonts, caption_paragraphs, handle=handle, handle_color=handle_color,
    )
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


def render_timeseries_by_direction(
    *,
    years: list[int],
    values: dict[int, float],
    title: str,
    subtitle: str,
    caption_paragraphs: list[str],
    handle: str | None = None,
    handle_color: str | None = None,
    out_path: Path,
    fonts: dict[str, fm.FontProperties] | None = None,
    y_step: float = 2_000_000,
    y_label_divisor: float = 1_000_000,
    y_label_suffix: str = "M",
    x_tick_step: int = 25,
    label_years: list[int] | None = None,
) -> None:
    """A single line over `years`, colored per-segment by whether it rose
    (--accent, blue) or fell (--oxblood, red) from the prior year - see
    this module's docstring for why this is a separate function from
    render_timeseries rather than a mode on it. Every year touching a
    decrease gets a small red marker (both the year it fell FROM and the
    year it fell TO, so the whole dip is visually bracketed); every other
    year is unmarked to keep a long series from turning into a wall of dots.
    """
    import math

    fonts = fonts or load_fonts()
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = _draw_title(fig, fonts, title, subtitle)
    caption_top = draw_caption_bottom(
        fig, fonts, caption_paragraphs, handle=handle, handle_color=handle_color,
    )
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

    decrease_years: set[int] = set()
    for y0, y1 in zip(years[:-1], years[1:]):
        falling = values[y1] < values[y0]
        color = OXBLOOD if falling else ACCENT
        if falling:
            decrease_years.add(y0)
            decrease_years.add(y1)
        ax.plot(
            [y0, y1], [values[y0], values[y1]], color=color,
            linewidth=2.75, solid_capstyle="round", zorder=3,
        )
    for y in decrease_years:
        ax.plot(
            y, values[y], marker="o", markersize=6,
            markerfacecolor=OXBLOOD, markeredgecolor=OXBLOOD, zorder=4,
        )

    label_years = label_years or [years[0], years[-1]]
    for y in label_years:
        color = ACCENT
        if y == years[0]:
            # See render_timeseries's own first-point comment: a small
            # upward nudge on top of the sideways float, so a point that
            # sits at (or very near) the y-axis floor - e.g. 1830's 280 on
            # an 18M-tall axis - doesn't land its label on top of the
            # floor's own tick label, which lives in the same left margin
            # at the same height.
            ax.annotate(
                f"{values[y]:,.0f}", xy=(y, values[y]), xytext=(-10, 14),
                textcoords="offset points", ha="right", va="center",
                color=color, fontproperties=fonts["bold"],
                fontsize=MIN.DATA_LABEL + 2, zorder=5,
            )
            continue
        if y == years[-1]:
            ax.annotate(
                f"{values[y]:,.0f}", xy=(y, values[y]), xytext=(-10, 12),
                textcoords="offset points", ha="right", va="center",
                color=color, fontproperties=fonts["bold"],
                fontsize=MIN.DATA_LABEL + 2, zorder=5,
            )
            continue
        dist_to_floor = values[y] - y_floor
        dist_to_ceil = y_ceil - values[y]
        va = "bottom" if dist_to_floor < dist_to_ceil else "top"
        # ha="right" (label entirely left of the point) rather than
        # centered, since on a curve that's still rising to the right of
        # this point (true for every interior milestone on an exponential
        # series like this one), a centered label's right half sits over
        # x-values where the line has already climbed higher - i.e. into
        # the line itself - while its left half sits over years where the
        # curve was lower, which is always clear.
        ax.annotate(
            f"{values[y]:,.0f}", xy=(y, values[y]), xytext=(-12, 20 if va == "bottom" else -20),
            textcoords="offset points", ha="right", va=va,
            color=color, fontproperties=fonts["bold"],
            fontsize=MIN.DATA_LABEL, zorder=5,
        )

    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], color=ACCENT, linewidth=2.75, label="Increase from prior year"),
        Line2D([0], [0], color=OXBLOOD, linewidth=2.75, label="Decrease from prior year"),
    ]
    legend = ax.legend(
        handles=handles, loc="upper left", bbox_to_anchor=(0.065, legend_top_y),
        bbox_transform=fig.transFigure,
        ncol=2, frameon=False, handlelength=2.2, columnspacing=1.4,
        fontsize=MIN.LEGEND, prop=fonts["bold"],
    )
    for text in legend.get_texts():
        text.set_color(INK)
        text.set_fontsize(MIN.LEGEND)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")


def render_dumbbell_log(
    *,
    rows: list[str],
    row_labels: dict[str, str],
    start_values: dict[str, float],
    end_values: dict[str, float],
    low_confidence_rows: set[str],
    title: str,
    subtitle: str,
    caption_paragraphs: list[str],
    handle: str | None = None,
    handle_color: str | None = None,
    out_path: Path,
    fonts: dict[str, fm.FontProperties] | None = None,
) -> None:
    """One row per `rows` entry (already in top-to-bottom display order,
    e.g. largest current membership first) - a gray dot at
    `start_values[row]` (last reported figure), a triangle at
    `end_values[row]` (2035 straight-line projection), joined by a line
    colored --accent if the projection is higher than the start, --oxblood
    if lower. X-axis is log-scaled - see this module's docstring for why
    that's load-bearing here, not decorative. Rows in `low_confidence_rows`
    get an asterisk appended to their y-axis label; the caption should
    explain what that covers.
    """
    import math
    from matplotlib.ticker import FixedLocator, FuncFormatter

    fonts = fonts or load_fonts()
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)

    subtitle_bottom = _draw_title(fig, fonts, title, subtitle)
    caption_top = draw_caption_bottom(
        fig, fonts, caption_paragraphs, handle=handle, handle_color=handle_color,
    )
    legend_top_y = caption_top + 0.02 + LEGEND_ROW_HEIGHT
    ax_top = subtitle_bottom - 0.03
    ax_bottom = legend_top_y + 0.03

    AXES_LEFT, AXES_WIDTH = 0.46, 0.50
    ax = fig.add_axes([AXES_LEFT, ax_bottom, AXES_WIDTH, ax_top - ax_bottom])
    ax.set_facecolor(PAPER)
    for spine in ax.spines.values():
        spine.set_visible(False)

    n = len(rows)
    all_vals = [start_values[r] for r in rows] + [end_values[r] for r in rows]
    x_min, x_max = min(all_vals), max(all_vals)
    ax.set_xscale("log")
    ax.set_xlim(x_min / 2.2, x_max * 1.9)

    def fmt_value(v, _pos=None):
        if v >= 1_000_000:
            n = v / 1_000_000
            s = f"{n:.2f}" if n < 10 else f"{n:.1f}"
            return s.rstrip("0").rstrip(".") + "M"
        if v >= 1_000:
            return f"{v / 1_000:.0f}K"
        return f"{v:.0f}"

    tick_vals = []
    decade = 10 ** math.floor(math.log10(x_min))
    while decade <= x_max * 10:
        for mult in (1, 3):
            t = decade * mult
            if x_min / 2.2 <= t <= x_max * 1.9:
                tick_vals.append(t)
        decade *= 10
    ax.xaxis.set_major_locator(FixedLocator(tick_vals))
    ax.xaxis.set_major_formatter(FuncFormatter(fmt_value))
    ax.tick_params(axis="x", length=0, pad=10, labelsize=MIN.AXIS_LABEL)
    for label in ax.get_xticklabels():
        label.set_fontproperties(fonts["bold"])
        label.set_color(INK)
    ax.grid(axis="x", color=BORDER, linewidth=1, zorder=1, which="major")

    ax.set_ylim(n - 0.5, -0.5)
    ax.set_yticks(range(n))
    ax.set_yticklabels([row_labels[r] + ("*" if r in low_confidence_rows else "") for r in rows])
    ax.tick_params(axis="y", length=0, pad=10)
    for tick_label in ax.get_yticklabels():
        tick_label.set_fontproperties(fonts["bold"])
        tick_label.set_fontsize(13.5)
        tick_label.set_color(INK)

    for i, r in enumerate(rows):
        start, end = start_values[r], end_values[r]
        growing = end >= start
        color = ACCENT if growing else OXBLOOD
        ax.plot([start, end], [i, i], color=color, linewidth=2.4, zorder=3, solid_capstyle="round")
        ax.plot(start, i, marker="o", markersize=7, markerfacecolor=CONTEXT_GRAY,
                 markeredgecolor=CONTEXT_GRAY, zorder=4)
        ax.plot(end, i, marker="^" if growing else "v", markersize=9,
                 markerfacecolor=color, markeredgecolor=color, zorder=4)

        # Vertical offsets (above/below the row's own line), not horizontal -
        # a horizontal float risks colliding with the y-axis row labels
        # whenever a point sits close to the shared x_min/x_max (e.g. PCUSA's
        # 2035 projection, which lands near the axis's own left edge).
        ax.annotate(
            fmt_value(start), xy=(start, i), xytext=(0, 11), textcoords="offset points",
            ha="center", va="bottom", color=MUTED, fontproperties=fonts["regular"],
            fontsize=MIN.DATA_LABEL - 1, zorder=5,
        )
        ax.annotate(
            fmt_value(end), xy=(end, i), xytext=(0, -12), textcoords="offset points",
            ha="center", va="top", color=color, fontproperties=fonts["bold"],
            fontsize=MIN.DATA_LABEL, zorder=5,
        )

    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], marker="o", color=PAPER, markerfacecolor=CONTEXT_GRAY,
               markeredgecolor=CONTEXT_GRAY, markersize=7, label="Last reported"),
        Line2D([0], [0], marker="^", color=PAPER, markerfacecolor=ACCENT,
               markeredgecolor=ACCENT, markersize=8, label="2035: growing"),
        Line2D([0], [0], marker="v", color=PAPER, markerfacecolor=OXBLOOD,
               markeredgecolor=OXBLOOD, markersize=8, label="2035: declining"),
    ]
    legend = ax.legend(
        handles=handles, loc="upper left", bbox_to_anchor=(0.065, legend_top_y),
        bbox_transform=fig.transFigure,
        ncol=len(handles), frameon=False, handlelength=1.6, columnspacing=1.2,
        fontsize=MIN.LEGEND, prop=fonts["bold"],
    )
    for text in legend.get_texts():
        text.set_color(INK)
        text.set_fontsize(MIN.LEGEND)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    print(f"wrote {out_path} ({FIG_W_IN * DPI}x{int(FIG_H_IN * DPI)}px)")
