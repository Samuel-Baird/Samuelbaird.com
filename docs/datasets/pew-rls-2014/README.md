# Pew Research Center — 2014 Religious Landscape Study

The middle wave of the Religious Landscape Study, between the 2007
original and 2023-24 wave already in `data/pew-rls-2023-24/`: 35,071 U.S.
adults interviewed by telephone (60% cell, 40% landline) June 4–Sept. 30,
2014, in English and Spanish, with a minimum of 300 interviews in every
state and D.C. This is the source of the widely cited "America's Changing
Religious Landscape" report.

## Recommended citation

> Pew Research Center. 2015. "2014 Religious Landscape Study."

- Study page: <https://www.pewresearch.org/religious-landscape-study/2014/>

## What's in here

Raw microdata lives in `data/pew-rls-2014/` (gitignored, not committed):

| File | What it is |
| --- | --- |
| `Dataset - ... 2014 Religious Landscape Study ... .sav` | SPSS microdata, N=35,071 |
| `Codebook - ... 2014 Religious Landscape Study ... .pdf` | Version 1.1 codebook, every variable/value label |

The `data/pew-rls-2014-recontact/` folder holds a related but separate
2015 recontact of 5,000 of these respondents — see its own README.

## Status

Landed, not yet analyzed. No JSON aggregates or charts have been built from
this dataset — see the Data Explorer entry (`src/lib/data-explorer.ts`,
slug `pew-rls-2014`), which currently ships with `graphics: []`. The most
natural first use is a three-point trendline against `pew-rls-2007` and
`pew-rls-2023-24` on a question all three waves share. Follow the
two-stage pattern in `scripts/pew-rls/` (analysis script reads the `.sav`,
writes a weighted-aggregate JSON here; a render script turns that JSON
into a PNG under `public/data-explorer/pew-rls-2014/`) when picking this up.
