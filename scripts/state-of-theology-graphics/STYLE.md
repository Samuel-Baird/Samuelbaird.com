# State of Theology graphics: website house style

**This is the website's style, not the social-media one.** @ithinkisam's
Instagram graphics have their own established style, documented in
[`STATISTICS_STYLE_GUIDE.md`](../social-graphics/STATISTICS_STYLE_GUIDE.md)
in `scripts/social-graphics/` — same color palette and typography as
here, but built for a feed (an optionally punchy title, a post-length
write-up alongside it). The website's [Data Explorer](../../src/app/data-explorer/)
is a different medium with a different job — a reader is here to look up
what the data actually says, not to be pulled through a feed — so it
departs from the social style on two points: **how a chart's title is
written** and **background color**. See "Titles: neutral, not editorial"
and the Palette section below for both.

**Status: the real website generator doesn't exist yet.** The palette and
type are locked (shared with the social style), but dedicated
website-specific R (or other) generator code is deliberately not being
built yet. `render_chart.py` — a Python/matplotlib script, not the eventual
generator — reads the quiz's full `data.json` directly and can render every
item (`--all`), so all 36 current statements have a graphic; that's a
depth-of-coverage milestone, not a signal that the pipeline itself is
finished. When the real website generator gets built, it should follow
this doc; update this doc first if that build changes anything here.

This doc is a distillation of two sources: the established R scripts —
[`state_of_theology_charts.R`](../social-graphics/state_of_theology_charts.R)
and [`state_of_theology_groups.R`](../social-graphics/state_of_theology_groups.R) —
and `STATISTICS_STYLE_GUIDE.md` itself, adapted for the website's own title
rule. If you change the shared palette or type, update `STATISTICS_STYLE_GUIDE.md`,
this file, [`scripts/ryan-burge/STYLE.md`](../ryan-burge/STYLE.md), and
[`scripts/chart_style.py`](../chart_style.py) (captions, mobile font floors,
heatmap gradients — the pieces every dataset folder now imports rather than
copy-pasting) together with `render_chart.py` — an undocumented style isn't a
style, it's a one-off.

## Row order, if a future chart here needs one

This dataset's existing charts use a fixed, identity-based color-per-tradition
palette (amber/moss/slate/wine/teal — see the Palette section below), and
that identity read comes with a fixed, curated row order that stays as-is.
But if a future chart here is a one-row-highlighted magnitude comparison
(single value per group, sorted by that value) rather than an identity read,
use `chart_style.sort_groups` instead of hand-curating an order — see
`BRANDING_AND_DESIGN.md`'s "Charts" section for the site-wide rule (sort
highest to lowest by the chart's own statistic; a named "Other" catch-all
sinks below every substantive row, an "average" aggregate sinks below even
that, and a total-population row, if present, sinks to the very bottom) and
`scripts/pew-rls/STYLE.md`'s "Magnitude bar" section for a worked example.

## Format

1080×1350px (Instagram 4:5). R: `ggsave(..., device = ragg::agg_png, width = 9,
height = 11.25, dpi = 120)`. Python: matplotlib figure `9in × 11.25in` at
`dpi=120` — same numbers, same result.

## Palette

| Token | Hex | Use |
|---|---|---|
| Ink | `#1A1A1A` | Titles, axis labels |
| Paper | `#FFFFFF` | Figure and panel background |
| Muted | `#6E6A63` | Subtitles, captions, source lines |
| Grid | `#D9D5CC` | Gridlines, dividers (by-year style only — see Composition) |

**Paper is pure white here, deliberately different from the Instagram
scripts' cream (`#F7F5F0`).** Every other token — ink, muted, grid, and the
full group palette below — is shared between the two styles. White
background is a website-specific requirement; don't "fix" it back to cream
by copying the R scripts' constant.

Group colors — consistent across every chart; a given group is always this
color, no exceptions:

| Group | Hex | Name |
|---|---|---|
| Evangelical | `#C9721C` | amber |
| Black Protestant | `#5B7553` | moss |
| Mainline | `#4E5D80` | slate |
| Roman Catholic | `#8C4A5F` | wine |
| All U.S. adults | `#2C7B8C` | teal |
| Other | `#8E8B84` | gray |

`Other` is in the R scripts' palette but is dropped from newer charts (see
[the evangelical-quiz workbook's own README](../evangelical-quiz/README.md) —
that survey category "mixes unrelated traditions, so its numbers aren't
interpretable"). Keep the color reserved for it in case a chart ever needs
it again, but don't use it for anything else.

`@ithinkisam` (the handle in every caption) renders in the amber
Evangelical color, bold — not muted, it's the one caption element meant to
stand out.

**Bar-color distinctness.** When one chart uses more than one bar hue, every
hue must come from a documented palette — the identity palette above, the
pew-rls rate tokens, or evenly-spaced picks from the site's 7-step ordinal
ramp (`--chart-ordinal-1..7`) — never adjacent ramp steps assigned to
adjacent segments, which reads as one smeared gradient rather than distinct
categories. Cap of 4 non-gray hues per chart, matching
[`docs/CHARTS.md`](../../docs/CHARTS.md)'s `MAX_SERIES`; context/gray bars
(the highlight-vs-gray convention) don't count against that cap. Any
same-hue light/dark pairing (like the decline chart's confident/uncertain
tones below) must clear the 60%-tint precedent: at least 3:1 non-text
contrast against white, and a lightness difference obvious without relying
on hue discrimination.

## Typography

- **Titles**: Roboto Slab, Bold. Nothing else uses this family — it's the
  one serif accent against an otherwise sans-serif chart. The title carries
  the quoted survey statement itself (see "Titles: neutral, not editorial"),
  so nothing else needs to quote it again.
- **Everything else** (subtitle, axis labels, value labels, caption):
  Roboto Condensed. Regular for body text and source lines; Bold for value
  labels, axis category labels, and the handle.

Font files (Apache 2.0, from Google Fonts) live in [`fonts/`](fonts/) next
to `render_chart.py` for the Python path. The R path expects the same
families installed as system fonts (`ragg`/`systemfonts` discover them from
the OS, not from a bundled file).

## Titles: accurate, not editorial

A title must do one of two jobs, and nothing else:

- **Measurement title** — what the data measures: the survey statement
  verbatim in quotes (`"The Bible is 100% accurate in all that it
  teaches"`), or a neutral description of the item ("Prayer frequency",
  "Attendance frequency, full distribution").
- **Factual-summary title** — a plain statement of what the chart shows,
  readable as true directly off a printed number on the chart itself
  ("Latter-day Saints report the highest weekly attendance", "Most
  traditions have lost more members than they gained").

**Both are equally house style.** What's still banned is spin. A
factual-summary title must clear all three:

1. **Verifiable from a value label already on the chart** — no outside
   knowledge required to confirm it's true.
2. **Direction words, not judgment words.** "Highest", "fewest", "more than
   half" are fine; "problem", "collapse", "surge", "alarming" are not — those
   hand the reader a conclusion the chart itself doesn't establish.
3. **No unplotted cause, motive, or trend.** A title can say what a chart
   shows; it can't say why, or what happens next, unless that's also a
   plotted value.

"America's Arianism problem" stays a social-only title (a judgment word, and
not literally readable off a bar). "A majority of evangelicals deny the
Trinity" is a legal website title *if and only if* the chart's own printed
value shows that majority.

This is a loosened version of this doc's former "always neutral" rule.
`STATISTICS_STYLE_GUIDE.md`'s social style is unchanged and still keeps its
own latitude to be punchier than either mode here — see that doc for the
social title rule.

## Composition

Every chart:

1. **Title** — top-left, Roboto Slab Bold, ink, per "Titles: accurate, not
   editorial" above. This is the largest, most prominent text on the chart —
   it IS the headline, there's no separate one above it. Wrap it across as
   many lines as it needs.
2. **Subtitle**, one line, Roboto Condensed, muted, directly under the
   title: "Share who strongly agree or somewhat agree, {year}." Always
   *agree* — measuring the same direction on every chart is itself part of
   staying neutral; picking disagree for whichever items would read more
   dramatically that way would be a framing choice, not a wording one.
   Never round "strongly + somewhat" into an unlabeled "% agree."
3. **The chart** — no chart title/axis title, no legend (colors are
   self-explanatory once you know the palette above; a caption line
   documents it if needed). Bars are colored per the group palette; value
   labels are bold text in the same color as the bar, placed just past the
   bar's end. Two established layouts:
   - **By religious tradition** (`state_of_theology_groups.R`,
     `render_chart.py`): horizontal bars, one wave, no gridlines
     (`panel.grid = element_blank()`), y-axis category labels bold ink.
   - **By survey year** (`state_of_theology_charts.R`): vertical grouped
     bars, one pair (Evangelical, All U.S. adults) per year, light
     horizontal gridlines only (`grid` token, thin), x-axis category labels
     bold ink.
4. **Caption**, bottom-anchored (see "Footnotes" below), small (≈10-11.5pt,
   exempt from the mobile floors below — fine print is allowed to stay fine
   print), muted, left-aligned:
   - Sponsor/fielder line: "The State of Theology survey · sponsored by
     Ligonier Ministries, conducted by Lifeway Research"
   - What "group" means for that chart (by-tradition charts: "Groups are
     religious tradition (denomination and church association)."
     By-year charts: "Evangelicals are classified by affiliation.")
   - Sample size and margin of error for the wave(s) shown
   - `@ithinkisam`, bold, amber

No drop shadows, no gradients, no 3D, no rounded bar corners — flat fills
only. (Heatmap ramps are the one sanctioned exception to "no gradients" — see
[`scripts/ryan-burge/STYLE.md`](../ryan-burge/STYLE.md) — and even there the
ramp is stepped per-cell, not a true continuous gradient fill.)

## Footnotes: bottom-anchored

The caption block anchors to the very bottom of the canvas — its lowest
line (the `@ithinkisam` handle, where present, otherwise the last source
line) sits at `y = 0.030`, with every line above it stacked upward. This
replaces the old pattern of a hardcoded `CAPTION_TOP` constant that the
caption was drawn downward from regardless of how much text it actually
had. Whatever vertical space the caption doesn't use belongs to the chart
above it — a short caption should mean a taller chart, not empty space.

Use [`chart_style.draw_caption_bottom(...)`](../chart_style.py) rather than
hand-rolling this. Its return value is the caption's actual top edge, which
feeds directly into the "vertical layout: centering the plot band" rule
(`scripts/pew-rls/STYLE.md`) as `caption_top` — call it *before* laying out
the chart's own axes. Caption grammar (sponsor line, population note, N,
handle) is unchanged; only its position and how that position is computed
changed.

## At-a-glance legibility and mobile floors

These images are read most often on a phone: a 1080px PNG renders at
roughly 335 CSS px in the `/graphics` gallery, about 1/3 scale. Every text
element that carries data has to survive that scale-down, or the chart
stops making sense at a glance — which defeats the point of a chart. Minimum
sizes at this pipeline's canvas (1080×1350px, dpi 120, so 1pt ≈ 1.67px):

| Element | Floor |
|---|---|
| Title (Roboto Slab Bold) | 24pt |
| Subtitle | 12.5pt |
| Value/data labels (bold) | 13pt |
| Axis / category / row / column labels (bold) | 12pt |
| Heatmap cell values (bold) | 12.5pt |
| Heatmap gradient-strip legend (min/mid/max) | 12pt |
| **Bar-chart legend/key text** | **24pt** |
| Footnotes/captions | exempt — 9-10.5pt as today |

These floors live in [`scripts/chart_style.py`](../chart_style.py) as `MIN`.
A render script may go bigger than a floor, never smaller. If content can't
fit at the floor — a heatmap with too many rows, a label with too many
words — that's a sign the chart is too dense for one image, not a reason to
shrink text past the point a phone screen can show it. Split the chart
before you shrink the type. This doc's existing "suppress a label once it
can't fit" rule (via `docs/CHARTS.md`) now has a number attached to what
"can't fit" means.

**Bar-chart legends/keys are ~2x the size of every other label** (24pt vs.
12-13pt elsewhere). A legend swatch-plus-word is easy to lose entirely at
1/3 scale in a way a data label sitting on its own bar isn't — the color
alone has to carry the meaning, so the word next to it has to survive the
scale-down at least as well as everything else does, if not better.

A matplotlib gotcha this floor ran into: **`ax.legend(fontsize=..., prop=a_FontProperties_instance)` silently ignores `fontsize`** — whichever
size (if any) is already baked into `prop` wins, and every render script's
`fonts["bold"]` loads at matplotlib's default (10pt) unless told otherwise.
The reliable fix, already used for axis tick labels throughout this
pipeline, is two calls: create the legend, then loop
`for text in legend.get_texts(): text.set_fontsize(MIN.LEGEND)` — `Text.set_fontsize()` overrides directly, independent of `prop`. Don't trust
`legend(fontsize=...)` alone to do anything when `prop=` is also passed.

Sizing a legend up this much means it needs real room, computed exactly —
see `chart_style.LEGEND_ROW_HEIGHT` and the worked formula in its docstring
for reserving that room and anchoring the legend to the figure (not the
narrower axes box) so a multi-word legend has the full canvas width to lay
out in.

## Always check for overlap and spillover

Before a render is considered done — every time a chart's layout changes,
not just the first time — open the actual PNG and look for:

- **Text overlapping other text.** A bigger label, a longer legend, an extra
  wrapped title line, or more rows than the last chart you tested can all
  push one text block into another. This has actually happened in this
  pipeline: a legend sized up for mobile legibility silently overlapped the
  caption underneath it because the reserved space was guessed rather than
  measured.
- **Text or a swatch spilling outside its own bar, cell, or legend key.** A
  value label wider than the bar it's printed on, a legend column wider
  than the space reserved for it.
- **Anything clipped at the canvas edge.** A wide legend centered on the
  axes' (not the full canvas') width is a common way for this to happen —
  see "Bar-chart legends/keys," above, for the fix.

Checking the rendered PNG at full size catches most of this; a chart that
looks fine at full size can still fail at the 1/3-scale gallery view (see
"At-a-glance legibility," above), so check there too when the layout is new
or has meaningfully changed. When a chart is parameterized (a shared
render function called for several items with different row counts, label
lengths, or value ranges), check more than one instance of it — the one
with the most rows, the longest label, and the widest value are where
overlap and spillover actually show up, not necessarily the first one you
render.

## Where graphics live on the website

Not a rendering rule, but part of the spec: every dataset's graphics get
their own page — `/data-explorer/<slug>/graphics` — a gallery of every
graphic for that dataset, each with its own download link (a plain
`<a download>` on the PNG; these are static files, nothing to gate). The
dataset's own page (`/data-explorer/<slug>`) shows a small preview
thumbnail of one graphic, below the quiz card if that dataset has one,
linking through to the gallery — not the full graphic inline. See
[`src/lib/data-explorer.ts`](../../src/lib/data-explorer.ts) for the
registry shape (`Dataset.graphics`) and
[`src/app/data-explorer/[slug]/graphics/page.tsx`](../../src/app/data-explorer/%5Bslug%5D/graphics/page.tsx)
for the gallery page itself.

## Adding an item

There's no canonical website generator yet (see Status, above) —
`render_chart.py` is the only generator for this style right now. When the
real website generator is built (in whatever language), point it at this
doc and update the workflow described here.

**`render_chart.py` reads directly from the quiz's own `data.json`** — it
never hand-enters a percentage. Adding a graphic for a new item is a data
change one level up: fill in that item in the workbook, regenerate
`data.json` (`scripts/evangelical-quiz/build_data.py`), then:

```bash
# One item, explicit output path:
python render_chart.py --item <item_id> --out <path>.png

# Every item in data.json, written as <item_id>.png:
python render_chart.py --all --out-dir ../../public/data-explorer/state-of-theology
```

`src/lib/data-explorer.ts`'s `stateOfTheologyGraphics()` builds the
gallery's metadata (titles, alt text, per-group percentages) from that same
`data.json` too, via `groupBreakdownRows()`/`fiveColumnPct()` — so the
chart image, the gallery page, and the quiz itself can never quietly
disagree with each other. Never hand-type a percentage into any of the
three; if a number needs to change, it changes in the workbook and
everything downstream regenerates.
