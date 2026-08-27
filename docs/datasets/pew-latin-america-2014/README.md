# Pew Research Center — Religion in Latin America

More than 30,000 face-to-face interviews with non-institutionalized adults
across 18 Latin American and Caribbean countries plus Puerto Rico, fielded
Oct. 2013–Feb. 2014 under the Pew-Templeton Global Religious Futures
project. Fielded by Princeton Survey Research Associates International
(Costa Rica, El Salvador, Guatemala, Honduras, Mexico, Nicaragua, Panama)
and Ipsos Public Affairs (the remaining 12 countries/territories). Covers
religious affiliation, belief, practice, and social/political views.
Latter-day Saints are a small share of most national samples here, but the
dataset is large enough to compare the region's Catholic-to-Protestant
shift against how much smaller traditions like LDS appear by comparison.

## Recommended citation

> Pew Research Center. 2014. "Religion in Latin America: Widespread Change
> in a Historically Catholic Region."

- Report: <https://www.pewresearch.org/religion/2014/11/13/religion-in-latin-america/>

## What's in here

Raw microdata lives in `data/pew-latin-america-2014/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `Religion in Latin America Dataset.sav` | SPSS microdata, 19 countries/territories |
| `Religion in Latin America Codebook.docx` | Sample design per country, every variable/value label |

## Status

One flagship chart shipped: `mormons-as-christian.json` (share across
Latin America who consider Mormons to be followers of the Christian
faith, by their own religion), computed by
`scripts/pew-latin-america-2014/mormons_as_christian.py` and rendered by
`render_mormons_as_christian_chart.py` to
`public/data-explorer/pew-latin-america-2014/mormons-as-christian.png`,
using the shared chart shape in `scripts/flagship-charts/common.py`. Wired
into the Data Explorer entry (`src/lib/data-explorer.ts`, slug
`pew-latin-america-2014`). Further charts from this dataset should follow
the same two-stage pattern.
