# Pew Research Center — Religious Composition of the World's Migrants, 1990-2020

Pew's global estimate of the religious composition of the world's
international migrant stock (people living outside the country where they
were born), for seven benchmark years (1990, 1995, 2000, 2005, 2010, 2015,
2020), broken out by country, region, and world total, and by direction
(incoming to a destination vs. outgoing from an origin). Built primarily
from 270 censuses and surveys, filled out with Pew's own indirect-estimation
methodology where a country's migrant population lacks a direct religious
breakdown. Published August 19, 2024.

There is no Latter-day Saint/Mormon-specific breakout in this dataset — its
religious categories are the broad ones (Christian, Muslim, Unaffiliated,
Hindu, Buddhist, Jewish, Other).

## What's in here

Raw files live in `data/pew-religion-migration/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `Incoming and Outgoing Migrant Counts.csv` / `.xlsx` | The core dataset: one row per (direction, year, country/region/world, religion), with migrant counts and shares. `level` distinguishes country (1, 232 countries/territories), region (2), and world total (3, labeled "Global Total"). |
| `readme.txt` + `FOTM_Peru_impute.Rmd`/`.pdf`, `a01_dd_demo_Peru_html.txt`, `b01_run_demo_Peru_html.do`, `c01_result3_demo_Peru.html`, `data0X_*.csv`/`.dta`, `result0X_*.csv`/`.dta` | Pew's "Peru case study": a worked Stata/R walkthrough of the indirect-estimation algorithm used to impute religious composition for migrant flows without direct source data. This is a methodology demo, not usable output data on its own, and isn't read by any chart script in this folder. |

## Citation

Kramer, Stephanie, Yunping Tong and Anne Fengyan Shi. 2024. "Religious
Composition of the World's Migrants, 1990-2020." Pew Research Center.
<https://www.pewresearch.org/religion/2024/08/19/religious-composition-of-the-worlds-migrants-1990-2020/>

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-religion-migration`), using the
shared chart shape in `scripts/flagship-charts/common.py`:

- `global-migrant-composition.json` (religious composition of the world's
  ~281 million international migrants in 2020, the world-total rows of the
  migrant-counts CSV) — computed by `global_migrant_composition.py`,
  rendered by `render_global_migrant_composition_chart.py`. Christians are
  the largest group (46.6%) though their share has slipped from a 2005 peak
  of 49.1% as the Muslim share has risen (26.1% in 1990 to 28.7% in 2020);
  the JSON also carries the full 1990-2020 Christian-share time series for
  a follow-up chart.

Further charts from this dataset (e.g. top destination countries for
Christian migrants, using the CSV's country-level `level == 1` rows) should
follow the same two-stage pattern.
