# Map style guide

Every world map on the site (Map Explorer, the Activity Estimator's attendance
map, and any future one) is one shared component. **Do not hand-roll a map.**
Build the values, pass them in, and everything below comes for free.

```
src/components/map/choropleth-map.tsx   the map: zoom, pan, tooltip, key, PNG export
src/components/map/classes.ts           banding, colors, legend labels
src/lib/world-map.ts                    server-side geometry (builds SVG paths)
```

Existing users: `src/components/map-explorer/map-explorer.tsx` and
`src/components/activity-estimator/attendance-map.tsx` (a thin wrapper — copy
its shape for a new map).

## Adding a map

1. Build the geometry on the **server**: `buildWorldMap(countryNames)` from
   `src/lib/world-map.ts`, and pass the result to the client component. No
   topology ships to the browser. Names must match Natural Earth's; differences
   are handled by `NAME_ALIASES` in that file (add to it if a country is
   missing from the map).
2. Render `<ChoroplethMap>` with:
   - `items`: `{ name, value }[]`. `value` is `null` for no data, `0` for a real
     zero (they look different).
   - `format`: how a value prints (`"1,234"`, `"14%"`). It is also used for the
     legend and the PNG.
   - `title`, `subtitle`, `source`, `filename`, `rankTitle`, `tooltip`.
3. Data goes in a committed JSON file under `docs/datasets/<slug>/`, with a
   script that regenerates it. Nothing hand-typed.

## Titles and subtitles (also the PNG headline)

- The title says what is shown, plainly: "Temples per 100,000 members by
  country". No editorializing.
- The subtitle says exactly what the shading means and, for anything derived
  or estimated, states the assumptions ("assuming 130 people per ward and 35
  per branch. Not a measured activity rate."). An estimate must never read as
  a measurement.

## Color and banding

- Countries are grouped into **up to five bands** with **round cut-offs**
  (`classify` in `classes.ts`). Never a smooth gradient: a single-hue gradient
  makes highs and lows impossible to tell apart at a glance.
- The ramp is pale yellow → amber → orange → red → dark plum. It is ordered by
  lightness as well as hue, so it survives grayscale and color blindness.
- Zero gets its own swatch, and "No data" another. Both are neutral grays.
- The ramp is **hardcoded hex on purpose** (a documented exception to the
  tokens-only rule in `BRANDING_AND_DESIGN.md`): the PNG export renders on its
  own white canvas and must match the on-screen map exactly. Same reasoning as
  the Python PNG pipeline's own palette in `docs/CHARTS.md`.
- Cut-offs: quintile targets, snapped to round numbers (1-2.5-5-10 for values
  ≥ 1,000; a finer set below that). If ties collapse the bands (temples, say),
  cut-offs spread evenly on a log scale instead. Some metrics end up with fewer
  than five bands; that is correct.
- Legend labels read `1,000–9,999` for counts and `10%–15%` for rates. The top
  band is open-ended (`100,000+`), never a fixed maximum. The lowest positive
  band is `1–999` for counts or `Under 10%` for rates.
- Ratios that are constant by construction (members per 100,000 members)
  must not be offered — the map goes one solid color.

## Legibility

Legends are the first thing lost when an image is shared small.

- **Screen key:** its own "Key" label, swatches 28×20 px, text `text-sm`
  (`sm:text-base`), foreground color (not muted).
- **PNG key:** 28 px labels, three swatches per row. Ranked-list text is 28 px,
  title 46 px, subtitle 28 px. Nothing in the PNG is below 21 px (the footer);
  do not shrink anything to make a longer legend fit — wrap it to another row.
- Tooltips are `text-sm`.

## Interaction

- Mouse: hover shows a floating card; double-click zooms; drag pans when zoomed.
- Ctrl/⌘ + wheel zooms (trackpad pinch arrives the same way). **Plain wheel
  scrolls the page** — a map must never trap scrolling.
- Touch: tap a country and its details show in a card *under* the map (a
  floating card is unreadable on a phone). The map only captures touch once it
  is zoomed, so the page still scrolls normally at 1×. Two-finger pinch zooms.
- +, − and reset buttons are always visible, 40 px each.
- Every country is keyboard-focusable and announced with its value.
- Circles mark countries too small to see (islands); they hover/tap like the
  shape.

## PNG export ("Save PNG")

Every map has one; both existing maps use the same code. It follows the
Data Explorer PNG house style in `docs/CHARTS.md`:

- 1080×1350, **white background**, serif type (Roboto Slab, falling back to
  Georgia), no shadows.
- Contents, top to bottom: title, subtitle, the map, the key, a "Top 10" list
  with exact numbers, and one bold footer line:
  `latterdaystats.samuelbaird.com | data: <short source>, <year>`.
- The map is exported **as currently zoomed**, so a reader can save a close-up
  of a region. Unzoomed, the bottom strip (Antarctica) is cropped so the map
  isn't padded with empty land.
- The export is a standalone SVG drawn to a canvas, so it can't use CSS
  variables or web fonts. Anything you add to it must use literal colors and
  system-safe fonts. Look at a real export before merging: check the footer
  fits inside the margins and the last ranked row clears the footer rule.

## Zooming into a country, and state/province maps

- **Click a country** on the world map and `ChoroplethMap` zooms to its outline
  (`focusName`) and dims everything else; a "← World map" button returns. The
  parent owns that state (`onItemClick` + `focusName`), so any map can opt in.
  The zoom animates unless the visitor prefers reduced motion.
- **Countries with subnational data drill down** to their own map instead:
  today only the United States (`buildUsStateMap()` in `src/lib/world-map.ts`,
  Albers USA with Alaska and Hawaii as insets, D.C. included, territories
  excluded). It returns the same `WorldMap` shape as the world map, so the same
  component draws it. Pass `exportCrop={1}` (nothing to crop) and a
  `noDataLabel` such as "Not yet published".
- The map explorer also shows a sortable table (`data-table.tsx`) for whichever
  level is on screen.
- **The Church publishes state and province pages one at a time.** As of
  Sep 2026 only nine U.S. states exist (Alabama, Alaska, Arizona, Arkansas,
  California, Colorado, Connecticut, Delaware, Hawaii); no Canadian provinces or
  any other country. Unpublished states draw grey with a plain "not published
  yet" note, and the page says how many are published. Never fill the gaps with
  guesses. To pick up new pages:

  ```bash
  node scripts/church-facts-statistics/scrape-subnational.mjs   # writes states.csv / states.json
  python scripts/church-facts-statistics/build_state_stats.py   # writes docs/datasets/lds-states/state-stats.json
  ```

  The scraper crawls every country page for "The Church in ..." cards and probes
  every U.S. state name directly, so a new country's provinces are found without
  code changes. To draw a new country's map, add a `build<Country>Map()` next to
  `buildUsStateMap()` and a `states[<country>]` branch in `map-explorer.tsx`.
- Blank counts in the state pages mean zero; the family-history-center field is
  the literal placeholder `fhcs`, so it is dropped.

## Checklist for a new or changed map

- [ ] Uses `ChoroplethMap`; no custom SVG map.
- [ ] Title and subtitle state what and how; estimates say they are estimates.
- [ ] Legend bands are round, top band open-ended, zero and no-data distinct.
- [ ] Save PNG works, and you have opened the PNG and read it.
- [ ] Works on a phone: tap shows details under the map, + zooms, page scrolls.
- [ ] Data is in a committed JSON file with a regenerating script.
- [ ] Missing data is shown as missing (grey, labelled), never estimated.
