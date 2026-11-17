# Pew Research Center — 2015 Survey of U.S. Catholics and Family Life

A nationally representative Pew telephone survey (landline and cellphone) of
5,122 U.S. adults 18+, fielded May 5–June 7, 2015, in English and Spanish —
of any religion, not Catholics only, but with a large enough Catholic
subsample (1,016 respondents, Catholic by religion) to analyze Catholic
opinion on its own. It underlies two 2015 Pew reports, "Catholics Divided
Over Global Warming" and "U.S. Catholics Open to Non-Traditional Families."
No Latter-day Saint/Mormon-specific breakout: RELIG has a Mormon code (3),
but the sample (n=88 self-identified Mormons, unweighted) is far too small
for a standalone LDS estimate, and the survey's Catholic-focused questions
(confession, annulment, the pope, etc.) weren't asked of non-Catholics
anyway.

## What's in here

Raw microdata lives in `data/pew-catholic-family-2015/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `Dataset - ... Version 1.1 - Mar 1, 2018.sav` | SPSS microdata, N=5,122 |
| `Codebook - ... Version 1.1 - Mar 1, 2018.pdf` | Pew's own codebook: question wording, response codes, weighting, sample-size/MOE table |

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-catholic-family-2015`), using the
shared chart shape in `scripts/flagship-charts/common.py`:

- `annulment-communion.json` (share of Catholics saying the Church should
  let divorced Catholics who remarry without an annulment receive
  Communion, Q.J31e/`qj31e`, restricted to `relig==2` and broken out by
  Mass-attendance frequency) — computed by `annulment_communion.py`,
  rendered by `render_annulment_communion_chart.py`.

Further charts from this dataset (e.g. confession frequency `qk5`,
Communion frequency `qk12`, or the other Q.J31 "should the Church allow..."
items — priests marrying, women priests, birth control, gay marriage,
cohabiting Catholics receiving Communion) should follow the same two-stage
pattern: an analysis script in `scripts/pew-catholic-family-2015/` reading
the .sav and writing a JSON aggregate to
`docs/datasets/pew-catholic-family-2015/`, rendered by a
`render_*_chart.py` using `scripts/flagship-charts/common.py`.
