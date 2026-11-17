// Builds the English -> Deseret word table used by the title reveal and the Latin/Deseret toggle.
// Run: npm run words   (re-run whenever page text changes; the output is committed)
//
// Deseret is phonemic: one letter per sound, not per spelled letter, so every word is looked up in the
// CMU Pronouncing Dictionary (downloaded once to scripts/.cache/). Words it doesn't know are left out of
// the table and stay in Latin letters on the page rather than being spelled out letter by letter.
// Port of Samuelbaird.com/scripts/deseret-words.mjs; keep PHONE and the 𐑏 rule in sync with it.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CACHE = path.join(ROOT, 'scripts', '.cache', 'cmudict.dict');
const OUT = path.join(ROOT, 'src', 'data', 'deseret-words.json');
const CMUDICT_URL = 'https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict';

// ARPAbet -> Deseret (lowercase). O is not ARPAbet: it is the short o (𐐱) of "not", for OVERRIDES.
const PHONE = {
  O: '𐐱',
  IY: '𐐨', EY: '𐐩', AA: '𐐪', AO: '𐐫', OW: '𐐬', UW: '𐐭', IH: '𐐮', EH: '𐐯', AE: '𐐰', AH: '𐐲', UH: '𐐳',
  AY: '𐐴', AW: '𐐵', OY: '𐑎', ER: '𐐲𐑉',
  W: '𐐶', Y: '𐐷', HH: '𐐸', P: '𐐹', B: '𐐺', T: '𐐻', D: '𐐼', CH: '𐐽', JH: '𐐾', K: '𐐿', G: '𐑀',
  F: '𐑁', V: '𐑂', TH: '𐑃', DH: '𐑄', S: '𐑅', Z: '𐑆', SH: '𐑇', ZH: '𐑈', R: '𐑉', L: '𐑊', M: '𐑋',
  N: '𐑌', NG: '𐑍',
};

// Hand corrections, as ARPAbet or Deseret text. Keys are lowercase with a straight apostrophe.
const OVERRIDES = {
  and: 'AE1 N D',
  not: 'N O1 T',
  deseret: '𐐼𐐯𐑅𐐨𐑉𐐯𐐻', // the spelling the alphabet's own publications use
  wiki: 'W IH1 K IY0',
  mormon: 'M AO1 R M AH0 N',
  pitman: 'P IH1 T M AH0 N',
  regents: 'R IY1 JH AH0 N T S',
  latin: 'L AE1 T AH0 N',
  unicode: 'Y UW1 N IH0 K OW2 D',
  youtube: 'Y UW1 T UW2 B',
  amazon: 'AE1 M AH0 Z O2 N',
  autography: 'AO0 T AA1 G R AH0 F IY0', // Woodruff's spelling of orthography, kept as he wrote it
  leters: 'L EH1 T ER0 Z',              // Parley P. Pratt's spelling
  schonfield: 'SH OW1 N F IY2 L D',
};

const toDeseret = (phones) => phones.split(/\s+/).map((p) => {
  const base = p.replace(/\d$/, '');
  if (!PHONE[base]) throw new Error(`unknown phone ${p}`);
  return PHONE[base];
}).join('').replace(/𐐷𐐭/gu, '𐑏'); // Y + UW is the single letter 𐑏 ("ew")

async function cmudict() {
  if (!fs.existsSync(CACHE)) {
    console.log('downloading cmudict…');
    const res = await fetch(CMUDICT_URL);
    if (!res.ok) throw new Error(`cmudict: HTTP ${res.status}`);
    fs.mkdirSync(path.dirname(CACHE), { recursive: true });
    fs.writeFileSync(CACHE, await res.text());
  }
  const dict = new Map();
  for (const line of fs.readFileSync(CACHE, 'utf8').split('\n')) {
    const m = line.match(/^([^\s(]+)(?:\(\d+\))?\s+([^#]+)/);
    if (m && !dict.has(m[1])) dict.set(m[1], m[2].trim()); // first pronunciation wins
  }
  return dict;
}

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (/\.(astro|md|mdx|json)$/.test(e.name) && p !== OUT) out.push(p);
  }
  return out;
}

// Visible-ish text only: drop URLs, code fences, front-matter scripts, tags and attributes.
function textOf(file) {
  let s = fs.readFileSync(file, 'utf8');
  if (file.endsWith('.json')) {
    return [...s.matchAll(/"(?:title|author|note|by|name|label|text)"\s*:\s*"([^"]*)"/g)].map((m) => m[1]).join(' ');
  }
  s = s.replace(/^---[\s\S]*?\n---/, ' ')
    .replace(/<(script|style)[\s\S]*?<\/\1>/g, ' ')
    .replace(/\]\([^)]*\)/g, '] ')
    .replace(/https?:\/\/\S+/g, ' ')
    .replace(/<[^>]*>/g, ' ')
    .replace(/\{[^{}]*\}/g, ' ');
  return s;
}

const dict = await cmudict();
const words = new Set();
for (const f of walk(path.join(ROOT, 'src'))) {
  for (const m of textOf(f).matchAll(/[A-Za-z]+(?:['’][A-Za-z]+)*/g)) words.add(m[0].toLowerCase().replace(/’/g, "'"));
}

const table = {};
let missing = 0;
for (const w of [...words].sort()) {
  const o = OVERRIDES[w];
  if (o && /[\u{10400}-\u{1044F}]/u.test(o)) { table[w] = o; continue; }
  const phones = o ?? dict.get(w);
  if (!phones) { missing++; continue; }
  table[w] = toDeseret(phones);
}
fs.writeFileSync(OUT, JSON.stringify(table));
console.log(`${Object.keys(table).length} words written to ${path.relative(ROOT, OUT)}; ${missing} not in cmudict (left in Latin)`);
