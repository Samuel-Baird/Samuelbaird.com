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

## Regenerating

Each dataset's own `scripts/<slug>/render_*.py` script is a thin CLI wrapper
around one of this module's functions - see that script's own docstring for
its exact `--out` usage. There's no single command that regenerates every
flagship chart at once; regenerate the specific dataset(s) you changed.
