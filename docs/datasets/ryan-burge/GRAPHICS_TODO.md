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

### CES stacked — party ID over time (N=5,955 LDS across 2006–2018)

- **Party ID (pid7), LDS men vs. LDS women, over time.** LDS N by year and
  gender: 2006 F=319/M=353, 2008 F=269/M=360, 2010 F=409/M=515, 2012
  F=496/M=410, 2014 F=385/M=473, 2016 F=414/M=456, 2017 F=134/M=139, 2018
  F=425/M=398. **NEEDS DESIGN DECISION**: splitting the full 7-point pid7
  by gender across 8 years produces thin cells in the smallest year
  (2017, N=273 total) — recommend collapsing to a 3-category party ID
  (Democrat/Independent/Republican, folding "leaners" into their party) for
  this chart specifically. Item 1 above isn't split further and can likely
  keep the full 7-point scale.

### VOTER Survey Panel — grouped by religion (2017 wave)

All four items below are from the 2017 wave. **NEEDS DESIGN DECISION**:
group by `religpew_2017` (matches the wave these items were asked in;
N=84 LDS, 83 non-missing per item) or `religpew_baseline` (larger N=141–149,
but reflects the respondent's religion as of the original baseline wave,
which may not match their 2017 identification for panel members who
converted or attrited differently by religion). Recommended default:
`religpew_2017`, for wave-matched accuracy over sample size — flag which
was chosen. Use `weight_2017` for all four.

- **"Feel like a stranger in my own country" — agree/disagree, by
  religion.** `stranger_2017`, 4-point (Strongly agree / Mostly agree /
  Mostly disagree / Strongly disagree). The variable label is short; pull
  the verbatim question stem from the Voter Study Group's own 2017 codebook
  before quoting it on the site — don't publish a paraphrase in quote
  marks.
- **Feeling thermometer matrix — racial and religious groups, by
  respondent's religion.** 7 targets, each `ft_*_2017`, 0–100 continuous
  (exclude sentinel codes 997/998/999 = Don't know/Skipped/Not asked
  before averaging): Blacks, Whites, Hispanics, Asians, Muslims, Jews,
  Christians. One heatmap/small-multiples graphic, not 7 separate charts.
- **Feeling thermometer matrix — political and social groups, by
  respondent's religion.** 9 targets, same 0–100 scale and sentinel
  handling as above: Feminists, Immigrants, Gays and lesbians, Labor
  unions, Police officers, The alt-right movement, Evangelical Christians,
  Democrats, Republicans. One heatmap/small-multiples graphic.
- **Issue-importance matrix — by respondent's religion.** 23 issues, each
  `imiss_*_2017`, 4-point (Very important / Somewhat important / Not very
  important / Unimportant): crime, the economy, immigration, the
  environment, religious liberty, terrorism, gay rights, education, family
  and medical leave, health care, money in politics, climate change,
  Social Security, infrastructure investment, jobs, the budget deficit,
  poverty, taxes, Medicare, abortion, size of government, racial equality,
  gender equality. **NEEDS DESIGN DECISION**: one heatmap needs a single
  number per cell — decide top-box ("% very important" alone) vs. top-two-box
  ("very" + "somewhat"), and flag which was chosen, the way the Pew RLS
  backlog's own cutpoint items do.

---

## Shipped

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
