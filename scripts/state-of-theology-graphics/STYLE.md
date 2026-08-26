# State of Theology graphics: website house style

**This is the website's style, not the social-media one.** @ithinkisam's
Instagram graphics have their own established style, documented in
[`STATISTICS_STYLE_GUIDE`](https://github.com/Samuel-Baird/ithinksam_statistics/blob/main/STATISTICS_STYLE_GUIDE)
in the `ithinksam_statistics` repo — same color palette and typography as
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
[`state_of_theology_charts.R`](https://github.com/Samuel-Baird/ithinksam_statistics/blob/main/state_of_theology_charts.R)
and [`state_of_theology_groups.R`](https://github.com/Samuel-Baird/ithinksam_statistics/blob/main/state_of_theology_groups.R) —
and `STATISTICS_STYLE_GUIDE` itself, adapted for the website's own title
rule. If you change the shared palette or type, update `STATISTICS_STYLE_GUIDE`,
this file, and `render_chart.py` together — an undocumented style isn't a
style, it's a one-off.

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

## Titles: neutral, not editorial

**The title is the survey statement itself, verbatim, in quotes — nothing
else.** Not "A majority also deny the Trinity." Not any other line that
tells the reader what to conclude before they've seen a bar. Set it large
and prominent (it's the biggest thing on the chart, per Composition below)
but let it be neutral: the reader should be able to look at the title and
the bars and reach their own read, not be handed one.

This is the one deliberate departure from `STATISTICS_STYLE_GUIDE`'s social
style. The two guides aren't the same rule applied twice:

- **Website (this doc): always neutral.** Every chart here is titled with
  the bare statement. No exceptions — a reader is here to check what the
  data says, not to be pulled through a feed.
- **Social (`STATISTICS_STYLE_GUIDE`): title is a judgment call.** A post
  may use a punchy or clever line ("America's Arianism problem") when one
  fits, or may not — it's not a rule that every post needs a claim, just
  that the option is open there in a way it deliberately isn't here.

Don't port the punchy convention into this doc's charts (it's specifically
not allowed here), and don't treat "always neutral" as something the social
side owes either — they're two different jobs.

## Composition

Every chart:

1. **Title** — top-left, Roboto Slab Bold, ink, the survey statement
   verbatim in quotes (see above). This is the largest, most prominent
   text on the chart — it IS the headline, there's no separate one above
   it. Wrap it across as many lines as it needs.
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
4. **Caption**, bottom-left, small (≈11.5pt), muted, left-aligned:
   - Sponsor/fielder line: "The State of Theology survey · sponsored by
     Ligonier Ministries, conducted by Lifeway Research"
   - What "group" means for that chart (by-tradition charts: "Groups are
     religious tradition (denomination and church association)."
     By-year charts: "Evangelicals are classified by affiliation.")
   - Sample size and margin of error for the wave(s) shown
   - `@ithinkisam`, bold, amber

No drop shadows, no gradients, no 3D, no rounded bar corners — flat fills
only.

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
