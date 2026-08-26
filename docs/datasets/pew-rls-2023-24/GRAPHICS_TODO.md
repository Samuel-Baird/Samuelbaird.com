# Pew RLS graphics: backlog

A work queue for graphics built from the 2023-24 Religious Landscape Study,
in the style established by `scripts/pew-rls/switching_rates.py` +
`render_switching_chart.py` (see `scripts/pew-rls/STYLE.md`) — a Python
script computes real numbers from the microdata into a JSON file, a second
script renders that JSON to a PNG in the house style, and
`src/lib/data-explorer.ts` wires the PNG into the Pew dataset's gallery
with alt text built from the same JSON. No chart here should ever have a
hand-typed number.

## Workflow

**Starting work**: pick an item from Pending, in priority order unless told
otherwise. If it's marked `BLOCKED`, don't build it — either resolve the
block (get restricted-use access, find an external data source) or ask
whether to skip it. If it's marked `NEEDS DESIGN DECISION`, either make a
reasonable, defensible call and note what you chose and why, or ask first —
your judgment on which, same as any other ambiguous spec.

**Finishing an item**: once a graphic is built, verified (rendered, looked
at, wired into the gallery, deployed, and confirmed live — see the
`pew-switching-rates-graphic` branch's own process as the template), delete
its entry from **Pending** and add a one-line entry to **Shipped** with the
date and a link to the PNG. Don't leave a "done" checkbox sitting in
Pending — an agent scanning this file for unfinished work should only ever
need to read the Pending section.

**This file is the source of truth for what's left.** If you build
something not on this list, add a Shipped entry for it anyway, for the
same reason the Data Explorer itself keeps one file (`data-explorer.ts`) as
the registry rather than scattering dataset entries across routes.

## Variable reference

Every item below cites Pew's own variable name(s) from
`docs/datasets/pew-rls-2023-24/codebook.json` — look them up there for the
complete value-label list before computing anything; the ones quoted here
are trimmed for readability. `WEIGHT` (+ `REPWT_001`–`REPWT_500` for a real
standard error via bootstrap, per `switching_rates.py`'s existing pattern)
applies to every item — Pew's numbers are never unweighted.

---

## Pending

### Blocked — no variable exists in the public file

These five needed real verification, not assumption, before being marked
this way — confirmed by direct keyword sweep across all 654 codebook
variable labels, cross-checked against the actual CSV. Don't reattempt
without either restricted-use access or a different data source; re-asking
the same public file won't produce a different answer.

- **America's largest Christian religious institutions (top 10, LDS/
  Catholic/JW as their own institutions, Protestant broken into
  denominations like the Southern Baptist Convention as its own entity)**
  — needs denomination-level detail (`DENOMREC2`, 86 codes, or the
  Protestant-specific `PROTFAM`). Both are **restricted-use only** — listed
  as such in Pew's own readme, confirmed empty in the actual CSV (checked
  directly, not just the codebook flag: 0 of 2,000 sampled rows populated).
  `RELTRAD` (public) tops out at 16 traditions with no finer Protestant
  split than Evangelical/Mainline/Historically Black — nowhere near
  denomination-specific. No substitute inside this dataset. Would need
  either an ICPSR restricted-use data agreement for the RUF, or an external
  source entirely (e.g., denominations' own reported membership rolls, or
  the Association of Religion Data Archives' congregational studies) — a
  different project, not a Pew RLS graphic.
- **"There are absolutely clear standards of right and wrong"** — no
  matching variable. The closest thing in the instrument is the `GUIDE_A`–
  `GUIDE_D` battery (how much religious teachings / logic and reason /
  practical experience / scientific information factor into *your own*
  right-and-wrong decisions) — a real question, but about decision inputs,
  not about whether absolute standards exist. Not a substitute.
- **"It is possible to be moral without believing in God"** — no matching
  variable anywhere in the instrument. This is a real, well-known Pew
  question, but from a different survey product, not the RLS.
- **Favorability toward *other* religious groups** ("describe other
  religious organizations positively") — no thermometer/favorability
  battery toward specific other faiths exists here. `RELINST_A`–`RELINST_G`
  (churches and religious organizations generically, agree/disagree) are
  the nearest thing in the instrument, but they ask about religious
  institutions in general, not a respondent's view of a group they don't
  belong to — a different question, not a substitute.
- **"Religion and science are compatible"** — no direct compatibility
  question. `SCIMPACT` and `RELIMPACT` (below) each ask about a single
  institution's impact on society, separately, not a joint compatibility
  framing.

### Switching, generalized

- **Net staying/leaving, standardized around being born into the faith —
  Christian denominations only + a Christian average.** A generalization
  of the shipped "Net change since childhood" graphic
  (`switching-rates.json`), but reframed: rather than one net-change
  number, show the *composition* of each tradition's current membership —
  what share of today's adherents were raised in it (retained) vs.
  converted in, and separately what share of those raised in it left. Data
  fully supports this (same `FRMREL`/`CURREL` cross-tab the shipped chart
  already computes), but the exact chart form needs a decision before
  building — candidates: a per-tradition stacked bar (retained % + gained
  % = current 100%), or a small-multiples pair (retention rate vs. loss
  rate) per tradition. Same six-group set as the shipped chart (Protestant
  combined — `FRMREL` still can't split it on the raised side; see that
  chart's own note) plus a weighted Christian-overall average bar/row as a
  reference. `FRMREL`, `CURREL`, `WEIGHT`, `REPWT_001`–`500`.

### Childhood formation — Christian denominations + Christian average

Same six-group set as the shipped switching chart (Evangelical/Mainline/
Historically Black combined as "Protestant," + Catholic, LDS, Orthodox,
Jehovah's Witness, Other Christian), plus a weighted average across all of
them as a reference bar/line. Every item in this group is answered by
**people raised Christian** describing their own childhood — the natural
population is people whose `FRMREL` falls in one of those six buckets, not
their current tradition.

- **Grew up attending church at least once a month** — `CHATTEND`
  (`More than once a week` / `Once a week` / `Once or twice a month` /
  `A few times a year` / `Seldom` / `Never`). "Monthly or more" = the first
  three categories.
- **Religion was very important to their family growing up** — `CHIMPREL_B`
  (`Very important` / `Somewhat` / `Not too` / `Not at all`). "Very
  important" = category 1.
- **Religious education received** — `CHEDU2` (`None` / `1-3 years` /
  `4-6 years` / `7 years or more`) — a 4-category stacked bar per
  tradition, not a single %, since the ask is the full distribution.

### Family and household — Christian denominations + Christian average

- **Share with children under 18 currently at home** — `CHILDREN`
  (`Yes`/`No`).
- **Pray or read scripture with their children at home** — `KIDACT_A`
  (`Yes, I do this` / `No, I do not do this`). Population per the request:
  Christian denominations + an **"other religions"** category (not just a
  Christian average — the request explicitly widens this one) + a
  **religiously-affiliated average**. **Filtered**: only asked of parents
  (`CHILDREN` = Yes) — the denominator for every group here is that
  group's *parents*, not everyone in the group. Handle the same way the
  RLS readme documents this filter, not by silently treating non-parents
  as missing/no.

### Practice — population varies by item, follow each one exactly

The requested population differs item to item here — don't default them
all to the same rule.

- **Religion important in their lives** — `RELIMP` (`Very`/`Somewhat`/
  `Not too`/`Not at all important`). Population: Christian **+ other
  religions**, **excluding** the religiously unaffiliated. Needs a decision
  on the cutpoint — "very important" alone (top box) vs. "very" + "somewhat"
  (top two) — flag which was chosen in the chart's own caption, the way the
  State of Theology charts always specify "strongly + somewhat agree."
- **Bible extremely/very important** — `BIBIMP` (`Extremely`/`Very`/
  `Somewhat`/`Not too`/`Not at all important`). Population: **Christian
  only**. "Extremely or very important" = categories 1+2, exactly as
  asked — no cutpoint decision needed here, the request already names it.
- **Attendance frequency, full distribution** (monthly+, weekly, once or
  twice, etc.) — `ATTNDPERRLS`, same 6-point scale as `CHATTEND` above.
  Population: **all religious groups** (this one isn't Christian-only).
  A full-distribution stacked bar per group, not a single %.
- **Attend in-person and/or online at least monthly** — needs a **derived**
  value combining `ATTNDPERRLS` and `ATTNDONRLS` (identical 6-point scales)
  with an OR: monthly-or-more on either one. Not a straight variable read —
  compute the derived flag first. Population: all religious groups.
- **Member of a house of worship** — `MEMB` (`Yes`/`No`). Population: all
  religions.
- **Pray, frequency** — `PRAY` (`Several times a day` / `Once a day` /
  `A few times a week` / `Once a week` / `A few times a month` / `Seldom` /
  `Never`). Population: all religions. The request's "daily,
  monthly/weekly, etc." suggests collapsing 7 categories into fewer
  buckets for readability — needs a decision on the exact bucketing before
  building.
- **Read scripture outside of religious services, weekly+** — `PRAC_B`
  (`At least once a week` / `Once or twice a month` / `Several times a
  year` / `Seldom` / `Never`). Population: **all religions** (as asked —
  note this one is *not* Christian-restricted, unlike the next item, which
  is the same battery but a different practice).
- **Read other holy texts aside from scripture, weekly+** (devotions,
  inspirational literature) — `PRAC_C`, same 5-point scale as `PRAC_B`.
  Population: **Christian only** — deliberately narrower than the scripture
  item above; keep that distinction, don't default both to the same
  population.
- **Pray or say grace before meals** — `GRACE` (`Always`/`Often`/
  `Sometimes`/`Seldom`/`Never`). Population: Christian only. Needs a
  decision on the cutpoint (Always alone, or Always+Often).
- **Participate in prayer groups, scripture study, or religious education
  programs** — `PRAC_A`, same 5-point scale as `PRAC_B`/`PRAC_C`.
  Population: Christian only. Needs a decision on the frequency threshold
  that counts (e.g., "at least once a week" alone, vs. any regular
  participation above "seldom").

### Beliefs

- **Belief in souls** — `SOUL` (`Yes`/`No`).
- **Belief in heaven** — `HVN` (`Yes`/`No`).
- **Belief in hell** — `HLL` (`Yes`/`No`).
- **Heaven vs. hell belief, compared across groups** — a paired/grouped
  chart combining `HVN` and `HLL` per group, once both exist individually.
- **Evolution guided by God** — `EVOL`. Three-way question
  (no role for God / guided or allowed by God / humans always existed in
  present form) — "guided by God" is category 2 exactly, an exact
  wording match to the request.

  All four belief items above have no population restriction specified in
  the request — default to **all religions** unless told otherwise; flag
  this as an open question rather than silently deciding.

### Spiritual experience — Christian, unless noted

- **Think about the meaning and purpose of life, at least weekly** —
  `EXP_G`, same 5-point scale as `PRAC_B`/`PRAC_C` (`At least once a
  week`/`Once or twice a month`/`Several times a year`/`Seldom`/`Never`).
- **Feel a deep sense of spiritual peace and well-being, weekly+** —
  `EXP_A`. Population: **Christians only**, per the request.
- **Feel the presence of something from beyond this world, weekly+** —
  `EXP_D`. Population: Christian.

### Public life and society — Christian, unless noted

- **"America's openness to people from all over the world is essential to
  who we are as a nation"** — `OPENIDEN`, a forced-choice between that
  statement and its opposite ("too open... we risk losing our identity").
  Category 1 is an exact wording match to the request.
- **Growing immigrant population is a change for the better** — `CHNG_A`
  (`Change for the better`/`Change for the worse`/`Hasn't made much
  difference` — part of a `CHNG_A`/`CHNG_B`/`CHNG_C` battery on social
  change). Category 1 is an exact match.
- **Racial/ethnic diversity strengthens American society** — `DIVRACPOP`
  (`Strengthens American society` / `Weakens` / `Doesn't make much
  difference`). Category 1 is an exact match.
- **Religious diversity strengthens society** — `DIVRELPOP`, identical
  3-point scale to `DIVRACPOP` (confirmed, not assumed from the shared
  naming). Category 1 is an exact match.
- **"God gave humans a duty to protect and care for the Earth"** —
  `HUMNTR_B` (`Completely`/`Mostly`/`Somewhat`/`A little bit`/`Not at all`
  describes their view). Population: Christian **+ other religions**, per
  the request. **Filtered**: `HUMNTR_A`/`HUMNTR_B` are only asked of those
  who answered "yes" in `GOD` (belief in God, per the RLS readme's own
  filter list) — the denominator per group is that group's God-believers,
  not the whole group. This could quietly distort a cross-group comparison
  if a group's belief-in-God rate itself varies a lot; worth a second look
  once the numbers are in, not just built and shipped blind.
- **Religion does more good than harm** — `RELIMPACT` (`does more harm
  than good` / `more good than harm` / `equal amounts`). Category 2 is an
  exact match. Population: **all religiously affiliated and unaffiliated**
  — the widest population rule of any item on this list, don't restrict to
  Christian.
- **Religious organizations bring people together** — `RELINST_F`, a plain
  `Agree`/`Disagree` (no middle category — confirmed, not a 4- or 5-point
  scale like `HUMNTR_B` above).
- **Religious organizations help the poor and needy** — `RELINST_G`, same
  `Agree`/`Disagree` scale.
- **Religious organizations protect and strengthen morality** —
  `RELINST_E`, same `Agree`/`Disagree` scale. (`RELINST_C` doesn't exist —
  Pew's own lettering skips it; not a gap on this project's end.)
- **Science does more harm than good** — `SCIMPACT` (`does more harm than
  good` / `more good than harm` / `equal amounts`). Category 1 is an exact
  match. Population: Christian, per the request.
- **Volunteered in the past 12 months** — `VOL12_CPS` (`Yes`/`No`).
  Population: **all religions and unaffiliated**.

---

## Shipped

- [Net change since childhood, by tradition](../../../public/data-explorer/pew-religious-landscape-study/switching-rates.png) — 2026-08-25. LDS vs. Catholic, Jehovah's Witness, Protestant (combined), Orthodox Christian, Other Christian; net raised-vs-current change with bootstrap confidence intervals, plus a current Evangelical/Mainline/Historically Black Protestant composition inset. Computed by `scripts/pew-rls/switching_rates.py`, rendered by `scripts/pew-rls/render_switching_chart.py`.
- [Birth-decade makeup, by tradition](../../../public/data-explorer/pew-religious-landscape-study/birth-decade-distribution.png) — 2026-08-25. `BIRTHDECADE` share (7 buckets) of each tradition's current (`CURREL`) membership, LDS vs. Protestant/Catholic/Orthodox/JW/Other Christian plus a weighted Christian average; numeric median age dropped per the item's own note (not computable from decade buckets without assuming a within-bucket distribution). New single-hue ordinal ramp on the site's `--accent` hue, validated with `dataviz` skill's `validate_palette.js --ordinal`. Computed by `scripts/pew-rls/birth_decade_distribution.py`, rendered by `scripts/pew-rls/render_birth_decade_chart.py`.
