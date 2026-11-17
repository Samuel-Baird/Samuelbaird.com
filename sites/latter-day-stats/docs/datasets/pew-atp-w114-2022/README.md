# Pew Research Center — American Trends Panel, Wave 114 (September 2022)

A general-topic wave of Pew's American Trends Panel: 10,588 U.S. adults
surveyed online, September 13–18, 2022, in English and Spanish. It fed
several Pew reports on religion and politics, including "45% of Americans
Say U.S. Should Be a 'Christian Nation'" (October 27, 2022) — see the
readme's release list below for the others.

Unlike Wave 70 (`pew-atp-w70-2020`), this wave does **not** carry the
`F_RELTRAD` frame variable other ATP waves in this dataset family use to
classify respondents into Evangelical/Mainline/Historically Black
Protestant/Catholic/Mormon/Jewish/Unaffiliated. Confirmed directly against
the .sav — there is no `F_RELTRAD` column in this file at all. The closest
available religious-affiliation variable is `F_RELIG` (self-reported
affiliation, 12 categories, including "Mormon (Church of Jesus Christ of
Latter-day Saints or LDS)" coded `3.0`) and the coarser `F_RELIGCAT1`
(4-way: Protestant/Catholic/Unaffiliated/Other). This dataset's chart uses
`F_RELIG`.

## What's in here

Raw microdata lives in `data/pew-atp-w114-2022/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `ATP W114.sav` | SPSS microdata, N=10,588 |
| `ATP W114 readme.txt` | Pew's own readme, incl. the release list and weight variable names |
| `ATP W114 methodology.pdf` | Sample design, weighting |
| `ATP W114 questionnaire.pdf` | Full survey instrument |
| `ATP W114 topline.pdf` | Weighted toplines for every question |

Per the wave's own readme, this wave fed (at least) these releases:

- Sept. 22, 2022 — "Gay or bisexual men express concern about monkeypox,
  are critical of government's response"
- Oct. 3, 2022 — "Growing share of Americans say their side in politics
  has been losing more often than winning"
- Oct. 5, 2022 — "Lack of Preparedness Among Top Reactions Americans Have
  to Public Health Officials' COVID-19 Response"
- Oct. 25, 2022 — "Americans Value U.S. Role as Scientific Leader, but 38%
  Say Country Is Losing Ground Globally"
- Oct. 27, 2022 — "A closer look at Americans who believe the U.S. should
  be a Christian nation"
- Oct. 27, 2022 — "In their own words: How Americans describe 'Christian
  nationalism'"
- **Oct. 27, 2022 — "45% of Americans Say U.S. Should Be a 'Christian
  Nation'"** (the report this dataset's flagship chart is drawn from)
- Nov. 30, 2022 — "Growing share of Americans see the Supreme Court as
  'friendly' toward religion"
- Dec. 12, 2022 — "At least four-in-ten U.S. adults have faced high
  levels of psychological distress during COVID-19 pandemic"
- Mar. 2, 2023 — "Mental health and the pandemic: What U.S. surveys have
  found"
- Mar. 15, 2023 — "Americans Feel More Positive Than Negative About Jews,
  Mainline Protestants, Catholics"
- Jul. 24, 2023 — "8 facts about Americans with disabilities"

If analyzing an item not obviously covered above, check the questionnaire
and topline first to confirm which report (if any) it fed before citing a
specific one.

The weight variable for most analysis is `WEIGHT_W114` (per-wave weight;
what Pew uses for most reports from this wave). Two longitudinal weights
also ship in this file — `WEIGHT_W84_W114` and
`WEIGHT_W64_W66_W83_W114` — for analyses spanning multiple waves; not used
here.

## Status

Five charts shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-atp-w114-2022`), using the shared
chart shape in `scripts/flagship-charts/common.py` (this section was
stale as of 2026-09-06 — it previously listed only the first chart even
though four more had already landed):

- `christian-nation.json` (share saying the U.S. should be a "Christian
  nation," NATCHRc_W114, by religious affiliation) — computed by
  `christian_nation.py`, rendered by `render_christian_nation_chart.py`.
  NATCHRc was only asked of a random half of the sample (Pew's own form
  split within the NATCHR item series), so its valid N (~5,174) is about
  half the wave's total. Latter-day Saints/Mormon respondents are the
  highest of any group shown (75%), well above Protestants generally
  (71%) and more than 25 points above the all-U.S.-adults figure (47%).
- `essent-jesus.json` (share saying a personal relationship with Jesus
  Christ is essential to their faith, ESSENT_k_W114, among the four
  Christian traditions the item was piped to) — computed by
  `essent_jesus.py`, rendered by `render_essent_jesus_chart.py`. Mormons
  highest at 83.5%.
- `essent-attend.json` (share saying regular attendance is essential to
  their faith, ESSENT_b_W114, among the 8 traditions the item was piped
  to) — computed by `essent_attend.py`, rendered by
  `render_essent_attend_chart.py`. Mormons 2nd only to Muslims at 49.1%.
- `essent-believe-god.json` (share saying believing in God is essential
  to their faith, ESSENT_a_W114, among the same 8 piped traditions) —
  computed by `essent_believe_god.py`, rendered by
  `render_essent_believe_god_chart.py`. Mormons 91.3%, 2nd only to
  Muslims (96.7%) and the highest of any Christian tradition.
- `relfav-mormons.json` (favorability toward Mormons, RELFAV_c_W114, by
  the outsider's own F_RELIG) — computed by `relfav_mormons.py`, rendered
  by `render_relfav_mormons_chart.py`. Mormons rate their own group 81.1%
  favorable; every other group clusters near the 18.9% national average.

Further charts from this dataset should follow the same two-stage
pattern, and should use `F_RELIG` (or `F_RELIGCAT1` for a coarser split)
for any by-religion breakout, since this wave has no `F_RELTRAD`.
Remaining untouched candidates, checked and dropped as of 2026-09-06:
ESSENT_g/h/i/j (patriotic/family traditions/moral life/community — all
mid-pack or politically coded, no distinctive LDS story), REL4_c (do you
personally know a Mormon — social contact, not an LDS belief/practice
item), and CHRNAT1a/b (Christian nationalism awareness/favorability —
politically coded, no clean doctrinal tie). The rest of RELFAV_* (views
of Evangelicals/Catholics/Jews/Muslims/Atheists/Mainline Protestants) is
still technically open but asks how *other* groups are viewed, not
Mormons specifically — weak fit unless a clear angle emerges.
