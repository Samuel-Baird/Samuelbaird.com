# Pew RLS graphics: website house style, decline-chart extension

Shares the website graphics system established in
[`../state-of-theology-graphics/STYLE.md`](../state-of-theology-graphics/STYLE.md) —
same canvas (1080×1350, white background), same fonts (Roboto Slab Bold
titles, Roboto Condensed everything else, loaded from that folder's
`fonts/`), same "neutral, not editorial" title rule, same
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
