// Precomputes every map's SVG geometry into src/data/map-shapes.json, which
// src/lib/world-map.ts serves at runtime. The raw TopoJSON atlases
// (world-atlas 110m + 50m, us-atlas states, Canada) are ~1 MB, and bundling
// them made the Cloudflare Worker too big for the free plan; the projected
// paths are a fraction of that. Output is deterministic: re-run after
// changing a projection, a size or an atlas, and commit the JSON.
//
// Usage: npx tsx scripts/maps/build-map-shapes.ts

import { writeFileSync } from "node:fs";
import path from "node:path";
import { geoAlbersUsa, geoConicConformal, geoNaturalEarth1, geoPath } from "d3-geo";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import countries110 from "world-atlas/countries-110m.json";
import countries50 from "world-atlas/countries-50m.json";
import usStates from "us-atlas/states-10m.json";
import canadaProvinces from "../../src/data/canada-provinces.topo.json";
import { MAP_HEIGHT, MAP_WIDTH, type MapShape, type WorldMap } from "../../src/lib/world-map";

/** Every country in the atlases, keyed by its Natural Earth name. */
function buildWorld(): WorldMap {
  const projection = geoNaturalEarth1().fitExtent(
    [
      [4, 4],
      [MAP_WIDTH - 4, MAP_HEIGHT - 4],
    ],
    { type: "Sphere" },
  );
  const path = geoPath(projection).digits(1);

  const land = feature(
    countries110 as unknown as Topology,
    (countries110 as unknown as Topology).objects.countries as GeometryCollection,
  );
  const landPath = path(land) ?? "";

  const detail = feature(
    countries50 as unknown as Topology,
    (countries50 as unknown as Topology).objects.countries as GeometryCollection,
  );
  const nameOf = (f: { properties: unknown }) => String((f.properties as { name?: string }).name);
  // Coarse outlines keep the payload small; islands the coarse atlas lacks
  // fall back to the detailed one.
  const byName = new Map(detail.features.map((f) => [nameOf(f), f]));
  for (const f of land.features) byName.set(nameOf(f), f);

  const shapes: Record<string, MapShape> = {};
  for (const [name, f] of [...byName].sort(([x], [y]) => x.localeCompare(y))) {
    const [[x0, y0], [x1, y1]] = path.bounds(f);
    const [cx, cy] = path.centroid(f);
    shapes[name] = {
      d: path(f) ?? "",
      cx: Math.round(cx * 10) / 10,
      cy: Math.round(cy * 10) / 10,
      small: Math.max(x1 - x0, y1 - y0) < 7,
      bbox: [x0, y0, x1, y1].map((n) => Math.round(n * 10) / 10) as MapShape["bbox"],
    };
  }
  return { width: MAP_WIDTH, height: MAP_HEIGHT, land: landPath, shapes };
}

const US_MAP_WIDTH = 960;
const US_MAP_HEIGHT = 600;
/** The five territories in us-atlas; the Albers USA projection can't place them. */
const TERRITORIES = new Set([
  "American Samoa",
  "Guam",
  "Commonwealth of the Northern Mariana Islands",
  "Puerto Rico",
  "United States Virgin Islands",
]);

/** The 50 states and D.C. on the Albers USA projection (Alaska and Hawaii as
 * insets), in the same shape as the world map so one map component draws both. */
function buildUsStateMap(): WorldMap {
  const projection = geoAlbersUsa().fitExtent(
    [
      [4, 4],
      [US_MAP_WIDTH - 4, US_MAP_HEIGHT - 4],
    ],
    feature(
      usStates as unknown as Topology,
      (usStates as unknown as Topology).objects.states as GeometryCollection,
    ),
  );
  const path = geoPath(projection).digits(1);
  const all = feature(
    usStates as unknown as Topology,
    (usStates as unknown as Topology).objects.states as GeometryCollection,
  );
  const shapes: Record<string, MapShape> = {};
  for (const f of all.features) {
    const name = String((f.properties as { name?: string }).name);
    if (TERRITORIES.has(name)) continue;
    const d = path(f);
    if (!d) continue;
    const [[x0, y0], [x1, y1]] = path.bounds(f);
    const [cx, cy] = path.centroid(f);
    shapes[name] = {
      d,
      cx: Math.round(cx * 10) / 10,
      cy: Math.round(cy * 10) / 10,
      small: Math.max(x1 - x0, y1 - y0) < 12,
      bbox: [x0, y0, x1, y1].map((n) => Math.round(n * 10) / 10) as MapShape["bbox"],
    };
  }
  return { width: US_MAP_WIDTH, height: US_MAP_HEIGHT, land: "", shapes };
}

const CA_MAP_WIDTH = 960;
const CA_MAP_HEIGHT = 640;

/** Canada's provinces and territories on a Lambert conformal conic projection (the
 * standard for Canada). Geometry is built by scripts/maps/build_canada_topology.mjs. */
function buildCanadaProvinceMap(): WorldMap {
  const topo = canadaProvinces as unknown as Topology;
  const all = feature(topo, topo.objects.provinces as GeometryCollection);
  const projection = geoConicConformal()
    .parallels([49, 77])
    .rotate([96, 0])
    .center([0, 62])
    .fitExtent(
      [
        [4, 4],
        [CA_MAP_WIDTH - 4, CA_MAP_HEIGHT - 4],
      ],
      all,
    );
  const path = geoPath(projection).digits(1);
  const shapes: Record<string, MapShape> = {};
  for (const f of all.features) {
    const name = String((f.properties as { name?: string }).name);
    const d = path(f);
    if (!d) continue;
    const [[x0, y0], [x1, y1]] = path.bounds(f);
    const [cx, cy] = path.centroid(f);
    shapes[name] = {
      d,
      cx: Math.round(cx * 10) / 10,
      cy: Math.round(cy * 10) / 10,
      small: Math.max(x1 - x0, y1 - y0) < 12,
      bbox: [x0, y0, x1, y1].map((n) => Math.round(n * 10) / 10) as MapShape["bbox"],
    };
  }
  return { width: CA_MAP_WIDTH, height: CA_MAP_HEIGHT, land: "", shapes };
}

const out = { world: buildWorld(), us: buildUsStateMap(), canada: buildCanadaProvinceMap() };
const file = path.resolve(__dirname, "../../src/data/map-shapes.json");
writeFileSync(file, JSON.stringify(out) + "\n");
console.log(
  `map-shapes.json: ${Object.keys(out.world.shapes).length} countries, ${Object.keys(out.us.shapes).length} states, ` +
    `${Object.keys(out.canada.shapes).length} provinces`,
);
