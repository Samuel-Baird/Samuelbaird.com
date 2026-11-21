// Regenerates the phonetic word table in /deseret.js. Run: node scripts/deseret-words.mjs [path/to/cmudict.dict]
// Deseret is phonemic: one letter per sound, not per spelled letter ("Collisions" is K-AH-L-IH-ZH-AH-N-Z,
// so the doubled "ll" is one 𐑊 and "si" is 𐑈). This script takes every word in the <h1> of each page that
// loads /deseret.js, looks up its pronunciation in the CMU Pronouncing Dictionary, and writes the
// word -> Deseret table between the WORDS markers in /deseret.js. Add hand corrections to OVERRIDES.
// Re-run whenever a page title changes; scripts/build.mjs warns if a title has a word missing from the table.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CMUDICT_URL = 'https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict';

// ARPAbet -> Deseret (lowercase). Stress digits are ignored. O is not ARPAbet: it is the short o (𐐱)
// of "not", which CMUdict folds into AA (the 𐐪 of "father"); use it in OVERRIDES.
const PHONE = {
  O: '𐐱',
  IY: '𐐨', EY: '𐐩', AA: '𐐪', AO: '𐐫', OW: '𐐬', UW: '𐐭', IH: '𐐮', EH: '𐐯', AE: '𐐰', AH: '𐐲', UH: '𐐳',
  AY: '𐐴', AW: '𐐵', OY: '𐑎', ER: '𐐲𐑉',
  W: '𐐶', Y: '𐐷', HH: '𐐸', P: '𐐹', B: '𐐺', T: '𐐻', D: '𐐼', CH: '𐐽', JH: '𐐾', K: '𐐿', G: '𐑀',
  F: '𐑁', V: '𐑂', TH: '𐑃', DH: '𐑄', S: '𐑅', Z: '𐑆', SH: '𐑇', ZH: '𐑈', R: '𐑉', L: '𐑊', M: '𐑋',
  N: '𐑌', NG: '𐑍',
};

// Hand corrections, as ARPAbet (or Deseret text). Keys are lowercase with a straight apostrophe.
const OVERRIDES = {
  and: 'AE1 N D', // stressed, as in a title, not the reduced "𐐲𐑌𐐼"
  not: 'N O1 T',
  lds: '𐐢𐐼𐑅', // initialism: first sound of Latter Day Saints (deseretalphabet.info rule 10)
  periodicals: 'P IH2 R IY0 O1 D IH0 K AH0 L Z',
  projects: 'P R O1 JH EH0 K T S',
  urim: 'Y UH1 R IH0 M', // as in Urim and Thummim
  peepstone: 'P IY1 P S T OW2 N',
  mcp: '𐑋𐐿𐐹', // initialism: Model Context Protocol
  the: '𐑄', // the single letter Thee, as on the Deseret Wiki
  a: '𐐪', // the single letter Ah (deseretalphabet.info rule 1)
  deseret: '𐐼𐐯𐑆𐐲𐑉𐐯𐐻', // DeZUret, as on the Deseret Wiki
};

const toDeseret = (phones) => phones.split(/\s+/).map((p) => {
  const base = p.replace(/\d$/, '');
  if (!PHONE[base]) throw new Error(`unknown phone ${p}`);
  return PHONE[base];
}).join('')
  // Y + UW is the single Deseret letter 𐑏 ("ew").
  .replace(/𐐷𐐭/gu, '𐑏');

async function loadDict(arg) {
  const text = arg ? fs.readFileSync(arg, 'utf8') : await (await fetch(CMUDICT_URL)).text();
  const dict = new Map();
  for (const line of text.split('\n')) {
    const m = line.match(/^(\S+?)(?:\(\d+\))?\s+([^#]+)/);
    if (m && !dict.has(m[1])) dict.set(m[1], m[2].trim()); // first listed pronunciation
  }
  return dict;
}

const decode = (s) => s.replace(/<[^>]+>/g, '').replace(/&rsquo;|&#8217;/g, '’').replace(/&amp;/g, '&')
  .replace(/&ndash;/g, '–').replace(/&mdash;/g, '—').replace(/&nbsp;/g, ' ');

export const WORD_RE = /[A-Za-z]+(?:['’][A-Za-z]+)*/g;
export const wordKey = (w) => w.toLowerCase().replace(/’/g, "'");

export function pageTitles() {
  const out = [];
  const walk = (dir) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      if (e.name.startsWith('.') || e.name === 'node_modules') continue;
      const p = path.join(dir, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.name.endsWith('.html')) {
        const html = fs.readFileSync(p, 'utf8');
        const h1 = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/);
        if (html.includes('/deseret.js') && h1) out.push({ file: path.relative(ROOT, p), text: decode(h1[1]).trim() });
      }
    }
  };
  walk(ROOT);
  return out;
}

export function readTable(src = fs.readFileSync(path.join(ROOT, 'deseret.js'), 'utf8')) {
  const m = src.match(/\/\* WORDS:start[^*]*\*\/\s*var WORDS = ([\s\S]*?);\s*\/\* WORDS:end \*\//);
  return m ? JSON.parse(m[1]) : {};
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const dict = await loadDict(process.argv[2]);
  const words = new Set(pageTitles().flatMap((t) => (t.text.match(WORD_RE) || []).map(wordKey)));
  const table = {}, missing = [];
  for (const w of [...words].sort()) {
    const o = OVERRIDES[w];
    if (o && /^\p{Script=Deseret}+$/u.test(o)) table[w] = o;
    else if (o || dict.has(w)) table[w] = toDeseret(o || dict.get(w));
    else missing.push(w);
  }
  if (missing.length) {
    console.error(`No pronunciation for: ${missing.join(', ')}. Add them to OVERRIDES in scripts/deseret-words.mjs.`);
    process.exit(1);
  }
  const file = path.join(ROOT, 'deseret.js');
  const src = fs.readFileSync(file, 'utf8');
  const body = '{\n' + Object.entries(table).map(([k, v]) => `    ${JSON.stringify(k)}: ${JSON.stringify(v)}`).join(',\n') + '\n  }';
  const next = src.replace(/(\/\* WORDS:start[^*]*\*\/\s*var WORDS = )[\s\S]*?(;\s*\/\* WORDS:end \*\/)/, `$1${body}$2`);
  if (next === src && !src.includes('WORDS:start')) throw new Error('WORDS markers not found in deseret.js');
  fs.writeFileSync(file, next);
  console.log(`deseret.js: ${Object.keys(table).length} words`);
}
