# The Samuel Baird family style

Every public site (samuelbaird.com, Latter-day Stats, Urim, Omni, Peepstone, Deseret MCP, and the Deseret Wiki itself) follows the Deseret Wiki's look: 1850s territorial printing by lamplight. The Deseret Wiki (`sites/deseret-wiki/src/styles/global.css`) is where the style comes from. This package is the shared copy for everything else.

## What is shared

| Piece | File | Notes |
|---|---|---|
| Palette, type, buttons, rules, register, panel | `assets/family.css` | Lamplight only (dark). Old "Archive" token names (`--background`, `--accent`, `--honey`…) are mapped onto the palette so older stylesheets follow. |
| Sidebar, top bar, panorama, colophon | `render.mjs` → HTML | Pre-rendered so every link is crawlable. `assets/family.js` only opens/closes it and marks the current page. |
| Icons, seal, Wasatch panorama | `assets/sprite.svg`, `seal.svg`, `mountains.svg` | Extracted from the Deseret Wiki's `Sprite.astro`, `Seal.astro`, `Mountains.astro`. |
| Project list | `projects.json` | One registry for every sidebar, samuelbaird.com's project pages, JSON-LD, sitemap, robots.txt and llms.txt. |
| Per-site menus | `sites.mjs` | Each site's own pages (icons) and shelves (coloured bars). |

## Rules

- **Palette**: paper `#16161A`, inset `#26221D`, ink `#EDE3CB`, soft ink `#B9AE96`, headings `#E8DCC0`, links `#D9B46A`, hairlines `#4A4134`, ornaments (brass) `#BF9A55`, seal `#9A4446`.
- **Type**: IM Fell English for display and headings (one weight, 400; never bold it), Libre Baskerville for text, Cinzel uppercase with wide tracking for labels, Grenze Gotisch only for a site's name in the colophon or masthead, Noto Sans Deseret for Deseret.
- **Shapes**: square corners (1–2px), double hairline rules, letterpress buttons (`.btn`), glass panels (`.panel`) over the night sky, roman-numbered registers for lists of links. No pills, no drop shadows on text.
- **Every page** has the floating sidebar (top-left button), the top bar with the seal and site name, the panorama, and the colophon that links back to samuelbaird.com and to the other projects.
- **Links between projects** use the registry's URLs. Every project except the Deseret Wiki family lives at `https://samuelbaird.com/<id>`.
- **Never** list private work (school, collector-items, content-creation) or link the Gospel Scholar Archive.

## Changing it

1. Edit this package (or `projects.json` / `sites.mjs`).
2. `node scripts/family-sync.mjs` from the repo root: copies the assets to every site and stamps the chrome in.
3. For samuelbaird.com also run `node sites/samuelbaird.com/scripts/build.mjs` (it renders the chrome itself, plus the project pages).
4. CI runs `node scripts/family-sync.mjs --check`, which fails if any site is out of date.

## Deploys

Each app's Vercel project skips a build unless its own folder or `packages/family` changed since its last deploy (`scripts/vercel-ignore.sh`, set as `ignoreCommand` in its `vercel.json`), so a change here redeploys every site.
