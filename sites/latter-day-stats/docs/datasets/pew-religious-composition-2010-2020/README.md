# Pew Research Center — How the Global Religious Landscape Changed From 2010 to 2020

Country-level population estimates for seven broad religious categories
(Christians, Muslims, Hindus, Buddhists, Jews, Other religions, and the
religiously unaffiliated), for 2010 and 2020, across 201 countries and
territories that each had at least 100,000 people in one of those two
years — collectively 99.98% of the world's population. Compiled from more
than 2,700 sources (national censuses, large-scale demographic surveys,
general population surveys, and population registers), not a single
Pew-fielded survey; country population totals come from the UN's 2024
World Population Prospects revision.

There is no Latter-day Saint/Mormon-specific breakout in this dataset — LDS
people are folded into the broad "Christians" category along with every
other Christian tradition. This dataset's natural angle for this site is
therefore Christianity at the global/country level, not an LDS-specific
one — e.g. where the Christian share of population changed the most, or how
the worldwide Christian population total moved, over the decade.

The dataset was updated Feb. 12, 2026 to add a Religious Diversity Index
(RDI) score, diversity level, and diversity rank per country/territory,
introduced alongside Pew's companion report "Religious Diversity Around the
World" (Feb. 12, 2026).

## What's in here

Raw data lives in `data/pew-religious-composition-2010-2020/` (gitignored,
not committed):

| File | What it is |
| --- | --- |
| `Religious Composition 2010-2020.xlsx` | Excel workbook, all four worksheets |
| `Religious Composition 2010-2020 (rounded counts).csv` | Population counts, rounded (Pew's recommended worksheet for reporting counts) |
| `Religious Composition 2010-2020 (unrounded counts).csv` | Population counts, unrounded ("should be used with caution," per Pew's own README — appropriate for regression analyses) |
| `Religious Composition 2010-2020 (percentages).csv` | Each category's share of population |
| `Religious Composition 2010-2020 (diversity statistics).csv` | RDI score, diversity level, and diversity rank per country/territory (added Feb. 2026) |
| `README.txt` | Pew's own readme |

Each of the four data CSVs carries a `Level` column: `1` = an individual
country/territory row (201 of them, one row per year), `2` = one of Pew's
six regional rollups, `3` = the "All World" total. `Countrycode` is Pew's
own numeric identifier, not ISO.

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-religious-composition-2010-2020`),
using the shared chart shape in `scripts/flagship-charts/common.py`:

- `christian-share-decline.json` (the ten countries/territories where the
  Christian share of population fell the most, 2010–2020, from the
  "percentages" worksheet's Level-1 rows) — computed by
  `christian_share_decline.py`, rendered by
  `render_christian_share_decline_chart.py`. Every one of the ten is a
  wealthy, secularizing country (Australia, Chile, Uruguay, the U.S.,
  Canada, the UK, Austria, Sweden, Switzerland, Ireland); worldwide, the
  raw Christian population count grew over the decade (2.15B → 2.27B,
  rounded counts, "All World" row) but slipped as a *share* of world
  population (30.6% → 28.8%) because global population grew faster.

Further charts from this dataset should follow the same two-stage pattern
(a `scripts/pew-religious-composition-2010-2020/*.py` analysis script
writing JSON to `docs/datasets/pew-religious-composition-2010-2020/`, then
a paired `render_*_chart.py`). Untapped angles in the remaining worksheets:
the fastest-*growing* Christian shares (small in magnitude compared to the
declines above — the biggest gain in the dataset is Mozambique at +5.0pp),
the unaffiliated ("nones") share by country, and the Religious Diversity
Index rankings.
