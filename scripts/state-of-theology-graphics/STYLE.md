# State of Theology graphics: website house style

**This is the website's style, not the social-media one.** @ithinkisam's
Instagram graphics have their own established style, documented in
[`STATISTICS_STYLE_GUIDE`](https://github.com/Samuel-Baird/ithinksam_statistics/blob/main/STATISTICS_STYLE_GUIDE)
in the `ithinksam_statistics` repo — same color palette and typography as
here, but built for a feed (punchy editorial titles, a post-length write-up
alongside it). The website's [Data Explorer](../../src/app/data-explorer/)
is a different medium with a different job — a reader is here to look up
what the data actually says, not to be pulled through a feed — so its one
real departure from the social style is **how a chart's title is written**;
see below.

**Status: the real website generator doesn't exist yet.** The palette and
type are locked (shared with the social style), but the actual
website-specific R (or other) code is deliberately not being built yet —
holding until the fuller dataset is delivered, so the pipeline gets
designed against real data rather than one item. `render_chart.py` and the
one graphic it's produced so far are a placeholder proving the style holds
up outside a social-post context, not the finished thing. When the real
website generator gets built, it should follow this doc; update this doc
first if that build changes anything here.

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
| Paper | `#F7F5F0` | Figure and panel background — never white |
| Muted | `#6E6A63` | Subtitles, captions, source lines |
| Grid | `#D9D5CC` | Gridlines, dividers (by-year style only — see Composition) |

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
style, which calls for "a short, punchy claim... not a variable name" —
that's the right call for a feed post competing for a scroll, and it stays
the house style there. It's the wrong call for a page whose whole point is
letting someone check what a dataset actually says. Don't port the punchy
convention into this doc's charts, and don't port the neutral convention
back into the Instagram scripts — they're solving different problems on
purpose.

## Composition

Every chart:

1. **Title** — top-left, Roboto Slab Bold, ink, the survey statement
   verbatim in quotes (see above). This is the largest, most prominent
   text on the chart — it IS the headline, there's no separate one above
   it. Wrap it across as many lines as it needs.
2. **Subtitle**, one line, Roboto Condensed, muted, directly under the
   title: "Share who strongly {agree|disagree} or somewhat {agree|disagree},
   {year}" — state the direction being measured explicitly. Never round
   "strongly + somewhat" into an unlabeled "% agree."
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

## Adding an item

There's no canonical website generator yet (see Status, above) —
`render_chart.py` is the only generator for this style right now. When the
real website generator is built (in whatever language), point it at this
doc and update the workflow described here.

**Python** (`render_chart.py`), for now: add a key to the `ITEMS` dict —
`item_id: (statement, direction, year, {group: percent, ...})` — and run:

```bash
python render_chart.py --item <item_id> --out <path>.png
```

Pull the percentages from the same place the quiz's own data comes from —
[`scripts/evangelical-quiz/build_data.py`](../evangelical-quiz/build_data.py)'s
output, or directly from the State of Theology data explorer / microdata
(see that script's README for how to fetch and verify it) — never
transcribe a number you haven't cross-checked against a real source.
