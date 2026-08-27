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

One flagship chart shipped: `evolution-belief.json` (share agreeing
evolution is the best explanation for human life on Earth, by religious
tradition), computed by `scripts/pew-rls-2007/evolution_belief.py` and
rendered by `render_evolution_chart.py` to
`public/data-explorer/pew-rls-2007/evolution-belief.png`, using the shared
chart shape in `scripts/flagship-charts/common.py`. Wired into the Data
Explorer entry (`src/lib/data-explorer.ts`, slug `pew-rls-2007`). The most
natural next chart is a three-point trendline against `pew-rls-2014` and
`pew-rls-2023-24` on a question all three waves share.
