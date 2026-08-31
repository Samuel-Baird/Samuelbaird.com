"""Shared house-style helpers for the Data Explorer PNG pipeline.

Every dataset folder under scripts/ (state-of-theology-graphics, pew-rls,
ryan-burge) renders its own 1080x1350 matplotlib PNGs, but three things kept
drifting because they were copy-pasted per script: where the caption/footnote
sits, how small type is allowed to get, and (for the heatmaps) how a value
maps to a fill color. This module is the one place those live now. Import it
the same way every script already reaches across folders for
DEFAULT_FONTS_DIR:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from chart_style import draw_caption_bottom, diverging_color, label_ink, MIN

Per scripts/state-of-theology-graphics/STYLE.md's sync contract: if you
change anything in this module, update that STYLE.md, scripts/ryan-burge/STYLE.md,
and scripts/pew-rls/STYLE.md together - an undocumented style isn't a style.
This includes `sort_groups` below (the site-wide row-order rule) - see
BRANDING_AND_DESIGN.md's "Charts" section for the canonical statement of the
rule and scripts/pew-rls/STYLE.md for a worked example of applying it.
"""

from __future__ import annotations

import re
import textwrap
from typing import Callable

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"
BORDER = "#D9D5CC"

# Bar-fill-safe lighten of MUTED, readable as a distinct fill at full
# opacity (unlike a line chart's stroke-only muted gray). Promoted here from
# per-render-script duplicates (scripts/pew-rls/render_*.py each defined
# their own CONTEXT_GRAY = "#8f8b82") so it has one home like every other
# shared token in this module.
CONTEXT_GRAY = "#8f8b82"

FIG_W_IN, FIG_H_IN, DPI = 9, 11.25, 120  # 1080x1350px


class MIN:
    """Minimum font sizes (pt, at this pipeline's fixed 1080x1350 canvas) so
    every chart survives being viewed at ~1/3 scale on a phone (a 1080px PNG
    renders at roughly 335 CSS px in the /graphics gallery). A render script
    may go bigger than these, never smaller. If content can't fit at the
    floor, the chart is too dense - split it into two images, or suppress a
    label, rather than shrinking text below floor. Footnotes/captions are
    exempt: fine print is allowed to stay fine print."""

    TITLE = 24
    SUBTITLE = 12.5
    DATA_LABEL = 13
    AXIS_LABEL = 12
    HEATMAP_CELL = 12.5
    HEATMAP_HEADER = 12
    HEATMAP_LEGEND = 12  # gradient-strip min/mid/max labels - stays compact, a thin strip has no room for 24pt
    LEGEND = 24  # bar-chart key/legend text - ~2x the old 12pt floor; legends were getting lost at 1/3 scale


# Figure-fraction height of one row of a matplotlib legend at MIN.LEGEND
# size (handlelength=1.6, handleheight=1.6, labelspacing=0.9) on this
# pipeline's fixed canvas - measured empirically (fig.canvas.draw() +
# legend.get_window_extent()), not estimated, because eyeballed constants
# here previously produced a legend that silently overlapped the caption
# below it. Use this to reserve exact room for a legend block:
#
#   legend_height = LEGEND_ROW_HEIGHT * n_rows
#   legend_bottom_y = caption_top + 0.02          # small gap above caption
#   legend_top_y = legend_bottom_y + legend_height
#   ax_bottom = legend_top_y + 0.02               # small gap below the axes
#
# then anchor the legend with loc="upper left", bbox_to_anchor=(left_margin,
# legend_top_y), bbox_transform=fig.transFigure - figure-anchored, not
# axes-anchored, so a long-label legend has the full canvas width to lay
# out in rather than clipping past the narrower axes box's right edge.
LEGEND_ROW_HEIGHT = 0.0403


def draw_caption_bottom(
    fig,
    fonts,
    paragraphs: list[str],
    *,
    left: float = 0.065,
    wrap_width: int = 98,
    fontsize: float = 11.5,
    line_step: float = 0.0165,
    bottom: float = 0.030,
    color: str = MUTED,
    handle: str | None = None,
    handle_color: str | None = None,
) -> float:
    """Draws the caption/footnote block bottom-anchored: the lowest line
    (the handle, if given, else the last wrapped caption line) sits at
    y=bottom, with every line above it stacked upward. This is the opposite
    of the old pattern (a CAPTION_TOP constant, drawn downward) - it means
    whatever vertical space the caption doesn't use belongs to the chart
    above it, instead of a fixed band being reserved regardless of how much
    text is actually in the caption.

    Call this BEFORE laying out the chart's own axes and use the return
    value as `caption_top` in the "vertical layout: centering the plot band"
    contract (scripts/pew-rls/STYLE.md) - i.e. `ax_bottom = caption_top + gap`.
    The return value is the y-fraction just above the top caption line.

    Site-wide caption convention (see BRANDING_AND_DESIGN.md's "Charts"
    section): every chart's footnote is exactly one bold line, "@ithinkisam
    | data: <short source title>" - no DOI/URL, no methodology paragraphs,
    no per-chart population/cutpoint notes. Pass it via `handle=` with
    `paragraphs=[]`; every render script across every dataset does this the
    same way, so the caption block is always exactly one line regardless of
    dataset. `paragraphs`/`wrap_width`/`line_step` remain general-purpose
    (a caller can still stack additional lines above the handle if some
    future need genuinely requires it), but nothing in this codebase does
    today - the single-line handle is the standard, not the exception.
    The `fontsize` default (11.5, up from the pre-2026-08 default of 10) is
    the "slightly larger" bump that came with this convention; still small
    enough to read as fine print, not a second subtitle.

    `paragraphs` are source/methodology lines, wrapped to `wrap_width`
    characters (matplotlib's own figure-level wrap is unreliable across
    versions and doesn't respect a figure's real margins - hence hand
    wrapping here, same as every script did before this helper existed).
    """
    lines = [ln for para in paragraphs for ln in textwrap.wrap(para, width=wrap_width)]

    y = bottom
    if handle:
        fig.text(
            left, y, handle, fontproperties=fonts["bold"], fontsize=fontsize,
            color=handle_color or color, ha="left", va="top",
        )
        y += line_step * 1.4  # a little extra breathing room above the handle

    for line in reversed(lines):
        fig.text(
            left, y, line, fontproperties=fonts["regular"], fontsize=fontsize,
            color=color, ha="left", va="top",
        )
        y += line_step

    return y


_TRAILING_QUALIFIER_RE = re.compile(r"^(.*\S)\s+(\([^()]*\))$")


def split_title_qualifier(title: str) -> tuple[str, str | None]:
    """Splits a trailing parenthetical qualifier - e.g. "Attendance
    frequency, full distribution (Christian only)" -> ("Attendance
    frequency, full distribution", "(Christian only)") - off the end of a
    chart title. Returns (title, None) unchanged if there's no trailing
    "(...)" group.

    Every _draw_title/draw_title in this pipeline uses this so the
    qualifier renders in a visibly smaller size than the primary title
    text instead of being wrapped in as if it were equally important -
    see BRANDING_AND_DESIGN.md's "Charts" section."""
    m = _TRAILING_QUALIFIER_RE.match(title)
    return (m.group(1), m.group(2)) if m else (title, None)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*(max(0, min(255, round(c))) for c in rgb))


# Named semantic anchors for diverging heatmap ramps - reuse the site's own
# tokens rather than inventing new hexes. The green is deliberately
# teal-shifted (not a pure green) so it stays separable from the oxblood red
# under deuteranopia by both hue and lightness, not hue alone.
DIV_NEG_RED = "#7c2d2d"  # --oxblood, the site's decline/negative token
DIV_POS_GREEN = "#1F6E5E"  # teal-shifted green
DIV_COOL_BLUE = "#1f4f7a"  # --accent
DIV_WARM_RED = "#7c2d2d"


def diverging_color(t: float, low_hex: str, high_hex: str, mid_hex: str = PAPER) -> str:
    """t in [0, 1] -> a hex color on a piecewise-linear low -> mid -> high
    ramp (t=0.5 is mid_hex exactly). Use this for every heatmap cell instead
    of a single-hue ramp: the midpoint should be the scale's own substantive
    midpoint (e.g. 50 on a 0-100 scale), not the data's median, so a reader
    can tell which side of "half" a cell sits on at a glance, not just how
    dark it is."""
    t = max(0.0, min(1.0, t))
    low, mid, high = _hex_to_rgb(low_hex), _hex_to_rgb(mid_hex), _hex_to_rgb(high_hex)
    if t <= 0.5:
        frac = t / 0.5
        rgb = tuple(lo + (m - lo) * frac for lo, m in zip(low, mid))
    else:
        frac = (t - 0.5) / 0.5
        rgb = tuple(m + (hi - m) * frac for m, hi in zip(mid, high))
    return _rgb_to_hex(rgb)


def _relative_luminance(hex_color: str) -> float:
    def chan(c: int) -> float:
        c_norm = c / 255
        return c_norm / 12.92 if c_norm <= 0.03928 else ((c_norm + 0.055) / 1.055) ** 2.4

    r, g, b = (chan(c) for c in _hex_to_rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _row_tier(label: str) -> int:
    lower = label.lower()
    total_pop_labels = {
        "u.s. adults", "general population", "total population", "all u.s. adults",
    }
    # Any "All <population>" baseline row (e.g. "All Black Americans", "All
    # attenders") is the same kind of tier-3 aggregate as "All U.S. adults" -
    # a survey-specific population baseline, not a named group of its own.
    if lower in total_pop_labels or "total population" in lower or lower.startswith("all "):
        return 3
    if "average" in lower:
        return 2
    # "Something else" is the same kind of named catch-all as an "Other X"
    # row (tier 1) - it just doesn't start with the word "Other".
    if lower.startswith("other") or lower == "something else":
        return 1
    return 0


def sort_groups(labels: list[str], value_of: Callable[[str], float]) -> list[str]:
    """Site-wide row-order rule for magnitude bar / paired bar / 100%-stacked
    bar / diverging bar charts (see BRANDING_AND_DESIGN.md's "Charts"
    section, which states this rule in plain terms): rows are sorted highest
    to lowest by their own statistic, except three kinds of rows that always
    sink to the bottom regardless of value, in this fixed tier order.

    Tier 0 (normal): sorted by `-value_of(label)`, i.e. descending.
    Tier 1 (named catch-all): any label that starts with "Other" (case-
    insensitive - "Other Christian", "Other religions", "Other world
    religions", "Other faiths"). Sorted by value *within* this tier too -
    it's not a frozen order, just always below every tier-0 row.
    Tier 2 (population average): any label containing "average" (case-
    insensitive - "Christian average", "Religiously affiliated average",
    "All religious average"). Always below tier 1 - a named "Other X" group
    is still a real, if miscellaneous, group of people; an "average" row is
    an aggregate over the whole chart and reads better anchored at the very
    bottom of the substantive rows. Sorted by value within this tier too.
    Tier 3 (total population): a literal total-population row, if a chart
    ever has one - "U.S. adults", "General population", "Total population",
    "All U.S. adults", or any label containing "total population" (case-
    insensitive). Sorted below tier 2, at the very bottom of everything. No
    chart in this dataset has one of these today, but the rule is written to
    be ready when one shows up.

    Returns a new list; `labels` itself is not mutated. Uses Python's stable
    sort, so ties within a tier (equal value_of()) keep their original
    relative order from the input `labels` list - callers that pass a
    curated `GROUP_ORDER`/`group_order` list as the *set* of rows (which
    group keys belong in a chart) can keep doing so; this function only
    changes what order they come out in, not which rows are included.
    """
    return sorted(labels, key=lambda label: (_row_tier(label), -value_of(label)))


# Per-denomination identity palette for the Pew RLS Data Explorer's
# magnitude-bar charts (see BRANDING_AND_DESIGN.md's "Charts" section for
# the full table, the plain-language rule, and the one accepted
# Muslim/Orthodox Christian tradeoff). Every named denomination/religion
# gets its own distinct identity color - the old "Latter-day Saint in
# --accent, everyone else in one gray" convention singled out LDS in a way
# that read as favoritism rather than a deliberate signal. Catholic and
# Protestant reuse colors already locked by the State of Theology charts
# (scripts/state-of-theology-graphics/STYLE.md's Palette section) so the
# same tradition reads as the same color everywhere on the site they
# appear together.
GROUP_COLORS = {
    "Latter-day Saint": "#1f4f7a",  # blue, the site's --accent
    "Catholic": "#8C4A5F",  # wine, matches State of Theology's Roman Catholic
    "Protestant": "#C9721C",  # amber, matches State of Theology's Evangelical
    "Orthodox Christian": "#5B7553",  # moss
    "Jehovah's Witness": "#6B4472",  # plum
    "Muslim": "#6B8C3D",  # olive
    "Hindu": "#9C2B2B",  # crimson
    "Buddhist": "#9C8A1F",  # ochre
    "Jewish": "#7A6BA6",  # periwinkle
    "Religiously unaffiliated": "#6B4A2F",  # umber
    # Added for the flagship-charts/ (one-off Pew dataset) and ryan-burge/
    # pipelines, which break Protestant into three RLS-style sub-traditions
    # that sometimes appear together as separate rows in the same chart
    # (e.g. pew-atp-w117-2022's in-person-attendance chart), so each needs
    # its own hex rather than all three collapsing onto generic Protestant's
    # amber. Kept in the amber family since they're still the same broad
    # tradition as "Protestant" - just distinguishable from each other.
    "Evangelical Protestant": "#D68A2E",
    "Mainline Protestant": "#E8B15E",
    "Historically Black Protestant": "#8B5A2B",
    # Non-religious / non-affiliated identity rows that appear as their own
    # named categories (not lumped into "Religiously unaffiliated") across
    # the ATP wave and ryan-burge charts.
    "Agnostic": "#4A6B7A",  # slate blue-gray
    "Atheist": "#2F4858",  # dark navy-slate
    "Nothing in particular": "#A67B5B",  # clay/tan
    # ryan-burge/'s own two denomination-level rows (VOTER Survey Panel's
    # pid-over-time series tracks specific denominations, not RLS-style
    # traditions), each needing a color distinct from generic Protestant.
    "Southern Baptist": "#7A3B2E",  # brick
    "United Methodist": "#3E5C76",  # navy
}

# Exact-string variants of a canonical GROUP_COLORS label - different Pew
# survey waves (and ryan-burge's own datasets) spell the same group
# differently ("Mormon" vs "Latter-day Saint", "Orthodox" vs "Orthodox
# Christian", "...Churches"/"...Tradition" suffixes on the RLS-style
# Protestant sub-traditions, capitalization drift on "Nothing in
# particular"). Resolved before the GROUP_COLORS lookup in color_for_group
# so every wave's spelling of the same group reads as the same color,
# without duplicating hex values across near-identical dict keys.
GROUP_ALIASES = {
    "Mormon": "Latter-day Saint",
    "Orthodox": "Orthodox Christian",
    "Unaffiliated": "Religiously unaffiliated",
    'Unaffiliated (religious "nones")': "Religiously unaffiliated",
    "Nothing in Particular": "Nothing in particular",
    "Evangelical Protestant Churches": "Evangelical Protestant",
    "Evangelical Protestant Tradition": "Evangelical Protestant",
    "Mainline Protestant Churches": "Mainline Protestant",
    "Mainline Protestant Tradition": "Mainline Protestant",
    "Historically Black Protestant Churches": "Historically Black Protestant",
    "Historically Black Protestant Tradition": "Historically Black Protestant",
}


def color_for_group(label: str) -> str:
    """Bar-fill color for one row of a per-group-identity magnitude bar
    chart. A named denomination/religion in `GROUP_COLORS` gets its own
    locked identity hex (resolving spelling variants via `GROUP_ALIASES`
    first). Everything else isn't a single identity to begin with, so it
    shares a neutral token instead, matching its own sink-to-bottom tier
    from `sort_groups` above: a named catch-all ("Other Christian",
    "Something else", tier 1) gets `CONTEXT_GRAY`; a population-average
    aggregate or total-population row (tiers 2/3) gets `MUTED`.
    See BRANDING_AND_DESIGN.md's "Charts" section for the full palette
    table and the accepted Muslim/Orthodox Christian color-distance
    tradeoff (legal here only because every bar also prints its group name
    and percentage directly on the chart - color is never the only
    encoding)."""
    label = GROUP_ALIASES.get(label, label)
    if label in GROUP_COLORS:
        return GROUP_COLORS[label]
    return CONTEXT_GRAY if _row_tier(label) == 1 else MUTED


def label_ink(bg_hex: str, ink: str = INK, paper: str = PAPER, threshold: float = 0.45) -> str:
    """White or ink label color for text drawn on top of bg_hex, by relative
    luminance. Replaces the old `t > 0.55` heatmap hack, which assumed the
    ramp only got darker at one end - wrong for a diverging ramp, which is
    dark at BOTH the low and high ends and light (white) in the middle."""
    return paper if _relative_luminance(bg_hex) < threshold else ink
