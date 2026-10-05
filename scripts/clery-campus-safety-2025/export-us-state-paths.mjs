// Writes docs/datasets/clery-campus-safety-2025/us-state-paths.json: the same Albers USA
// state outlines (Alaska and Hawaii as insets, D.C. included, no territories) that
// buildUsStateMap() in src/lib/world-map.ts draws, as SVG path strings in a 960x600 box.
// The Python renderer reads this so the PNG map matches the site's state map exactly.
import { geoAlbersUsa, geoPath } from "d3-geo";
import { feature } from "topojson-client";
import { readFileSync, writeFileSync } from "node:fs";

const topo = JSON.parse(readFileSync("node_modules/us-atlas/states-10m.json", "utf8"));
const all = feature(topo, topo.objects.states);
const territories = new Set(["American Samoa", "Guam", "Commonwealth of the Northern Mariana Islands", "Puerto Rico", "United States Virgin Islands"]);
const W = 960, H = 600;
const projection = geoAlbersUsa().fitExtent([[4, 4], [W - 4, H - 4]], all);
const path = geoPath(projection).digits(1);
const shapes = {};
for (const f of all.features) {
  const name = String(f.properties.name);
  if (territories.has(name)) continue;
  const d = path(f);
  if (d) shapes[name] = d;
}
writeFileSync(
  "docs/datasets/clery-campus-safety-2025/us-state-paths.json",
  JSON.stringify({ width: W, height: H, shapes }) + "\n",
);
console.log(Object.keys(shapes).length, "shapes");
