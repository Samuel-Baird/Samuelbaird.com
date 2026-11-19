import mapShapes from "@/data/map-shapes.json";

// Map geometry is precomputed (projected SVG paths) by
// scripts/maps/build-map-shapes.ts into src/data/map-shapes.json, so neither
// the TopoJSON atlases nor d3-geo ship in the Worker or to the browser.

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
  "Democratic Republic of the Congo": "Dem. Rep. Congo",
  "Cote d'Ivoire": "Côte d'Ivoire",
  Swaziland: "eSwatini",
  "Central African Republic": "Central African Rep.",
  "Cayman Islands": "Cayman Is.",
  "Saint Kitts and Nevis": "St. Kitts and Nevis",
  Curacao: "Curaçao",
  "Virgin Islands": "U.S. Virgin Is.",
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

const MAPS = mapShapes as unknown as { world: WorldMap; us: WorldMap; canada: WorldMap };

/** World map shapes for the given Church country names (see NAME_ALIASES). */
export function buildWorldMap(churchCountries: string[]): WorldMap {
  const shapes: Record<string, MapShape> = {};
  for (const name of churchCountries) {
    const shape = MAPS.world.shapes[NAME_ALIASES[name] ?? name];
    if (shape) shapes[name] = shape;
  }
  return { width: MAPS.world.width, height: MAPS.world.height, land: MAPS.world.land, shapes };
}

/** The 50 states and D.C. on the Albers USA projection (Alaska and Hawaii as
 * insets), in the same shape as the world map so one map component draws both. */
export function buildUsStateMap(): WorldMap {
  return MAPS.us;
}

/** Canada's provinces and territories on a Lambert conformal conic projection. */
export function buildCanadaProvinceMap(): WorldMap {
  return MAPS.canada;
}
