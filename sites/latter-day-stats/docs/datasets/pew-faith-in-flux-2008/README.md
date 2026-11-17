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

Three charts shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-faith-in-flux-2008`), using the
shared chart shape in `scripts/flagship-charts/common.py`:

- `reasons-joined-lds.json` (why the survey's 38 converts to Mormonism
  say they joined) — computed by `reasons_joined_lds.py`, rendered by
  `render_reasons_joined_lds_chart.py` (wider `axes_left` margin, since
  its row labels are full survey-item phrases).
- `reasons-left-religion.json` (why all 2,867 recontacted switchers left
  the religion they grew up in, q4 battery) — computed by
  `reasons_left_religion.py`, rendered by `render_reasons_left_chart.py`
  (same wider `axes_left`). The former-Mormon subgroup here is only
  n=26 — too thin even by this dataset's own loose small-n convention —
  so this chart reports the general switcher population instead of
  isolating Mormon leavers.
- `leave-vs-join.json` (whether changing religion was driven more by
  wanting to leave the old one or join the new one, q6) — computed by
  `leave_vs_join.py`, rendered by `render_leave_vs_join_chart.py`.
- `leaving-decision-maker.json` (whether leaving was mostly the
  respondent's own decision or their family's, q2) — computed by
  `leaving_decision_maker.py`, rendered by
  `render_leaving_decision_chart.py`.
- `faith-strength-before-after.json` (share with strong faith, as a
  teenager vs. now, q12/q13) — computed by
  `faith_strength_before_after.py`, rendered by
  `render_faith_strength_chart.py`.

Further charts from this dataset should follow the same two-stage
pattern.
