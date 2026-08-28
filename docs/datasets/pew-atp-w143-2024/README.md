# Pew Research Center — American Trends Panel, Wave 143 (February 2024)

A general-topic wave of Pew's American Trends Panel, with oversamples of
Jewish and Muslim Americans: 12,693 U.S. adults surveyed online (a small
number by phone via SSRS's CATI omnibus) Feb. 13–25, 2024, in English and
Spanish.

**Note, unlike other ATP waves in this repo:** this wave does **not** carry
the usual `F_RELTRAD` frame variable (checked the .sav's own 140-variable
list directly, not just the readme/questionnaire text — it simply isn't
present). The closest substitute for a by-religion breakout is `F_RELIG`,
this wave's own religious-affiliation variable, which classifies Latter-day
Saints as code `3.0` — labeled `"Mormon (Church of Jesus Christ of
Latter-day Saints or LDS)"` — not the `20000` code F_RELTRAD normally uses.
`F_RELIG`'s categories are individual religions (Protestant, Catholic,
Mormon, Orthodox Christian, Jewish, Muslim, Buddhist, Hindu, Atheist,
Agnostic, Other, Nothing in particular), not F_RELTRAD's coarser
Evangelical/Mainline/Historically Black Protestant tradition buckets — any
future chart from this wave should group by `F_RELIG`, not assume
F_RELTRAD exists.

## What's in here

Raw microdata lives in `data/pew-atp-w143-2024/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `ATP W143.sav` | SPSS microdata, N=12,693 |
| `ATP W143.csv` | Same data, CSV form |
| `ATP W143 Readme.txt` | Pew's own readme, incl. weight variable name and the list of releases this wave fed |
| `ATP W143 Codebook.xlsx` | Variable/value-label codebook |
| `ATP W143 Methodology.pdf` | Sample design, weighting |
| `ATP W143 Questionnaire.pdf` | Full survey instrument |

Weight variable: `WEIGHT_W143`.

This wave fed at least 16 published Pew items between March 2024 and May
2025 (full list in the readme), spanning U.S. religion-and-politics topics
(religion's influence in public life, Christian nationalism, views of
Donald Trump and Joe Biden) and the Israel-Hamas war (a large share of this
wave's own questionnaire). None of those release titles obviously names
`RELIGMINORITY_W143` specifically as their source item, so the chart below
cites the wave itself rather than a specific downstream report — check
Pew's site before citing a specific report title if that becomes important.
The two most likely candidates for this wave's general religion content are
"8 in 10 Americans Say Religion Is Losing Influence in Public Life" (March
15, 2024) and "5 facts about religion and Americans' views of Donald Trump"
(March 15, 2024).

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-atp-w143-2024`), using the shared
chart shape in `scripts/flagship-charts/common.py`:

- `religious-minority.json` (share who consider themselves part of a
  minority group because of their religious beliefs, `RELIGMINORITY_W143`,
  grouped by `F_RELIG` since this wave has no `F_RELTRAD`) — computed by
  `religious_minority.py`, rendered by `render_religious_minority_chart.py`.
  Latter-day Saints (59%) stand out well above every other Christian group
  (Protestants 29%, Catholics 25%, Orthodox Christians 49%) — closer to
  Muslims (57%) and Hindus (56%) than to other Christians, second only to
  Jewish respondents (84%). Groups under 30 valid respondents would be
  omitted (none were, in this wave).

Further charts from this dataset should follow the same two-stage pattern,
grouping by `F_RELIG` rather than assuming `F_RELTRAD`.
