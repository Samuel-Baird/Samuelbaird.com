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

Landed, not yet analyzed. No JSON aggregates or charts have been built from
this dataset — see the Data Explorer entry (`src/lib/data-explorer.ts`,
slug `pew-latin-america-2014`), which currently ships with `graphics: []`.
Follow the two-stage pattern in `scripts/pew-rls/` (analysis script reads
the `.sav`, writes a weighted-aggregate JSON here; a render script turns
that JSON into a PNG under `public/data-explorer/pew-latin-america-2014/`)
when picking this up.
