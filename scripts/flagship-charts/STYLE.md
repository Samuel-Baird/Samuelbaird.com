# Flagship-charts house style

`scripts/flagship-charts/common.py` is the shared render module for every
one-off Pew dataset registered in the Data Explorer that doesn't warrant its
own duplicated `render_magnitude_bar` (unlike `scripts/pew-rls/` or
`scripts/ryan-burge/`, which accumulate many charts per dataset family and so
duplicate their own copy - see those folders' `STYLE.md`). Read
`common.py`'s own module docstring first - it documents every chart shape
this file provides (`render_magnitude_bar`, `render_100_stack`,
`render_timeseries`, `render_range_projection`,
`render_timeseries_by_direction`, `render_dumbbell_log`) and why each needed
its own function rather than a mode flag on an existing one.

This file only documents what's specific to this module; canvas size, fonts,
caption convention, mobile font floors, and the row-order rule are all
defined once in `scripts/chart_style.py` and `scripts/state-of-theology-graphics/STYLE.md`
- don't redefine them here.

## Group-identity vs. subject-highlight coloring

`render_magnitude_bar` has two coloring modes, chosen by the caller:

- **`group_identity=True`** (the default for any chart comparing named
  religious groups): every row gets its own locked identity color via
  `chart_style.color_for_group`. This is the site-wide rule - see
  `BRANDING_AND_DESIGN.md`'s "Charts" section for the full palette and why
  no chart singles out Latter-day Saint in `--accent` against every other
  group grayed out. Pass `highlight_rows=None` alongside it.
- **`highlight_rows={...}`** (default, `group_identity=False`): a binary
  highlight - the named row(s) in `--accent`, everything else in
  `CONTEXT_GRAY`. This remains legitimate for a chart whose subject is a
  specific country, time period, or tracked category rather than a
  religious identity (e.g. highlighting `"United States"` among a list of
  countries, or `"Now"` among a set of life-stage time periods) - that's
  drawing attention to what the chart is actually about, not the
  highlight-vs-gray pattern the group-identity rule targets. Don't convert
  one of these to `group_identity=True` just because the shape looks the
  same; check whether the highlighted row actually names a religious group
  before deciding.

In both modes, the y-axis tick label itself is always plain ink - never
colored to match its bar - per the universal row-label rule in
`BRANDING_AND_DESIGN.md`'s "Charts" section. This applies regardless of
which coloring mode a chart uses.

## `render_dumbbell_log`'s accent/oxblood coloring is a different encoding

`render_dumbbell_log` (used by `ten-largest-us-churches-2035`) colors each
denomination's connecting line by growth direction - `--accent` for
growing, `--oxblood` for declining - not by religious identity. This isn't
the highlight-vs-gray pattern and doesn't use `color_for_group`; leave it
as-is.

## Bigger row labels and black outlines are now pipeline defaults

As of 2026-08-31, this module rolls out the same two readability
treatments `scripts/pew-rls/` and `scripts/ryan-burge/` made their
defaults the same day (see `scripts/pew-rls/STYLE.md`'s "Bigger row
labels and black outlines are now pipeline defaults" section for the full
background and rationale):

- **Group/axis (row) labels at `MIN.LEGEND` (24pt)** instead of the old
  smaller floor (`MIN.AXIS_LABEL`/12pt for `n_rows > 8`, or a hardcoded
  14pt/16pt/13.5pt below that threshold or in a different shape).
- **Black (`INK`) bar/segment and legend-swatch outlines** instead of the
  old default (`PAPER`/white, invisible where a segment touches a chart's
  outer edge or another segment).

Function by function:

- `render_magnitude_bar` - row-label (y-tick) fontsize is now
  unconditionally `MIN.LEGEND`, dropping the old `n_rows > 8 ? MIN.AXIS_LABEL
  : 14` branch. This shape's bars have no edge (a single bar per row never
  touches a neighbor), so no edge color to change.
- `render_100_stack` - row-label fontsize changed from a hardcoded 16pt to
  `MIN.LEGEND`; its stacked-segment `edgecolor` and legend-swatch
  `edgecolor` both changed from `PAPER` to `INK`.
- `render_dumbbell_log` - row-label fontsize changed from a hardcoded
  13.5pt to `MIN.LEGEND`. Its dot/triangle markers already color
  `markeredgecolor` to match their own `markerfacecolor` (gray dot,
  accent/oxblood triangle) - that's a different, intentional device (no
  visible ring), not the invisible-white-edge problem this rollout
  targets, so left unchanged.
- `render_timeseries`, `render_range_projection`,
  `render_timeseries_by_direction` - unchanged; see "Line charts are
  exempt" below.

### Line charts are exempt

`render_timeseries`, `render_range_projection`, and
`render_timeseries_by_direction` have no group/axis row label in the
bar-chart sense - their y-axis ticks are a numeric scale (a membership
count), not one label per group, so they correctly keep `MIN.AXIS_LABEL`.
Same reasoning as `scripts/ryan-burge/STYLE.md`'s "Line charts are
exempt". Their point markers already set `markeredgecolor` to match each
point's own fill color (status- or direction-coded) rather than `PAPER`,
so there was no invisible-white-edge problem to fix there either.

### `render_magnitude_bar`'s auto-widening left margin

Unlike `pew-rls/render_family_household_charts.render_magnitude_bar` and
`ryan-burge/render_voter_ideas_longitudinal.render_paired_bar`, which each
needed a one-off `axes_left` bump on one or two call sites, this module's
`render_magnitude_bar` is called by ~55 datasets whose row labels range
from a single word ("Mormon") to full RELTRAD tradition names
("Historically Black Protestant Churches") - often in the *same* chart.
An automated edge-pixel scan after the `MIN.LEGEND` bump (dark pixels
touching the canvas's left border) flagged 27 of the pipeline's 63
regenerated PNGs as clipped at the old fixed `axes_left` default - clearly
pipeline-wide crowding, not an isolated chart or two, so per this
pipeline's own "prefer a shared fix over per-caller overrides unless only
one or two callers are affected" rule, `render_magnitude_bar` gained
auto-widening logic instead of 27 individual `axes_left=` call-site edits:
after setting the row-label fontsize, it draws the figure once, measures
the actual rendered pixel width of the widest y-tick label via
matplotlib's renderer (not a character count - the bold condensed font
isn't monospace), and repositions the axes to whatever `axes_left` that
label needs, floored at (never narrower than) the function's own
`axes_left` parameter. A chart whose labels already fit inside the
default keeps the default; only the ones that don't get widened, and each
by exactly as much as its own longest label requires. Re-scanned all 63
regenerated PNGs after this change: 0 flagged.

## Regenerating

Each dataset's own `scripts/<slug>/render_*.py` script is a thin CLI wrapper
around one of this module's functions - see that script's own docstring for
its exact `--out` usage. There's no single command that regenerates every
flagship chart at once; regenerate the specific dataset(s) you changed.
