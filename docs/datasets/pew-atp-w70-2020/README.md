# Pew Research Center — American Trends Panel, Wave 70 (July 2020)

A general-topic wave of Pew's American Trends Panel: 10,211 U.S. adults
surveyed online (a small non-internet subsample by mail) July 13–19, 2020,
in English and Spanish. Like other ATP waves, it carries a `F_RELTRAD`
frame variable classifying each respondent's religious tradition
(Latter-day Saints coded `20000`), which is what makes an otherwise
general-topic wave usable for breaking its substantive questions out by
religion.

## What's in here

Raw microdata lives in `data/pew-atp-w70-2020/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `ATP W70.sav` | SPSS microdata, N=10,211 |
| `ATP 70 readme.txt` | Pew's own readme, incl. the `F_RELTRAD` value labels |
| `ATP W70 methodology.pdf` | Sample design, weighting |
| `ATP W70 questionnaire.pdf` | Full survey instrument |
| `ATP W70 topline.pdf` | Weighted toplines for every question |

Note: this dataset arrived without a "topic report" citation — check the
questionnaire before analyzing to identify which Pew report(s) this wave
fed, and cite that report specifically rather than the wave in the
abstract.

## Status

Landed, not yet analyzed. No JSON aggregates or charts have been built from
this dataset — see the Data Explorer entry (`src/lib/data-explorer.ts`,
slug `pew-atp-w70-2020`), which currently ships with `graphics: []`. Follow
the two-stage pattern in `scripts/pew-rls/` (analysis script reads the
`.sav`, writes a weighted-aggregate JSON here; a render script turns that
JSON into a PNG under `public/data-explorer/pew-atp-w70-2020/`) when
picking this up.
