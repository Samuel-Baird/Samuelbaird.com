// Builds public/stars.json from NASA HEASARC's copy of the Yale Bright Star Catalogue (BSC5, 9,110 stars).
// Run: npm run stars [path/to/heasarc_bsc5p.tdat.gz]   (output is committed; re-run only to change the cut)
//
// Output is a flat array [ra, dec, vmag, bv, ra, dec, ...]: J2000 degrees (2 dp), V magnitude, B−V colour.
// Only stars down to MAG_LIMIT are kept, roughly what a dark Utah sky shows to the naked eye.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const URL = 'https://heasarc.gsfc.nasa.gov/FTP/heasarc/dbase/tdat_files/heasarc_bsc5p.tdat.gz';
const OUT = path.join(ROOT, 'public', 'stars.json');
const MAG_LIMIT = 5.6;

const local = process.argv[2];
const gz = local ? fs.readFileSync(local) : Buffer.from(await (await fetch(URL)).arrayBuffer());
const text = zlib.gunzipSync(gz).toString('utf8');

const fields = text.match(/^line\[1\] = (.*)$/m)[1].trim().split(/\s+/);
const col = (n) => fields.indexOf(n);
const [iRa, iDec, iMag, iBv] = ['ra', 'dec', 'vmag', 'bv_color'].map(col);

const rows = [];
for (const line of text.split('<DATA>')[1].split('\n')) {
  if (!line.includes('|')) continue;
  const c = line.split('|');
  const ra = parseFloat(c[iRa]), dec = parseFloat(c[iDec]), mag = parseFloat(c[iMag]);
  if (!Number.isFinite(ra) || !Number.isFinite(dec) || !Number.isFinite(mag) || mag > MAG_LIMIT) continue;
  const bv = parseFloat(c[iBv]);
  rows.push([+ra.toFixed(2), +dec.toFixed(2), +mag.toFixed(1), Number.isFinite(bv) ? +bv.toFixed(1) : 0.6]);
}
rows.sort((a, b) => a[2] - b[2]); // brightest first
fs.writeFileSync(OUT, JSON.stringify(rows.flat()));
console.log(`${rows.length} stars (V ≤ ${MAG_LIMIT}) written to ${path.relative(ROOT, OUT)}, ${fs.statSync(OUT).size} bytes`);
