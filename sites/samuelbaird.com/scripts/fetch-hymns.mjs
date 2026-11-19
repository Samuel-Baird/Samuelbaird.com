// Build the open dataset of Latter-day Saint hymnbooks, one record per hymn per edition:
// data/lds-hymns.json and .csv. Run: node scripts/fetch-hymns.mjs [--refresh]
//
// Editions and sources (facts only: number, title, first line, credits; no lyrics are stored):
//   1835  A Collection of Sacred Hymns (Emma Smith, Kirtland): the Joseph Smith Papers transcription's
//         table of contents ("Hymn N • first line"). The book has no titles or author credits.
//   1841  A Collection of Sacred Hymns (Emma Smith, Nauvoo): same, from the Joseph Smith Papers.
//   1985  Hymns of The Church of Jesus Christ of Latter-day Saints: the Church's Gospel Library pages
//         (number, title, first line, the "Text:" and "Music:" credits as printed).
//   2024- Hymns—For Home and Church: the Church's Gospel Library pages, same fields. The book is still
//         being released in batches; only the hymns published so far are in it.
//   Wikidata (CC0): an author's or composer's religion (P140), only when the Wikidata person has the
//         same name and the same birth and death years as the hymnbook credit.
//
// Change status ("added", "kept", "removed") compares an edition with the one before it in this
// dataset, and only where that is the book's real predecessor: 1841 against 1835, and Hymns—For Home
// and Church against 1985. 1985 is left blank: its predecessor (Hymns, 1948/1950) is not in the dataset
// yet. Hymns—For Home and Church has no "removed" records until the whole book is out.
// Hymns are linked across editions by their normalized first line (hymnKey); see KEY_OVERRIDES for the
// hand links, each with its reason.
//
// Gaps: every run lists what is missing (a number with no hymn, a hymn with no first line or credit, a hand
// entry still to verify) in the JSON's `missing` list and data/lds-hymns-missing.csv. Hand entries for hymns a
// source skips go in scripts/hymn-additions.json (with their own source); what was tried and where to look next
// goes in scripts/hymn-missing.json.
//
// Pages are cached in scripts/cache/hymns.json (facts only) so reruns only fetch what is new;
// --refresh refetches every page. Polite: one request at a time, ~0.3 s apart. No dependencies.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT_JSON = path.join(ROOT, 'data', 'lds-hymns.json');
const OUT_CSV = path.join(ROOT, 'data', 'lds-hymns.csv');
const OUT_MISSING = path.join(ROOT, 'data', 'lds-hymns-missing.csv');
const CACHE = path.join(ROOT, 'scripts', 'cache', 'hymns.json');
const REFRESH = process.argv.includes('--refresh');
const CHURCH = 'https://www.churchofjesuschrist.org';
const STUDY_API = `${CHURCH}/study/api/v3/language-pages/type/content?lang=eng&uri=`;
const JSP = 'https://www.josephsmithpapers.org';
const UA_BROWSER = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36';
const UA_BOT = 'lds-hymns-dataset/1.0 (open data script)';

const EDITIONS = [
  { id: '1835', year: 1835, short: '1835 Kirtland', title: 'A Collection of Sacred Hymns, for the Church of the Latter Day Saints', compiler: 'Emma Smith', place: 'Kirtland, Ohio', kind: 'jsp', uri: 'collection-of-sacred-hymns-1835', previous: null, words: 'texts only' },
  { id: '1841', year: 1841, short: '1841 Nauvoo', title: 'A Collection of Sacred Hymns, for the Church of Jesus Christ of Latter Day Saints', compiler: 'Emma Smith', place: 'Nauvoo, Illinois', kind: 'jsp', uri: 'collection-of-sacred-hymns-1841', previous: '1835', words: 'texts only' },
  { id: '1985', year: 1985, short: 'Hymns (1985)', title: 'Hymns of The Church of Jesus Christ of Latter-day Saints', compiler: 'The Church of Jesus Christ of Latter-day Saints', place: 'Salt Lake City, Utah', kind: 'study', uri: '/manual/hymns', previous: null, words: 'words and music' },
  { id: 'hfhc', year: 2024, short: 'Hymns—For Home and Church', title: 'Hymns—For Home and Church', compiler: 'The Church of Jesus Christ of Latter-day Saints', place: 'Salt Lake City, Utah', kind: 'study', uri: '/music/hymns-for-home-and-church', previous: '1985', words: 'words and music', partial: true },
];

// Hand links between editions where the first lines differ, each with its reason.
// Key: `${edition}:${number}` -> the hymnKey of the same text in another edition.
const KEY_OVERRIDES = JSON.parse(fs.readFileSync(path.join(ROOT, 'scripts', 'hymn-overrides.json'), 'utf8'));
const ADDITIONS = JSON.parse(fs.readFileSync(path.join(ROOT, 'scripts', 'hymn-additions.json'), 'utf8'));
const MISSING_NOTES = JSON.parse(fs.readFileSync(path.join(ROOT, 'scripts', 'hymn-missing.json'), 'utf8'));

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const cache = fs.existsSync(CACHE) ? JSON.parse(fs.readFileSync(CACHE, 'utf8')) : { pages: {}, wikidata: {} };
cache.pages ||= {}; cache.wikidata ||= {};
const saveCache = () => { fs.mkdirSync(path.dirname(CACHE), { recursive: true }); fs.writeFileSync(CACHE, JSON.stringify(cache, null, 1) + '\n'); };

async function get(url, { ua = UA_BROWSER, accept = 'text/html', tries = 3 } = {}) {
  for (let i = 1; ; i++) {
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(30000), headers: { 'User-Agent': ua, Accept: accept, 'Accept-Language': 'en-US,en;q=0.9' } });
      if (r.ok) return await r.text();
      if (r.status === 404) return null;
      throw new Error(`HTTP ${r.status}`);
    } catch (e) {
      if (i >= tries) throw new Error(`${url}: ${e.message}`);
      await sleep(1500 * i);
    }
  }
}

const decode = (s) => String(s || '').replace(/&amp;/g, '&').replace(/&#39;|&#x27;|&rsquo;|&#8217;/g, '’').replace(/&quot;/g, '"').replace(/&nbsp;|&#160;/g, ' ').replace(/&ndash;/g, '–').replace(/&mdash;/g, '—');
const text = (h) => decode(String(h || '').replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').replace(/\s+([,.;:!?’)])/g, '$1').trim();

// ---------- Joseph Smith Papers: the transcription's table of contents ----------
async function jspEdition(ed) {
  const url = `${JSP}/paper-summary/${ed.uri}/1`;
  const html = await get(url);
  if (!html) throw new Error(`${url} not found`);
  const m = html.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/);
  if (!m) throw new Error(`${url}: no page data`);
  const toc = JSON.parse(m[1]).props.pageProps.tableOfContents;
  const out = new Map();
  (function walk(o) {
    if (Array.isArray(o)) return o.forEach(walk);
    if (!o || typeof o !== 'object') return;
    const h = typeof o.pageTitle === 'string' && o.pageTitle.match(/^Hymn+\s+(\d+)\s*•\s*(.+)$/);
    if (h && !out.has(+h[1])) out.set(+h[1], { number: +h[1], firstLine: text(h[2]), source: `${JSP}/paper-summary/${ed.uri}/${o.intPageNumber}` });
    Object.values(o).forEach(walk);
  })(toc);
  return [...out.values()].sort((a, b) => a.number - b.number);
}

// ---------- Gospel Library: table of contents, then one page per hymn ----------
async function studyEdition(ed) {
  const toc = JSON.parse(await get(STUDY_API + ed.uri, { accept: 'application/json' }));
  const body = toc.content.body;
  // Section headings (Restoration, Sabbath and Weekday...) and the links under each.
  const links = [];
  let section = '';
  for (const m of body.matchAll(/<h2 class="label"><p class="title">([^<]+)<\/p><\/h2>|<a href="(\/study[^"?]+)\?lang=eng"/g)) {
    if (m[1]) section = text(m[1]);
    else if (!links.some((l) => l.path === m[2])) links.push({ path: m[2], section });
  }
  const out = [];
  for (const l of links) {
    const uri = l.path.replace(/^\/study/, '');
    let page = !REFRESH && cache.pages[uri];
    if (!page) {
      const raw = await get(STUDY_API + uri, { accept: 'application/json' });
      await sleep(300);
      if (!raw) { console.warn('  missing page', uri); continue; }
      page = parseStudyHymn(JSON.parse(raw).content.body);
      cache.pages[uri] = page;
    }
    out.push({ ...page, ...credits(page.credits), section: l.section, source: `${CHURCH}${l.path}?lang=eng` });
  }
  saveCache();
  return out;
}

// Facts from one hymn page: number, title, first line and the credit block (no lyrics are kept).
function parseStudyHymn(body) {
  const number = text((body.match(/class="song-number"[^>]*>([\s\S]*?)<\/p>/) || [])[1]);
  const title = text((body.match(/<h1[^>]*>([\s\S]*?)<\/h1>/) || [])[1]);
  const line = (body.match(/<p class="line"[^>]*>([\s\S]*?)<\/p>/) || [])[1] || '';
  const firstLine = text(line.replace(/<span class="verse-number">[\s\S]*?<\/span>/, '')).replace(/^\d+\.\s*/, '').replace(/[,;:—–-]+$/, '').trim();
  const ci = (body.match(/<div class="citation-info">([\s\S]*?)<\/div>/) || [])[1] || '';
  return { number, title, firstLine, credits: ci.replace(/\s+data-aid="\d+"|\s+id="[^"]*"/g, '').trim() };
}

// The "Text:" and "Music:" lines as printed, without the copyright notice that may follow.
function credits(ci) {
  const out = { text: [], music: [], tune: [] };
  for (const p of String(ci || '').matchAll(/<p[^>]*>([\s\S]*?)<\/p>/g)) {
    // The label is usually italic ("<em>Text:</em>"), but a few 1985 pages print it plain ("Music: From ...").
    const LABEL = '(Text and music|Words and music|Text|Words|Music)';
    const km = p[1].match(new RegExp(`^\\s*(?:<em>\\s*${LABEL}\\s*:?\\s*</em>|${LABEL}\\s*:)`, 'i'));
    const kind = km && (km[1] || km[2]);
    if (!kind) continue; // copyright notices, notes and sheet-music links
    // Hymns—For Home and Church sets the tune name in small caps after a bar: "... | <small>NETTLETON</small>".
    for (const t of p[1].matchAll(/<small>([\s\S]*?)<\/small>/g)) out.tune.push(text(t[1]));
    let val = text(p[1].slice(km[0].length).replace(/\s*\|?\s*<small>[\s\S]*?<\/small>/g, ''))
      .replace(/^[:,\s]+/, '')
      .replace(/\.\s+From\s[^©]*(?=©)/, '') // "alt. From Light of the Years, © 1936": the source of a copyrighted text
      .replace(/\s*(?:\*|©).*$/, '')
      .replace(/\.\s+(?:From the English Hymnal|Tune and setting|Used by|Reproduced|Making copies|English translation|All rights)\b.*$/i, '')
      .replace(/[.\s|]+$/, '');
    // Hymns (1985) prints the tune name in capitals at the start of the music credit: "FOREST GREEN, arranged by ...".
    const t85 = /music/i.test(kind) && val.match(/^((?:[A-Z][A-Z’'.-]+\s?)+),\s*/);
    if (t85 && t85[1].trim().length > 2) { out.tune.push(t85[1].trim()); val = val.slice(t85[0].length); }
    if (!val) continue;
    if (/music/i.test(kind)) out.music.push(val);
    if (!/^music$/i.test(kind)) out.text.push(val);
  }
  return { text: out.text.join('; '), music: out.music.join('; '), tune: [...new Set(out.tune)].join('; ') };
}

// ---------- names, dates and denominations from the credits ----------
// "Parley P. Pratt, 1807–1857" -> { name, born: 1807, died: 1857 }; "Robert Robinson, 1758; alt." -> { name, year: 1758 };
// "Penelope Moody Allen, b. 1939" -> { name, born: 1939 }. Translators and arrangers are left out (role 'other').
const NOT_A_NAME = /\b(anon|anonymous|traditional|unknown|tune|carol|folk|melody|psalter|psalm|psalms|hymns?|hymnal|cantiques|collection|repository|harmony|songs?|sacred|music|book|chant|spiritual|liturgy|plainsong|source|edition|journal|times|magazine)\b/i;
const NAME_WORD = /^(?:[A-Z][\p{L}’'-]+\.?|[A-Z]\.(?:[A-Z]\.)*|de|von|van|der|of|la|le|du|da|y)$/u;
function people(credit, { primaryOnly = true } = {}) {
  const out = [];
  for (let clause of String(credit || '').split(/;|\|/)) {
    clause = clause.trim();
    if (!clause || /^(based on|alt\b|see\b)/i.test(clause)) continue;
    const lead = (clause.match(/^([a-z][a-z., ]*?)\bby\s+/) || [])[1] || '';
    const secondary = /^(trans|transl|translated|english transl|arr|arranged|adapt|adapted|harm|harmonized|music arr|descant|alt\.? by)/i.test(clause) || /arr|adapt|harm|collect|trans/i.test(lead);
    if (secondary && primaryOnly) continue;
    clause = clause.replace(/^(?:attr\.?|attributed|attr\. to|attributed to)\s*(?:to\s+)?/i, '').replace(/^[a-z., ]*\bby\s+/, '');
    const m = clause.match(/^(.+?)(?:,\s*(?:ca\.\s*)?(b\.\s*)?(\d{4})(?:\s*[–-]\s*(?:ca\.\s*)?(\d{4}))?)?(?:,?\s*alt\.?)?$/);
    if (!m) continue;
    const names = m[1].split(/\s*,\s*|\s+and\s+|\s*&\s*/).map((n) => n.trim()).filter(Boolean);
    for (const name of names) {
      const words = name.split(/\s+/);
      if (words.length < 2 || name === name.toUpperCase() || NOT_A_NAME.test(name) || !words.every((w) => NAME_WORD.test(w)) || !/^[A-Z]/.test(name)) continue;
      const y1 = m[3] ? +m[3] : null, y2 = m[4] ? +m[4] : null;
      out.push({ name, born: y2 || m[2] ? y1 : null, died: y2, year: !y2 && !m[2] ? y1 : null });
    }
  }
  return out;
}

// Wikidata: a person with this exact English label or alias, born and died in the given years.
async function wikidataReligion(list) {
  const want = list.filter((p) => p.born && !(key(p) in cache.wikidata));
  for (let i = 0; i < want.length; i += 40) {
    const batch = want.slice(i, i + 40);
    const values = batch.map((p) => `"${p.name.replace(/"/g, '')}"@en`).join(' ');
    const q = `SELECT ?name ?p ?b ?d (GROUP_CONCAT(DISTINCT ?relLabel; separator="|") AS ?rels) WHERE {
      VALUES ?name { ${values} }
      ?p rdfs:label|skos:altLabel ?name; wdt:P31 wd:Q5; wdt:P569 ?bd.
      OPTIONAL { ?p wdt:P570 ?dd. }
      BIND(YEAR(?bd) AS ?b) BIND(YEAR(?dd) AS ?d)
      OPTIONAL { ?p wdt:P140 ?rel. ?rel rdfs:label ?relLabel. FILTER(LANG(?relLabel) = "en") }
    } GROUP BY ?name ?p ?b ?d`;
    const raw = await get('https://query.wikidata.org/sparql?format=json&query=' + encodeURIComponent(q), { ua: UA_BOT, accept: 'application/sparql-results+json' });
    await sleep(1000);
    const rows = JSON.parse(raw).results.bindings;
    for (const p of batch) {
      const hits = rows.filter((r) => r.name?.value === p.name && +r.b?.value === p.born && (p.died ? +r.d?.value === p.died : !r.d));
      const ids = [...new Set(hits.map((h) => h.p.value))];
      cache.wikidata[key(p)] = ids.length === 1
        ? { qid: ids[0].split('/').pop(), religion: (hits[0].rels?.value || '').split('|').filter(Boolean) }
        : { qid: null, religion: [], note: ids.length ? 'ambiguous' : 'not found' };
    }
  }
  saveCache();
}
const key = (p) => `${p.name}|${p.born}|${p.died}`;

// ---------- linking editions ----------
const SPELL = { 'ev’ry': 'every', "ev'ry": 'every', 'heav’n': 'heaven', "heav'n": 'heaven', 'o’er': 'over', "o'er": 'over', 'e’er': 'ever', "e'er": 'ever', 'ne’er': 'never', "ne'er": 'never', 'pow’r': 'power', "pow'r": 'power', 'th’': 'the', 'flow’rs': 'flowers', "flow'rs": 'flowers', 'ris’n': 'risen', "ris'n": 'risen', wonderous: 'wondrous', 'wo': 'woe', 'saviour': 'savior', 'honour': 'honor' };
const normLine = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
  .replace(/[,;:!?.—–()"“”]+/g, ' ').replace(/\bto day\b/g, 'today')
  .split(/\s+/).map((w) => w.replace(/^[^a-z’']+|[^a-z’']+$/g, '')).map((w) => SPELL[w] ?? w)
  .map((w) => w.replace(/[’']/g, '')).filter(Boolean).join(' ');
const keyOf = (r) => normLine(r.firstLine).split(' ').slice(0, 6).join(' ');

// ---------- build ----------
const editions = {};
for (const ed of EDITIONS) {
  console.log('edition', ed.id);
  editions[ed.id] = ed.kind === 'jsp' ? await jspEdition(ed) : await studyEdition(ed);
  await sleep(300);
}
// Hand additions for hymns the main source skips (each with its own source). A main source wins once it has the hymn.
for (const [ref, a] of Object.entries(ADDITIONS)) {
  if (ref.startsWith('_')) continue;
  const [e, n] = ref.split(':');
  if (!editions[e]) { console.warn(`  addition ${ref}: no such edition`); continue; }
  if (editions[e].some((r) => String(r.number) === n)) { console.warn(`  addition ${ref}: the source has it now; remove it from hymn-additions.json`); continue; }
  editions[e].push({ number: +n, title: a.title || null, firstLine: a.firstLine, text: a.text || '', music: a.music || '', source: a.source, hand: a });
  editions[e].sort((x, y) => +x.number - +y.number);
}

const allPeople = [];
for (const ed of EDITIONS) for (const r of editions[ed.id]) allPeople.push(...people(r.text), ...people(r.music));
// HFHC credits give the year written, not life dates: borrow life dates from the same name in 1985.
const life = new Map(allPeople.filter((p) => p.born).map((p) => [p.name, p]));
await wikidataReligion([...new Map(allPeople.map((p) => [p.name, life.get(p.name) || p])).values()]);
const religionOf = (p) => { const l = life.get(p.name); return l ? cache.wikidata[key(l)] : null; };

const records = [];
for (const ed of EDITIONS) {
  for (const r of editions[ed.id]) {
    const authors = people(r.text), composers = people(r.music);
    const denoms = [...new Set(authors.flatMap((p) => religionOf(p)?.religion || []))];
    const written = authors.find((p) => p.year)?.year ?? null;
    const hymnKey = KEY_OVERRIDES[`${ed.id}:${r.number}`]?.key || keyOf(r);
    records.push({
      id: `${ed.id}-${r.number}`,
      edition: ed.id,
      editionYear: ed.year,
      number: /^\d+$/.test(String(r.number)) ? +r.number : r.number,
      section: r.section || null,
      title: r.title || null,
      firstLine: r.firstLine,
      text: r.text || null,
      music: r.music || null,
      tune: r.tune || null,
      authors: authors.map((p) => p.name),
      composers: composers.map((p) => p.name),
      yearWritten: written,
      authorDenomination: denoms.join('; ') || null,
      authorWikidata: authors.map((p) => religionOf(p)?.qid).filter(Boolean),
      hymnKey,
      change: null,
      previousNumber: null,
      source: r.source,
      handEntered: r.hand ? (r.hand.verify ? 'verify' : 'checked') : null,
    });
  }
}

// Added / kept / removed against the real predecessor.
for (const ed of EDITIONS.filter((e) => e.previous)) {
  const prev = records.filter((r) => r.edition === ed.previous && r.change !== 'removed');
  const cur = records.filter((r) => r.edition === ed.id);
  const prevBy = new Map();
  for (const r of prev) if (!prevBy.has(r.hymnKey)) prevBy.set(r.hymnKey, r); // the first (congregational) number wins
  for (const r of cur) {
    const p = prevBy.get(r.hymnKey);
    r.change = p ? 'kept' : 'added';
    r.previousNumber = p ? p.number : null;
  }
  if (ed.partial) continue;
  const curKeys = new Set(cur.map((r) => r.hymnKey));
  for (const p of prev.filter((r) => !curKeys.has(r.hymnKey))) {
    records.push({ ...p, id: `${ed.id}-removed-${p.number}`, edition: ed.id, editionYear: ed.year, number: null, section: null, change: 'removed', previousNumber: p.number });
  }
}
// The first edition: everything in it is new.
for (const r of records) if (r.edition === EDITIONS[0].id) r.change = 'added';

// Every edition a text appears in, for per-hymn history.
const history = {};
for (const r of records) if (r.change !== 'removed') (history[r.hymnKey] ||= []).push(`${r.edition}:${r.number}`);
for (const [ref, o] of Object.entries(KEY_OVERRIDES)) {
  const [e, n] = ref.split(':');
  if (!history[o.key]?.some((s) => !s.startsWith(e + ':'))) console.warn(`  override ${ref} links to no other edition: "${o.key}"`);
  if (!records.some((r) => r.edition === e && String(r.number) === n)) console.warn(`  override ${ref}: no such hymn`);
}

// ---------- what is missing (rebuilt on every run; notes in scripts/hymn-missing.json) ----------
const missing = [];
const ranges = (nums) => nums.reduce((acc, x) => { const l = acc.at(-1); if (l && x === l[1] + 1) l[1] = x; else acc.push([x, x]); return acc; }, []);
for (const ed of EDITIONS) {
  const list = records.filter((r) => r.edition === ed.id && r.change !== 'removed');
  const nums = list.map((r) => +r.number).filter(Number.isFinite).sort((a, b) => a - b);
  const gaps = [];
  for (let i = nums[0]; i <= nums.at(-1); i++) if (!nums.includes(i)) gaps.push(i);
  for (const [a, b] of ranges(gaps)) {
    // A book still being released has numbers it has not published yet; that is not a hymn gone missing.
    if (ed.partial) missing.push({ id: `${ed.id}:${a}-${b}`, edition: ed.id, number: `${a}-${b}`, title: null, missing: 'unpublished', source: null });
    else for (let i = a; i <= b; i++) missing.push({ id: `${ed.id}-${i}`, edition: ed.id, number: i, title: null, missing: 'hymn', source: null });
  }
  for (const r of list) {
    if (!r.firstLine) missing.push({ id: r.id, edition: ed.id, number: r.number, title: r.title, missing: 'firstLine', source: r.source });
    // Credits only exist in the books that print them.
    if (ed.words === 'words and music') for (const f of ['text', 'music']) if (!r[f]) missing.push({ id: r.id, edition: ed.id, number: r.number, title: r.title, missing: f, source: r.source });
    if (r.handEntered === 'verify') missing.push({ id: r.id, edition: ed.id, number: r.number, title: r.title || r.firstLine, missing: 'verify', source: r.source });
  }
}
for (const m of missing) {
  const n = MISSING_NOTES[m.id] || {};
  m.tried = n.tried || [];
  m.leads = n.leads || [];
}
for (const k of Object.keys(MISSING_NOTES)) if (!k.startsWith('_') && !missing.some((m) => m.id === k)) console.warn(`  hymn-missing.json: ${k} is no longer missing; remove its note`);
for (const m of missing) if (!m.tried.length && m.missing !== 'unpublished') console.warn(`  missing ${m.id} (${m.missing}) has no notes in hymn-missing.json yet`);

const count = (ed) => records.filter((r) => r.edition === ed && r.change !== 'removed').length;
const out = {
  name: 'Latter-day Saint hymnbooks: every hymn in every edition',
  generated: new Date().toISOString().slice(0, 10),
  note: 'Not an official Church site or dataset. Facts only: numbers, titles, first lines and credits as printed. No lyrics.',
  editions: EDITIONS.map(({ kind, uri, ...e }) => ({ ...e, hymns: count(e.id), source: kind === 'jsp' ? `${JSP}/paper-summary/${uri}/1` : `${CHURCH}/study${uri}?lang=eng` })),
  count: records.length,
  sources: [
    { name: 'The Joseph Smith Papers: Collection of Sacred Hymns, 1835 and 1841 (transcriptions)', url: `${JSP}/paper-summary/collection-of-sacred-hymns-1835/1`, use: 'hymn numbers and first lines of the 1835 and 1841 collections' },
    { name: 'The Church of Jesus Christ of Latter-day Saints: Gospel Library hymn pages', url: `${CHURCH}/study/manual/hymns?lang=eng`, use: 'numbers, titles, first lines and text and music credits of Hymns (1985) and Hymns—For Home and Church' },
    { name: 'Wikidata', url: 'https://www.wikidata.org/', license: 'CC0 1.0', use: "authors' religion (P140), matched on name plus birth and death years" },
    { name: 'Internet Archive scans (Church History Library copies)', url: 'https://archive.org/details/collectionofsacr01smit', use: 'hymns a transcription skips (scripts/hymn-additions.json), each with its page' },
  ],
  fields: {
    edition: EDITIONS.map((e) => `${e.id} (${e.short})`).join(' | '),
    number: 'Hymn number in that edition (blank for a removed record)',
    section: 'Section of the book on the Church pages (1985 and Hymns—For Home and Church)',
    title: 'Title as printed (the 1835 and 1841 books have none; they are known by first line)',
    firstLine: 'First line as printed (as transcribed by the Joseph Smith Papers for 1835 and 1841)',
    text: 'Text credit as printed, life dates or year included (copyright notices left out)', music: 'Music credit as printed', tune: 'Tune name as printed',
    yearWritten: 'Year in the text credit when the book gives one (Hymns—For Home and Church does; 1985 gives life dates instead)',
    authorDenomination: "Authors' religion from Wikidata, only when the Wikidata person matches name and life dates; blank when unknown",
    hymnKey: 'Links the same text across editions (normalized first six words of the first line, or a hand link)',
    change: 'added | kept | removed, against the previous edition in this dataset; blank for 1985, whose predecessor is not in the dataset yet',
    previousNumber: 'Number in the previous edition (kept and removed records)',
    source: 'Page the record comes from',
    handEntered: 'verify (entered by hand from a scan, not yet checked against the page image) | checked | blank (from the main source)',
    missing: 'Gaps found on this run: missing = hymn | firstLine | text | music | verify | unpublished, with what was tried and where to look next (also data/lds-hymns-missing.csv)',
  },
  gaps: [
    'Editions between 1841 and 1985 (the Manchester/Liverpool Sacred Hymns and Spiritual Songs line, Latter-day Saint Hymns 1927, Hymns 1948 and 1950) are not in yet, so 1985 has no change status.',
    'Hymns—For Home and Church is still being released; it has only the hymns published so far and no removed records.',
    'The 1835 and 1841 books print no author credits.',
    'Wording changes between editions are not tracked yet.',
  ],
  missing,
  history,
  hymns: records,
};

const n = (e) => out.editions.find((x) => x.id === e).hymns;
if (n('1835') < 85 || n('1841') < 290 || n('1985') < 330 || n('hfhc') < 50) {
  console.error('Refusing to write: an edition came back short.', out.editions.map((e) => `${e.id}=${e.hymns}`).join(' '));
  process.exit(1);
}
fs.writeFileSync(OUT_JSON, JSON.stringify(out, null, 1) + '\n');

const COLS = ['id', 'edition', 'editionYear', 'number', 'section', 'title', 'firstLine', 'text', 'music', 'tune', 'authors', 'composers', 'yearWritten', 'authorDenomination', 'hymnKey', 'change', 'previousNumber', 'source', 'handEntered'];
const cell = (v) => { const s = v == null ? '' : Array.isArray(v) ? v.join('; ') : String(v); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
fs.writeFileSync(OUT_CSV, [COLS.join(','), ...records.map((r) => COLS.map((c) => cell(r[c])).join(','))].join('\n') + '\n');
const MCOLS = ['id', 'edition', 'number', 'title', 'missing', 'source', 'tried', 'leads'];
fs.writeFileSync(OUT_MISSING, [MCOLS.join(','), ...missing.map((m) => MCOLS.map((c) => cell(m[c])).join(','))].join('\n') + '\n');

console.log('wrote', path.relative(ROOT, OUT_JSON), records.length, out.editions.map((e) => `${e.id}=${e.hymns}`).join(' '));
for (const ed of EDITIONS.filter((e) => e.previous)) {
  const t = records.filter((r) => r.edition === ed.id).reduce((c, r) => ((c[r.change] = (c[r.change] || 0) + 1), c), {});
  console.log(`  ${ed.id} vs ${ed.previous}:`, JSON.stringify(t));
}
console.log('  missing:', JSON.stringify(missing.reduce((c, m) => ((c[m.missing] = (c[m.missing] || 0) + 1), c), {})), 'see', path.relative(ROOT, OUT_MISSING));
console.log('  with denomination:', records.filter((r) => r.authorDenomination).length, 'with year written:', records.filter((r) => r.yearWritten).length);
