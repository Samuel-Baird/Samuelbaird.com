# Social media posts — restyled to the Data Explorer look

Two standalone R/ggplot2 scripts that generate Instagram carousel slides
(1080×1350) for the State of Theology survey, restyled to match this repo's
Data Explorer chart pipeline instead of an ad-hoc palette.

- `post1-evangelical-trends/post1_evangelical_trends.R` — evangelicals vs.
  all U.S. adults, 2016–2025.
- `post2-tradition-comparison/post2_tradition_comparison.R` — four
  traditions compared on nine statements.

Each folder gets its own `png/` output directory when you run its script
(`Rscript post1_evangelical_trends.R` from inside that folder, or with a
full path — the script locates its own directory either way).

## Requirements

R packages: `ggplot2`, `dplyr`, `tibble`, `forcats`, `ggtext`, `ragg`,
`systemfonts`. Fonts are **not** required system-wide — both scripts
register Roboto Condensed + Roboto Slab straight from this repo's
`scripts/state-of-theology-graphics/fonts/` at runtime via
`systemfonts::register_font()`, the same TTFs the Python Data Explorer
chart renderer for this same survey uses.

## Token mapping (repo → chart element)

Canonical source: `scripts/state-of-theology-graphics/render_chart.py`
(this repo's own Python renderer for the same survey — same 1080×1350
canvas, same fonts, same five-group palette) and `scripts/chart_style.py`.

| Repo token | Value | Used for |
|---|---|---|
| `render_chart.py` `INK` | `#1A1A1A` | Titles, axis/value labels |
| `render_chart.py` `PAPER` | `#FFFFFF` | Canvas background — **changed from the old Instagram cream `#F7F5F0`**; the explorer deliberately uses pure white |
| `render_chart.py` `MUTED` | `#6E6A63` | Subtitle, caption/footnote, secondary text |
| `render_chart.py` `GRID` (= `chart_style.py` `BORDER`) | `#D9D5CC` | Gridlines, legend divider |
| `PALETTE["Evangelical"]` | `#C9721C` (amber) | Evangelical series |
| `PALETTE["Black Protestant"]` | `#5B7553` (moss) | Black Protestant series (post2 only) |
| `PALETTE["Mainline"]` | `#4E5D80` (slate) | Mainline series (post2 only) |
| `PALETTE["Roman Catholic"]` | `#8C4A5F` (wine) | Roman Catholic series (post2 only) |
| `PALETTE["All U.S. adults"]` | `#2C7B8C` (teal) | All U.S. adults series (post1 only — see below) |
| Roboto Condensed / Roboto Slab | — | Body / display fonts, both scripts, self-hosted from `state-of-theology-graphics/fonts/` |

Every one of these already matched almost exactly what the R scripts had
hardcoded before (amber/teal/wine/moss/slate/ink/muted/grid were already
the right hex values) — the one real change is the canvas background,
cream → white. Everything else in this table is just now a named constant
with a comment citing where it came from, so it stays in sync when the
design system changes: re-check `render_chart.py`'s `PALETTE`/`INK`/
`PAPER`/`MUTED`/`GRID` and update both scripts' constant blocks together
if those ever move.

## What changed

- **Titles**: 34pt → 48pt (both scripts' per-item charts; the two
  already-46pt text-card titles bumped to 48pt too for consistency), via
  `element_textbox_simple` so a long title wraps to a second line instead
  of running off the canvas. Checked every regenerated PNG (both an
  automated right-edge clipping scan and a visual spot-check of the
  longest titles in each script, including post2's "In most traditions,
  half say he isn't God") — **nothing clipped or wrapped badly**, no
  wording changes needed.
- **Footnote**: stripped to exactly two lines, `Data: The State of
  Theology survey` / `@ithinkisam`, muted, small (11.5pt, unchanged size).
  All sponsor/fielder/method/panel-size/margin-of-error copy and every
  per-slide `notes` entry removed — the `notes` field is gone from both
  scripts' `items` lists, and the caption-branching code that used to
  splice notes in ahead of the source line is gone too, not just unused.
- **post2 only**: `"Other"` and `"All U.S. adults"` removed — both the
  data rows and their palette entries (`gray`/`teal` constants deleted
  since nothing in that file uses them anymore). Four bars per chart,
  ordered Evangelical / Black Protestant / Mainline / Roman Catholic, as
  specified.
- **post1 groups: decided — kept.** A throwaway preview showed what
  dropping "All U.S. adults" would do to the "Many roads" slide (the one
  where evangelicals sit 16 points below the national figure in 2025, 49%
  vs. 65%): as a single series it read as an unremarkable up-and-down
  46–58% line with no visible point, since the finding only exists as a
  comparison. Confirmed to keep both series everywhere in post1 — no code
  change needed there, it was never touched.
- Zero-based y-axes, every value label, and the 1080×1350 `ragg::agg_png`
  9×11.25in/120dpi output are all unchanged. No survey numbers were
  touched.

## Verification

R wasn't installed on this machine — it was installed for this task
(`winget install RProject.R`, packages into a user library) specifically
so both scripts could actually be run and every PNG regenerated and
inspected, rather than edited blind.

## What changed (round two: titles, decluttering, larger type)

- **Titles now quote the survey statement**, not a punchy claim — every
  per-statement chart slide in both scripts (post1's `make_chart`, post2's
  `make`). See `../STATISTICS_STYLE_GUIDE.md`'s updated "Title/subtitle/caption
  convention" for the rule. Hook cards, the intro/closing text cards, and
  post1's scorecard slide keep their thematic titles — none of them is
  about one measured statement, so there's no single question to quote.
  Long quotes step the title font down (post1: 40/34/30pt; post2: 48/40/34pt,
  by quote length) so the longest statements still wrap to at most three
  lines without crowding the chart below — checked every regenerated PNG,
  nothing clips or overlaps.
- **Decluttered subtitles**: the quote used to appear twice per slide (once
  in the subtitle, again — now — as the title). The subtitle line that
  restated it in italics is gone; each chart's subtitle is now just the
  direction line ("Share who strongly agree or somewhat agree, {year}")
  plus, where relevant, the color legend.
- **Larger type for readability**: subtitle 16→18pt; footnote/caption
  11.5→16pt everywhere (both scripts' chart, card, and hook functions),
  recolored to ink (was muted in a couple of spots) to match; post1's
  inline legend swatches (`■ Group`) bumped to an explicit 20pt so the
  color key survives Instagram's scaled-down feed view; post2's y-axis
  group labels 20→24pt, matching the site-wide "group/identity labels
  render at MIN.LEGEND" convention documented in
  `../../state-of-theology-graphics/STYLE.md`; post1's x/y axis tick labels
  17→19pt / 12.5→14pt.
- Both scripts' every PNG was regenerated and copied into
  `public/social-graphics/state-of-theology/post1/` and `post2/`; the
  gallery pages at `src/app/data-explorer/state-of-theology/social/post1`
  and `post2` had their own `SLIDES` captions updated to match the new
  quoted titles.

## What changed (round three: subtitle color, hook-slide type)

- **Per-statement chart subtitles are now ink (black), not muted gray** —
  both scripts' `plot.subtitle`, plus post1's scorecard (shares
  `theme_burge()`). Only the direction word itself (`agree`/`disagree`) is
  bold now, not the whole "strongly ... or somewhat ..." phrase — was
  `Share who <b>strongly agree or somewhat agree</b>`, now `Share who
  strongly <b>agree</b> or somewhat <b>agree</b>`.
- **Hook slides** (`make_hook`, post1 only — `hook_a_created.png`,
  `hook_b_not_god.png`, `hook_c_combined.png`): every non-headline text
  size bumped and recolored to ink/black — the `lines` block 30→34pt, the
  optional `kicker` 24→28pt (was muted gray), and hook_c's nested
  "61%/44%/55%" list 26→30pt. The giant headline stat (96pt) stays teal —
  it's the slide's de facto title, there's no `labs(title=...)` on a hook
  card to hold that role instead.
