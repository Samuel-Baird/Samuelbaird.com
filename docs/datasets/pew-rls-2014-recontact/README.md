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

Landed, not yet analyzed. No JSON aggregates or charts have been built from
this dataset — see the Data Explorer entry (`src/lib/data-explorer.ts`,
slug `pew-rls-2014-recontact`), which currently ships with `graphics: []`.
Follow the two-stage pattern in `scripts/pew-rls/` (analysis script reads
the `.sav`, writes a weighted-aggregate JSON here; a render script turns
that JSON into a PNG under
`public/data-explorer/pew-rls-2014-recontact/`) when picking this up.
