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

import textwrap
from typing import Callable

INK = "#1A1A1A"
PAPER = "#FFFFFF"
MUTED = "#6E6A63"
BORDER = "#D9D5CC"

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
    fontsize: float = 10,
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
    if lower in total_pop_labels or "total population" in lower:
        return 3
    if "average" in lower:
        return 2
    if lower.startswith("other"):
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


def label_ink(bg_hex: str, ink: str = INK, paper: str = PAPER, threshold: float = 0.45) -> str:
    """White or ink label color for text drawn on top of bg_hex, by relative
    luminance. Replaces the old `t > 0.55` heatmap hack, which assumed the
    ramp only got darker at one end - wrong for a diverging ramp, which is
    dark at BOTH the low and high ends and light (white) in the middle."""
    return paper if _relative_luminance(bg_hex) < threshold else ink
