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

One flagship chart shipped: `ordination-by-activity.json` (belief that
women should be ordained to the priesthood, by activity level in the
Church), computed by `scripts/pew-mormon-survey-2011/ordination_by_activity.py`
and rendered by `render_ordination_chart.py` to
`public/data-explorer/pew-mormon-survey-2011/ordination-by-activity.png`,
using the shared chart shape in `scripts/flagship-charts/common.py`. Wired
into the Data Explorer entry (`src/lib/data-explorer.ts`, slug
`pew-mormon-survey-2011`). Further charts from this dataset should follow
the same two-stage pattern.
