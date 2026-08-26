# Chart style guide

This is the house style for every in-app chart — the hand-rolled SVG/HTML
components under `src/components/charts/` and their call sites (channel
growth, the premium comparison chart, the eternal-increase timeline, and the
data-explorer "Interactive" figures). It draws on Ryan Burge's
(Graphs About Religion, @ryanburge) ggplot2 conventions — direct labeling,
minimal gridlines, highlight-vs-gray, a fixed caption grammar — translated
onto this site's own tokens and fonts rather than copied wholesale. Read
[BRANDING_AND_DESIGN.md](../BRANDING_AND_DESIGN.md) first; this file is the
detail behind its five-line "Charts" section.

**Scope.** This guide covers the in-app SVG/HTML charts only. The
downloadable PNG graphics (`scripts/state-of-theology-graphics/STYLE.md`,
`scripts/pew-rls/STYLE.md`, `scripts/social-graphics/STATISTICS_STYLE_GUIDE.md`)
are a separate pipeline — white canvas, Roboto Slab, a different palette —
because they have to stand alone once downloaded and shared off-site. The
two systems share reasoning (neutral titles, every number traceable to a
source, nothing hand-typed) but not tokens or components. Don't import one
pipeline's colors into the other's charts.

## Anatomy of a chart

Every chart sits inside `ChartFrame` (`src/components/charts/chart-frame.tsx`):

- **Eyebrow** (optional) — small-caps, honey, e.g. "Interactive."
- **Title** — set in **Fraunces**, not a bold sans. Burge's Product Sans
  titles run about 2.5× his body text; the same ratio here is the frame's
  `text-lg sm:text-xl font-semibold` title over ~12–13px in-plot labels.
  Prefer sentence-case, question-form titles that name what the reader is
  looking at ("Party ID over time, by tradition"), the same as the chart
  titles already shipping in `src/lib/data-explorer.ts`.
- **Subtitle** — carries the methodology or question wording the title
  doesn't have room for: cutpoints ("somewhat + strongly agree"), weighting
  status, what a reference line means.
- **Plot area** — `children`.
- **Caption** — fixed grammar, via `ChartCaption`:
  `Data: <source> · latterdaystats.com`, or `Data: <source> via <curator> · latterdaystats.com`
  when the data reached this site through a redistributor (e.g. Ryan Burge's
  CCES/VOTER extracts — see `docs/datasets/ryan-burge/GRAPHICS_TODO.md`).

## Axes and gridlines

- **No axis titles, ever.** The title and subtitle carry that meaning
  instead of `x`/`y` labels nobody reads.
- **Delete the value axis entirely** once every mark carries its own printed
  label (a stacked bar's in-segment percentages, a dot plot's value text) —
  the axis becomes redundant and just adds ink.
- **One axis of gridlines, not two.** Major lines solid `var(--border)` 1px;
  minor lines the same, dashed `4 2`. No tick marks on the rule itself.
- **Explicit category ticks** on a wave/wave-year axis — the real survey
  years, not interpolated date ticks.
- Percent values are formatted `42%`, not `42.0%`, unless the spread in the
  data genuinely needs the extra digit (`fmtPctLabel` in `scales.ts` takes a
  `decimals` override for that case).

## Direct labels over legends

- **Every bar or segment prints its own value.** Suppress the label once a
  segment drops under ~4% of the bar's width — a number that can't fit reads
  worse than no number (`stacked-bars.tsx`'s `minLabelPct`).
- **Label the line, not the legend.** A line chart's series are named at
  their last point (`EndOfLineLabel` in `direct-labels.tsx`), not in a
  legend box competing for the reader's attention.
- When a legend is genuinely unavoidable (an ordinal stack with more
  segments than fit as end labels), put it below the chart, no title, in
  the same order the segments stack in.
- **In-segment label ink comes from a literal map** (`LABEL_ON` in
  `palette.ts`), never runtime luminance math — add an entry whenever a new
  paint value needs to carry text, and check it in both themes.

## Color assignment

- **`SERIES_PAINT`** (`palette.ts`) is the canonical order for a chart with
  no natural focal series: `--accent`, `--honey`, `--oxblood`, `--foreground`
  — the same four ink families the rest of the site already uses, so a
  chart never introduces a color the reader hasn't learned elsewhere.
- **Hard cap: 4 distinct chart colors** (`MAX_SERIES`). This is why the
  premium comparison chart caps channel selection at four.
- **Highlight-vs-gray.** When one series is the point of the chart (LDS
  against six other groups, Evangelical against three other traditions),
  draw the focal series in a house color and every other series in
  `CONTEXT_GRAY` (`var(--muted)`) at reduced opacity, labeled at the line's
  end. Grayed context series **do not count against the 4-color cap** —
  that's how a chart legitimately carries seven lines and still reads
  cleanly (see `WaveLineChart`'s `highlight` flag).
- **Decline is always `var(--oxblood)`.** Growth/positive change is always
  `var(--accent)`. Don't reassign these on a chart-by-chart basis.
- Every bar, segment, and dot gets a **1px `var(--border)` stroke** — the
  thin-outline tic that makes flat fills read as discrete marks rather than
  a smear of color.
- Dots use the "shape-21" treatment: series-color fill, `var(--foreground)`
  outline at 1.5px, knocked out from whatever's beneath with a
  `var(--surface)` circle first — the same `ring-[color:var(--surface)]`
  knockout rule `BRANDING_AND_DESIGN.md` already documents for badges.

## Line charts

The default chart for anything with a time dimension (Burge's own
1,635-graph corpus is more than a third line charts — nothing else comes
close). `WaveLineChart` (`wave-line-chart.tsx`):

- **Donut markers** at every plotted wave: a `var(--surface)` core, a ring
  in the series color, a small filled center — not a plain filled dot.
- **Dashed connector across a gap** (a wave a series wasn't fielded in),
  never a silently interpolated solid line.
- **End-of-line labels**, not a legend.
- Explicit wave-year x ticks below the plot.

## Dot plots with confidence intervals

`DotPlot` (`dot-plot.tsx`) — the default for "rank these groups against each
other" (net change since childhood, percentile comparisons):

- **Capless whiskers.** No end-caps on the CI line — Burge's own
  `error_bar()`/dot-plot convention.
- **Data-driven ordering.** Rows sort by value, never alphabetically, unless
  the axis itself is intrinsically ordered.
- **De-emphasize rows whose interval crosses the reference value** (e.g. a
  95% CI on net change that includes zero) — drawn in `CONTEXT_GRAY` at
  reduced opacity rather than hidden, so an inconclusive result stays
  visible but reads as inconclusive.
- **Dashed, labeled reference line** — never a bare line with no annotation
  explaining what it marks ("No change," "U.S. average").
- Default to a **95% interval**; the codebase also has the option of an
  **84% interval**, where non-overlap of two 84% intervals approximates a
  pairwise 5%-significance test — useful when the point of the chart is
  "which of these differ from each other," not just "what's the estimate."
  Flag which was chosen in the subtitle if you use 84%.

## 100%-stacked composition

`StackedBars` (`stacked-bars.tsx`) — the default for "what's this group made
of":

- One full-width bar per row, horizontal, printed in-segment percentages,
  value axis fully blanked.
- Suppress a segment's label under `minLabelPct` (default 4).
- Ordinal data (e.g. birth decade) uses `ACCENT_ORDINAL_RAMP` — a single-hue
  ramp of its own tokens (`--chart-ordinal-1..7` in `globals.css`), faintest
  to most intense, so it reads as "which decade" rather than introducing a
  second identity color. These are real tokens authored per theme, not a
  `color-mix()` built from `--accent` — every semantic token in this
  palette flips which end reads as "light" between themes, so a mix toward
  a token like `--foreground` as a fixed anchor inverts the ramp's order in
  dark mode. Any future ordinal ramp needs the same per-theme authoring.
- Legend at the bottom, matching the visual stacking order, when the
  segments won't fit as in-place labels alone.

## Faceted small multiples

`FacetGrid` (`facet-grid.tsx`) — the default when the same small chart
repeats once per group or item (agreement by tradition, one panel per
survey statement):

- A grid of bordered mini-panels, each with a small-caps strip label.
- The caller owns the shared scale across facets — don't let one panel's
  axis silently differ from its neighbors.
- Keep facet content minimal (`MiniBars` in `mini-bars.tsx`): no gridlines,
  no axis, just bars/reference line/value — twenty competing full charts
  read worse than twenty small ones.

## When to use which chart

| Question the chart answers | Chart type |
| --- | --- |
| How has this changed over time? | Wave line chart (default) |
| How do these groups compare on one number? | Dot plot with CI |
| What is this group made of? | 100%-stacked bars |
| Does the same small comparison repeat per group/item? | Facet grid |

Avoid: pie charts, dual y-axes, 3D effects, and a charting library's default
palette (`BRANDING_AND_DESIGN.md`'s existing rule — this site draws every
chart by hand for exactly this reason).

## Uncertainty and reference lines

Any dashed reference line (a sample average, a "no change" zero line, a
comparison group's value) must carry a short text label — never a bare line
the reader has to guess the meaning of.

## Dark mode, accessibility, and hover

- **All paint is a literal `var(...)` string** — `palette.ts`'s maps, never
  a computed class name or a raw hex. Tailwind v4 can't see a constructed
  class, and SVG paint attributes take a CSS variable directly, so this is
  free dark-mode support with zero `dark:` variants anywhere in a chart.
- **All chart text is an HTML overlay, percent-positioned over the SVG —
  never SVG `<text>`.** Every chart here sets
  `preserveAspectRatio="none"` on its `<svg>` so the plot fills its box
  exactly; that same setting stretches SVG text unevenly. An HTML overlay
  also inherits the site's fonts and theme automatically.
- Root SVG carries `role="img"` and an `aria-label` built from the data
  itself, the same pattern `src/lib/data-explorer.ts`'s alt-text functions
  already use for the PNG gallery.
- Numbers are always `tabular-nums`.
- Hover is a bonus, not the only way to read a chart — every value that
  matters is already printed as a direct label. `hover.ts`'s
  `nearestByX`/`nearestDot` generalize the pointer-hit-testing logic; don't
  reimplement per-dot hit circles (see `nearestDot`'s comment for why).
- **Empty state**: a dashed-border card with a muted one-line explanation —
  the existing pattern in `growth-chart.tsx` and `comparison-chart.tsx`.
- Charts add no animation; if one ever does, gate it on
  `prefers-reduced-motion` per `BRANDING_AND_DESIGN.md`'s Motion section.

## Axis-domain honesty

Carried forward from `graph-shared.ts`'s original comments, now policy for
every chart, not just the timeline:

- **Pin a time axis to the whole relevant span, not just the plotted data**,
  when an absence is itself informative — a question last raised a decade
  ago should show a decade of empty space, not silently rescale until its
  last point sits at the (falsely current-looking) right edge.
- **Report the true first/last data point in captions even when the axis
  is padded** to round numbers for layout — the axis bounds and the caption
  bounds are allowed to differ, but the caption must never overstate them.
- **Redundant encoding for color-blind readers**: where position and color
  both carry the same information (a lane plus a color, a sort order plus a
  highlight), keep both — don't drop the redundant channel to save a pixel.
- **Nearest-wins pointer hit-testing with a give-up radius**, not a hit
  circle per mark — dense axes overlap per-mark targets and the last-painted
  one silently wins; a single generous hit-test layer keeps every mark
  reachable at any chart width.

## Extending the kit

Adding a chart of one of the four types above: use the existing component
and wire real data through a server-component figure (see
`src/components/charts/figures/` and `figures/index.tsx`'s
`DATASET_FIGURES` registry) — don't hand-type numbers into a chart's props;
compute them from committed JSON or a `src/lib/data.ts` query the same way
every figure here does.

Adding a genuinely new chart type: add it under `src/components/charts/`,
follow this guide's anatomy/axis/label/color rules, and add a row to the
"when to use which" table above.

**Known gap, not yet migrated**: `src/components/evangelical-quiz/group-breakdown-chart.tsx`
is a div-based diverging bar chart that predates this kit. It's live and
correct — leave it as-is rather than risk a live page for a style-only
pass — but a future cleanup should bring it onto `StackedBars` (or a
diverging variant of it) so the site has one stacked-bar implementation,
not two.
