# Pew Research Center — 2011 National Survey of Mormons

A survey of 1,019 self-identified Mormon adults, fielded Oct. 25–Nov. 16,
2011 by SSRS (landline and cell, English and Spanish), oversampling
high-Mormon-density counties and recontacting self-identified Mormons from
earlier Pew/SSRS surveys. Unlike most Pew religion surveys, this one asks
Mormons about their own beliefs, practices, and sense of acceptance rather
than asking the general public about Mormons.

## Recommended citation

> Pew Research Center. 2012. "2011 National Survey of Mormons."

- Report: <https://www.pewresearch.org/religion/2012/01/12/mormons-in-america-executive-summary/>

## What's in here

Raw microdata lives in `data/pew-mormon-survey-2011/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `Dataset - ... 2011 National Survey of Mormons.sav` | SPSS microdata, N=1,019 |
| `Codebook - ... 2011 National Survey of Mormons.pdf` | Background, sample design, and every variable/value label |

## Status

Landed, not yet analyzed. No JSON aggregates or charts have been built from
this dataset — see the Data Explorer entry (`src/lib/data-explorer.ts`,
slug `pew-mormon-survey-2011`), which currently ships with `graphics: []`.
Follow the two-stage pattern in `scripts/pew-rls/` (analysis script reads
the `.sav`, writes a weighted-aggregate JSON here; a render script turns
that JSON into a PNG under `public/data-explorer/pew-mormon-survey-2011/`)
when picking this up.
