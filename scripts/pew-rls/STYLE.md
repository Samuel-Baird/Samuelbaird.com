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

## Data source and regeneration

Never hand-type a percentage, per the existing house rule. The numbers
come from `scripts/pew-rls/switching_rates.py`, which reads the RLS
microdata directly (`FRMREL`, `CURREL`, `RELTRAD`, `WEIGHT`, and all 500
replicate weight columns) and writes
`docs/datasets/pew-rls-2023-24/switching-rates.json`. `render_switching_chart.py`
reads only that JSON — regenerate the JSON first if the underlying numbers
ever need to change, then re-render:

```bash
python scripts/pew-rls/switching_rates.py
python scripts/pew-rls/render_switching_chart.py \
  --out ../../public/data-explorer/pew-religious-landscape-study/switching-rates.png
```

`src/lib/data-explorer.ts`'s Pew entry builds its graphic metadata (alt
text especially — it carries the full raised/current numbers per group,
since the image itself only labels the net-change value) from that same
JSON, so the image, the alt text, and the gallery page can't quietly
disagree.

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

## Magnitude bar (highlight-vs-gray) and paired bar

Most of the dataset's remaining backlog sections (childhood formation,
family and household, practice, beliefs, spiritual experience, public life
and society) ship as a **magnitude bar**: one row per group, a single
percentage, sorted by the site-wide row-order rule — highest to lowest by
each group's own value, with catch-all/aggregate rows ("Other Christian,"
"Christian average," and the like) always sunk below every substantive row
regardless of their own number, sorted by value within that bottom tier —
via `chart_style.sort_groups` (see `BRANDING_AND_DESIGN.md`'s "Charts"
section for the canonical statement of the rule). There's no per-tradition
identity color and no decline signal here, so these reuse the site's
highlight-vs-gray convention instead — Latter-day Saint in `--accent`
(`#1f4f7a`), every other group in a bar-safe gray (`#8f8b82`, a lightened
`--muted` that still reads as a distinct fill at full opacity, unlike the
line chart's stroke-only `CONTEXT_GRAY`). The population each chart draws
from (Christian only, Christian + other religions, or every
religiously-affiliated tradition individually + the unaffiliated) still
varies item to item — a `GROUP_ORDER`/`group_order` constant still says
*which* group keys belong in a given chart, it just no longer dictates the
order they're drawn in; see each compute script's own docstring
(`childhood_formation.py`, `family_household.py`, `practice.py`,
`beliefs.py`, `spiritual_experience.py`, `public_life.py`) for which set a
given chart uses and why.

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
