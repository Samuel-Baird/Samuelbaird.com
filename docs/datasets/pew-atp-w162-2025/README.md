# Pew Research Center — American Trends Panel, Wave 162 (February 2025)

A Pew American Trends Panel wave focused mainly on Catholicism (fielded
around Pope Francis's final months and the run-up to his death in April
2025), plus a handful of general religion and civic-trust items: 9,544 U.S.
adults surveyed online and by phone (CATI) February 3–9, 2025, in English
and Spanish.

**Unlike other ATP waves already in this pipeline (see
`pew-atp-w70-2020`), Wave 162 does not carry an `F_RELTRAD` frame
variable.** Checked by listing all 131 columns in the .sav directly — no
`F_RELTRAD`-shaped variable exists in this wave. This wave's own
religion-classification variables (`RELIGCAT1_W162`, 4-category;
`RELIGCAT2_W162`, 12-category) were purpose-built for the Catholicism
focus and don't have their own Mormon/Jewish/Muslim/etc. codes — all fall
into "Other." The variable that does separate out Latter-day Saints is
`RELIG_W162` ("What is your present religion, if any?"), where code `3.0`
is labeled `"Mormon (Church of Jesus Christ of Latter-day Saints or
LDS)"`. This dataset's one chart groups by `RELIG_W162` instead.

## What's in here

Raw microdata lives in `data/pew-atp-w162-2025/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `ATP W162.sav` | SPSS microdata, N=9,544 |
| `ATP W162.csv` | Same data, CSV |
| `ATP W162 Codebook.xlsx` | Full variable/value-label codebook |
| `ATP W162 Readme.txt` | Pew's own readme — weight variable, backcoding notes, list of reports this wave fed |
| `ATP W162 Methodology.pdf` | Sample design, weighting |
| `ATP W162 Questionnaire.pdf` | Full survey instrument |

The wave's own readme lists the reports it fed, including "Growing Share
of U.S. Adults Say Religion Is Gaining Influence in American Life"
(Oct. 20, 2025) — this dataset's chart recomputes and extends a finding
from that report (see below), so unlike `pew-atp-w70-2020`, this dataset
does **not** need a "check before citing" caveat: the source report for
its one flagship chart is confirmed.

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-atp-w162-2025`), using the shared
chart shape in `scripts/flagship-charts/common.py`:

- `religious-conflict.json` (share who feel at least some conflict
  between their own religious beliefs and mainstream American culture,
  `RELIGCONFLICT_W162`, grouped by `RELIG_W162`) — computed by
  `religious_conflict.py`, rendered by
  `render_religious_conflict_chart.py`.

  Pew's own October 2025 report leads with this same question's
  topline ("a majority of U.S. adults (58%) say they feel at least some
  conflict") — this script's weighted top-line reproduces 58.2%,
  confirming the methodology matches. That report explicitly declined to
  break Mormons out on their own ("there are not enough respondents from
  these smaller groups to report on their answers separately," grouping
  Latter-day Saints with Muslims, Hindus, and Buddhists). Wave 162's
  Mormon unweighted N (135) clears this pipeline's own `MIN_VALID_N=30`
  threshold, so this chart reports the breakout Pew's own report didn't —
  and Latter-day Saints come out on top: 78% report at least some
  conflict with mainstream culture, higher than every other group in the
  wave (next highest: Muslims at 70%, Orthodox Christians at 68%,
  Protestants at 67%; Catholics 55%).

Further charts from this dataset (e.g. from its Catholicism-connection
items, `RELIG_INFL1/2`, `BORN_W162`, or `SOCTRUST2_W162`) should follow the
same two-stage pattern, grouping by `RELIG_W162` rather than `F_RELTRAD`
since this wave lacks the latter.
