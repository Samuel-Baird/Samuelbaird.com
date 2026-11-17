# Worldwide Church membership, 1830-2025

The Data Explorer's second "Mixed Datasets" entry: the full worldwide
Church membership history, year by year, from the Church's 1830 founding
to today. Unlike `us-membership-growth-2000-2025` (which has real gaps
because no single source publishes a complete annual U.S.-only series),
this one has none — worldwide totals are documented for every single
year in one coherent source lineage.

## Source

Wikipedia's [Membership history of the Church of Jesus Christ of
Latter-day Saints](https://en.wikipedia.org/wiki/Membership_history_of_the_Church_of_Jesus_Christ_of_Latter-day_Saints)
article, which sources 1830-2011 to the 2013 Church Almanac and 2012-2025
to the Church's own annual statistical reports. 2025's figure (17,887,212)
was independently cross-checked against the Church's own current
newsroom facts-and-statistics page during this same research session —
it matches exactly.

## What's in here

`membership-by-year.json`: one entry per year, 1830-2025 (196 years, no
gaps), each `{"members": <int>, "status": "reported"}`. Every value was
transcribed directly from the source article's own table — see
`build_data.py`'s `MEMBERSHIP_BY_YEAR` dict, the single source of truth.
Never hand-edit the JSON; edit that dict and regenerate.

**The no-gaps claim was independently audited** (2026-08-27): every year
1830-2025 is present exactly once, no duplicates, no missing years. The
series isn't monotonically increasing either, which is a good sign against
fabrication rather than a data problem — four years show a real decrease:
1839 (following the 1838 Missouri Extermination Order) and 1855-1857 (the
difficult early Utah years, disease and emigration losses). See the
direction chart below, which visualizes exactly this.

## Regenerating

```bash
python scripts/worldwide-membership-history/build_data.py
python scripts/worldwide-membership-history/render_chart.py \
  --out public/data-explorer/worldwide-membership-history/membership-by-year.png
```

Uses the shared `render_timeseries` line-chart shape in
`scripts/flagship-charts/common.py`, with sparser x-axis ticks
(`x_tick_step=25`) and no per-year marker dot (`show_markers=False`) — 196
points is dense enough that a dot every year is visual noise, not signal.

## Second chart: colored by direction

`render_direction_chart.py` renders the same series a different way — no
new data file, just `render_timeseries_by_direction` from
`scripts/flagship-charts/common.py` coloring each segment blue (grew from
the prior year) or red (shrank), with red markers bracketing every
decrease so the four found above are easy to spot even at this chart's
1830-2025 scale (they're a tiny fraction of the y-axis range).

```bash
python scripts/worldwide-membership-history/render_direction_chart.py \
  --out public/data-explorer/worldwide-membership-history/membership-by-direction.png
```
