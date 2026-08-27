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

Landed, not yet analyzed. No JSON aggregates or charts have been built from
this dataset — see the Data Explorer entry (`src/lib/data-explorer.ts`,
slug `pew-faith-in-flux-2008`), which currently ships with `graphics: []`.
Follow the two-stage pattern in `scripts/pew-rls/` (analysis script reads
the `.sav`, writes a weighted-aggregate JSON here; a render script turns
that JSON into a PNG under `public/data-explorer/pew-faith-in-flux-2008/`)
when picking this up.
