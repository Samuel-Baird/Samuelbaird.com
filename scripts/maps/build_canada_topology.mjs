// Turns scripts/maps/canada-provinces.geojson (Code for America's click_that_hood, MIT,
// derived from Natural Earth) into a simplified TopoJSON the site can draw quickly:
// src/data/canada-provinces.topo.json. The raw file is ~700 KB of coastline detail; this
// keeps it under ~60 KB, which is plenty at map scale.
//
// Usage: node scripts/maps/build_canada_topology.mjs

import { readFileSync, writeFileSync } from 'node:fs';
import { topology } from 'topojson-server';
import { presimplify, simplify, quantile } from 'topojson-simplify';

const geo = JSON.parse(readFileSync(new URL('./canada-provinces.geojson', import.meta.url), 'utf8'));
// Use the Church's/common names.
const RENAME = { 'Yukon Territory': 'Yukon' };
for (const f of geo.features) f.properties = { name: RENAME[f.properties.name] ?? f.properties.name };

let topo = topology({ provinces: geo }, 1e5);
topo = presimplify(topo);
topo = simplify(topo, quantile(topo, 0.06));
const out = JSON.stringify(topo);
writeFileSync(new URL('../../src/data/canada-provinces.topo.json', import.meta.url), out);
console.log(`${geo.features.length} provinces, ${(out.length / 1024).toFixed(0)} KB`);
