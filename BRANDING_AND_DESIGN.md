# Latter-day Stats Branding and Design Guidelines

Last updated: August 10, 2026

This document is the design source of truth for the site. Read it before building
any new page or component, and follow it — the point is that a page added six
months from now still looks like it belongs to the same publication.

The current identity is **"the Archive"**: nineteenth-century print-almanac
conventions executed with modern data-journalism discipline, plus restrained
Deseret-era seasoning (a beehive mark, a honey accent, and a decorative Deseret
alphabet flourish). It replaced an earlier generic look built on rounded-full
pills, `rounded-2xl` white cards with soft shadows, and nineteen different bright
Tailwind pastels for tags. **Do not reintroduce those.**

The organizing idea: every item on this site is *a record with a source*.
Channels are a gazetteer, studies are a library catalog, timelines are annals.
The design should make that reading feel obvious.

## Brand Positioning

Latter-day Stats is a public, independent data hub for statistics, research, and
creator data related to the Latter-day Saint community.

The brand should feel:

- Clear and research-minded, with an academic/editorial tone.
- Warm and approachable, not corporate or cold.
- Data-forward, compact, and useful for scanning.
- Respectful of the subject matter without looking institutionally official.
- Independent from The Church of Jesus Christ of Latter-day Saints.

Core product language:

- "Statistics, research, and creator data on the Latter-day Saint community."
- "LDS YouTube creators"
- "Research library"
- "A public hub for Latter-day Saint statistics & research."

## Name and Mark

- Primary name: `Latter-day Stats`, always with the hyphen in `Latter-day`.
- Wordmark: the beehive mark followed by the name in Fraunces, semibold, tight
  tracking. In the nav the name is wrapped in `<DeseretTitle>` (see Typography).
- **Beehive mark** — `src/components/beehive-mark.tsx`. A line-drawn skep, stroked
  rather than filled, so it reads as an engraving rather than clip art. It takes
  `className` and optional `title`, and inherits `currentColor`. Used in the nav
  wordmark, the footer, the favicon (`src/app/icon.tsx`), OG images
  (`src/lib/og.tsx`), and as the centered glyph in a `.dinkus` section break.
  Usually honey-colored; muted or ink is fine where honey would shout.
- Do not use official Church marks, temple silhouettes, or anything implying
  affiliation. The beehive is a regional/pioneer motif, not an institutional one.

## Color System

Tokens live in `src/app/globals.css` (`:root` and `html.dark`) and are exposed to
Tailwind v4 through `@theme inline`. **Always reference tokens** — never hardcode
a hex value or reach for a default Tailwind color ramp (`emerald-100`, `red-600`,
etc.) in site UI.

| Token | Light | Dark | Role |
| --- | --- | --- | --- |
| `--background` | `#f4eeda` | `#0f1115` | Page canvas — aged creme paper / dark stone |
| `--surface` | `#fcf9ef` | `#161a20` | Card and panel surfaces (see note below) |
| `--foreground` | `#1a1a1a` | `#e9e7e2` | Primary text |
| `--muted` | `#63605a` | `#9a9a9a` | Secondary text, captions, metadata |
| `--muted-soft` | `#ece4cf` | `#1d2027` | Subtle fills, table headers, hover states |
| `--border` | `#ded5bf` | `#2a2e36` | Hairline rules — the primary separator |
| `--accent` | `#1f4f7a` | `#7fb0d8` | Interactive blue: links, primary actions, eyebrows |
| `--accent-soft` | `#e8eff6` | `#1a2733` | Soft accent fills |
| `--honey` | `#8a5a06` | `#d9a441` | Identity accent: mark, dinkus, drop caps, chart highlight |
| `--honey-soft` | `#f6ecd6` | `#2b230f` | Honey tag fills |
| `--oxblood` | `#7c2d2d` | `#d98787` | Second ink family: warnings, contested/critical states |
| `--oxblood-soft` | `#f4e6e3` | `#2a1a1a` | Oxblood tag fills |
| `--radius` | `3px` | — | **The one radius on the site** |
| `--page-texture` | SVG | SVG | Body background texture (see below) |

Two accents, two jobs: **`--accent` is the interactive color** (if it's blue, you
can click it) and **`--honey` is the identity color** (mark, flourishes, a single
emphasized data series). Don't let honey become a second link color.

### Surfaces and texture

The body carries `--page-texture`, an inline-SVG `feTurbulence` tile: fine umber
fiber grain on light, low-frequency stone mottle plus sparse pale specks on dark.
It is a data URI in a custom property — no image assets, no network requests.

Cards stay **flat and untextured** and sit on `--surface`, reading as clean sheets
laid on an aged desk. Card markup is authored as `bg-white`; an unlayered rule in
`globals.css` remaps `.bg-white` to `var(--surface)` in both themes, so no call
site needs a `dark:` variant. Prefer writing `bg-white` for card surfaces to match
existing code. Never texture a card, table, or chart surface — texture belongs to
the page only.

Any element that needs to "knock out" against a card (a ring around a chart dot,
for instance) should use `ring-[color:var(--surface)]`, not `ring-white`.

## Typography

Loaded in `src/app/layout.tsx` via `next/font/google` (build-time, self-hosted).

| Font | Variable | Role |
| --- | --- | --- |
| Inter | `--font-inter` | Body text, UI, tables, controls |
| Fraunces | `--font-fraunces` | Wordmark, headlines, section headings, large stat values |
| Noto Sans Deseret | `--font-deseret` | Decorative title reveal only |

Utility classes in `globals.css`:

- `.serif` — Fraunces with Georgia fallback.
- `.serif-onum` — Fraunces with old-style figures, for dates and year spans set in
  running text (annals, bylines, timeline metadata).
- `.small-caps` — `font-variant-caps: all-small-caps` with slight tracking. **This
  is the house label style.** Use it for eyebrows, tag text, table headers, and
  secondary button microcopy, in place of the old `uppercase tracking-wider`.
- `.dinkus` — a centered flourish flanked by hairline rules, for section breaks.
  Put a `<BeehiveMark className="h-3.5 w-3.5" />` inside it.
- `.drop-cap-lead` — applied to a container, drops a large honey Fraunces cap on
  its first paragraph. For editorial leads and study abstracts; use sparingly.

### Type patterns

- Page H1: `.serif`, `text-4xl font-semibold tracking-tight`, `sm:text-5xl`.
- Eyebrow above an H1: `.small-caps text-xs font-medium`, accent color.
- Section heading: `.serif text-2xl font-semibold tracking-tight`.
- Body copy: `text-base leading-relaxed`, `sm:text-lg` on editorial pages.
- Metadata labels: `.small-caps`, `text-[11px]`, muted.
- Numbers: always `tabular-nums` in columns; `.serif-onum` for dates in prose.

### The Deseret title reveal

`src/components/deseret-title.tsx` renders text that appears briefly in the
Deseret alphabet, then "translates" itself into Latin character by character.

```tsx
<h1 className="serif text-4xl font-semibold tracking-tight">
  <DeseretTitle text="Sources over time." />
</h1>
```

Rules, all of them load-bearing:

- **Decorative only.** Deseret is never the sole carrier of any information.
  The server render and the first client render are plain Latin, so crawlers,
  no-JS visitors, and reduced-motion users only ever see Latin. The mapping is an
  approximate per-letter stand-in, not a real transliteration (Deseret is
  phonemic) — never present it as authentic transliterated text.
- `text` must be a plain string. Keep the surrounding `<h1>` and its classes.
- Page titles use the default `replay="always"`. The nav wordmark uses
  `replay="session"` with a `sessionKey`, so it doesn't re-animate on every
  navigation.
- Apply it to public page H1s only — not to H2s, admin pages, or `[slug]` titles.

## Layout

**Every public page fills the `mx-auto max-w-6xl px-5 sm:px-8` rail** — the same
rail as the nav and footer. Do not build new pages on a narrow `max-w-2xl` /
`max-w-3xl` column; that leaves dead whitespace down both sides.

Filling the rail does **not** mean stretching prose to 1100px. Keep body text at a
readable measure (`max-w-2xl`) and use the remaining width deliberately:

- A two-column split with a marginalia aside:
  `lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-14`, with the aside carrying
  `lg:border-l lg:border-[color:var(--border)] lg:pl-10`. Put real content there —
  sources, contact details, a sticky table of contents, related links.
- A header band above a `border-b` hairline, with the H1 and lede side by side.
- Full-bleed (`w-full`, no max-width) is correct for dense data tables — the
  channels and studies pages already do this.
- Asides stack below the main column on mobile: apply the grid, sticky, and border
  treatments at the `lg:` breakpoint only.

Vertical rhythm: page padding `py-14 sm:py-20` (or `py-16 sm:py-24` for editorial
pages); major sections `mt-12`–`mt-16`.

## Components and UI Patterns

### Shape and depth

- **One radius: `rounded-[var(--radius)]`** (3px) on buttons, inputs, cards,
  panels, tags, and tooltips. No `rounded-full`, no `rounded-2xl`, no `rounded-md`.
  The only legitimate circles are avatar images, status dots, and chart points.
- **Borders, not shadows.** Cards are `border border-[color:var(--border)]` with
  no `shadow-*`. A modest shadow is acceptable only on genuinely floating layers
  (modal, command palette, mobile drawer) where depth conveys stacking.

### Tags

Use the shared `Tag` component (`src/components/tag.tsx`) for every badge, pill,
category label, and status chip. Square corners, small caps, hairline ring, faint
tint. It takes `ink`, one of five families:

| Ink | Meaning |
| --- | --- |
| `accent` | Institutional / faith-affiliated / primary |
| `oxblood` | Critical, contested, outside, needs-verification, warning |
| `honey` | Culture, lifestyle, media, thematic highlight |
| `ink` | Neutral reference / orthodox baseline |
| `muted` | Default, unknown, or de-emphasized |

Channel types map to these in `src/lib/channel-types.ts` via `inkForType()`;
timeline categories, hearsay grades, and correlation statuses map in
`src/app/eternal-increase-timeline/constants.ts`. **Group new values into an
existing family — never add a sixth color.** The families carry meaning; that's
the whole point of having only five.

Tailwind v4 needs literal class strings, so keep these maps as literals rather
than building class names by concatenation.

### Buttons and links

- Primary: `rounded-[var(--radius)]`, accent background, white text, `h-10`/`h-11`.
- Secondary: same radius, `border border-[color:var(--border)]`, surface fill,
  hover `bg-[color:var(--muted-soft)]`. Small-caps microcopy suits these well.
- Text links: accent, underline on hover; inline editorial links underline with
  `underline-offset-2`.
- Icon buttons: `lucide-react`, square `h-10 w-10`, same radius, hairline border.

### Tables

Desktop tables sit in a bordered container with hairline row rules. Headers are
`.small-caps`, muted, over a rule. Numeric cells are `tabular-nums` and
right-aligned. Row hover uses `--muted-soft` at low opacity. Mobile gets purpose-
built cards, never a squeezed table.

### Charts

Every color traces to a token: `--accent` for the primary series, `--border` for
hairline gridlines, `--muted` for axis labels, `--oxblood` for decline/negative
signals, and `--honey` reserved for a *single* deliberate highlight. Never use a
charting library's default palette.

Full chart anatomy, the shared component kit (`src/components/charts/`), and
per-chart-type specs (line, dot plot with CI, 100%-stacked, faceted small
multiples) live in **[docs/CHARTS.md](docs/CHARTS.md)**. Read it before
building a new chart or adding a chart type. Downloadable Data Explorer PNG
graphics have their own pipeline and must stay legible at roughly 1/3 scale
(how they render on a phone) — the mobile font floors live in
`scripts/state-of-theology-graphics/STYLE.md`.

**Row order for magnitude/comparison charts:** when a chart shows one row per
group (a magnitude bar, a paired bar, a 100%-stacked bar, or a diverging bar),
rows sort highest to lowest by the chart's own statistic — not a curated,
hardcoded order. Three kinds of rows are the exception and always sink below
every substantive row regardless of their value, in this order: a named
catch-all ("Other Christian," "Other religions," and the like — still a real,
if miscellaneous, group of people) sinks just below the substantive rows,
sorted by value among themselves; a population-average aggregate ("Christian
average," "All religious average") sinks below that, since it's an aggregate
over the whole chart rather than a group of people at all; a literal
total-population row ("U.S. adults," "Total population"), if a chart ever has
one, sinks below even those, at the very bottom. The canonical implementation
is `sort_groups` in `scripts/chart_style.py`.

**Gallery order for a dataset's graphics:** each Data Explorer dataset's own
graphics page (`/data-explorer/[slug]/graphics`) lists that dataset's charts
in alphabetical order by title — not the order they were added, not grouped
by topic. This is unrelated to the row-order rule above (that one sorts the
bars *inside* one chart by value; this one sorts *which chart* comes first in
the gallery, by title) and applies to every dataset, including ones whose
graphics are built dynamically rather than listed by hand (e.g. State of
Theology's one-graphic-per-survey-item page). The canonical implementation
is `sortGraphicsAlphabetically` in `src/lib/data-explorer.ts`, applied once
centrally when `DATASETS` is exported — an individual dataset's own
`graphics: [...]` array (or a helper function that builds one) can list its
entries in whatever order is most convenient to write; nothing needs to be
hand-sorted or kept in sync as graphics are added or removed. Leading
punctuation (a quotation mark opening a survey-statement title, straight or
curly) is stripped before comparing, so a quoted title alphabetizes by its
first real word rather than sorting before or after every unquoted title as
a block.

**Per-group identity colors, site-wide:** every Data Explorer chart that
compares named denominations/religions (a magnitude bar, a 100%-stacked
bar, or a longitudinal line chart with one line per group) gives each
group its own distinct identity color. No chart singles out Latter-day
Saint in `--accent` against every other group flattened to one gray —
that older "highlight-vs-gray" convention read as favoritism once every
group in the same dataset needed its own identity, and it's retired
everywhere on the site, not just for the Pew RLS pipeline. This applies
across every dataset folder: `scripts/pew-rls/`, the one-off Pew datasets
sharing `scripts/flagship-charts/common.py`'s `render_magnitude_bar`, and
`scripts/ryan-burge/`. Several Christian traditions reuse colors already
locked by the State of Theology charts
(`scripts/state-of-theology-graphics/STYLE.md`'s Palette section) so the
same tradition reads as the same color everywhere on the site it appears.

| Group | Color name | Hex |
|---|---|---|
| Latter-day Saint (alias: Mormon) | Blue (`--accent`) | `#1f4f7a` |
| Catholic | Wine | `#8C4A5F` |
| Protestant | Amber | `#C9721C` |
| Evangelical Protestant | Amber (light) | `#D68A2E` |
| Mainline Protestant | Amber (pale) | `#E8B15E` |
| Historically Black Protestant | Amber (dark) | `#8B5A2B` |
| Orthodox Christian (alias: Orthodox) | Moss | `#5B7553` |
| Jehovah's Witness | Plum | `#6B4472` |
| Muslim | Olive | `#6B8C3D` |
| Hindu | Crimson | `#9C2B2B` |
| Buddhist | Ochre | `#9C8A1F` |
| Jewish | Periwinkle | `#7A6BA6` |
| Religiously unaffiliated (alias: Unaffiliated) | Umber | `#6B4A2F` |
| Agnostic | Slate blue-gray | `#4A6B7A` |
| Atheist | Dark navy-slate | `#2F4858` |
| Nothing in particular | Clay/tan | `#A67B5B` |
| Southern Baptist | Brick | `#7A3B2E` |
| United Methodist | Navy | `#3E5C76` |

The Evangelical/Mainline/Historically Black Protestant trio stays in the
amber family (same broad tradition as generic Protestant) but each gets
its own distinct shade, since a chart can show all three as separate rows
at once (e.g. an ATP wave's attendance-by-tradition breakdown) — reusing
one amber for all three would make them indistinguishable from each
other. Different survey waves spell the same group differently ("Mormon"
vs. "Latter-day Saint," "Evangelical Protestant" vs. "...Churches" vs.
"...Tradition," "Unaffiliated" vs. "Unaffiliated (religious \"nones\"),"
capitalization drift on "Nothing in Particular") — `GROUP_ALIASES` in
`scripts/chart_style.py` resolves every spelling variant to one canonical
color before lookup, rather than duplicating hex values across
near-identical dict keys.

Two more row kinds aren't a single identity, so they share existing neutral
tokens instead of getting their own hue — matching their own sink-to-bottom
tier from the row-order rule above: any "Other..." catch-all (Other
Christian, Other religions, "Something else," and the like — tier 1 above)
uses the existing bar-safe gray, `CONTEXT_GRAY` (`#8f8b82`); any
"...average" aggregate or an "All &lt;population&gt;" baseline row (tiers
2/3 above — e.g. "All U.S. adults," "All Black Americans," "All
attenders") uses the existing `MUTED` token (`#6E6A63`).

**Not every "highlight one row, gray the rest" chart is this pattern.** A
handful of one-off flagship-charts callers highlight the chart's own
subject — a specific country among many (`highlight_rows={"United
States"}`), a top-ranked subset, a tracked time period or category — not a
religious identity. That's a different, legitimate encoding (drawing
attention to what the chart is actually about) and is unaffected by this
rule; only a chart whose highlighted row *is* a religious/denominational
identity needs to convert to per-group identity colors.

**Row/tick/group labels are always plain ink, regardless of chart shape or
dataset.** A bar's own fill (or a line's own stroke, or a data value
printed next to it) can carry its group's identity color, but the axis
label naming that row/line — the group's name itself — is never colored to
match. This is a separate, universal rule from the identity-color table
above and applies even to charts that don't do per-group identity coloring
at all (e.g. a chart highlighting a country or time period still owes
every tick label plain ink).

**Accepted tradeoff:** Muslim (olive, `#6B8C3D`) and Orthodox Christian
(moss, `#5B7553`) are visually closer than the usual colorblind/low-vision
floor when they land next to each other on a chart. This is accepted,
not a bug to fix, because every bar in this chart type already prints its
full group name and its percentage directly on the bar — color is never
the only way to identify a row, which is the secondary-encoding condition
under which a sub-floor color pair is allowed. The same reasoning applies
to Latter-day Saint (blue, `#1f4f7a`) and United Methodist (navy,
`#3E5C76`) landing near each other on a line chart
(`scripts/ryan-burge/render_pid_over_time_chart.py`) — every line there
also carries its own printed end-of-line label.

The canonical implementation is `GROUP_COLORS`/`GROUP_ALIASES`/
`color_for_group` in `scripts/chart_style.py`; see `scripts/pew-rls/STYLE.md`'s
"Magnitude bar (per-group identity color)" section for a worked example.

**Title qualifiers render smaller than the primary title.** A trailing
parenthetical qualifier on a chart title — e.g. "Attendance frequency,
full distribution (Christian only)" — renders on its own line at roughly
55% of the primary title's font size, not wrapped in as if it were equally
important. The canonical implementation is `split_title_qualifier` in
`scripts/chart_style.py`, used by every title-drawing function in
`scripts/pew-rls/*.py`.

**Footnote/caption, every Data Explorer PNG:** one bold line, nothing else —
`@ithinkisam | data: <short source title>`. No DOI, no URL, no full academic
citation, no per-chart population/cutpoint/exclusion methodology note. The
short title is a plain human name for the dataset (e.g. "Pew 2023-24 RLS,"
"Ryan Burge, CCES 2016," "Church membership compilation"), not a formal
citation — someone who wants the full source can already find it in the
dataset's own `docs/datasets/<slug>/README.md`, so the chart image itself
only needs to say *which* dataset, not cite it. This replaced the older,
per-dataset pattern of stacking 2-3 caption paragraphs (a methodology note,
an `N =` line, and a full "Pew Research Center. 2025. ... doi: ..." citation
line) — that pattern is retired everywhere, not just on new charts. Draw it
with `chart_style.draw_caption_bottom(fig, fonts, [], handle="@ithinkisam |
data: <short title>")` — empty `paragraphs`, the whole line as `handle` (bold,
`fontsize` defaults to 11.5, up from the pre-2026-08 default of 10 — "slightly
larger," not a second subtitle). Every render script across every dataset
folder draws its caption this same way; there is no dataset-specific
exception.

### Forms

Inputs and selects use the standard radius and a hairline border; focus moves the
border to accent and removes the default outline. Labels are small and functional;
helper text is muted.

## Motion

The site is nearly static by design, and motion should stay incidental —
`transition-colors` on hover, skeleton pulses, the Deseret reveal.

**All non-essential motion must be gated on reduced-motion preference.** The
pattern is established in `globals.css`: keyframes live inside
`@media (prefers-reduced-motion: no-preference)`, and any "hidden" starting state
belongs *inside the keyframes*, never in an inline style — so when the block
doesn't apply, content is simply visible rather than stuck invisible. Client
components should also check
`window.matchMedia("(prefers-reduced-motion: reduce)")` before animating.

## Voice and Copy

Direct, transparent, and careful. Plainspoken rather than promotional. Comfortable
with data terms without being jargon-heavy. Respectful toward faith and
scholarship.

Prefer: "public data", "tracked", "refreshed regularly", "curated academic
studies", "independent", "not affiliated".

Avoid: overclaiming authority or official status, marketing hype, insider-only
language without context, and any copy implying endorsement by the Church.

## Implementation Notes

- Next.js `16.2.6`, React `19.2.4`, Tailwind CSS v4 (`@import "tailwindcss"` +
  `@theme inline`), `lucide-react` for icons.
- Tokens and utilities: `src/app/globals.css`. Fonts: `src/app/layout.tsx`.
- Shared identity components: `src/components/tag.tsx`,
  `src/components/beehive-mark.tsx`, `src/components/deseret-title.tsx`.
- Admin pages under `src/app/admin/` are held to a looser standard than public
  pages; bring them along opportunistically.

Checklist when adding UI:

- [ ] Colors come from tokens; no raw hex, no default Tailwind ramps.
- [ ] `rounded-[var(--radius)]` everywhere; no pills, no `rounded-2xl`.
- [ ] Borders instead of shadows on cards and panels.
- [ ] Badges use `<Tag>` with one of the five inks.
- [ ] Page fills the `max-w-6xl` rail; prose still capped at a readable measure.
- [ ] Labels and eyebrows use `.small-caps`; dates in prose use `.serif-onum`.
- [ ] Any new animation is gated on `prefers-reduced-motion`.
- [ ] Works in both light and dark mode.
- [ ] New charts follow [docs/CHARTS.md](docs/CHARTS.md).
