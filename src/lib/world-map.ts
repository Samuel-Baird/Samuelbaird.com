import { geoAlbersUsa, geoNaturalEarth1, geoPath } from "d3-geo";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import countries110 from "world-atlas/countries-110m.json";
import countries50 from "world-atlas/countries-50m.json";
import usStates from "us-atlas/states-10m.json";

export const MAP_WIDTH = 960;
export const MAP_HEIGHT = 500;

/** Church facts-and-statistics country names that differ from Natural Earth's. */
const NAME_ALIASES: Record<string, string> = {
  "United States": "United States of America",
  "Dominican Republic": "Dominican Rep.",
  "French Polynesia": "Fr. Polynesia",
  "Cape Verde": "Cabo Verde",
  "Republic of the Congo": "Congo",
  "Marshall Islands": "Marshall Is.",
  "Czech Republic": "Czechia",
  "Cook Islands": "Cook Is.",
  Macau: "Macao",
  "Saint Vincent and the Grenadines": "St. Vin. and Gren.",
  "Antigua and Barbuda": "Antigua and Barb.",
  "Bosnia and Herzegovina": "Bosnia and Herz.",
};

export type MapShape = {
  d: string;
  /** Centroid, for a marker where the country is too small to see. */
  cx: number;
  cy: number;
  small: boolean;
  /** Bounding box [x0, y0, x1, y1], so a view can zoom to the country. */
  bbox: [number, number, number, number];
};

export type WorldMap = {
  width: number;
  height: number;
  /** Every country in the atlas, as one silhouette path. */
  land: string;
  /** Shapes keyed by the Church's country name. */
  shapes: Record<string, MapShape>;
};

/** Builds SVG paths on the server so no geometry ships to the client. */
export function buildWorldMap(churchCountries: string[]): WorldMap {
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
  for (const name of churchCountries) {
    const f = byName.get(NAME_ALIASES[name] ?? name);
    if (!f) continue;
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
export function buildUsStateMap(): WorldMap {
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
