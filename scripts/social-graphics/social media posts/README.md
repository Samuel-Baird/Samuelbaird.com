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

## What changed (round four: subtitles bigger, hook body ~half the headline, text-card sizes matched)

- **Chart subtitles bumped again**: 18→22pt in both scripts (`theme_burge()`
  in post1, `make()`'s `plot.subtitle` in post2), plus post1's inline
  legend swatches 20→22pt to match. post1's scorecard subtitle needed a
  manual `<br>` added (`Share of evangelicals by affiliation who strongly
  agree` / `or somewhat agree, 2022`) — at 22pt the un-wrapped line ran off
  the canvas edge.
- **Hook slides' `lines` text is now ~half the headline stat's size**:
  34→48pt (96pt headline / 2 = 48pt), per this rollout's explicit target.
  `kicker` and hook_c's nested percentage list went 28/30→36pt to keep the
  hierarchy under the bigger `lines` text. All three hook calls' manual
  `<br>` breaks had to be retightened for the larger size (e.g. "of
  American evangelicals say" → "of American evangelicals<br>say", to stop
  the line running off the right edge) — checked every regenerated PNG for
  clipping after the resize, not just after the initial edit.
- **"Words without weight" (post1) and "Still the beam" (post2) matched**:
  post1's text-card stats block 32→36pt and paragraph 20→24pt; post2's
  closing-card stats block 30→36pt and paragraph 22→24pt (now identical to
  post1's), 0_intro's single block 27→32pt. Both cards' `<br>` breaks were
  retightened for the larger sizes — "Across the four Christian traditions
  here:" and one Spirit-not-a-person line needed new breaks to stop
  clipping.

## What changed (round five: scorecard title dropped, text cards fill the canvas)

- **post1's scorecard (`9_scorecard.png`) lost its punchy title.** "Firmer,
  but not firm" is gone; the description that used to live in the subtitle
  ("Share of evangelicals by affiliation who strongly agree or somewhat
  agree, 2022") is now the title itself (34pt — the same >65-char step-down
  `make_chart` uses for a long title, since this description runs long).
  The subtitle is now just the color-key legend. Also dropped: "No
  statement clears 80%." (was the first subtitle line) and "Every statement
  is shown as the survey worded it; all bars are share who agree." (was the
  first caption line, above `SRC`) — the caption is now just `SRC`. The
  gallery page's own caption for this slide
  (`src/app/.../post1/page.tsx`) was updated to match the new title text.
- **"Words without weight" (post1) and "Still the beam" (post2) now fill
  the canvas instead of leaving empty space at the bottom**: title moved up
  (`plot.title`'s bottom margin and the plot's own top margin both shrunk),
  the smaller paragraph text bumped again (post1: 24→28pt; post2: 24→28pt),
  the stats block also bumped in post1 (36→40pt) to stay proportionate, and
  extra `<br>` breaks added between blocks so the larger text spreads
  further down the canvas. post2's shared `card()` function backs both
  `0_intro.png` and `11_closing.png`, so the title-position change applies
  to both, though only `11_closing.png`'s own body text was resized. Every
  `<br>` break in both cards was rechecked/retightened at the new sizes —
  none clip.

## What changed (round six: post3 matched to post1/post2's type sizes)

`post3-membership-scale/post3_membership_scale.py` (Python/matplotlib, not
R — see its own module docstring for why) generates a third carousel using
the same house style. It already had post1/post2's quote-as-title
convention and black/bold subtitle from earlier rounds; this round matched
its remaining type sizes to post1/post2's rounds three/four bumps:

- Subtitle (`SUB_FONTSIZE`) 18→22pt, matching post1/post2's chart subtitle.
- Y-axis tradition row labels 20→24pt, matching post2's y-axis group-label
  convention (MIN.LEGEND) — this pushed "Black Protestant" wide enough to
  clip past the figure's left edge, so `CHART_LEFT` widened 0.24→0.30 to
  give the bigger label room.
- Caption 11.5pt/muted → 16pt/ink, matching post1/post2's footnote. The
  caption's wrap width is character-count-based (`textwrap`), so it had to
  shrink roughly in proportion to the fontsize increase (132→95 chars) or
  the now-bigger text would run past the canvas edge.
- The bottom LDS-contrast block's old three-line title ("Total membership
  of The Church of Jesus Christ of Latter-day Saints") plus separate
  "Total U.S. membership, 2025" subtitle collapsed into one all-caps line,
  "U.S. LDS MEMBERSHIP, 2025", per explicit request — shorter, and reads
  at a glance same as the rest of the slide.

Every regenerated PNG was checked for the script's own built-in overlap
warning (LDS bar vs. caption) and visually spot-checked (longest 3-line
title, and the widest "Black Protestant" row) — no warnings, nothing
clips.
