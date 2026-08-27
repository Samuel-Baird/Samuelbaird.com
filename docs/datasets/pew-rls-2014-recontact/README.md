# Pew Research Center — 2014 Religious Landscape Study, Recontact Survey

A 2015 follow-up survey of 5,000 respondents drawn from the main 2014
Religious Landscape Study (see `data/pew-rls-2014/`), fielded March 17–May
6, 2015. Respondents were sorted into 15 strata by religious/demographic
characteristics (oversampling groups like the religiously intermarried)
and reweighted afterward to restore proper proportions. Shares respondent
IDs (`RESP`) and key variables (`RELTRAD`, `CHRELTRAD`, `CREGION`) with the
main 2014 file, so the two can be merged. Underlies the report "One-in-Five
U.S. Adults Were Raised in Interfaith Homes."

## Recommended citation

> Pew Research Center. 2016. "One-in-Five U.S. Adults Were Raised in
> Interfaith Homes."

- Report: <https://www.pewresearch.org/religion/2016/10/26/one-in-five-u-s-adults-were-raised-in-interfaith-homes/>

## What's in here

Raw microdata lives in `data/pew-rls-2014-recontact/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `RLS II recontact public release.sav` | SPSS microdata, N=5,000 |
| `public release codebook-Oct2022.pdf` | Every variable/value label, incl. which are pulled from the main 2014 file |

## Status

One flagship chart shipped: `marriage-shared-beliefs.json` (share saying
shared religious beliefs are very important for a successful marriage, by
tradition), computed by
`scripts/pew-rls-2014-recontact/marriage_shared_beliefs.py` and rendered by
`render_marriage_shared_beliefs_chart.py` to
`public/data-explorer/pew-rls-2014-recontact/marriage-shared-beliefs.png`,
using the shared chart shape in `scripts/flagship-charts/common.py`. Wired
into the Data Explorer entry (`src/lib/data-explorer.ts`, slug
`pew-rls-2014-recontact`). Further charts from this dataset should follow
the same two-stage pattern.
