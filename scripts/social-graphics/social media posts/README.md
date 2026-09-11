# Social media posts — restyled to the Data Explorer look

Standalone scripts that generate Instagram-carousel-style slides for the
State of Theology survey, restyled to match this repo's Data Explorer
chart pipeline instead of an ad-hoc palette.

- `post1-evangelical-trends/post1_evangelical_trends.R` — evangelicals vs.
  all U.S. adults, 2016–2025. R/ggplot2, 1080×1350 (4:5).
- `post2-tradition-comparison/post2_tradition_comparison.R` — four
  traditions compared on nine statements. R/ggplot2, 1080×1350 (4:5).
- `post3-membership-scale/post3_membership_scale.py` — post2's same ten
  statements, converted from survey percentages to estimated raw
  headcounts, contrasted against the Church's own published U.S.
  membership. Python/matplotlib (see its own module docstring for why),
  1080×1350 (4:5).
- `post4-tradition-comparison-widescreen/post4_tradition_comparison_widescreen.R`
  — post2's exact data, copy, and styling, reformatted 1920×1080 (16:9)
  for platforms that want landscape instead of an Instagram-portrait
  carousel. R/ggplot2. If post2's data or copy ever changes, mirror the
  change here too - see "What changed (round nine..." below for the
  layout differences this reformat required.
- `post5-membership-scale-widescreen/post5_membership_scale_widescreen.py`
  — post3's exact data, copy, and styling, reformatted 1920×1080 (16:9),
  the same relationship post4 has to post2. Python/matplotlib. If post3's
  data or copy ever changes, mirror the change here too - see "What
  changed (round eleven..." below for the layout differences this
  reformat required (more involved than post4's, since this script hand-
  positions everything rather than relying on ggplot's automatic layout).

Each folder gets its own `png/` output directory when you run its script
(`Rscript post1_evangelical_trends.R` from inside that folder, or with a
full path — the script locates its own directory either way; post3's
script is run the same way but with `python3` instead of `Rscript`).

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

## What changed (round seven: scorecard bars are now all "tradition-consistent", not always "agree")

post1's scorecard (`9_scorecard.png`) used to plot every statement's %
agree, even though "agree" means something different depending on the
statement: agreeing with an orthodox social statement (the two Ethics
rows) is the tradition-consistent position, but agreeing with a Doctrine
row is NOT - every one of those five rows states a historic heresy
(Arianism, denial of the Trinity/Christ's deity, Pelagianism, religious
pluralism), so DISAGREEING is what's tradition-consistent there. Mixing
both under one "% agree" axis made the five Doctrine bars measure the
opposite of what the two Ethics bars did, without saying so.

- **Every bar is now "% giving the tradition-consistent response"**,
  and each bar's own label says which direction that was (`"77% Agree"`,
  `"30% Disagree"` - `dirword_cap()`), not just a bare percentage. Title
  changed from the (already non-editorial, previous-round) description
  to name this directly: "Share of evangelicals giving the
  tradition-consistent response, 2022".
- **The five Doctrine rows' plotted values flipped from % agree to %
  disagree**: arian 61→30, all_religions 58→35, spirit_force 55→34,
  good_by_nature 55→40, jesus_not_god 44→53. The Ethics rows are
  unchanged (sex/abortion stay % agree - already tradition-consistent
  agreeing; the homo row stays at 65, already % disagree from its
  original sourcing, just with the "— disagree" now-redundant suffix
  dropped from its statement text since the bar's own label says it).
- **Where the new disagree numbers came from**: `arian`'s disagree% (30)
  was already implicit in data.json's raw_pct. The other four had no
  disagree% published anywhere in this repo - Ligonier's public 2022
  report only breaks agree/disagree out by tradition for one of them
  (spirit_force: "Evangelicals are the mostly likely to Disagree (34%)").
  Recomputed all four directly from the State of Theology 2022
  respondent microdata (`responses-2022.csv`, same file
  `ARIAN_CSV_URL`/`build_data.py`'s `arian_wave_reference` already uses
  for `arian`'s own number): WT-weighted response share among RELTRAD==1
  (Evangelical) rows, summing strongly_disagree + somewhat_disagree,
  using each item's own 2022 Q-column (all_religions=Q21_3,
  jesus_not_god=Q22_3, spirit_force=Q23_1, good_by_nature=Q24_1, per the
  2022 Full Report PDF's own item numbering). Cross-checked two ways
  before trusting the numbers: the same computation's agree% for all
  five items lands within 1pt of this script's existing (unchanged) 2022
  agree numbers, and the recomputed spirit_force disagree% (34.2→34)
  matches Ligonier's own published bullet exactly.
- The value-label text is much longer now ("NN% Disagree" vs. the old
  bare "NN%"), so `scale_x_continuous`'s upper limit widened 118→200. A
  pixel-level scan (rightmost non-white column, not just a visual read)
  showed nothing past the canvas edge at 200, but the longest labels were
  touching the plot margin with zero breathing room - which reads as
  clipped even though it technically isn't, and did read that way once
  seen at full size outside this scan. Widened again, 200→260, which
  scanned back to a comfortable margin.

## What changed (round eight: post3 whitespace filled, two titles now match)

- **Both titles on every post3 slide now share one fontsize**: the
  bottom "U.S. LDS MEMBERSHIP, 2025" line used to always render at the
  fixed `TITLE_FONTSIZE` (34pt), while the top quoted-statement title
  steps down to 27pt for a long quote (>4 wrapped lines) - so a slide
  with a long quote had two visibly different-sized titles. The bottom
  title now reuses the top one's own `title_fontsize`/`line_step`
  variables instead of the fixed constants, so they always match.
- **Filled the whitespace between the LDS bar and the caption** by
  widening four gap constants (subtitle→chart, chart→divider,
  divider→bottom title, bottom title→bottom bar), without touching any
  font size or the bar-thickness constant (`SLOT_HEIGHT`, shared with the
  chart above and sized for the worst-case 3-line title). Before: gap
  ranged 0.105–0.205 (figure-fraction) depending on how many lines the
  top title took; after: 0.030–0.130. Checked every regenerated PNG
  against the script's own overlap warning (none fired) and
  visually spot-checked the tightest (3-line title) and loosest (1-line,
  "Abortion is a sin") cases.

## What changed (round nine: post4, post2 reformatted 16:9)

New post: `post4-tradition-comparison-widescreen/post4_tradition_comparison_widescreen.R`.
Same data, same per-item copy, same palette/fonts/sizes as
`post2-tradition-comparison` - only the canvas dimensions (1920×1080
instead of 1080×1350) and the layout math that depends on them changed.
If post2's data or copy ever changes, mirror the change here too.

- **Canvas**: `FIG_W_IN`/`FIG_H_IN` = 16/9 (vs. post2's 9/11.25), same
  120dpi. ggplot lays the panel out automatically around the title/
  subtitle/caption margins, so no manual axis positioning was needed
  (unlike post3's Python script) - changing the two dimensions was
  enough for the bar chart slides to reflow correctly.
- **Title wrap width**: 7.8in → 14.6in. The same quoted statements that
  wrapped to 2-3 lines in post2's narrower canvas now mostly fit on one
  line - checked every item, longest is 2 lines (`10_gender.png`,
  `9_homo.png`).
- **Text cards** (`0_intro.png`, `11_closing.png`) needed real
  rewrapping, not just a dimension change: post2's `<br>` breaks were
  short lines tuned for a 9in-wide canvas, which at 16in left the text
  stranded in a narrow left column against a mostly-empty right
  two-thirds of the frame - rewrapped onto fewer, longer lines so the
  text uses more of the width. That in turn overflowed `11_closing.png`
  past its caption (this canvas is 9in tall, 20% shorter than post2's
  11.25in, with the same absolute point-sized gaps) - fixed by shrinking
  two `<br><br><br><br>`/`<br><br><br>` paragraph gaps down to
  `<br><br>`, not by shrinking any font size.
- New Next.js page (`src/app/data-explorer/state-of-theology/social/post4/page.tsx`,
  copied from post2's own page and pointed at
  `/social-graphics/state-of-theology/post4/` with 1920×1080 image
  dimensions) and a new `socialSets` entry in `src/lib/data-explorer.ts`.

## What changed (round ten: post2 intro fills the canvas, post3 caption/title tweaks)

- **post2's `0_intro.png` ("Evangelicals won") now fills the canvas**:
  body text 32→48pt, rewrapped onto more/shorter lines (was 5 lines
  across two paragraphs, now 8) so the bigger text still fits without
  clipping and spreads further down toward the caption instead of
  leaving the bottom third empty. Note this was post2 only, per the
  request - `post4`'s copy of this same card (`post4-tradition-comparison-widescreen/png/0_intro.png`)
  is unchanged and now out of sync with post2's; mirror this edit there
  too next time post4 gets touched (see that script's own "SAME
  content... mirror the change here too" header comment).
- **post3's bottom title is now "U.S. LDS membership, 2025"**, not
  all-caps "MEMBERSHIP" - matches the top title's normal sentence case.
- **post3's caption is now one flowing gray paragraph, not two black
  lines**: color 16pt/INK → 16pt/MUTED (including the `@ithinkisam`
  handle - no amber highlight now, a deliberate one-off departure from
  the site-wide "handle stays amber" convention, per explicit request),
  and the old two-paragraph list (sources, then a separate "Estimated
  headcounts..." line) merged into one paragraph that leads with
  "Estimated headcounts, not survey sample sizes." before flowing
  straight into the source list inline. The merge changed how
  `textwrap.wrap` breaks the text, and the old `wrap_width=95` let the
  widest resulting lines run past the canvas edge (caught with the same
  pixel-level scan used earlier for post1's scorecard labels, not a
  visual read - this is genuinely easy to miss by eye at this
  resolution); narrowed to 85, checked clear with real margin.

## What changed (round eleven: post1 hook_c bold words, new post5 (post3 in 16:9))

- **post1's `hook_c_combined.png`** ("92% believe in the Trinity"): the
  words `created`, `not God`, and `a force` in its nested 61%/44%/55% list
  are now bold, matching the emphasis already given to the percentages
  themselves.

New post: `post5-membership-scale-widescreen/post5_membership_scale_widescreen.py`
- post3's exact data, per-item copy, and styling, reformatted 1920×1080
  (16:9) the same way post4 is post2 reformatted widescreen. If post3's
  data or copy ever changes, mirror the change here too.
- Unlike post4 (ggplot, automatic layout), post3/post5 hand-position every
  element with `fig.add_axes`/`fig.text` at figure-fraction coordinates -
  changing `FIG_W_IN`/`FIG_H_IN` alone does NOT reflow this script the way
  it did post4's. A figure-fraction *distance* means less absolute (inch)
  space at a shorter canvas height, which is backwards for anything that
  has to clear a fixed-size (point) font - most visibly, stacked title
  lines at the same point size would sit closer together with less
  leading. Introduced `VSCALE = 11.25 / FIG_H_IN` and multiplied every
  constant that exists to clear a line of text by it (`LINE_STEP`, the
  title's own top margin, the caption's `line_step`/`bottom`) so those
  hold their absolute size across both canvas heights. Left the pure
  whitespace/bar-thickness constants (section gaps, `SLOT_HEIGHT`) alone -
  nothing sets a minimum absolute size they have to clear, so letting the
  whole chart get proportionally shorter at the shorter canvas is fine.
- Title wrap width scales automatically from `TITLE_MAX_WIDTH_PX`
  (already a `FIG_W_IN`-derived formula in post3) - at 16in wide, every
  quote now wraps to at most 2 lines, down from up to 3 in post3's 9in.
- Caption `wrap_width` scaled up too (85 → 151, roughly ×16/9) - this is a
  character count, not a distance, so it doesn't need `VSCALE`; it needs
  to grow with the extra WIDTH instead, or the caption wraps into more
  (needlessly short) lines than the wider canvas actually requires.
- Verified with the same two checks as post3's own rollout: the script's
  built-in overlap warning (none fired across all 16 regenerated PNGs)
  and a pixel-level scan for the rightmost non-background pixel, run
  twice - once naively (caught the full-width divider line, a false
  positive - it's drawn edge-to-edge on purpose) and once restricted to
  the palette's actual text/bar colors (clean, 150px+ margin on every
  slide).
- New Next.js page (`src/app/data-explorer/state-of-theology/social/post5/page.tsx`,
  copied from post3's own page, pointed at
  `/social-graphics/state-of-theology/post5/` with 1920×1080 image
  dimensions and post4's two-column grid instead of post3's three-column
  one) and a new `socialSets` entry in `src/lib/data-explorer.ts`.
