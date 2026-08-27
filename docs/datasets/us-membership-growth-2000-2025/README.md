# U.S. Church membership, 2000-2025 (compiled timeline)

The Data Explorer's first "mixed data" entry: not one survey's microdata,
but a year-by-year U.S. membership timeline for The Church of Jesus Christ
of Latter-day Saints, compiled from several separately-cited sources
because no single source publishes a complete annual U.S.-only series.

## What's in here

`membership-by-year.json` has one entry per year, 2000-2025, each with its
own `status` and `source`:

| Status | Meaning |
| --- | --- |
| `reported` | An exact Church-reported (or Church-published round-estimate) figure |
| `rounded` | A real reported figure, but only known to the nearest 10,000 |
| `interpolated` | No source found for that year; linearly interpolated between its nearest real neighbors |

### Sources, by year

- **2000** (5,208,827) and **2010** (6,144,582): the U.S. Religion Census
  (Association of Statisticians of American Religious Bodies), a decennial
  survey the Church self-reports its membership to.
- **2002, 2004, 2006, 2008** (rounded to the nearest 10,000): Deseret News
  Church Almanac figures, as compiled by [cumorah.com's LDS Church growth
  archive](https://www.cumorah.com/countries/viewReports/58/United%20States) —
  the print-only Almanac itself isn't text-searchable online, so these are
  taken from a secondary compilation rather than the original.
- **2009** (6,058,907): Deseret News 2011 Church Almanac, as compiled by
  [rickety.us](https://www.rickety.us/2010/12/united-states-lds-church-membership-statistics/).
- **2012-2025**: the Church's own newsroom country page
  (<https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/united-states>),
  as compiled in Wikipedia's [United States membership statistics (LDS
  Church)](https://en.wikipedia.org/wiki/United_States_membership_statistics_(LDS_Church))
  table — 2025's figure (6,929,770) matches the Church's own reported
  membership as of Oct. 13, 2025.
- **2001, 2003, 2005, 2007, 2011**: no U.S.-only total was found in any
  source checked. The Church's annual General Conference statistical
  report only gives *worldwide* totals for this era; the print Deseret
  News Church Almanac likely has these figures but isn't accessible as
  searchable text. These five years are linearly interpolated between
  their nearest real neighbors and marked `"status": "interpolated"` — if
  the real figures for these years are ever found, replace the
  interpolated entries in `build_data.py` with cited ones.

## Regenerating

```bash
python scripts/us-membership-growth-2000-2025/build_data.py
python scripts/us-membership-growth-2000-2025/render_chart.py \
  --out public/data-explorer/us-membership-growth-2000-2025/membership-by-year.png
```

`build_data.py` is the single source of truth for every number and its
citation — never hand-edit `membership-by-year.json`. The render script
uses the shared `render_timeseries` line-chart shape in
`scripts/flagship-charts/common.py` (solid line/filled markers for real
figures, dashed/hollow for interpolated years).
