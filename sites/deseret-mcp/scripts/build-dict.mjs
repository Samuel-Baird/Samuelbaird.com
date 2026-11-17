// Builds data/cmudict.tsv (word -> every CMUdict pronunciation) from the CMU Pronouncing Dictionary.
// Run: npm run build:dict   (the output is committed; re-run only to move to a newer CMUdict)
//
// The source is pinned to one cmusphinx/cmudict commit so the table is reproducible. A copy already
// downloaded by the Deseret Wiki (../deseret/scripts/.cache/cmudict.dict) is reused when it is present.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const COMMIT = '74790861f652b15e4ac49015a90074ad62a27690';
const URL_ = `https://raw.githubusercontent.com/cmusphinx/cmudict/${COMMIT}/cmudict.dict`;
const CACHE = path.join(ROOT, 'scripts', '.cache', `cmudict-${COMMIT.slice(0, 10)}.dict`);
const OUT = path.join(ROOT, 'data', 'cmudict.tsv');

async function source() {
  if (fs.existsSync(CACHE)) return fs.readFileSync(CACHE, 'utf8');
  console.log(`downloading ${URL_}`);
  const res = await fetch(URL_);
  if (!res.ok) throw new Error(`cmudict: HTTP ${res.status}`);
  const text = await res.text();
  fs.mkdirSync(path.dirname(CACHE), { recursive: true });
  fs.writeFileSync(CACHE, text);
  return text;
}

const dict = new Map();
for (const line of (await source()).split('\n')) {
  const m = line.match(/^([^\s(]+)(?:\(\d+\))?\s+([^#]+)/);
  if (!m) continue;
  const word = m[1].toLowerCase();
  const phones = m[2].trim();
  if (!dict.has(word)) dict.set(word, []);
  const list = dict.get(word);
  if (!list.includes(phones)) list.push(phones);
}
const lines = [...dict.keys()].sort().map((w) => `${w}\t${dict.get(w).join('|')}`);
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, `# CMU Pronouncing Dictionary, cmusphinx/cmudict@${COMMIT.slice(0, 10)} (BSD-2-Clause, see data/CMUDICT-LICENSE)\n${lines.join('\n')}\n`);
console.log(`${lines.length} words written to ${path.relative(ROOT, OUT)}`);
