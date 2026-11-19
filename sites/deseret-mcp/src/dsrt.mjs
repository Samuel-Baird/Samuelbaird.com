// English <-> Deseret Alphabet. Same method as the Deseret Wiki (deseret/scripts/deseret-words.mjs and
// src/lib/dsrt.js): every word is looked up in the CMU Pronouncing Dictionary and its ARPAbet phones are
// mapped one to one onto Deseret letters, with hand overrides on top. Unlike the wiki's table, which only
// holds the site's own vocabulary, this uses the whole dictionary (126,052 words), builds a spelling for
// many words it lacks from their parts (faith + -ful + -ness), and reports every word it could not spell.
// No runtime dependencies; data is passed in so the same code runs on Vercel, in stdio and in tests.

// ARPAbet -> Deseret (lowercase). Keep in step with the wiki's PHONE table. O is not ARPAbet: it is the
// short o (𐐱) of "not", used in overrides.
export const PHONE = {
  O: '𐐱',
  IY: '𐐨', EY: '𐐩', AA: '𐐪', AO: '𐐫', OW: '𐐬', UW: '𐐭', IH: '𐐮', EH: '𐐯', AE: '𐐰', AH: '𐐲', UH: '𐐳',
  AY: '𐐴', AW: '𐐵', OY: '𐑎', ER: '𐐲𐑉',
  W: '𐐶', Y: '𐐷', HH: '𐐸', P: '𐐹', B: '𐐺', T: '𐐻', D: '𐐼', CH: '𐐽', JH: '𐐾', K: '𐐿', G: '𐑀',
  F: '𐑁', V: '𐑂', TH: '𐑃', DH: '𐑄', S: '𐑅', Z: '𐑆', SH: '𐑇', ZH: '𐑈', R: '𐑉', L: '𐑊', M: '𐑋',
  N: '𐑌', NG: '𐑍',
};

// Letter names, sounds and key words as the wiki's front page gives them (the 38 letters of 1854),
// plus the two letters added in 1859 that the wiki's table also uses.
export const LETTERS = [
  ['Long I', 'iː', 'eat'], ['Long E', 'eɪ', 'ate'], ['Long A', 'ɑː', 'art'], ['Long Ah', 'ɔː', 'aught'], ['Long O', 'oʊ', 'oat'], ['Long Oo', 'uː', 'ooze'],
  ['Short I', 'ɪ', 'it'], ['Short E', 'ɛ', 'egg'], ['Short A', 'æ', 'at'], ['Short Ah', 'ɒ', 'odd'], ['Short O', 'ʌ', 'up'], ['Short Oo', 'ʊ', 'book'],
  ['Ay', 'aɪ', 'ice'], ['Ow', 'aʊ', 'owl'], ['Wu', 'w', 'woe'], ['Yee', 'j', 'ye'], ['H', 'h', 'hay'], ['Pee', 'p', 'pay'], ['Bee', 'b', 'bee'],
  ['Tee', 't', 'tea'], ['Dee', 'd', 'day'], ['Chee', 'tʃ', 'cheese'], ['Jee', 'dʒ', 'jay'], ['Kay', 'k', 'key'], ['Gay', 'ɡ', 'gay'],
  ['Ef', 'f', 'fee'], ['Vee', 'v', 'vie'], ['Eth', 'θ', 'thigh'], ['Thee', 'ð', 'thy'], ['Es', 's', 'sea'], ['Zee', 'z', 'zeal'],
  ['Esh', 'ʃ', 'she'], ['Zhee', 'ʒ', 'vision'], ['Er', 'r', 'ray'], ['El', 'l', 'lay'], ['Em', 'm', 'may'], ['En', 'n', 'nay'], ['Eng', 'ŋ', 'sing'],
  ['Oi', 'ɔɪ', 'boy'], ['Ew', 'juː', 'few'],
].map(([name, ipa, word], i) => ({ glyph: String.fromCodePoint(0x10428 + i), capital: String.fromCodePoint(0x10400 + i), name, ipa, word }));
const LETTER_BY_GLYPH = new Map(LETTERS.map((l) => [l.glyph, l]));

// Latin respelling of each letter, used when Deseret text has a word no dictionary entry matches.
const RESPELL = {
  '𐐨': 'ee', '𐐩': 'ay', '𐐪': 'ah', '𐐫': 'aw', '𐐬': 'oh', '𐐭': 'oo', '𐐮': 'i', '𐐯': 'e', '𐐰': 'a', '𐐱': 'o', '𐐲': 'u', '𐐳': 'uu',
  '𐐴': 'ai', '𐐵': 'ow', '𐐶': 'w', '𐐷': 'y', '𐐸': 'h', '𐐹': 'p', '𐐺': 'b', '𐐻': 't', '𐐼': 'd', '𐐽': 'ch', '𐐾': 'j', '𐐿': 'k', '𐑀': 'g',
  '𐑁': 'f', '𐑂': 'v', '𐑃': 'th', '𐑄': 'dh', '𐑅': 's', '𐑆': 'z', '𐑇': 'sh', '𐑈': 'zh', '𐑉': 'r', '𐑊': 'l', '𐑋': 'm', '𐑌': 'n', '𐑍': 'ng',
  '𐑎': 'oi', '𐑏': 'ew',
};

const CASE_OFFSET = 0x28; // Deseret capitals sit 0x28 below lowercase
const isDsrtUpper = (cp) => cp >= 0x10400 && cp <= 0x10427;
const lowerDsrt = (s) => Array.from(s).map((c) => { const cp = c.codePointAt(0); return isDsrtUpper(cp) ? String.fromCodePoint(cp + CASE_OFFSET) : c; }).join('');
const upperDsrt = (s) => Array.from(s).map((c) => { const cp = c.codePointAt(0); return cp >= 0x10428 && cp <= 0x1044f ? String.fromCodePoint(cp - CASE_OFFSET) : c; }).join('');
const HAS_DSRT = /[\u{10400}-\u{1044F}]/u;

const IPA = /[ɐ-ʯʰ-˿ᴀ-ᶿı]/u;
export const WORD_RE = /\p{Script=Latin}+(?:['’]\p{Script=Latin}+)*/gu;
const DSRT_RE = /[\u{10400}-\u{1044F}]+(?:['’][\u{10400}-\u{1044F}]+)*/gu;

/** Lowercase key: straight apostrophe, accents removed (café -> cafe). */
export const keyOf = (w) => w.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase().replace(/’/g, "'");

/** ARPAbet phones ("AE1 N D") -> lowercase Deseret. Throws on an unknown phone. */
export function phonesToDeseret(phones) {
  return phones.trim().split(/\s+/).map((p) => {
    const base = p.replace(/\d$/, '');
    if (!PHONE[base]) throw new Error(`unknown ARPAbet phone "${p}"`);
    return PHONE[base];
  }).join('').replace(/𐐷𐐭/gu, '𐑏'); // Y + UW is the single letter 𐑏 ("ew"), as on the wiki
}

// Syllabic values: a letter written on its own is read as its name, so a whole word that sounds exactly like
// a letter's name is written with that one letter (be/bee 𐐺, tea/tee 𐐻, gay 𐑀, thee 𐑄). Never inside a
// longer word ("bees" is 𐐺𐐨𐑆). The list is the one the Deseret Wiki's article gives; keep it in step with
// SYLLABIC in the wiki's scripts/deseret-words.mjs. ("the" is 𐑄 through the overrides; "you" is already 𐑏.)
export const SYLLABIC = {
  '𐐶𐐭': '𐐶', '𐐷𐐨': '𐐷', '𐐸𐐪': '𐐸', '𐐹𐐨': '𐐹', '𐐺𐐨': '𐐺',
  '𐐻𐐨': '𐐻', '𐐽𐐨': '𐐽', '𐐾𐐨': '𐐾', '𐑀𐐩': '𐑀', '𐑄𐐨': '𐑄',
};
// Reading a lone letter back: the usual word first; other words spelled as the name follow as alternatives.
const SYLLABIC_READ = { '𐐶': 'woo', '𐐷': 'ye', '𐐸': 'ha', '𐐹': 'pea', '𐐺': 'be', '𐐻': 'tea', '𐐾': 'gee', '𐑀': 'gay', '𐑄': 'the' };
/** Lowercase whole-word Deseret -> its single-letter form when it is a letter's name. */
export const syllabic = (d) => SYLLABIC[d] ?? d;

/** Reapply the Latin word's case: UPPER (2+ letters), Title, or lower. */
export function applyCase(latin, dsrt) {
  const letters = latin.replace(/[^\p{L}]/gu, '');
  if (letters.length > 1 && letters === letters.toUpperCase() && letters !== letters.toLowerCase()) return upperDsrt(dsrt);
  if (latin[0] !== latin[0].toLowerCase()) { const [first, ...rest] = Array.from(dsrt); return upperDsrt(first) + rest.join(''); }
  return dsrt;
}

/** Parse data/cmudict.tsv into Map<word, phones[]>. */
export function parseDict(tsv) {
  const dict = new Map();
  for (const line of tsv.split('\n')) {
    if (!line || line[0] === '#') continue;
    const tab = line.indexOf('\t');
    dict.set(line.slice(0, tab), line.slice(tab + 1).split('|'));
  }
  return dict;
}

// ---- deriving a spelling for a word the dictionary lacks
const base = (p) => p.replace(/\d$/, '');
const last = (phones) => base(phones.trim().split(/\s+/).pop());
const SIBILANT = new Set(['S', 'Z', 'SH', 'ZH', 'CH', 'JH']);
const VOICELESS = new Set(['P', 'T', 'K', 'F', 'TH']);
const sEnd = (ph) => (SIBILANT.has(last(ph)) ? 'IH0 Z' : VOICELESS.has(last(ph)) ? 'S' : 'Z');
const edEnd = (ph) => (['T', 'D'].includes(last(ph)) ? 'IH0 D' : [...VOICELESS, 'S', 'SH', 'CH'].includes(last(ph)) ? 'T' : 'D');
const yToSchwa = (ph) => ph.replace(/IY0$/, 'AH0');
const doubled = (s) => (s.length > 2 && s.at(-1) === s.at(-2) && !/[aeiouyls]/.test(s.at(-1)) ? s.slice(0, -1) : null);

// [suffix, stems(word without suffix) -> candidate stems, phones of stem -> phones of word]
const SUFFIXES = [
  ["'s", (s) => [s], (p) => `${p} ${sEnd(p)}`],
  ['ies', (s) => [s + 'y'], (p) => `${p} Z`],
  ['es', (s) => (/(s|x|z|ch|sh|o)$/.test(s) ? [s] : []), (p) => `${p} ${sEnd(p)}`],
  ['s', (s) => [s], (p) => `${p} ${sEnd(p)}`],
  ['ied', (s) => [s + 'y'], (p) => `${p} D`],
  ['ed', (s) => [s, s + 'e', doubled(s)], (p) => `${p} ${edEnd(p)}`],
  ['ing', (s) => [s, s + 'e', doubled(s)], (p) => `${p} IH0 NG`],
  ['ers', (s) => [s, s + 'e', doubled(s)], (p) => `${p} ER0 Z`],
  ['er', (s) => [s, s + 'e', doubled(s)], (p) => `${p} ER0`],
  ['est', (s) => [s, s + 'e', doubled(s)], (p) => `${p} AH0 S T`],
  ['ily', (s) => [s + 'y'], (p) => `${yToSchwa(p)} L IY0`],
  ['ly', (s) => [s], (p) => `${p} L IY0`],
  ['iness', (s) => [s + 'y'], (p) => `${yToSchwa(p)} N AH0 S`],
  ['ness', (s) => [s], (p) => `${p} N AH0 S`],
  ['ments', (s) => [s], (p) => `${p} M AH0 N T S`],
  ['ment', (s) => [s], (p) => `${p} M AH0 N T`],
  ['fully', (s) => [s], (p) => `${p} F AH0 L IY0`],
  ['ful', (s) => [s], (p) => `${p} F AH0 L`],
  ['lessly', (s) => [s], (p) => `${p} L AH0 S L IY0`],
  ['less', (s) => [s], (p) => `${p} L AH0 S`],
  ['ships', (s) => [s], (p) => `${p} SH IH2 P S`],
  ['ship', (s) => [s], (p) => `${p} SH IH2 P`],
  ['hood', (s) => [s], (p) => `${p} HH UH2 D`],
  ['dom', (s) => [s], (p) => `${p} D AH0 M`],
  ['like', (s) => [s], (p) => `${p} L AY2 K`],
  ['wise', (s) => [s], (p) => `${p} W AY2 Z`],
  ['ward', (s) => [s], (p) => `${p} W ER0 D`],
  ['wards', (s) => [s], (p) => `${p} W ER0 D Z`],
  ['able', (s) => [s, s + 'e', doubled(s)], (p) => `${p} AH0 B AH0 L`],
  ['ism', (s) => [s, s + 'e'], (p) => `${p} IH2 Z AH0 M`],
  ['ist', (s) => [s, s + 'e'], (p) => `${p} IH0 S T`],
  ['ish', (s) => [s, s + 'e', doubled(s)], (p) => `${p} IH0 SH`],
  ['y', (s) => [s, s + 'e', doubled(s)], (p) => `${p} IY0`],
].sort((a, b) => b[0].length - a[0].length); // longest ending first: -ness before -s
const PREFIXES = [
  ['un', 'AH0 N'], ['re', 'R IY0'], ['pre', 'P R IY0'], ['dis', 'D IH0 S'], ['mis', 'M IH0 S'], ['non', 'N AA1 N'],
  ['over', 'OW1 V ER0'], ['under', 'AH1 N D ER0'], ['out', 'AW1 T'], ['anti', 'AE1 N T IY0'], ['inter', 'IH1 N T ER0'],
  ['sub', 'S AH1 B'], ['super', 'S UW1 P ER0'], ['self', 'S EH1 L F'], ['fore', 'F AO1 R'], ['counter', 'K AW1 N T ER0'],
];

const COMPOUND_HEADS = [
  'keepers', 'keeper', 'makers', 'maker', 'holders', 'holder', 'writers', 'writer', 'setters', 'setter', 'lighters', 'lighter',
  'houses', 'house', 'women', 'woman', 'men', 'man', 'lands', 'land', 'works', 'work', 'lights', 'light', 'stones', 'stone',
  'fields', 'field', 'books', 'book', 'boards', 'board', 'rooms', 'room', 'yards', 'yard', 'places', 'place', 'sides', 'side',
  'ways', 'way', 'days', 'day', 'times', 'time', 'water', 'fire', 'wood', 'craft', 'folk', 'mind', 'minded', 'born', 'bound',
  'proof', 'master', 'masters', 'fold', 'line', 'lines', 'point', 'power', 'sight', 'song', 'songs', 'letters', 'letter',
  'type', 'types', 'face', 'faces', 'stead', 'worthy', 'wide', 'smith', 'smiths', 'hold', 'holds', 'ward', 'wards',
].sort((a, b) => b.length - a.length);

// Common heteronyms: the reading used when nothing else decides, and the words before it that pick the other.
const HETERONYMS = {
  read: { phones: 'R IY1 D', after: { phones: 'R EH1 D', words: ['have', 'has', 'had', 'having', "i've", "we've", "you've", "they've", 'was', 'were', 'been', 'being', 'is', 'are', 'be'] } },
  live: { phones: 'L IH1 V' },
  lead: { phones: 'L IY1 D' },
  wind: { phones: 'W IH1 N D' },
  tear: { phones: 'T IH1 R' },
  close: { phones: 'K L OW1 Z' },
  use: { phones: 'Y UW1 Z', after: { phones: 'Y UW1 S', words: ['the', 'a', 'no', 'of', 'any', 'its', 'his', 'her', 'their', 'our', 'my', 'your', 'some', 'what', 'much'] } },
  wound: { phones: 'W UW1 N D' },
  bow: { phones: 'B AW1' },
  minute: { phones: 'M IH1 N AH0 T' },
};

/**
 * Create a transliterator.
 * @param {{dict: Map<string,string[]>, overrides?: Record<string,string>, freq?: Map<string,number>}} opts
 *   overrides: word -> ARPAbet or Deseret text (hand corrections, as on the wiki)
 *   freq: word counts used to choose between homophones when reading Deseret back into Latin
 */
export function createEngine({ dict, overrides = {}, freq = new Map() }) {
  const cache = new Map();

  const toDsrt = (spec) => (HAS_DSRT.test(spec) ? lowerDsrt(spec) : phonesToDeseret(spec));

  function direct(k, extra) {
    const o = (extra && extra[k]) ?? overrides[k];
    if (o) return { deseret: toDsrt(o), phones: HAS_DSRT.test(o) ? null : o, source: extra && extra[k] ? 'given' : 'override' };
    const p = dict.get(k);
    if (p) {
      const h = HETERONYMS[k];
      const phones = h ? h.phones : p[0];
      return { deseret: phonesToDeseret(phones), phones, source: 'cmudict' };
    }
    return null;
  }

  function stemPhones(stem, depth, extra) {
    if (!stem || stem.length < 2) return null;
    const d = direct(stem, extra);
    if (d && d.phones) return { phones: d.phones, how: [stem] };
    if (depth > 0) {
      const r = derive(stem, depth - 1, extra);
      if (r) return r;
    }
    return null;
  }

  function derive(k, depth, extra) {
    for (const [suf, stems, build] of SUFFIXES) {
      if (!k.endsWith(suf) || k.length - suf.length < 2) continue;
      if (suf === 's' && /(ss|us|is)$/.test(k)) continue; // glass, focus, basis are not plurals
      const rest = k.slice(0, -suf.length);
      for (const s of stems(rest)) {
        if (!s || s.length < 3) continue;
        const st = stemPhones(s, depth, extra);
        if (st) return { phones: build(st.phones), how: [...st.how, `-${suf.replace("'", '’')}`] };
      }
    }
    for (const [pre, ph] of PREFIXES) {
      if (!k.startsWith(pre) || k.length - pre.length < 3) continue;
      const st = stemPhones(k.slice(pre.length), depth, extra);
      if (st) return { phones: `${ph} ${st.phones}`, how: [`${pre}-`, ...st.how] };
    }
    // compound ending in a common head word (lamplighters = lamp + lighter -s). Splitting at any point
    // turns names into nonsense (zara + hem + lit), so only these heads are allowed.
    for (const head of COMPOUND_HEADS) {
      if (!k.endsWith(head) || k.length - head.length < 3) continue;
      const a = direct(k.slice(0, -head.length), extra);
      const b = direct(head, extra);
      if (a && a.phones && b && b.phones) return { phones: `${a.phones} ${b.phones}`, how: [k.slice(0, -head.length), '+', head] };
    }
    return null;
  }

  /** Spell one word (any case). Returns null if it has no spelling. */
  function word(w, extra) {
    const k = keyOf(w);
    const ck = extra ? null : k;
    let r = ck !== null ? cache.get(ck) : undefined;
    if (r === undefined) {
      r = direct(k, extra);
      if (!r) {
        const d = derive(k, 2, extra);
        r = d ? { deseret: phonesToDeseret(d.phones), phones: d.phones, source: 'derived', how: d.how.join(' ') } : null;
      }
      if (ck !== null) cache.set(ck, r);
    }
    if (!r) return null;
    const one = syllabic(r.deseret);
    return { ...r, deseret: applyCase(w, one), ...(one !== r.deseret ? { syllabic: true } : {}) };
  }

  /** Every spelling we know for a word, with letter names: for the deseret_word tool. */
  function explain(w) {
    const k = keyOf(w);
    const chosen = word(w);
    const prons = dict.get(k) || [];
    const alternatives = prons.map((p) => ({ phones: p, deseret: applyCase(w, phonesToDeseret(p)) }));
    const letters = chosen ? Array.from(lowerDsrt(chosen.deseret)).map((g) => {
      const l = LETTER_BY_GLYPH.get(g);
      return l ? { glyph: g, name: l.name, sound: `/${l.ipa}/`, as_in: l.word } : { glyph: g };
    }) : [];
    return {
      word: w,
      found: !!chosen,
      deseret: chosen ? chosen.deseret : null,
      source: chosen ? chosen.source : null,
      phones: chosen ? chosen.phones : null,
      ...(chosen && chosen.how ? { derived_from: chosen.how } : {}),
      ...(chosen && chosen.syllabic ? { syllabic: 'Written with one letter: the word sounds like the letter’s name (its syllabic value).' } : {}),
      ...(HETERONYMS[k] ? { note: 'Heteronym: the spelling depends on the sense. to_deseret picks one from the words before it; pass `spellings` to force one.' } : {}),
      alternatives: alternatives.length > 1 || (alternatives.length && chosen && alternatives[0].deseret !== chosen.deseret) ? alternatives : undefined,
      letters,
    };
  }

  // ---- text
  const PROTECT = {
    plain: [/https?:\/\/[^\s<>()]+/gu, /\bwww\.[^\s<>()]+/gu, /[\w.+-]+@[\w-]+\.[\w.-]+/gu],
    markdown: [
      /^---\r?\n[\s\S]*?\r?\n---(?=\r?\n|$)/gu, // frontmatter (only matched at offset 0, see below)
      /^(```|~~~)[^\n]*\n[\s\S]*?\n\1[^\n]*$/gmu, // fenced code
      /`+[^`\n]+`+/gu, // inline code
      /<!--[\s\S]*?-->/gu,
      /<\/?[A-Za-z][^>\n]*>/gu, // html tags
      /\]\([^)\s]*(?:\s+"[^"]*")?\)/gu, // link / image destination
      /^\s{0,3}\[[^\]]+\]:\s*\S+.*$/gmu, // reference definitions
      /\[\^[^\]]+\]/gu, // footnote marks
      /&#?\w+;/gu,
      /https?:\/\/[^\s<>()\]]+/gu, /\bwww\.[^\s<>()\]]+/gu, /[\w.+-]+@[\w-]+\.[\w.-]+/gu,
    ],
    html: [
      /<!--[\s\S]*?-->/gu,
      /<(script|style|code|pre|textarea)\b[^>]*>[\s\S]*?<\/\1>/giu,
      /<[^>]+>/gu,
      /&#?\w+;/gu,
      /https?:\/\/[^\s<>()]+/gu,
    ],
  };

  function protectedSpans(text, format) {
    const spans = [];
    for (const re of PROTECT[format] || PROTECT.plain) {
      re.lastIndex = 0;
      let m;
      while ((m = re.exec(text))) {
        if (!m[0]) { re.lastIndex++; continue; }
        if (re.source.startsWith('^---') && m.index !== 0) continue;
        spans.push([m.index, m.index + m[0].length]);
      }
    }
    spans.sort((a, b) => a[0] - b[0]);
    const merged = [];
    for (const s of spans) {
      const top = merged.at(-1);
      if (top && s[0] <= top[1]) top[1] = Math.max(top[1], s[1]);
      else merged.push([...s]);
    }
    return merged;
  }

  /**
   * Transliterate text. format: plain | markdown | html. strict: leave derived spellings in Latin.
   * spellings: per-call word -> ARPAbet or Deseret.
   * respell: optional (latinWord, deseret) => deseret, applied to every spelled word (see historical1868).
   */
  function text(input, { format = 'plain', strict = false, spellings, respell } = {}) {
    let extra = null;
    if (spellings && Object.keys(spellings).length) {
      extra = {};
      for (const [w, spec] of Object.entries(spellings)) {
        toDsrt(String(spec)); // validate now, so a bad phone is reported once
        extra[keyOf(w)] = String(spec);
      }
    }
    const stats = { words: 0, from_dictionary: 0, derived: 0, unknown: 0 };
    const unknown = new Map();
    const derived = new Map();
    const hetero = new Map();
    let prevKey = '';

    const convertRun = (run) => run.replace(WORD_RE, (w, off, whole) => {
      const before = whole[off - 1] || '';
      const after = whole[off + w.length] || '';
      if (/\d/.test(before) || /\d/.test(after)) return w; // 1st, 2nd, 10am
      if (IPA.test(w)) return w; // phonetic notation (/ˈdɛzərɛt/) is not English spelling
      stats.words++;
      const k = keyOf(w);
      let r;
      const h = HETERONYMS[k];
      if (h && !(extra && extra[k]) && !overrides[k]) {
        const phones = h.after && h.after.words.includes(prevKey) ? h.after.phones : h.phones;
        r = { deseret: applyCase(w, syllabic(phonesToDeseret(phones))), phones, source: 'cmudict' };
        if (!hetero.has(k)) hetero.set(k, { word: k, alternatives: (dict.get(k) || []).map((p) => phonesToDeseret(p)).filter((d, i, a) => a.indexOf(d) === i), used: new Set() });
        hetero.get(k).used.add(lowerDsrt(r.deseret));
      } else {
        r = word(w, extra);
      }
      prevKey = k;
      if (!r || (strict && r.source === 'derived')) {
        stats.unknown++;
        unknown.set(w, (unknown.get(w) || 0) + 1);
        if (r) derived.set(k, { word: k, deseret: lowerDsrt(r.deseret), from: r.how, kept_in_latin: true });
        return w;
      }
      if (r.source === 'derived') {
        stats.derived++;
        if (!derived.has(k)) derived.set(k, { word: k, deseret: lowerDsrt(r.deseret), from: r.how });
      } else stats.from_dictionary++;
      return respell ? respell(w, r.deseret) || r.deseret : r.deseret;
    });

    let out = '';
    let pos = 0;
    for (const [a, b] of protectedSpans(input, format)) {
      out += convertRun(input.slice(pos, a)) + input.slice(a, b);
      pos = b;
    }
    out += convertRun(input.slice(pos));

    const unknownList = [...unknown].map(([w, count]) => ({ word: w, count })).sort((a, b) => b.count - a.count || a.word.localeCompare(b.word));
    return {
      deseret: out,
      stats,
      unknown: unknownList,
      derived: [...derived.values()],
      heteronyms: [...hetero.values()].filter((h) => h.alternatives.length > 1).map((h) => ({ word: h.word, used: [...h.used], alternatives: h.alternatives })),
    };
  }

  // ---- Deseret -> Latin
  let reverse = null;
  function reverseIndex() {
    if (reverse) return reverse;
    reverse = new Map();
    const add = (key, w, rank) => {
      if (!reverse.has(key)) reverse.set(key, []);
      const list = reverse.get(key);
      if (!list.some((e) => e.w === w)) list.push({ w, rank });
    };
    for (const [w, spec] of Object.entries(overrides)) add(toDsrt(spec), w, 0);
    for (const [w, prons] of dict) {
      if (!/^[a-z]+(?:'[a-z]+)?$/.test(w)) continue;
      prons.forEach((p, i) => { try { add(phonesToDeseret(p), w, i === 0 ? 1 : 2); } catch { /* skip */ } });
    }
    // 1868 printing forms (see historical1868), so period Deseret text reads back too.
    add('𐑄', 'the', 1);
    add('𐐼𐐯𐑅𐐨𐑉𐐯𐐻', 'deseret', 1); // DeSEEret, the primers' spelling
    add('𐐱𐑂', 'of', 1);
    for (const [full, one] of Object.entries(SYLLABIC)) {
      if (SYLLABIC_READ[one]) add(one, SYLLABIC_READ[one], 0);
      for (const e of reverse.get(full) || []) if (e.w.length > 1) add(one, e.w, Math.max(1, e.rank)); // not the letter names b, t
    }
    // Hand corrections (rank 0) beat dictionary entries; then first pronunciations, frequency, length.
    const score = (e) => [e.rank === 0 ? 0 : 1, e.rank === 2 ? 1 : 0, -(freq.get(e.w) || 0), e.w.includes("'") ? 1 : 0, e.w.length, e.w];
    const cmp = (a, b) => { const x = score(a), y = score(b); for (let i = 0; i < x.length; i++) if (x[i] !== y[i]) return x[i] < y[i] ? -1 : 1; return 0; };
    for (const list of reverse.values()) list.sort(cmp);
    return reverse;
  }

  const latinCase = (dsrt, latin) => {
    const glyphs = Array.from(dsrt);
    const caps = glyphs.filter((g) => isDsrtUpper(g.codePointAt(0))).length;
    if (glyphs.length > 1 && caps === glyphs.length) return latin.toUpperCase();
    if (caps && isDsrtUpper(glyphs[0].codePointAt(0))) return latin[0].toUpperCase() + latin.slice(1);
    return latin;
  };

  function fromDeseret(input) {
    const idx = reverseIndex();
    const ambiguous = new Map();
    const respelled = new Map();
    const stats = { words: 0, matched: 0, ambiguous: 0, respelled: 0 };
    const latin = input.replace(DSRT_RE, (d) => {
      stats.words++;
      const key = lowerDsrt(d).replace(/’/g, "'");
      // 1868 forms the dictionary spells differently: 𐐸𐐶 for "wh", -𐐮𐑅 for -ness/-less.
      const hits = idx.get(key)
        || (key.startsWith('𐐸𐐶') && idx.get(key.slice(2))) // drop 𐐸 (one letter = two UTF-16 units)
        || (key.endsWith('𐐮𐑅') && (idx.get(key.slice(0, -4) + '𐐲𐑅') || idx.get(key.slice(0, -4) + '𐐯𐑅')));
      if (hits) {
        stats.matched++;
        if (hits.length > 1) {
          stats.ambiguous++;
          if (!ambiguous.has(key)) ambiguous.set(key, { deseret: key, chose: hits[0].w, also: hits.slice(1, 6).map((e) => e.w) });
        }
        return latinCase(d, hits[0].w);
      }
      stats.respelled++;
      const r = Array.from(key).map((g) => RESPELL[g] ?? g).join('');
      if (!respelled.has(key)) respelled.set(key, { deseret: key, respelled: r });
      return latinCase(d, r);
    });
    return { latin, stats, ambiguous: [...ambiguous.values()], respelled: [...respelled.values()] };
  }

  return { word, explain, text, fromDeseret, size: dict.size };
}

// 1868-69 printing conventions (Orson Pratt's transcriptions: the Deseret First and Second Books and the
// 1869 Book of Mormon), limited to patterns the Deseret Wiki documents with printed examples:
//   "the" is the single letter 𐑄 ("𐐸𐐬𐑊𐐨𐑌𐐮𐑅 𐐻𐐭 𐑄 𐐢𐐫𐑉𐐼", 1860 coin; "𐑅𐐲𐑉𐑂 𐑄 𐐢𐐫𐑉𐐼", Second Book hymn); now the default too
//   "Deseret" is 𐐔𐐯𐑅𐐨𐑉𐐯𐐻 (DeSEEret), as in the primers' titles; the modern default is 𐐔𐐯𐑆𐐲𐑉𐐯𐐻
//   "of" is 𐐱𐑂 (title page of the First and Second Books, "𐐱𐑂 𐑄 𐐔𐐇𐐝𐐀𐐡𐐇𐐓 ...")
//   "wh" keeps its h: 𐐸𐐶 ("𐐸𐐶𐐴𐑊" while, "𐐸𐐶𐐩𐑉𐑁𐐬𐑉" wherefore; no wine-whine merger)
//   -ness/-less end in 𐐮𐑅 ("𐐸𐐬𐑊𐐨𐑌𐐮𐑅" Holiness)
// Use as engine.text(s, historical1868). Everything else follows the modern dictionary spelling.
export const historical1868 = {
  spellings: { the: '𐑄', of: '𐐱𐑂', deseret: '𐐼𐐯𐑅𐐨𐑉𐐯𐐻' },
  respell(latin, dsrt) {
    const k = keyOf(latin);
    let out = dsrt;
    if (k.startsWith('wh') && /^[𐐶𐐎]/u.test(out)) out = (/^𐐎/u.test(out) ? '𐐐𐐶' : '𐐸𐐶') + Array.from(out).slice(1).join('');
    if (/(ness|less)$/.test(k)) out = out.replace(/[𐐲𐐯]𐑅$/u, '𐐮𐑅').replace(/[𐐊𐐇]𐐝$/u, '𐐆𐐝');
    return out;
  },
};
