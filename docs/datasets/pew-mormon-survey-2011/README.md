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

Two charts shipped, both wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-mormon-survey-2011`):

- `ordination-by-activity.json` (belief that women should be ordained to
  the priesthood, by activity level in the Church) — computed by
  `scripts/pew-mormon-survey-2011/ordination_by_activity.py`, rendered by
  `render_ordination_chart.py` using the shared magnitude-bar shape in
  `scripts/flagship-charts/common.py`.
- `mormonism-christian.json` ("Is Mormonism a Christian religion?", q442,
  Mormons vs. the U.S. general public) — computed by
  `scripts/pew-mormon-survey-2011/mormonism_christian.py`, rendered by
  `render_mormonism_christian_chart.py` using the shared 100%-stack shape
  (`render_100_stack`) in the same common module. The "U.S. general
  public" row is Pew's own published comparison number from a separate
  November 2011 survey of non-Mormons this site doesn't hold microdata
  for — copied verbatim with its own source note in the analysis script,
  not computed here; see that script's docstring before reusing the
  pattern elsewhere.

Further charts from this dataset should follow the same two-stage pattern.
