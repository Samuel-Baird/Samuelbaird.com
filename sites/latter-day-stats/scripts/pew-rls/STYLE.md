# Pew RLS graphics: website house style, decline-chart extension

Shares the website graphics system established in
[`../state-of-theology-graphics/STYLE.md`](../state-of-theology-graphics/STYLE.md) —
same canvas (1080×1350, white background), same fonts (Roboto Slab Bold
titles, Roboto Condensed everything else, loaded from that folder's
`fonts/`), same "accurate, not editorial" title rule, same bottom-anchored
caption and mobile font floors (via
[`scripts/chart_style.py`](../chart_style.py)), same
`/data-explorer/<slug>/graphics` gallery wiring. This file only documents
what's genuinely new for this dataset's charts.

## Why a new file rather than reusing that palette

State of Theology's charts are all one job: agreement-by-tradition, a
straight magnitude comparison, so a fixed color-per-tradition palette
(amber/moss/slate/wine/teal) is the right tool — the color *is* the
tradition's identity, consistent on every chart.

This dataset's first chart is a different job: **net change from a zero
baseline** (share raised in a tradition vs. share currently in it). That's
a polarity/magnitude read, not an identity read — per the site's own
chart-color rule in [`BRANDING_AND_DESIGN.md`](../../BRANDING_AND_DESIGN.md)
("Charts" section): `--oxblood` (`#7c2d2d`) is reserved sitewide for
decline/negative signals. Every bar in a decline chart uses that one hue,
not six identity hues — there's no per-tradition color to assign in the
first place, since the value being encoded is a rate, not an identity.

| Token | Hex | Use |
|---|---|---|
| Decline (confident) | `#7c2d2d` | Net-change bar fill + its own bold value label. 95% CI excludes zero. |
| Decline (uncertain) | `#b08181` (60% tint of confident, over white) | Net-change bar fill. 95% CI includes zero — not statistically distinguishable from no change. |
| Whisker | `#6E6A63` (Muted, matching the shared Muted token) | 95% confidence interval, drawn over the bar. Also the uncertain rows' value label — muted rather than the confident bars' oxblood, so the "we don't actually know" reading survives even for a reader who only looks at label color. |

The 60% tint was picked, not eyeballed: it's the lightest tint of `#7c2d2d`
over white that still clears WCAG's 3:1 non-text contrast floor (1.4.11) —
lighter tints tested down to 2.1:1, unreadable as a distinct fill against
white paper. Full confident oxblood is 9.25:1 against white; the two tones
are easily told apart at a glance, and neither depends on hue
discrimination (same hue, only lightness differs), so the distinction
holds under any color-vision deficiency.

The Protestant-composition inset (see below) is a different job again —
current share by tradition, the same job State of Theology's charts do —
so it reuses that locked identity palette directly: Evangelical `#C9721C`,
Mainline `#4E5D80`, Historically Black Protestant `#5B7553`. Two color
languages on one image, each doing the job it's actually suited for, not
one language stretched to cover both.

## Why some bars are two-toned

`FRMREL`/`CURREL` are self-reported by 36,908 people; Pew's own 500
bootstrap replicate weights (`REPWT_001`–`REPWT_500`) give a real standard
error per group, and small groups (Jehovah's Witness raised n=158,
Orthodox n=266) have wide ones. A bar whose 95% CI crosses zero cannot
honestly be shown identically to one that doesn't — the confident tone
would silently overclaim a decline the data doesn't establish. The muted
tone plus the CI whisker itself carry that distinction; a reader who only
sees the bar length still sees the honest range via the whisker.

## New composition element: the diverging bar with a CI whisker

No existing chart in `state-of-theology-graphics/STYLE.md` crosses a zero
baseline or shows uncertainty, so this is new:

- A thin vertical zero-reference line (Grid token) somewhere in the plot
  interior; bars start there rather than at the y-axis edge.
- Category labels stay in the same place as the existing "by tradition"
  layout (left margin, bold ink) regardless of which direction the bar
  extends — a reader already knows to look left for the label in a
  horizontal bar chart.
- A CI whisker (thin muted line, small end-caps) drawn over each bar at
  its vertical center, extending past the bar's own tip by the margin of
  error. Drawn in Muted rather than the bar's own hue, matching the
  existing "value labels are the bar's color, structural elements are
  muted/ink" split.
- The value label sits past the bar's tip (further in the bar's own
  growth direction — here, further left), bold, in the bar's own tone.

## 100%-stacked composition: "switching, generalized" and birth-decade

Two more chart shapes on this dataset's `/graphics` page follow this same
compute-then-render split, but as a 100%-stacked horizontal bar rather than
a diverging one — "what's this group made of," not "how has it changed."
Both retired an in-app "Interactive" `StackedBars` twin on 2026-08-26 (see
`docs/CHARTS.md`'s "History" note) in favor of the PNG being the only copy.

**Switching, generalized** (`switching_generalized.py` →
`switching-generalized.json` → `render_switching_generalized_chart.py` →
two PNGs, `switching-current-composition.png` and
`switching-raised-cohort.png`): reuses the identity-neutral palette from
the net-change chart above, not a per-tradition color, because the segments
here are also a rate/status split (raised-in vs. converted-in; stayed vs.
left), not a group identity. `--accent` for "raised in it"/"stayed" (the
same weighted headcount read against two different denominators), `--honey`
for "converted in," `--oxblood` for "left" per the site's decline-token
rule.

**Birth-decade makeup** (`birth_decade_distribution.py` →
`birth-decade-distribution.json` → `render_birth_decade_chart.py` →
`birth-decade-distribution.png`): a genuinely ordinal scale (which decade),
so it uses a single-hue ramp instead — the light-mode hex values of
`--chart-ordinal-1..7` from `src/app/globals.css`, hardcoded in the render
script the same way every other token in this pipeline is (the PNG
pipeline never reads CSS custom properties or Tailwind classes; see
`docs/CHARTS.md`'s Scope note). Steps 1-4 (the faint end) get dark label
text, steps 5-7 (the intense end) get white — the same split
`src/components/charts/palette.ts` used to document for the in-app kit's
now-deleted `LABEL_ON` map, before that map's only consumers were removed.

Regenerate either:

```bash
python scripts/pew-rls/switching_generalized.py
python scripts/pew-rls/render_switching_generalized_chart.py \
  --composition-out ../../public/data-explorer/pew-religious-landscape-study/switching-current-composition.png \
  --raised-cohort-out ../../public/data-explorer/pew-religious-landscape-study/switching-raised-cohort.png

python scripts/pew-rls/birth_decade_distribution.py
python scripts/pew-rls/render_birth_decade_chart.py \
  --out ../../public/data-explorer/pew-religious-landscape-study/birth-decade-distribution.png
```

## Magnitude bar (per-group identity color) and paired bar

Most of the dataset's remaining backlog sections (childhood formation,
family and household, practice, beliefs, spiritual experience, public life
and society) ship as a **magnitude bar**: one row per group, a single
percentage, sorted by the site-wide row-order rule — highest to lowest by
each group's own value, with a named catch-all ("Other Christian" and the
like) always sunk below every substantive row and a population-average
aggregate ("Christian average" and the like) sunk below even that,
regardless of either's own number, each sorted by value within its own
bottom tier — via `chart_style.sort_groups` (see `BRANDING_AND_DESIGN.md`'s
"Charts" section for the canonical statement of the rule).

Each named denomination/religion gets its own locked identity color — the
full 10-color palette and the plain-language rule live in
`BRANDING_AND_DESIGN.md`'s "Charts" section; the canonical implementation
is `chart_style.GROUP_COLORS`/`chart_style.color_for_group`. A catch-all
("Other Christian" and the like) falls back to the bar-fill-safe gray
(`CONTEXT_GRAY`, `#8f8b82`); a population-average or total-population row
falls back to `MUTED` (`#6E6A63`) — both via `color_for_group`, matching
each row's own tier from `sort_groups` rather than getting a made-up color.
This replaced the old highlight-vs-gray convention (Latter-day Saint alone
in `--accent`, every other group flattened to one gray) on 2026-08-28:
singling out LDS's bar color (and, previously, its row-label text) read as
favoritism rather than a deliberate signal once every other group in the
same dataset needed its own identity too. Row-label (y-axis tick) text is
now always `INK` in every magnitude-bar and paired-bar function — it no
longer bolds/colors the Latter-day Saint row differently from the rest,
for the same reason. The one accepted tradeoff: Muslim (olive, `#6B8C3D`)
and Orthodox Christian (moss, `#5B7553`) sit closer together than the
usual colorblind-safe floor when they land next to each other on a chart;
this is legal only because every bar already prints its group name and
percentage directly on it, so color is never the sole way to identify a
row — see `BRANDING_AND_DESIGN.md` for the full statement of why this is
accepted rather than fixed.

The population each chart draws from (Christian only, Christian + other
religions, or every religiously-affiliated tradition individually + the
unaffiliated) still varies item to item — a `GROUP_ORDER`/`group_order`
constant still says *which* group keys belong in a given chart, it just no
longer dictates the order they're drawn in; see each compute script's own
docstring (`childhood_formation.py`, `family_household.py`, `practice.py`,
`beliefs.py`, `spiritual_experience.py`, `public_life.py`) for which set a
given chart uses and why.

**Practice's own 100%-stack** (`practice.py` → `render_practice_charts.py`'s
`render_distribution_stack`, used for the attendance- and prayer-frequency
full-distribution charts) uses the same single-hue ordinal ramp as
birth-decade above, since its segments are a frequency scale, not a group
identity — that part was never the highlight-vs-gray pattern. Its row
(y-axis tick) label *was* still colored `ACCENT` for the Latter-day Saint
row via a local `HIGHLIGHT_GROUP` check, left over from before the
magnitude-bar fix above — fixed on 2026-08-31 the same way: every row
label is unconditionally `INK`, regardless of which group it names.

**Heaven vs. hell** (`beliefs.py` → `render_beliefs_charts.py`) needed a
shape none of the above cover: two independent yes/no items shown side by
side per group rather than one value or a 100%-stack. Built as a **paired
bar** — two bars per row sharing one zero baseline (heaven in `--accent`,
hell in `--honey`), a small top legend instead of in-place labels since
neither color maps to a single fixed meaning across the whole page.

## Vertical layout: centering the plot band

Every chart in this pipeline computes its axes' vertical position and
height dynamically from the actual rendered title/subtitle block above it
and the actual caption block below it — never a fixed axes position chosen
to fit one particular chart's row count. A fixed position is exactly what
produced the bug this section documents fixing (2026-08-26): a handful of
charts with few rows (7-8, mostly the Christian-only magnitude bars) had
their axes pinned low on the canvas regardless of how short their
title/subtitle ran, leaving a large dead band between the subtitle and the
bars while the caption sat close underneath — visually bottom-heavy and
uncentered, not because those charts had more content but because the
axes math never looked at how much space the text actually used.

The fix, in every render script's magnitude-bar/stacked-bar/paired-bar
function:

1. Compute `subtitle_bottom`, the real y-fraction where the subtitle text
   ends — title lines are already placed one `fig.text()` call per line
   with a known `line_spacing`, so their bottom is exact; the subtitle is
   one `fig.text()` call with an embedded `\n`, so its height is
   `subtitle_fontsize * 1.2 / 72 / FIG_H_IN` per line (matplotlib's default
   linespacing, converted from points to figure-fraction units) times its
   line count.
2. `caption_top = chart_style.draw_caption_bottom(...)` — since the caption
   itself is now bottom-anchored (see the parent doc's "Footnotes:
   bottom-anchored" section) rather than drawn from a fixed constant,
   `caption_top` is no longer a known constant either: it's the return
   value of that call, which depends on how many lines the caption actually
   wrapped to. Call `draw_caption_bottom` *before* laying out the axes.
3. The axes' top and bottom are `subtitle_bottom - TOP_GAP` and
   `caption_top + BOTTOM_GAP` (`TOP_GAP`/`BOTTOM_GAP` ≈ 0.03-0.04, a small
   fixed breathing margin) — the axes' height is whatever's left between
   them, not a formula keyed to row count.

Because the axes now always fill the true available band, the bars inside
it (via matplotlib's own `ax.margins()`) land vertically centered with
consistent space above (below the subtitle) and below (above the caption)
regardless of how many rows a given chart has, how long its title wrapped
to, or how many lines its own caption needed. A short-titled 7-row chart, a
long-titled 14-row chart, and a chart with an unusually short caption all
get a properly centered, evenly-spaced plot band that uses all the room the
caption doesn't need — the plot band now genuinely grows when the caption
is short, which is the point of moving the caption to a bottom anchor in
the first place.

## Bigger row labels and black outlines are now pipeline defaults

`render_christian_only_variants.py`'s attendance-distribution chart
(`practice-attend-distribution-christian.png`) originally introduced two
readability treatments as an *optional override*, passed explicitly to
`render_practice_charts.render_distribution_stack` alongside that one
chart's own larger title and tighter margins:

- **Group/axis (row) labels at `MIN.LEGEND` (24pt)** instead of the
  pipeline's old smaller floor (`MIN.AXIS_LABEL`, 12pt, or a chart's own
  hardcoded 14-15pt) - legends were already bumped to `MIN.LEGEND` for the
  same 1/3-scale-on-a-phone reason (see `MIN`'s own docstring in
  `chart_style.py`); row labels are read at the same distance as a legend
  key, so there's no reason they should be smaller.
- **Black (`INK`) bar/segment and legend-swatch outlines** instead of the
  pipeline's old default (`PAPER`/white, invisible at a chart's outer edge
  and on the palest steps of the ordinal ramp against the white canvas).

As of 2026-08-31, both are the *default* everywhere in this pipeline, not
an override - every `render_*.py` in `scripts/pew-rls/` (except
`render_christian_only_variants.py`, which only calls the others) now
draws every group/axis row label at `MIN.LEGEND` and every bar/segment
patch and legend swatch with an `INK` edge, unconditionally:

- `render_practice_charts.py` - `render_magnitude_bar`'s row-label
  fontsize is now unconditionally `MIN.LEGEND` (dropping the old
  `n_rows > 8` branch); `render_distribution_stack`'s `box_edgecolor`
  parameter default changed from `PAPER` to `INK`, and its
  `group_label_fontsize` parameter's `None` fallback changed from
  `MIN.AXIS_LABEL`/14 to `MIN.LEGEND`. The parameters themselves are
  unchanged - `render_christian_only_variants.py` still passes
  `box_edgecolor=practice_r.INK` and `group_label_fontsize=practice_r.MIN.LEGEND`
  explicitly to its one reference chart; those calls are now redundant
  with the new defaults but harmless, and were left in place rather than
  stripped, so that chart's own explicit intent stays visible at the call
  site.
- `render_beliefs_charts.py` - both `render_magnitude_bar`'s row-label
  fontsize and `render_paired_bar`'s row-label fontsize (drawn via
  `ax.text`, not a tick label, since that shape hides the y-axis) are now
  `MIN.LEGEND`; `render_paired_bar`'s two legend swatches now use
  `edgecolor=INK` instead of `PAPER`.
- `render_public_life_charts.py` - row-label fontsize is unconditionally
  `MIN.LEGEND` (same `n_rows > 8` branch dropped as practice's magnitude
  bar). No stacked segments or legend swatches in this file's one shape,
  so no edge color to change.
- `render_family_household_charts.py`, `render_spiritual_experience_charts.py`
  - row-label fontsize changed from a hardcoded 14pt to `MIN.LEGEND`
  (both files needed a fresh `MIN` import from `chart_style`).
- `render_childhood_formation_charts.py`, `render_birth_decade_chart.py`,
  `render_switching_generalized_chart.py` - row-label fontsize changed
  from a hardcoded 15pt to `MIN.LEGEND`; every `edgecolor=PAPER` on a
  stacked-bar segment or legend swatch changed to `INK`.

**Two charts needed a widened left margin as a result.** `MIN.LEGEND` at
24pt roughly doubles the pixel width of the longest row labels in this
pipeline; the site-wide vertical-centering contract above already re-flows
each chart's *vertical* band automatically, but the *horizontal* left
margin each magnitude-bar function reserves for row labels was still a
fixed constant. Two charts have a group whose label is long enough at
24pt to clip past the canvas's left edge (x=0) at that fixed constant:
`family_household.py`'s `KIDACT_ORDER` and `public_life.py`'s
`CHRISTIAN_PLUS_OTHER_ORDER`, both of which include a
"Religiously affiliated average" row (30 characters - longer than any
other label in this pipeline). Both `render_magnitude_bar` functions
gained an `axes_left` parameter (default unchanged: 0.34 for
family-household, 0.36 for public-life) and their one call site with that
row (`family-kidact-prayer.png`, `public-humntr.png`) now passes
`axes_left=0.46` to reserve more room. Every other chart in this pipeline
fits its widest label inside the existing default margin at `MIN.LEGEND`
size without adjustment - this is a per-chart fix, not a pipeline-wide
margin change, per this doc's general rule that a crowding fix belongs on
the specific chart that needs it.

## Title/subtitle/footnote bigger and darker are now pipeline defaults

`render_christian_only_variants.py`'s attendance-distribution chart
(`practice-attend-distribution-christian.png`) — the same chart that
originally introduced the bigger-row-labels/black-outlines treatments
documented above as an *optional override* — also introduced three
title/subtitle/footnote readability treatments the same way, passed
explicitly to `render_practice_charts.render_distribution_stack` alongside
that one chart's own tighter margins:

- **Title at 32pt** (`title_fontsize`), up from the pipeline's old 26-27pt,
  with a **wider wrap budget of 42 characters** (`title_wrap_width`), up
  from 24-27 — the old value was conservative relative to the canvas's real
  width (see `_draw_title`'s own docstring in `render_practice_charts.py`),
  wrapping a line earlier than the 9in canvas actually required.
- **Subtitle at 16pt** (`subtitle_fontsize`), up from 13.5-14pt, in `INK`
  (`subtitle_color`) instead of `MUTED`.
- **Footnote/caption at 16pt** (`caption_fontsize`), up from 11.5pt — the
  pipeline-wide `draw_caption_bottom` default in `chart_style.py` — matching
  the new subtitle size, in `INK` (`caption_color`) instead of `MUTED`.
  Bold styling is unchanged; it already came from `draw_caption_bottom`'s
  existing handle styling, nothing to touch there.

As of 2026-08-31, all three are the *default* everywhere in this pipeline,
not an override - every `render_*.py` in `scripts/pew-rls/` (except
`render_christian_only_variants.py`, which only calls the others) now draws
its title at 32pt/42-char wrap, its subtitle at 16pt `INK`, and its
footnote at 16pt `INK`, unconditionally:

- `render_practice_charts.py` - `_draw_title`'s `title_fontsize`/
  `title_wrap_width`/`subtitle_fontsize`/`subtitle_color` defaults and
  `_draw_caption`'s `caption_fontsize`/`caption_color` defaults changed to
  the new values; `render_distribution_stack`'s same-named parameters'
  defaults changed to match. The parameters themselves are unchanged -
  `render_christian_only_variants.py` still passes all of them explicitly
  to its one reference chart; those calls are now redundant with the new
  defaults but harmless, left in place so that chart's own explicit intent
  stays visible at the call site, same as the row-label/edgecolor rollout.
- `render_beliefs_charts.py`, `render_birth_decade_chart.py`,
  `render_childhood_formation_charts.py`, `render_family_household_charts.py`,
  `render_public_life_charts.py`, `render_spiritual_experience_charts.py`,
  `render_switching_generalized_chart.py` - each file's own local
  title-drawing code (a `draw_title`/`_draw_title` function, or inline
  `fig.text()` calls in `render_birth_decade_chart.py`'s and
  `render_switching_generalized_chart.py`'s single render function - this
  dataset's title/caption drawing was never behind one shared helper, each
  file evolved its own copy) had its hardcoded `title_fontsize` (26-27 ->
  32), wrap width (24-27 -> 42), `subtitle_fontsize` (13.5-14 -> 16), and
  subtitle color (`MUTED` -> `INK`) changed directly; every
  `draw_caption_bottom(...)` call gained explicit `fontsize=16, color=INK`
  arguments, since `chart_style.draw_caption_bottom`'s own default
  (11.5pt/`MUTED`) was deliberately left alone - it's shared by every other
  Data Explorer pipeline, which haven't had this rollout yet (see
  `BRANDING_AND_DESIGN.md`'s "Charts" section).

**Several titles needed a narrower per-chart wrap-width override.** A
character-count wrap budget is only an approximation of a title's actual
rendered pixel width - RobotoSlab Bold's letterforms vary enough (an
m/w/g-heavy title runs visibly wider than a same-length title with more
i/l/t's) that the new 42-character default, while safe for most titles
including the reference chart's own ("Attendance frequency, full
distribution," 41 characters), let a handful of longer, wider-lettered
titles run past the canvas's right edge despite fitting the 42-character
count as a single (unwrapped) line. Caught by rendering every chart and
edge-scanning each PNG's title band for dark pixels touching the canvas's
right edge - the same triage technique used for the row-label/edgecolor
rollout's clipping check, aimed at the top of the canvas instead of the
bottom. Found and fixed by lowering that one title's own wrap width to 38
(verified by actually measuring each candidate line's rendered width with
matplotlib's text extent, not re-guessing a magic number) at these seven
call sites, via a new `title_wrap_width`/`title_width` parameter added to
whichever render function each one calls:

- `render_practice_charts.py`'s `render_magnitude_bar` - previously took no
  title-sizing parameters at all (unlike `render_distribution_stack`, which
  already exposed them); gained an optional `title_wrap_width` passed
  through to `_draw_title`. Used at the `attend_monthly_out` and
  `praca_out` call sites ("Attend in-person and/or online, monthly or
  more" and "Prayer or scripture study groups, weekly+").
- `render_christian_only_variants.py`'s call for
  `practice-attend-monthly-plus-christian.png` ("Attend in-person and/or
  online, monthly+ (Christian only)") - same fix, same parameter.
- `render_childhood_formation_charts.py`'s `render_magnitude_bar` and
  `render_education_stack` - gained an optional `title_width` passed
  through to `draw_title`. Used at `attendance_out` ("Grew up attending
  church monthly or more") and `education_out` ("Religious education
  received growing up").
- `render_spiritual_experience_charts.py`'s `render_magnitude_bar` - gained
  an optional `title_width` passed through to `draw_title`. Used at
  `meaning_out` ("Think about life's meaning and purpose, weekly+") and
  `presence_out` ("Feel a presence beyond this world, weekly+").

Every other chart in this pipeline fits its own title inside the default
42-character wrap without adjustment - this is a per-chart fix, not a
pipeline-wide wrap-width change, per this doc's general rule (established
by the row-label/edgecolor rollout's `axes_left` fix) that a crowding fix
belongs on the specific chart that needs it.

## Title qualifiers render smaller than the primary title

`render_christian_only_variants.py` builds titles like "Attendance
frequency, full distribution (Christian only)" — a trailing parenthetical
noting which population a variant chart covers. Every `_draw_title`/
`draw_title` in this pipeline (`render_practice_charts.py`,
`render_beliefs_charts.py`, `render_public_life_charts.py`) splits that
qualifier off via `chart_style.split_title_qualifier` and renders it on
its own line at roughly 55% of the primary title's font size, rather than
wrapping it in as if it were equally important. See `BRANDING_AND_DESIGN.md`'s
"Charts" section for the site-wide statement of this rule. A mid-sentence
parenthetical that isn't a trailing qualifier (e.g. a title that just
happens to end a clause in parens) is left alone — `split_title_qualifier`
only matches a `(...)` group at the very end of the string.
