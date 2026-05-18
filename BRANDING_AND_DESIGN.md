# Latter-day Stats Branding and Design Guidelines

Last updated: May 18, 2026

This document captures the current visual identity and interface patterns for the Latter-day Stats website. Treat it as the working design source of truth for future edits so new pages and components stay consistent with the site as built.

## Brand Positioning

Latter-day Stats is a public, independent data hub for statistics, research, and creator data related to the Latter-day Saint community.

The current brand should feel:

- Clear and research-minded, with an academic/editorial tone.
- Warm and approachable, not corporate or cold.
- Data-forward, compact, and useful for scanning.
- Respectful of the subject matter without looking institutionally official.
- Independent from The Church of Jesus Christ of Latter-day Saints.

Core product language used across the site:

- "Statistics, research, and creator data on the Latter-day Saint community."
- "LDS YouTube creators"
- "Research library"
- "A public hub for Latter-day Saint statistics & research."

## Logo and Name

The site currently uses text-only branding:

- Primary name: `Latter-day Stats`
- Nav wordmark: serif, semibold, tight tracking, foreground color.
- No logo mark or icon system is currently defined.

Recommended usage:

- Use `Latter-day Stats` exactly, with the hyphen in `Latter-day`.
- Keep the wordmark typographic unless a future logo is intentionally designed.
- Do not use official Church marks, temple silhouettes, or anything that could imply affiliation.

## Color System

Defined in `src/app/globals.css` as CSS variables and exposed to Tailwind v4 through `@theme inline`.

| Token | Hex | Role |
| --- | --- | --- |
| `--background` | `#fbfaf7` | Warm page background, nav background, drawer background |
| `--foreground` | `#1a1a1a` | Primary text |
| `--muted` | `#6b6b6b` | Secondary text, captions, table metadata |
| `--muted-soft` | `#f0eee9` | Subtle panels, table headers, inactive pills, hover fills |
| `--border` | `#e6e3dd` | Hairline borders for cards, tables, nav, forms |
| `--accent` | `#1f4f7a` | Primary actions, links, eyebrow labels, selected states |
| `--accent-soft` | `#e8eff6` | Soft blue tags, callouts, counters, avatar fallback |

### Color Usage

- Use the warm off-white `--background` as the default page canvas.
- Use white cards on top of the warm background for data surfaces.
- Use `--accent` sparingly for primary calls to action, links, section eyebrows, and active UI.
- Use `--accent-soft` for non-dominant emphasis such as study tags, filter counters, callout backgrounds, and avatar initials.
- Use red only for warnings or methodological concerns:
  - `red-600` / `red-700` for icons and danger text.
  - `red-50`, `red-200`, `red-300`, `red-900` for flagged-study panels.
- Preserve the warm neutral base. Avoid introducing a saturated, one-note palette.

### Channel Type Colors

Channel pills are defined in `src/lib/channel-types.ts`.

Current category colors:

- Faith and scholarship: emerald, blue, indigo, teal, sky, violet, amber.
- Critical or outside: rose, orange, stone.
- Lifestyle and culture: pink, yellow, purple, lime, fuchsia, green.
- Media and business: slate, zinc.
- Unknown or missing: `--muted-soft` background with `--muted` text.

Keep all Tailwind color class names literal in source because Tailwind v4 needs to see the complete classes.

## Typography

Fonts are loaded in `src/app/layout.tsx` with `next/font/google`.

| Font | CSS Variable | Role |
| --- | --- | --- |
| Inter | `--font-inter` | Body text, UI, tables, controls |
| Fraunces | `--font-fraunces` | Wordmark, hero headlines, section headings, large stat values |

Global body settings:

- Body font: Inter, with `ui-sans-serif`, `system-ui`, `sans-serif` fallback.
- Serif utility class: `.serif`, using Fraunces with `ui-serif`, Georgia, serif fallback.
- Body feature settings: `"ss01", "cv11"`.
- Serif feature settings: `"ss01"`.
- Font rendering: antialiased and optimized for legibility.

### Type Patterns

- Hero/page H1: `.serif`, `text-4xl`, `font-semibold`, `tracking-tight`, scaling to `sm:text-5xl`; homepage scales to `md:text-6xl`.
- Page eyebrow: `text-xs`, `font-medium`, uppercase, `tracking-[0.18em]`, accent color.
- Section heading: `.serif`, `text-2xl`, `font-semibold`, `tracking-tight`, scaling to `sm:text-3xl`.
- Card title: usually `.serif` for editorial content and Inter semibold for compact channel rows.
- Body copy: `text-base`, `leading-relaxed`, muted or foreground depending on emphasis, often `sm:text-lg` on editorial pages.
- Metadata labels: uppercase, `text-[10px]` or `text-[11px]`, `tracking-wider`, muted.
- Numeric stats: use `tabular-nums`; large metrics use Fraunces.

## Layout

Main content is centered with consistent horizontal padding:

- Wide pages: `mx-auto max-w-6xl px-5 sm:px-8`.
- Editorial/detail pages: `mx-auto max-w-3xl` or `max-w-4xl`.
- Vertical rhythm:
  - Page top padding: `py-14 sm:py-20` or `py-16 sm:py-24`.
  - Major sections: `mt-16`, `mt-20`.
  - Card lists: `mt-6`.

Responsive behavior:

- Navigation collapses below `md`.
- Channel filters become a right-side mobile drawer below `md`.
- Tables are desktop-first at `md`; mobile uses cards.
- Cards usually grid to `sm:grid-cols-2` and `lg:grid-cols-3` where appropriate.

## Components and UI Patterns

### Navigation

Files:

- `src/components/site-nav.tsx`
- `src/components/site-nav-client.tsx`
- `src/components/auth-menu.tsx`

Current pattern:

- Sticky top header.
- Warm translucent background: `bg-[color:var(--background)]/85`.
- Bottom border and backdrop blur.
- Text-only serif wordmark.
- Desktop nav uses muted inactive links and foreground active links.
- Mobile menu is a full-width dropdown below the header.
- Auth menu uses a rounded avatar button and compact dropdown.

### Footer

File: `src/components/site-footer.tsx`

Current pattern:

- Top border.
- Soft muted background: `bg-[color:var(--muted-soft)]/40`.
- Short disclaimer copy.
- Simple text links.

### Buttons and Links

Primary action:

- Rounded full pill.
- `h-10` or `h-11`.
- Accent background, white text.
- Medium text weight.
- Hover usually `opacity-90`; login uses hover foreground.

Secondary action:

- Rounded full pill.
- Border with `--border`.
- White or background fill.
- Foreground text.
- Hover fills with `--muted-soft`.

Text links:

- Accent color.
- Hover underline for list/detail links.
- Inline editorial links use underline with `underline-offset-2`.

Icon buttons:

- Use `lucide-react`.
- Rounded full button, square `h-10 w-10`.
- Border and white/background fill.
- Saved bookmark state fills icon with accent.

### Cards

Primary card style:

- `rounded-2xl`
- `border border-[color:var(--border)]`
- `bg-white`
- Padding between `p-4` and `p-6`
- Hover border changes to accent for clickable cards.

Use cards for repeated data items, detail metric tiles, forms, callouts, and auth panels. Avoid nested cards when possible.

### Tables

Current table pattern:

- Desktop tables are enclosed in a rounded, bordered white container.
- Header rows use `--muted-soft` fill, muted uppercase labels, and tracking.
- Numeric cells use `tabular-nums` and right alignment.
- Row hover uses `--muted-soft` at low opacity.
- Mobile equivalents should become cards, not squeezed tables.

### Forms and Inputs

Current form pattern:

- Search inputs and selects use rounded full pills.
- Admin edit fields use rounded-md inputs where dense editing is needed.
- Focus state changes border to accent and removes default outline.
- Labels are small and functional; helper text is muted.

### Filters

Channel filters use:

- Desktop sidebar card with sticky positioning.
- Mobile right drawer with dark overlay.
- Accordion groups with `details` / `summary`.
- Checkbox accent color set to `--accent`.
- Active filter chips use muted-soft fill, with accent-soft hover.

## Page Patterns

### Homepage

The homepage is an editorial/data dashboard hybrid:

- Large hero statement with minimal copy.
- Two primary links: channels and studies.
- Four core metric tiles.
- Featured channels as compact avatar cards.
- Top channels as a ranked bordered list.
- Featured studies as editorial cards.

### Channels

The channels page emphasizes utility:

- Page eyebrow and serif title.
- Short explanatory paragraph.
- Filter/sidebar plus sortable searchable table.
- Mobile cards for channel data.
- Soft accent callout for creator suggestions.

### Channel Detail

The channel detail page uses:

- Back link.
- Channel type pill.
- Avatar plus serif channel name.
- Metadata definition list.
- YouTube ID code pill.
- Primary YouTube action, bookmark action, optional admin edit.
- Metric tiles in a responsive grid.

### Studies

The studies list uses editorial cards:

- Year and tag pills.
- Serif study titles.
- Author line and abstract preview.
- Bookmark button positioned in the card corner.
- Red warning treatment when flagged for methodological concerns.

### Study Detail

The study detail page uses:

- Context and warning callout panels.
- Serif title.
- Accent section labels.
- Rounded action buttons.
- Embedded PDF/content container with rounded border.

### About

The About page is more editorial:

- Narrower `max-w-3xl` measure.
- Larger readable body text.
- Serif subheads.
- Muted source and disclaimer copy.
- Independent/non-affiliation message is explicit.

## Voice and Copy

Tone should be:

- Direct, transparent, and careful.
- Plainspoken rather than promotional.
- Comfortable with data terms, but not jargon-heavy.
- Respectful toward faith and scholarship.

Prefer:

- "public data"
- "tracked"
- "refreshed regularly"
- "curated academic studies"
- "independent"
- "not affiliated"

Avoid:

- Overclaiming authority or official status.
- Marketing hype.
- Insider-only language without context.
- Copy that implies endorsement by the Church.

## Implementation Notes

- Framework: Next.js `16.2.6`, React `19.2.4`.
- Styling: Tailwind CSS v4 via `@import "tailwindcss"` and `@theme inline`.
- Icons: `lucide-react`.
- Design tokens currently live in `src/app/globals.css`.
- Font setup lives in `src/app/layout.tsx`.
- Channel pill colors live in `src/lib/channel-types.ts`.

When adding new UI:

- Reuse CSS variables instead of hard-coded custom colors.
- Use Inter for controls/body and Fraunces via `.serif` for brand/editorial emphasis.
- Keep dense data surfaces scan-friendly.
- Use rounded full pills for actions and filters.
- Use `rounded-2xl` bordered white cards for repeated data content.
- Keep responsive mobile equivalents intentionally designed rather than merely compressed.

