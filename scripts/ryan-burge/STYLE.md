# Ryan Burge graphics: website house style, heatmap extension

Shares the website graphics system established in
[`../state-of-theology-graphics/STYLE.md`](../state-of-theology-graphics/STYLE.md)
— same canvas (1080×1350, white background), same fonts (Roboto Slab Bold
titles, Roboto Condensed everything else, loaded from that folder's
`fonts/`), same "accurate, not editorial" title rule, same bottom-anchored
caption and mobile font floors (via
[`scripts/chart_style.py`](../chart_style.py)), same
`/data-explorer/<slug>/graphics` gallery wiring. This file only documents
what's genuinely new: this folder renders the pipeline's only **heatmaps**
(`render_voter_matrices.py`'s `render_heatmap()`, reused by
`render_voter_ideas_matrices.py`) and its CCES/PID bar and line shapes.

## Heatmaps: tri-color diverging, semantically anchored

Heatmap cells use a **diverging low → white → high ramp**, not the single-hue
light-to-dark blue ramp this pipeline shipped with (retired 2026-08). At a
glance, a single-hue ramp only tells a reader "more" or "less" — it can't
say which side of the scale's own midpoint a cell sits on without reading
the printed number. A diverging ramp answers that at a glance, which is the
whole point of a heatmap over a table of numbers.

- **White midpoint = the scale's substantive midpoint** — 50 on a 0-100
  thermometer or a 0-100% share scale — not the data's own median or
  midrange. The legend strip prints all three anchors: min, midpoint, max.
- **Anchor choice follows survey semantics, per chart**, using the named
  anchors in [`chart_style.py`](../chart_style.py):
  - **Valence scales** (high = a positive view of the target, low = a
    negative one): `DIV_NEG_RED` (`#7c2d2d`, the site's decline token) at
    low → `DIV_POS_GREEN` (`#1F6E5E`) at high. The green is deliberately
    teal-shifted, never a pure green — separable from the oxblood red under
    deuteranopia by hue *and* lightness, not hue alone.
  - **Warm/cold scales** (feeling thermometers): `DIV_COOL_BLUE` at low →
    `DIV_WARM_RED` at high — the thermometer's own metaphor, and fully
    colorblind-safe since it doesn't rely on red/green discrimination at
    all.
  - **Non-valenced intensity** (issue importance, media viewership, org
    membership, volunteering — where high means "more", not "better"):
    neutral `DIV_COOL_BLUE` ↔ `DIV_WARM_RED` (classic blue-white-red).
    Deliberately *not* green-for-high here — green would fake a value
    judgment ("this is good") that an intensity item doesn't actually carry.
- **Colorblind backstop:** every cell prints its own value regardless of
  ramp choice (this pipeline's existing "every mark carries its own printed
  label" rule) — color is never the only channel encoding the number.
- **Cell-label ink** flips via `chart_style.label_ink` (a WCAG-luminance
  check), not a fixed ramp-position cutoff — a diverging ramp is dark at
  *both* ends and light in the middle, so a single `t > x` threshold (the
  old approach) gets the low end wrong.
- **White cells on white paper:** cell borders use the Border/Grid token
  (`#D9D5CC`), not Paper — a near-midpoint cell needs a visible edge or it
  disappears into the page. `n/a` cells are white fill + Border edge +
  muted "n/a" label (not the old `#F2F0EA` gray, which on a diverging ramp
  would misleadingly read as "slightly below midpoint").
- **Density floors** (per the parent doc's mobile-legibility table): cell
  height ≥ 34px canvas, row/column labels ≥ 12pt, cell values ≥ 12.5pt,
  legend anchor labels ≥ 12pt. A matrix that can't meet these at its current
  row count splits into two PNGs rather than shrinking below floor.

### Per-chart anchor assignment

| Chart (JSON stem) | Ramp | Why |
|---|---|---|
| `voter-ft-racial-religious`, `voter-ft-political-social` | `DIV_COOL_BLUE` → `DIV_WARM_RED` | Thermometer's own cold/warm metaphor |
| `voter-issue-importance`, `voter-ideas-sexism`, `voter-ideas-promises`, `voter-ideas-media`, `voter-ideas-orgs`, `voter-ideas-volunteering`, `voter-ideas-pride` | `DIV_COOL_BLUE` → `DIV_WARM_RED` (neutral) | Intensity/support share ("how much"), not a value judgment the item itself carries. `voter-ideas-sexism` lands here specifically because its six statements are a **mixed-worded battery** — some regressive ("Women should return to traditional roles"), some where agreeing is the sympathetic-to-equality response ("Women miss out on jobs due to discrimination") — so a single agree=negative ramp would color half the rows backwards. Also includes the politically loaded, non-mixed items (policy support, national pride), where assigning green to "more" would imply an opinion the site doesn't take. |
| `voter-ideas-muslim-distrust` | `DIV_POS_GREEN` (low) → `DIV_NEG_RED` (high) | All three proposals point the same direction — agreeing *is* the discriminatory/restrictive position in every row, so one ramp direction is honest across the whole matrix |
| `voter-ideas-immigration`, `voter-ideas-trade` | `DIV_NEG_RED` (low) → `DIV_POS_GREEN` (high) | Each row is independently normalized to "share holding the positive view" (per that chart's own caption note) before it reaches this chart — high already means the same thing in every row, so the ramp can too |

Confirm a chart's own subtitle/wording before assuming which end is
"positive" — the table above is a starting point per dataset, not a
substitute for reading what a given item actually measures. Two guardrails
this pipeline learned the hard way (2026-08 heatmap recolor):

- **Mixed-worded batteries get the neutral ramp.** If a matrix's rows don't
  all point the same semantic direction when agreement goes up, a single
  valence-coded ramp will misrepresent whichever rows are worded the
  opposite way. Check every row's wording, not just the chart's title,
  before choosing a valenced ramp.
- **Politically contested topics default to neutral.** When a topic is
  politically contested and reasonable people would disagree which side is
  "positive" (support for a policy proposal, national pride), default to
  the neutral ramp rather than picking a side.

## CCES/PID bar and line charts

`render_cces2016_by_religion_charts.py`, `render_pid_by_gender_chart.py`,
and `render_pid_over_time_chart.py` reuse the magnitude-bar and
highlight-vs-gray conventions documented in
[`../pew-rls/STYLE.md`](../pew-rls/STYLE.md) ("Magnitude bar" section) rather
than inventing new shapes — Latter-day Saint in `--accent` (`#1f4f7a`),
other groups in the bar-safe gray (`#8f8b82`) or muted context lines. See
each compute script's own docstring (`cces2016_by_religion.py`,
`pid_by_gender.py`, `pid_over_time.py`) for population and wave specifics.

## Regeneration

All charts in this folder read committed JSON under
`docs/datasets/ryan-burge/` (produced by the compute scripts, e.g.
`voter_matrices.py`, `voter_ideas_matrices.py`) — no number is hand-typed.
Regenerate after any compute-script or render-script change:

```bash
cd scripts/ryan-burge
python render_voter_matrices.py \
  --racial-out ../../public/data-explorer/voter-survey-panel/ft-racial-religious.png \
  --political-out ../../public/data-explorer/voter-survey-panel/ft-political-social.png \
  --imiss-out ../../public/data-explorer/voter-survey-panel/issue-importance.png
python render_voter_ideas_matrices.py --out-dir ../../public/data-explorer/voter-survey-panel
```

`src/lib/data-explorer.ts`'s Voter Survey Panel entries build graphic
metadata from that same JSON (alt text does not describe ramp colors, so a
gradient change here never causes alt-text drift).
