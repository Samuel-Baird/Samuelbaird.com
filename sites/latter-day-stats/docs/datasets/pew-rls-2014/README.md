# Pew Research Center — 2014 Religious Landscape Study

The middle wave of the Religious Landscape Study, between the 2007
original and 2023-24 wave already in `data/pew-rls-2023-24/`: 35,071 U.S.
adults interviewed by telephone (60% cell, 40% landline) June 4–Sept. 30,
2014, in English and Spanish, with a minimum of 300 interviews in every
state and D.C. This is the source of the widely cited "America's Changing
Religious Landscape" report.

## Recommended citation

> Pew Research Center. 2015. "2014 Religious Landscape Study."

- Study page: <https://www.pewresearch.org/religious-landscape-study/2014/>

## What's in here

Raw microdata lives in `data/pew-rls-2014/` (gitignored, not committed):

| File | What it is |
| --- | --- |
| `Dataset - ... 2014 Religious Landscape Study ... .sav` | SPSS microdata, N=35,071 |
| `Codebook - ... 2014 Religious Landscape Study ... .pdf` | Version 1.1 codebook, every variable/value label |

The `data/pew-rls-2014-recontact/` folder holds a related but separate
2015 recontact of 5,000 of these respondents — see its own README.

## Status

Five charts shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-rls-2014`), using the shared chart
shape in `scripts/flagship-charts/common.py`:

By current religious tradition (RELTRAD):
- `samesex-marriage.json` (support for same-sex marriage, qb22) — computed
  by `samesex_marriage.py`, rendered by `render_samesex_marriage_chart.py`.
- `weekly-attendance.json` (share attending religious services weekly or
  more, ATTEND) — computed by `weekly_attendance.py`, rendered by
  `render_weekly_attendance_chart.py`.
- `certainty-of-god.json` (share of believers absolutely certain God
  exists, qg1b) — computed by `certainty_of_god.py`, rendered by
  `render_certainty_chart.py`; a companion to the same-named chart in
  `scripts/pew-rls-2007/`.
- `millennial-share.json` (share born 1981-1996, cohort5cat) — computed
  by `millennial_share.py`, rendered by `render_millennial_share_chart.py`.

Cross-wave:
- `nones-growth-2007-2014.json` (unaffiliated share, 2007 vs. 2014) —
  computed by `nones_growth_2007_2014.py`, which unusually reads BOTH
  `data/pew-rls-2007/` and this dataset's own .sav (justified since the
  whole point is the two-wave comparison), rendered by
  `render_nones_growth_chart.py`.

The most natural next chart is a three-point trendline against
`pew-rls-2007` and `pew-rls-2023-24` on a question all three waves share.
