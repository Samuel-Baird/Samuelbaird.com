# Pew Research Center — American Trends Panel, Wave 117 (November 2022)

A general-topic wave of Pew's American Trends Panel: 11,377 U.S. adults
surveyed online, in English and Spanish, November 16–27, 2022. Like other
ATP waves, it carries a `F_RELTRAD` frame variable classifying each
respondent's religious tradition (Latter-day Saints/Mormon coded `20000`),
which is what makes an otherwise general-topic wave usable for breaking
its substantive questions out by religion.

## What's in here

Raw microdata lives in `data/pew-atp-w117-2022/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `ATP W117.sav` | SPSS microdata, N=11,377 |
| `ATP W117 readme.txt` | Pew's own readme, incl. the `F_RELTRAD` value labels and weight variables |
| `ATP W17 methodology.pdf` | Sample design, weighting (filename is Pew's own, missing the "1") |
| `ATP W117 questionnaire.pdf` | Full survey instrument |
| `ATP W117 topline.pdf` | Weighted toplines for every question |

This wave carries the standard sample weight (`WEIGHT_W117`) plus three
special-purpose weights added later for validated-voter analysis
(`WEIGHT_W117_VOTE`, `WEIGHT_W117_VALIDATEDVOTE`,
`WEIGHT_W78_W117_VALIDATEDVOTE`) — none of those are relevant to the
religion items used here; `WEIGHT_W117` is correct for this chart.

Per Pew's own readme, this wave fed (at least) four released reports:

- "Public Has Modest Expectations for Washington's Return to Divided
  Government" (Dec. 1, 2022) — uses `WEIGHT_W117_VOTE`, not the religion
  items.
- **"How the Pandemic Has Affected Attendance at U.S. Religious Services"**
  (Mar. 28, 2023) — <https://www.pewresearch.org/religion/2023/03/28/how-the-pandemic-has-affected-attendance-at-u-s-religious-services/>.
  This is the report the wave's religion/attendance battery
  (`ATTENDMONTH_W117`, `ATTENDONLINE_W117`, `ATTENDPERSON2_W117`, etc.)
  was fielded for, and the one the chart below draws on.
- "Online Religious Services Appeal to Many Americans, but Going in
  Person Remains More Popular" (Jun. 2, 2023) — also draws on the same
  attendance battery.
- "Why some Americans prefer to go to religious services in person and
  others prefer to watch virtually" (Sep. 6, 2023) — same battery,
  `ATTENDPREF_W117`.
- "Republican Gains in 2022 Midterms Driven Mostly by Turnout Advantage"
  (Jul. 12, 2023) — uses the validated-voter weights/variables, not
  relevant here.

The chart in this dataset uses `ATTENDMONTH_W117`, part of the same
battery behind the March 2023 pandemic-attendance report and the June
2023 online-vs-in-person report; cite whichever of those two is closest
to the specific claim being made, or the wave itself for a general
"Pew asked this in Nov. 2022" citation.

## Status

One chart shipped, by religious tradition (F_RELTRAD) with groups under
30 valid respondents omitted, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-atp-w117-2022`), using the shared
chart shape in `scripts/flagship-charts/common.py`:

- `inperson-attendance.json` (share who attended religious services in
  person in the past month, `ATTENDMONTH_W117`) — computed by
  `inperson_attendance.py`, rendered by
  `render_inperson_attendance_chart.py`. Latter-day Saints report by far
  the highest rate of any tradition in this wave (80%), well above the
  next-highest group (Evangelical Protestants, 50%) and nearly triple the
  all-adults figure (29%) — a starker gap than the same item showed in
  ATP Wave 70's pandemic-era version
  (`docs/datasets/pew-atp-w70-2020/inperson-attendance-covid.json`),
  consistent with in-person attendance broadly recovering by late 2022
  while Latter-day Saints' own rate stayed unusually high.

This wave's religion/media-use battery (`ONLINESATIS1_W117`,
`ATTENDPREF_W117`, `ONLINEMANY_W117`, the `RELIGAPP*_W117` items on
prayer/scripture apps and religious podcasts, etc.) has plenty of room
for further charts from this dataset; they should follow the same
two-stage pattern.
