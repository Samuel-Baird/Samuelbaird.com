# State of Theology graphics: house style

The visual style for @ithinkisam's State of Theology graphics, extracted
from the R scripts that established it — [`state_of_theology_charts.R`](https://github.com/Samuel-Baird/ithinksam_statistics/blob/main/state_of_theology_charts.R)
(comparison across survey years, Evangelical vs. All U.S. adults) and
[`state_of_theology_groups.R`](https://github.com/Samuel-Baird/ithinksam_statistics/blob/main/state_of_theology_groups.R)
(comparison across religious traditions, one wave). **Those R scripts are
the canonical generator** — this doc exists so the style is written down
somewhere instead of living only in code, and so [`render_chart.py`](render_chart.py)
(a Python/matplotlib port for when R/ggplot2/ragg isn't available — this is
what a Claude Code session reaches for) can be kept visually identical to
them rather than drifting into its own look.

If you change the R scripts' palette, type, or layout, update this file and
`render_chart.py` in the same pass — an undocumented style isn't a style,
it's a one-off.

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
  one serif accent against an otherwise sans-serif chart.
- **Everything else** (subtitle, quote, axis labels, value labels, caption):
  Roboto Condensed. Regular for body text and source lines; Bold for value
  labels, axis category labels, and the handle; Italic for the quoted
  survey statement.

Font files (Apache 2.0, from Google Fonts) live in [`fonts/`](fonts/) next
to `render_chart.py` for the Python path. The R path expects the same
families installed as system fonts (`ragg`/`systemfonts` discover them from
the OS, not from a bundled file).

## Composition

Every chart:

1. **Title** — top-left, Roboto Slab Bold, ink. A short editorial line, not
   a restatement of the question (e.g. "A majority also deny the Trinity,"
   not "Percent agreeing Jesus was created").
2. **Subtitle**, two lines, Roboto Condensed, muted:
   - The survey statement itself, verbatim, in quotes, italic.
   - "Share who strongly {agree|disagree} or somewhat {agree|disagree},
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

**R** (canonical): add a row (or set of rows) to the `tribble()` data block
and an entry to the `items` list, in either script depending on which
layout fits — see the scripts themselves for the exact shape.

**Python** (`render_chart.py`): add a key to the `ITEMS` dict —
`item_id: (title, quote, direction, year, {group: percent, ...})` — and run:

```bash
python render_chart.py --item <item_id> --out <path>.png
```

Pull the percentages from the same place the quiz's own data comes from —
[`scripts/evangelical-quiz/build_data.py`](../evangelical-quiz/build_data.py)'s
output, or directly from the State of Theology data explorer / microdata
(see that script's README for how to fetch and verify it) — never
transcribe a number you haven't cross-checked against a real source.
