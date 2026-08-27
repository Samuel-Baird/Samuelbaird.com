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

Three charts shipped, all by current religious tradition (reltrad) with
groups under 30 valid respondents omitted (this recontact reached only
5,000 of the main 2014 RLS's 35,071 respondents), wired into the Data
Explorer entry (`src/lib/data-explorer.ts`, slug `pew-rls-2014-recontact`),
using the shared chart shape in `scripts/flagship-charts/common.py`:

- `marriage-shared-beliefs.json` (share saying shared religious beliefs
  are very important for a successful marriage, qd1g) — computed by
  `marriage_shared_beliefs.py`, rendered by
  `render_marriage_shared_beliefs_chart.py`.
- `raised-interfaith.json` (share who think of themselves as raised in
  more than one religion, qb19) — computed by `raised_interfaith.py`,
  rendered by `render_raised_interfaith_chart.py`.
- `spouse-religion-mattered.json` (share of the ever-married saying their
  spouse's religion was very important in deciding to marry them, qd6a) —
  computed by `spouse_religion_mattered.py`, rendered by
  `render_spouse_religion_chart.py`.

Further charts from this dataset should follow the same two-stage pattern.
