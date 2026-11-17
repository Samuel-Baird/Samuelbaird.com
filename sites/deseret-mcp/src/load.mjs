// Loads the committed data (data/) once per process and builds the engine and the wiki index.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createEngine, parseDict } from './dsrt.mjs';
import { createWiki } from './wiki.mjs';

export const DATA_DIR = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'data');
const read = (f) => fs.readFileSync(path.join(DATA_DIR, f), 'utf8');

let cached;
export function load() {
  if (cached) return cached;
  const overrides = Object.fromEntries(Object.entries(JSON.parse(read('overrides.json'))).filter(([k]) => !k.startsWith('_')));
  const corpus = JSON.parse(read('wiki.json'));
  const wiki = createWiki(corpus);
  const engine = createEngine({ dict: parseDict(read('cmudict.tsv')), overrides, freq: wiki.wordFreq() });
  cached = { engine, wiki, corpus };
  return cached;
}
