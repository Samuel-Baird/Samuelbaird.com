# Pew Research Center — 2007 U.S. Religious Landscape Survey

The original Religious Landscape Survey: 35,556 continental-U.S. adults
interviewed by telephone in summer 2007 by Princeton Survey Research
Associates International (PSRAI), plus a separate supplemental sample of
200 Alaska and 201 Hawaii adults fielded spring 2008 (reported separately —
neither file carries a weight for combining the two). This is the survey
that established the RELTRAD religious-tradition classification the 2014
and 2023-24 waves still use, and the baseline the site's switching-rate and
trend graphics for those later waves are implicitly measured against.

## Recommended citation

> Pew Research Center. 2008. "U.S. Religious Landscape Survey."

- Study page: <https://www.pewresearch.org/religious-landscape-study/2007/>

## What's in here

Raw microdata lives in `data/pew-rls-2007/` (gitignored, not committed):

| File | What it is |
| --- | --- |
| `Religious Landscape Survey Data - Continental US.sav` | Main survey, N=35,556 |
| `Religious Landscape Survey Data - Alaska and Hawaii.sav` | Supplemental survey, N=401 |
| `Religious Landscape Survey Codebook.doc` | Every variable/value label |
| `Background and Survey Methodology.doc` | Sample design, weighting, response rates |

## Status

Five charts shipped, continental-US main survey only, wired into the Data
Explorer entry (`src/lib/data-explorer.ts`, slug `pew-rls-2007`), using
the shared chart shape in `scripts/flagship-charts/common.py`:

By current religious tradition (RELTRAD):
- `evolution-belief.json` (share agreeing evolution is the best
  explanation for human life on Earth, q10c) — computed by
  `evolution_belief.py`, rendered by `render_evolution_chart.py`.
- `certainty-of-god.json` (share of believers absolutely certain God or a
  universal spirit exists, q31) — computed by `certainty_of_god.py`,
  rendered by `render_certainty_chart.py`.
- `daily-prayer.json` (share who pray at least once a day outside of
  religious services, q41) — computed by `daily_prayer.py`, rendered by
  `render_daily_prayer_chart.py`.

Other breakdowns:
- `retention-rate.json` (share raised in each of five coarse traditions
  who still identify with it as adults, q50 vs. RELTRAD) — computed by
  `retention_rate.py`, rendered by `render_retention_chart.py`.
- `lds-share-by-region.json` ("Where do Mormons live?", share of U.S.
  Mormons in each Census region, cregion) — computed by
  `lds_share_by_region.py`, rendered by
  `render_lds_share_by_region_chart.py`.

The most natural next chart is a three-point trendline against
`pew-rls-2014` and `pew-rls-2023-24` on a question all three waves share.
