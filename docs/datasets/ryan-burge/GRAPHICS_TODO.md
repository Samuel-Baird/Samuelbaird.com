# Ryan Burge LDS graphics: backlog

A work queue for graphics built from the LDS-relevant survey extracts
publicly redistributed by Ryan Burge (github.com/ryanburge) and curated into
this repo per `data/ryan-burge/INVENTORY.md` — in the style established by
`scripts/pew-rls/switching_rates.py` + `render_switching_chart.py` (see
`scripts/pew-rls/STYLE.md`): a script computes real numbers from the
microdata into a JSON file, a second script renders that JSON to a PNG in
the house style, and `src/lib/data-explorer.ts` wires the PNG into the
right dataset's gallery with alt text built from the same JSON. No chart
here should ever have a hand-typed number.

These extracts are Burge's own tabulations of other people's surveys, not
his own fielded research — the underlying sponsor/fielder for citation
purposes is the CCES team (a multi-university consortium) and YouGov for
the CCES/CES items, and the Democracy Fund Voter Study Group and YouGov for
the VOTER Survey Panel. Credit Burge as the curator/redistributor, not as
the survey's sponsor.

## Workflow

**Starting work**: pick an item from Pending, in priority order unless told
otherwise. If it's marked `NEEDS DESIGN DECISION`, either make a
reasonable, defensible call and note what you chose and why (in the
chart's own caption/alt text, the way the Pew RLS backlog's items do), or
ask first — your judgment on which, same as any other ambiguous spec.

**Finishing an item**: once a graphic is built, verified (rendered, looked
at, wired into the gallery, deployed, and confirmed live), delete its entry
from **Pending** and add a one-line entry to **Shipped** with the date and
a link to the PNG. Don't leave a "done" checkbox sitting in Pending — an
agent scanning this file for unfinished work should only ever need to read
the Pending section.

**This file is the source of truth for what's left.** If you build
something not on this list, add a Shipped entry for it anyway.

**Once every item in Pending has shipped**: say so directly in your
response to the user — don't silently start pulling more variables from
the VOTER Survey Panel on your own initiative. Tell them plainly that this
backlog is clear and that it's a good time for them to sit down with the
VOTER Survey Panel in depth themselves: it's an 867-variable, six-wave
panel (`data/ryan-burge/reference/voter_survey_panel_variable_list.tsv`
has the full list) and only four items from one wave are queued here —
there's a lot more in it than this file scopes out.

## Variable reference

- **CCES 2016** (`data/ryan-burge/tier1-strong/cces2016_small_cces.csv`,
  N=870 LDS) — full column → original-CCES-code → verified question wording
  table in `data/ryan-burge/tier1-strong/cces2016_small_cces_codebook.md`.
  Do not use `data/ryan-burge/reference/cces_codebook.html` for this file —
  that's a different, later cumulative-file codebook with different
  variable names. **This file has no survey weight column** (Burge's build
  script never selected `commonweight`) — every number is unweighted;
  treat as good for shape/direction, not a number that needs to be exact.
- **CES stacked 2006–2018**
  (`data/ryan-burge/tier1-strong/ces_stacked_2006-2018_css_small.csv`) —
  only 5 columns (`trad`, `pid7`, `race`, `gender`, `year`), self-explanatory
  except `race`, which is numeric with no label column in this file: CCES's
  standard coding is 1=White, 2=Black, 3=Hispanic, 4=Asian, 5=Native
  American, 6=Mixed, 7=Other, 8=Middle Eastern (verified against the CCES
  team's own 2016 guide). No weight column here either. Mormon N by year:
  2006=672, 2008=629, 2010=924, 2012=906, 2014=858, 2016=870, 2017=273,
  2018=823.
- **VOTER Survey Panel**
  (`data/ryan-burge/tier1-strong/voter_survey_panel.dta`) — full 867-row
  labeled variable list in
  `data/ryan-burge/reference/voter_survey_panel_variable_list.tsv`. Unlike
  the two CCES extracts above, **this file does carry per-wave weights**
  (e.g. `weight_2017`) — use them.

---

## Pending

Empty — every item that was queued here has shipped. Per this file's own
workflow note: **don't silently start pulling more variables from the
VOTER Survey Panel on your own initiative.** Tell the user this backlog is
clear and that it's a good time for them to sit down with the VOTER
Survey Panel in depth themselves — it's an 867-variable, six-wave panel
(`data/ryan-burge/reference/voter_survey_panel_variable_list.tsv` has the
full list) and only four items from one wave were ever scoped out here.

---

## Shipped

- **2026-08-26 — All 20 VOTER Survey Panel ideas from
  [VOTER_PANEL_IDEAS.md](VOTER_PANEL_IDEAS.md) (23 PNGs).** That file is a
  brainstorm list, not a backlog — nothing here was ever queued as a
  formal item — but the user asked for all twenty built, so per this
  file's own rule ("if you build something not on this list, add a
  Shipped entry for it anyway") they're recorded here. See
  `VOTER_PANEL_IDEAS.md` itself for the per-idea build notes (each idea's
  entry there now links its shipped PNG); the short version:
  - **Six longitudinal graphics** (ideas 1/2/3/5/20) fix every
    respondent's group at their `religpew_baseline` (~2011) identity and
    track that cohort forward through 2016/2017, regardless of later
    religious identification — the one thing a repeated cross-section
    (Pew RLS, CCES) can't do. Idea 3 is scoped to 2012 → 2016, not → 2020
    as originally drafted: the actual `.dta` file only contains baseline,
    2012, 2016, and 2017 waves (confirmed via `pyreadstat` metadata, not
    assumed from the dataset's own wider description). Two new chart
    shapes for this pipeline: a percentage-axis line chart (adapted from
    `render_pid_over_time_chart.py`) and a two-series paired bar (adapted
    from Pew RLS's `render_beliefs_charts.py`).
  - **Eight single-value magnitude bars** (ideas 4/6/10/13/15/19) and
    **nine heatmap matrices** (ideas 7/8/9/11/12/14/16/17/18) are
    single-wave cross-sections reusing this file's already-shipped shapes
    exactly. A few needed their own polarity note, documented in
    `scripts/ryan-burge/voter_ideas_matrices.py`'s own docstring: the
    trade-attitude matrix rescales each of five differently-worded
    `free_trade_*` items onto one consistent "good for consumers" share
    rather than a raw "% Increase" (which means something different for
    jobs than for prices); the immigration matrix mixes 0-100%-share rows
    with four 1-10-slider means rescaled to 0-100, since the source
    battery mixes scale types.
  - Every idea's own population/wave choice, cutpoint, and thin-group
    exclusion is documented in whichever `voter_ideas_*.py` compute
    script computed it — same "no hand-typed numbers, decisions flagged
    in the script that made them" rule as every other chart in this
    pipeline.
- **2026-08-26 — Feeling thermometer matrices + issue-importance matrix
  (3 heatmaps).** [Racial/religious](../../../public/data-explorer/voter-survey-panel/ft-racial-religious.png)
  (7 targets), [political/social](../../../public/data-explorer/voter-survey-panel/ft-political-social.png)
  (9 targets), [issue importance](../../../public/data-explorer/voter-survey-panel/issue-importance.png)
  (23 issues) — all × the same 9 religion groups as the stranger-in-my-
  -own-country item, grouped by `religpew_2017`. A new chart shape for
  this pipeline: one row per target, one column per religion group, each
  cell colored by a continuous single-hue ramp (the site's own
  `--chart-ordinal-1`/`-7` anchors, interpolated) and printing its own
  value, plus a low→high gradient legend since the color language is new
  here. Thermometers exclude sentinel codes (997/998/999) before averaging
  weighted means. **Design decision made** for issue importance: top-two-
  box ("very" + "somewhat" important), matching this project's existing
  cutpoint convention rather than top-box alone. Computed by
  `scripts/ryan-burge/voter_matrices.py`, rendered by
  `scripts/ryan-burge/render_voter_matrices.py`.
- **2026-08-26 — "Feel like a stranger in my own country," by religion
  (2017 wave).** [PNG](../../../public/data-explorer/voter-survey-panel/stranger-2017.png).
  Verbatim question stem pulled from the Voter Study Group's own VOTER
  Survey codebook (fetched via web search + the codebook PDF's own topline
  text, not paraphrased): "How much do you agree or disagree with this
  statement? - These days I feel like a stranger in my own country."
  Grouped by `religpew_2017` per this section's own recommended default.
  **Design decision made**: three of the twelve religion categories
  excluded as too thin to show individually — Orthodox (n=18), Muslim
  (n=13), Hindu (n=3) — well below every other group here (next-smallest
  is Buddhist, n=51) and below any group shown individually elsewhere in
  this project (Pew RLS's thinnest kept group is n=99); noted in the
  chart's own caption. Computed by `scripts/ryan-burge/voter_stranger.py`,
  rendered by `scripts/ryan-burge/render_voter_stranger_chart.py`.
- **2026-08-26 — Party ID (pid7), LDS men vs. LDS women, over time.**
  [PNG](../../../public/data-explorer/ces-stacked-2006-2018/pid-by-gender.png).
  **Design decision made** (per this item's own recommendation): pid7
  collapsed to 3 categories (Democrat/Independent/Republican, leaners
  folded in) — the smallest year/gender cell (2017 women, N=134) is too
  thin for the full 7-point split. 16 rows (8 waves × 2 genders),
  most-recent wave at top, a thin divider between each wave's two rows.
  Colors avoid literal red/blue and the site's `--oxblood` decline token
  (not a party signal): `--accent` for Democrat, `--honey` for Republican,
  a neutral gray for Independent. Computed by
  `scripts/ryan-burge/pid_by_gender.py`, rendered by
  `scripts/ryan-burge/render_pid_by_gender_chart.py`. Wired into
  `/data-explorer/ces-stacked-2006-2018/graphics`.
- **2026-08-26 — CCES 2016 by religion (8 charts).** Four immigration
  select-all items ([pathway](../../../public/data-explorer/cces-2016/pathway.png),
  [border](../../../public/data-explorer/cces-2016/border.png),
  [dreamer](../../../public/data-explorer/cces-2016/dreamer.png),
  [deport](../../../public/data-explorer/cces-2016/deport.png)), two
  abortion items
  ([prochoice](../../../public/data-explorer/cces-2016/prochoice.png),
  [prolife](../../../public/data-explorer/cces-2016/prolife.png)), same-sex
  marriage
  ([gaym](../../../public/data-explorer/cces-2016/gaym.png)), and
  [religious attendance, full distribution](../../../public/data-explorer/cces-2016/attend-distribution.png).
  **Design decision made**: all 12 `religion` categories shown
  individually, not collapsed — even the thinnest (Hindu N=299, Muslim
  N=436) are large enough for a rough %, the same call already made for
  Pew RLS's even-thinner "Other world religions" (n=99). Unweighted per
  this file's own note (`cces2016_small_cces.csv` carries no weight
  column). Computed by `scripts/ryan-burge/cces2016_by_religion.py`,
  rendered by `scripts/ryan-burge/render_cces2016_by_religion_charts.py`.
  Wired into `/data-explorer/cces-2016/graphics`.
- **2026-08-25/26 — Party ID (pid7) over time, by religious tradition.**
  Shipped 2026-08-25 as an in-app interactive chart (`WaveLineChart`), then
  replaced 2026-08-26 with a downloadable PNG when the site retired its
  interactive-figure/PNG "twin" pattern site-wide (see `docs/CHARTS.md`) —
  every data-explorer graphic is now the single PNG, no in-app duplicate.
  **Design decision made**: hand-picked group set (Mormon, Catholic,
  Southern Baptist, United Methodist, Nothing in Particular, Atheist, Jewish
  — the last aggregating five Jewish denominational rows in the source,
  since it has no single unified "Jewish" category), per this file's own
  recommendation, rather than a RELTRAD rollup that would erase LDS
  entirely. Data: `scripts/ryan-burge/pid_over_time.py` →
  `docs/datasets/ryan-burge/pid-over-time.json`. Rendered by
  `scripts/ryan-burge/render_pid_over_time_chart.py` (the first PNG line
  chart in this codebase's graphics pipeline — translates `WaveLineChart`'s
  own conventions onto the static canvas: donut markers, a dashed connector
  across a gap, end-of-line labels instead of a legend, highlight-vs-gray
  with Latter-day Saint as the one highlighted series). Wired into
  `/data-explorer/ces-stacked-2006-2018/graphics` via
  `cesPidOverTimeGraphic()` in `src/lib/data-explorer.ts`.
