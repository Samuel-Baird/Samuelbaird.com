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

Five charts shipped, all wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-religious-knowledge-2010`), using
the shared magnitude-bar shape in `scripts/flagship-charts/common.py`:

By respondent's own present religion (qn20), groups under 30 valid
respondents omitted:
- `mormon-founding-knowledge.json` (share correctly saying the Mormon
  religion was founded after 1800, qn42) — computed by
  `mormon_founding_knowledge.py`, rendered by
  `render_mormon_founding_chart.py`.
- `joseph-smith-knowledge.json` (share correctly identifying Joseph
  Smith's religion as Mormon, qn48c) — computed by
  `joseph_smith_knowledge.py`, rendered by `render_joseph_smith_chart.py`.
- `book-of-mormon-knowledge.json` (share correctly saying the Book of
  Mormon places Jesus's post-resurrection appearance in the Americas,
  qn43) — computed by `book_of_mormon_knowledge.py`, rendered by
  `render_book_of_mormon_chart.py`.
- `jesus-birthplace-knowledge.json` (share correctly saying Bethlehem,
  qn41) — computed by `jesus_birthplace_knowledge.py`, rendered by
  `render_jesus_birthplace_chart.py`.

Single-population ranking across all U.S. adults:
- `church-state-law.json` ("What can public school teachers do?", qn50a/
  b/c) — computed by `church_state_law.py`, rendered by
  `render_church_state_chart.py`.

Further charts from this dataset should follow the same two-stage pattern.
