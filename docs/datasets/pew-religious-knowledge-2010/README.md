# Pew Research Center — 2010 U.S. Religious Knowledge Survey

A 32-question religious-knowledge quiz fielded May 19–June 6, 2010 among
3,412 U.S. adults by landline and cell phone, with oversamples of Jewish,
Mormon, and atheist/agnostic respondents (recontacted from earlier surveys
that had identified them as belonging to those groups). One of the few Pew
datasets of this era with a usable standalone Mormon subsample on a
knowledge — rather than belief or practice — battery.

## Recommended citation

> Pew Research Center. 2010. "U.S. Religious Knowledge Survey."

- Report: <https://www.pewresearch.org/religion/2010/09/28/u-s-religious-knowledge-survey/>

## What's in here

Raw microdata lives in `data/pew-religious-knowledge-2010/` (gitignored,
not committed):

| File | What it is |
| --- | --- |
| `Dataset - ... 2010 US Religious Knowledge Survey.sav` | SPSS microdata, N=3,412 |
| `Codebook - ... 2010 US Religious Knowledge Survey.docx` | Every variable/value label |
| `Questionnaire - ... .pdf` | Full survey instrument |
| `Answers to Knowledge Questions - ... .pdf` | Correct answers for each quiz item |
| `Topline Survey Results - ... .pdf` | Weighted toplines for every question |

## Status

Landed, not yet analyzed. No JSON aggregates or charts have been built from
this dataset — see the Data Explorer entry (`src/lib/data-explorer.ts`,
slug `pew-religious-knowledge-2010`), which currently ships with
`graphics: []`. Follow the two-stage pattern in `scripts/pew-rls/`
(analysis script reads the `.sav`, writes a weighted-aggregate JSON here; a
render script turns that JSON into a PNG under
`public/data-explorer/pew-religious-knowledge-2010/`) when picking this up.
