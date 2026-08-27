# Pew Research Center — Faith in Flux (2008 Conversion Recontact Survey)

A follow-up to the 2007 U.S. Religious Landscape Survey (`data/pew-rls-2007/`),
which found that 28% of American adults had changed religious tradition
since childhood (44% including moves within a tradition). This 2008
recontact survey re-interviewed 2,867 of those respondents by phone between
Oct. 3 and Nov. 7, 2008, asking specifically why they left, why they
joined, and how they feel about the change — the reasons behind religious
switching, not just its incidence.

## Recommended citation

> Pew Research Center. 2009. "Faith in Flux: Changes in Religious
> Affiliation in the U.S."

- Report: <https://www.pewresearch.org/religion/2009/04/27/faith-in-flux/>

## What's in here

Raw microdata lives in `data/pew-faith-in-flux-2008/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `Dataset - ... 2008 Conversion Recontact Survey.sav` | SPSS microdata, N=2,867 |
| `Codebook - ... 2008 Conversion Recontact Survey.doc` | Every variable/value label |
| `Questionnaire - ... .doc` | Full survey instrument |
| `Topline Survey Results - ... .pdf` | Weighted toplines for every question |

## Status

One flagship chart shipped: `reasons-joined-lds.json` (why the survey's 38
converts to Mormonism say they joined), computed by
`scripts/pew-faith-in-flux-2008/reasons_joined_lds.py` and rendered by
`render_reasons_joined_lds_chart.py` to
`public/data-explorer/pew-faith-in-flux-2008/reasons-joined-lds.png`, using
the shared chart shape in `scripts/flagship-charts/common.py` (with a
wider `axes_left` margin, since its row labels are full survey-item
phrases rather than short group names). Wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-faith-in-flux-2008`). Further charts
from this dataset should follow the same two-stage pattern.
