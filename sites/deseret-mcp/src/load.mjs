// Loads the committed data (data/) once per process and builds the engine and the wiki index.
// Node (CLI, stdio server, tests, Vercel) reads data/ from disk. Hosts without a filesystem (the
// Cloudflare Worker, src/worker.mjs) call provideData() with the same three files, bundled in.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createEngine, parseDict } from './dsrt.mjs';
import { createWiki } from './wiki.mjs';

export const DATA_DIR = (() => {
  try {
    return path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'data');
  } catch {
    return null; // bundled into a Worker: no module path, data comes from provideData()
  }
})();

let provided;
let cached;

/** Supply the data instead of reading data/: { overrides, wiki, cmudict }, each the file's text or (JSON) parsed value. */
export function provideData(data) {
  provided = data;
  cached = undefined;
}

function readData() {
  if (provided) return provided;
  const read = (f) => fs.readFileSync(path.join(DATA_DIR, f), 'utf8');
  return { overrides: read('overrides.json'), wiki: read('wiki.json'), cmudict: read('cmudict.tsv') };
}

const json = (v) => (typeof v === 'string' ? JSON.parse(v) : v);

export function load() {
  if (cached) return cached;
  const data = readData();
  const overrides = Object.fromEntries(Object.entries(json(data.overrides)).filter(([k]) => !k.startsWith('_')));
  const corpus = json(data.wiki);
  const wiki = createWiki(corpus);
  const engine = createEngine({ dict: parseDict(data.cmudict), overrides, freq: wiki.wordFreq() });
  cached = { engine, wiki, corpus };
  return cached;
}
