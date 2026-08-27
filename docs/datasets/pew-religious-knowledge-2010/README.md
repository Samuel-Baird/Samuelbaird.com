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

One flagship chart shipped: `mormon-founding-knowledge.json` (share
correctly saying the Mormon religion was founded after 1800, by the
respondent's own religion), computed by
`scripts/pew-religious-knowledge-2010/mormon_founding_knowledge.py` and
rendered by `render_mormon_founding_chart.py` to
`public/data-explorer/pew-religious-knowledge-2010/mormon-founding-knowledge.png`,
using the shared chart shape in `scripts/flagship-charts/common.py`. Wired
into the Data Explorer entry (`src/lib/data-explorer.ts`, slug
`pew-religious-knowledge-2010`). Further charts from this dataset should
follow the same two-stage pattern.
