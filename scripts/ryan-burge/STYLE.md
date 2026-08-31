# Ryan Burge graphics: website house style, heatmap extension

Shares the website graphics system established in
[`../state-of-theology-graphics/STYLE.md`](../state-of-theology-graphics/STYLE.md)
— same canvas (1080×1350, white background), same fonts (Roboto Slab Bold
titles, Roboto Condensed everything else, loaded from that folder's
`fonts/`), same "accurate, not editorial" title rule, same bottom-anchored
caption and mobile font floors (via
[`scripts/chart_style.py`](../chart_style.py)), same
`/data-explorer/<slug>/graphics` gallery wiring. Every chart here follows
the site-wide one-line caption convention (`BRANDING_AND_DESIGN.md`'s
"Charts" section): `draw_caption_bottom(fig, fonts, [], handle="@ithinkisam
| data: <short title>")`, no per-chart methodology/population paragraphs.
This file only documents
what's genuinely new: this folder renders the pipeline's only **heatmaps**
(`render_voter_matrices.py`'s `render_heatmap()`, reused by
`render_voter_ideas_matrices.py`) and its CCES/PID bar and line shapes.

## Row order, if a future chart here needs one

This folder's existing charts are heatmaps and CCES/PID bar and line shapes,
not one-row-highlighted magnitude comparisons, so there's no `sort_groups`
call to make here yet. If a future chart in this folder is a magnitude bar
(single value per group, sorted by that value), use `chart_style.sort_groups`
rather than hand-curating an order — see `BRANDING_AND_DESIGN.md`'s "Charts"
section for the site-wide rule (sort highest to lowest by the chart's own
statistic; a named "Other" catch-all sinks below every substantive row, an
"average" aggregate sinks below even that, and a total-population row, if
present, sinks to the very bottom) and `scripts/pew-rls/STYLE.md`'s
"Magnitude bar (per-group identity color)" section for a worked example.
If a future chart here needs a per-group identity color rather than a
heatmap ramp, use `chart_style.color_for_group` (same "Charts" section for
the palette) rather than inventing a new color scheme.

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
| `voter-ideas-immigration`, `voter-ideas-trade` | `DIV_NEG_RED` (low) → `DIV_POS_GREEN` (high) | Each row is independently normalized to "share holding the positive view" (documented in the compute script, e.g. `voter_ideas_matrices.py` — no longer in the rendered caption, which is now the site-wide one-line handle only) before it reaches this chart — high already means the same thing in every row, so the ramp can too |

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

`render_cces2016_by_religion_charts.py`, `render_voter_ideas_bars.py`,
`render_voter_volunteering_summary_chart.py`, `render_pid_over_time_chart.py`,
and `render_voter_ideas_longitudinal.py`'s line-chart shape reuse the
magnitude-bar and per-group-identity-color line-chart conventions documented
in [`../pew-rls/STYLE.md`](../pew-rls/STYLE.md) ("Magnitude bar" section)
rather than inventing new shapes — every named group gets its own locked hex
from `chart_style.color_for_group`, not one highlighted group in `--accent`
against everyone else in a single undifferentiated gray (retired 2026-08-31
site-wide: singling out Latter-day Saint that way read as favoritism rather
than a deliberate signal, and for the line charts it also made every other
tradition's own trend unreadable against everyone else's). `render_pid_by_gender_chart.py`
is the one exception in this folder — its Democrat/Independent/Republican
rows are party categories, not denominations, so it keeps the
`--accent`/`--honey`/gray convention documented in its own docstring, which
was never the group-highlight pattern to begin with. Every row/tick/end-of-
line label across every chart in this folder stays plain ink regardless of
its bar's or line's own fill color — labels are never colored to match, per
`BRANDING_AND_DESIGN.md`'s "Charts" section. See each compute script's own
docstring (`cces2016_by_religion.py`, `voter_ideas_bars.py`,
`voter_volunteering_summary.py`, `pid_over_time.py`,
`voter_ideas_longitudinal.py`) for population and wave specifics.

## Bigger row labels and black outlines are now pipeline defaults

As of 2026-08-31, this folder rolls out the same two readability
treatments `scripts/pew-rls/` made its default the same day (see that
folder's STYLE.md, "Bigger row labels and black outlines are now pipeline
defaults", for the full background and rationale) to every `render_*.py`
in `scripts/ryan-burge/`:

- **Group/axis (row) labels at `MIN.LEGEND` (24pt)** instead of the
  pipeline's old smaller floor (`MIN.AXIS_LABEL`, 12pt, or a chart's own
  hardcoded 13-14pt).
- **Black (`INK`) bar/segment and legend-swatch outlines** instead of the
  old default (`PAPER`/white, invisible where a segment touches a chart's
  outer edge or another segment).

File by file:

- `render_cces2016_by_religion_charts.py` — `render_magnitude_bar`'s and
  `render_distribution_stack`'s row-label fontsize both changed from
  `MIN.AXIS_LABEL` to `MIN.LEGEND`; `render_distribution_stack`'s stacked-
  segment `edgecolor` and its legend-swatch `edgecolor` both changed from
  `PAPER` to `INK`. `render_magnitude_bar`'s bars have no edge (a single
  bar per row never touches a neighbor, same as every pew-rls magnitude
  bar), so no edge color to change there.
- `render_pid_by_gender_chart.py` — row-label fontsize `MIN.AXIS_LABEL` →
  `MIN.LEGEND`; stacked-segment and legend-swatch `edgecolor` `PAPER` →
  `INK`.
- `render_voter_ideas_bars.py`, `render_voter_volunteering_summary_chart.py`
  — row-label fontsize `MIN.AXIS_LABEL` → `MIN.LEGEND`. Both are plain
  magnitude bars (no stacked segments, no legend), so no edge color to
  change.
- `render_voter_ideas_longitudinal.py` — `render_paired_bar`'s row label
  (drawn via `ax.text`, not a tick label, since this shape hides the
  y-axis) changed from `MIN.AXIS_LABEL` to `MIN.LEGEND`; its two legend
  swatches changed `edgecolor` from `PAPER` to `INK`. The bars themselves
  have no edge (same paired-bar convention as
  `pew-rls/render_beliefs_charts.render_paired_bar`). `render_line_chart`
  in this file is unchanged — see "Line charts are exempt" below.
- `render_voter_stranger_chart.py` — row-label fontsize (hardcoded `13`) →
  `MIN.LEGEND`; stacked-segment and legend-swatch `edgecolor` `PAPER` →
  `INK`.
- `render_pid_over_time_chart.py` — unchanged; see "Line charts are
  exempt" below.
- `render_voter_matrices.py` (`render_heatmap`, reused by
  `render_voter_ideas_matrices.py`) — unchanged; see "Heatmaps are exempt"
  below.

### Line charts are exempt

`render_pid_over_time_chart.py` and `render_voter_ideas_longitudinal.py`'s
`render_line_chart` have no group/axis row labels in the bar-chart sense —
their y-axis ticks are a numeric scale (party ID, a percentage), not one
label per group, so they correctly keep `MIN.AXIS_LABEL`. The one
per-group identifier each line carries — its end-of-line label — already
draws at `MIN.DATA_LABEL` (13pt, bigger than the old `MIN.AXIS_LABEL`
floor this rollout replaces elsewhere) with its own collision-avoidance
pass (`MIN_GAP`) tuned for that size; bumping it to `MIN.LEGEND` for 7-9
simultaneous series would collide labels against each other on the narrow
end-of-line margin this shape reserves. Left as `MIN.DATA_LABEL`,
unchanged by this rollout.

### Heatmaps are exempt

`render_heatmap`'s row/column labels already draw at their own
purpose-built floors (`MIN.HEATMAP_HEADER`, `MIN.HEATMAP_CELL`,
`MIN.HEATMAP_LEGEND` — see `chart_style.MIN`'s docstring: a thin legend
strip has no room for 24pt), not the `MIN.AXIS_LABEL`/hardcoded sizes this
rollout replaces, so there's nothing to bump. Its cell border was also
never `PAPER` — cells already outline in the Border/Grid token (`#D9D5CC`,
see this file's own "White cells on white paper" note above), a
deliberate near-midpoint-cell-visibility fix that predates this rollout,
not the invisible-white-edge problem the bar/segment treatment addresses.
Checked and left as-is.

### One crowding fix: `render_paired_bar`'s `axes_left`

Both charts built on `render_voter_ideas_longitudinal.render_paired_bar`
(`idea-vote-2012-2016.png`, `idea-gaymar-shift.png`) share the same
9-group `group_order`, which includes a "Nothing in particular" row (20
characters) — long enough at `MIN.LEGEND` size to clip past the canvas's
left edge at the shape's old default `axes_left=0.30` (narrower than any
pew-rls magnitude-bar default, since this shape's bars start closer to
the row labels). `render_paired_bar` gained an `axes_left` parameter
(default unchanged: 0.30) and both call sites now pass `axes_left=0.40`.
Every other chart in this folder fits its widest label inside its
existing default margin at `MIN.LEGEND` size without adjustment — this is
a per-chart fix, not a pipeline-wide margin change, per pew-rls STYLE.md's
general rule that a crowding fix belongs on the specific chart that needs
it.

Regenerated every PNG this pipeline produces and spot-checked the widest
chart per shape (12-row magnitude bar and 12-row distribution stack in
`render_cces2016_by_religion_charts.py`, 16-row stacked bar in
`render_pid_by_gender_chart.py`, 9-row stacked bar in
`render_voter_stranger_chart.py`, 23-row heatmap in
`render_voter_matrices.py`, the two `render_paired_bar` charts, and the
7-series line chart in `render_pid_over_time_chart.py`) for
clipping/overlap — all clean after the `axes_left` fix above.

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
