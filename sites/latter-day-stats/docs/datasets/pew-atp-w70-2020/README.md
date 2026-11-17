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

Three charts shipped, all by religious tradition (F_RELTRAD) with groups
under 30 valid respondents omitted, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-atp-w70-2020`), using the shared
chart shape in `scripts/flagship-charts/common.py`:

- `online-worship-covid.json` (share who watched religious services
  online or on TV during the pandemic, ATTENDONLINE_W70) — computed by
  `online_worship_covid.py`, rendered by `render_online_worship_chart.py`.
- `prayer-covid-coping.json` (share who prayed daily to cope with the
  coronavirus outbreak, SPIRIT2_a_W70) — computed by
  `prayer_covid_coping.py`, rendered by `render_prayer_covid_chart.py`.
- `inperson-attendance-covid.json` (share who attended religious services
  in person in the past month, ATTENDMONTH_W70) — computed by
  `inperson_attendance_covid.py`, rendered by
  `render_inperson_attendance_chart.py`.
- `financial-threat-covid.json` (share calling COVID a major threat to
  their personal finances, COVIDTHREAT_d_W70) — computed by
  `financial_threat_covid.py`, rendered by
  `render_financial_threat_chart.py`.
- `blm-sermons.json` (share hearing a pro-Black Lives Matter sermon,
  SERMONISSUE_b_W70) — computed by `blm_sermons.py`, rendered by
  `render_blm_sermons_chart.py`. Unlike this dataset's other charts, its
  population is respondents who attend religious services at least
  monthly (SERMONISSUE's own skip pattern), not all U.S. adults.

Further charts from this dataset should follow the same two-stage pattern.
