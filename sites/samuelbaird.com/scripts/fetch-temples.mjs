// Build the open dataset of every temple of The Church of Jesus Christ of Latter-day Saints:
// data/lds-temples.json and data/lds-temples.csv. Run: node scripts/fetch-temples.mjs [--refresh]
//
// Sources, merged in this order (facts only; no text or photos are copied from anywhere):
//   1. The Church's official temple list and each temple's official page
//      (churchofjesuschrist.org/temples): name, status, location, address, milestones.
//   2. Wikidata (CC0): coordinates and Wikipedia links, matched by temple name.
//   3. OpenStreetMap Nominatim (ODbL, attribution required): coordinates for temples Wikidata
//      lacks: the temple itself when OSM has it mapped under its name, else the street address,
//      else the city, else the country. `coordPrecision` says which.
//
// Official pages and geocodes are cached in scripts/cache/temples.json so reruns only fetch what
// is new. --refresh refetches every official page; --refresh-changing (the weekly workflow) refetches
// only temples not yet operating or whose status changed, since only those gain new milestones.
// Polite: one request at a time, ~0.4 s between Church pages, 1.1 s between Nominatim calls.
// No dependencies.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT_JSON = path.join(ROOT, 'data', 'lds-temples.json');
const OUT_CSV = path.join(ROOT, 'data', 'lds-temples.csv');
const CACHE = path.join(ROOT, 'scripts', 'cache', 'temples.json');
const OVERRIDES = JSON.parse(fs.readFileSync(path.join(ROOT, 'scripts', 'temple-overrides.json'), 'utf8'));
const REFRESH = process.argv.includes('--refresh');
const REFRESH_CHANGING = process.argv.includes('--refresh-changing');
const OFFICIAL = 'https://www.churchofjesuschrist.org/temples';
const UA_BROWSER = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36';
const UA_BOT = 'lds-temple-dataset/1.0 (open data script)';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const cache = fs.existsSync(CACHE) ? JSON.parse(fs.readFileSync(CACHE, 'utf8')) : { details: {}, geocode: {} };
const saveCache = () => { fs.mkdirSync(path.dirname(CACHE), { recursive: true }); fs.writeFileSync(CACHE, JSON.stringify(cache, null, 1) + '\n'); };

async function get(url, { ua = UA_BROWSER, accept = 'text/html', tries = 3 } = {}) {
  for (let i = 1; ; i++) {
    try {
      const r = await fetch(url, { headers: { 'User-Agent': ua, Accept: accept, 'Accept-Language': 'en-US,en;q=0.9' } });
      if (r.ok) return await r.text();
      if (r.status === 404) return null;
      throw new Error(`HTTP ${r.status}`);
    } catch (e) {
      if (i >= tries) throw new Error(`${url}: ${e.message}`);
      await sleep(1500 * i);
    }
  }
}

const nextData = (html) => {
  const m = html && html.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/);
  return m ? JSON.parse(m[1]).props.pageProps : null;
};

const MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'];
function isoDate(s) {
  const m = String(s || '').trim().match(/^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$/);
  if (!m) return null;
  const mo = MONTHS.indexOf(m[1].toLowerCase());
  return mo < 0 ? null : `${m[3]}-${String(mo + 1).padStart(2, '0')}-${m[2].padStart(2, '0')}`;
}

// Spelling slips in the official data, mapped to the usual English name.
const COUNTRY_FIX = { Filippyne: 'Philippines', England: 'United Kingdom', Scotland: 'United Kingdom', Wales: 'United Kingdom', 'Northern Ireland': 'United Kingdom' };
const STATUS = { OPERATING: 'operating', ANNOUNCED: 'announced', CONSTRUCTION: 'under-construction', RENOVATION: 'under-renovation', 'OPENING SOON': 'opening-soon', CLOSED: 'closed' };
const clean = (s) => String(s || '').trim();
const norm = (s) => clean(s).toLowerCase().replace(/^the\s+/, '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\btemple\b/g, '').replace(/[^a-z0-9]+/g, ' ').trim();

// ---------- 1. official list + pages ----------
async function officialTemples() {
  const pp = nextData(await get(`${OFFICIAL}/list?lang=eng`));
  if (!pp?.templeList?.length) throw new Error('Official temple list not found (page layout changed?)');
  return pp.templeList;
}

async function officialDetails(id) {
  const pp = nextData(await get(`${OFFICIAL}/details/${id}?lang=eng`));
  if (!pp) return null;
  const ti = pp.templeInformation || {};
  const addr = (ti.details || []).find((d) => d.addLine1 !== undefined);
  const milestones = (pp.historicalMilestones?.dates || [])
    .map((d) => ({ event: clean(d.milestone), date: d.dedicationDate || isoDate(d.date) }))
    .filter((d) => d.event);
  return {
    address: addr ? [addr.addLine1, addr.addLine2, addr.addLine3].map(clean).filter(Boolean).join('\n') : '',
    milestones,
    fetched: new Date().toISOString().slice(0, 10),
  };
}

// ---------- 2. Wikidata ----------
async function wikidata() {
  const q = `SELECT ?t ?tLabel ?coord ?article WHERE {
    ?t wdt:P31/wdt:P279* wd:Q2142152 ; wdt:P140 wd:Q42504 .
    OPTIONAL { ?t wdt:P625 ?coord }
    OPTIONAL { ?article schema:about ?t ; schema:isPartOf <https://en.wikipedia.org/> }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }`;
  const txt = await get('https://query.wikidata.org/sparql?query=' + encodeURIComponent(q), { ua: UA_BOT, accept: 'application/sparql-results+json' });
  const map = new Map();
  for (const b of JSON.parse(txt).results.bindings) {
    const key = norm(b.tLabel?.value);
    if (!key || map.has(key)) continue;
    const c = b.coord?.value.match(/Point\(([-\d.]+) ([-\d.]+)\)/);
    map.set(key, {
      qid: b.t.value.split('/').pop(),
      lat: c ? +(+c[2]).toFixed(5) : null,
      lng: c ? +(+c[1]).toFixed(5) : null,
      wikipedia: b.article?.value || null,
    });
  }
  return map;
}

// ---------- 3. Nominatim ----------
let lastGeo = 0;
async function geocode(query) {
  if (!query) return null;
  if (query in cache.geocode) return cache.geocode[query];
  const wait = 1100 - (Date.now() - lastGeo);
  if (wait > 0) await sleep(wait);
  lastGeo = Date.now();
  const txt = await get('https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&accept-language=en&q=' + encodeURIComponent(query), { ua: UA_BOT, accept: 'application/json' });
  const hit = txt && JSON.parse(txt)[0];
  cache.geocode[query] = hit ? { lat: +(+hit.lat).toFixed(5), lng: +(+hit.lon).toFixed(5), kind: `${hit.category}/${hit.type}`, label: String(hit.display_name || '').split(',')[0], where: String(hit.display_name || '') } : null;
  return cache.geocode[query];
}

// The temple building itself, if OSM has it mapped under the temple's name.
async function findBuilding(name) {
  const g = await geocode(name);
  if (!g || !/^(amenity\/place_of_worship|building\/|historic\/|landuse\/religious)/.test(g.kind || '') || norm(g.label).replace(/\blds\b\s*/g, '') !== norm(name)) return null;
  return g;
}

// Street address minus the country line and ZIP+4 suffix, which trip up Nominatim.
const addressQuery = (address, country) => {
  const lines = address.split('\n').map(clean).filter(Boolean);
  if (lines.length > 1 && lines.at(-1).toUpperCase() === lines.at(-1)) lines.pop();
  return lines.length ? [...lines.map((l) => l.replace(/(\d{5})-\d{4}\b/, '$1')), country].filter(Boolean).join(', ') : '';
};

// ---------- main ----------
const list = await officialTemples();
console.log(`official list: ${list.length} temples`);

let fetched = 0;
for (const t of list) {
  const id = t.templeNameId;
  const cached = cache.details[id];
  const changing = REFRESH_CHANGING && (t.status !== 'OPERATING' || cached?.status !== t.status);
  if (cached && !REFRESH && !changing) continue;
  const fresh = await officialDetails(id);
  cache.details[id] = fresh ? { ...fresh, status: t.status } : cached || null;
  if (++fetched % 25 === 0) { console.log(`  pages: ${fetched}`); saveCache(); }
  await sleep(400);
}
saveCache();
console.log(`official pages fetched: ${fetched} (cached: ${list.length - fetched})`);

const wd = await wikidata();
console.log(`wikidata temples: ${wd.size}`);

const firstDate = (ms, re) => ms.find((m) => re.test(m.event) && m.date)?.date || null;
const temples = [];
for (const t of list) {
  const d = cache.details[t.templeNameId] || { address: '', milestones: [] };
  const city = clean(t.city), region = clean(t.stateRegion);
  // Announced temples often have only the free-text location ("Busan, South Korea" or just "South Korea").
  const rawCountry = clean(t.country) || clean(t.location).split(',').pop().trim();
  const country = COUNTRY_FIX[rawCountry] || rawCountry;
  const ms = d.milestones || [];
  const w = wd.get(norm(t.name));
  let lat = w?.lat ?? null, lng = w?.lng ?? null, precision = lat != null ? 'site' : null, coordSource = lat != null ? 'wikidata' : null;
  if (lat == null && t.status !== 'ANNOUNCED') {
    const b = await findBuilding(clean(t.name));
    if (b) { ({ lat, lng } = b); precision = 'site'; coordSource = 'openstreetmap'; }
  }
  if (lat == null) {
    const tries = [
      ['address', addressQuery(d.address || '', country)],
      ['city', city ? [city, region, country].filter(Boolean).join(', ') : ''],
      [city ? 'city' : 'country', clean(t.location)],
      ['country', country || clean(t.location).split(',').pop().trim()],
    ];
    // No city published (most announced temples): the name usually carries it, e.g. "Busan Korea Temple".
    // Accept that only if the result lands in the published country.
    if (!city) {
      const stem = clean(t.name).replace(/\s+temple$/i, '');
      const g = await geocode(stem);
      const want = norm(country || clean(t.location).split(',').pop());
      if (g && want && norm(g.where || '').includes(want)) { ({ lat, lng } = g); precision = 'city'; coordSource = 'openstreetmap'; }
    }
    if (lat == null) for (const [p, q] of tries) {
      if (!q) continue;
      const g = await geocode(q);
      if (g) { ({ lat, lng } = g); precision = p; coordSource = 'openstreetmap'; break; }
    }
  }
  const o = OVERRIDES[t.templeNameId];
  if (o?.lat != null) { lat = o.lat; lng = o.lng; precision = o.coordPrecision || 'city'; coordSource = 'manual'; }
  temples.push({
    id: t.templeNameId,
    name: clean(t.name),
    status: STATUS[t.status] || clean(t.status).toLowerCase(),
    city, region, country,
    location: clean(t.location),
    address: d.address || '',
    lat, lng, coordPrecision: precision, coordSource,
    announced: firstDate(ms, /^announced/i),
    groundbreaking: firstDate(ms, /^groundbreaking/i),
    dedicated: firstDate(ms, /^dedicated/i),
    rededicated: ms.filter((m) => /^rededicated/i.test(m.event) && m.date).map((m) => m.date),
    milestones: ms,
    officialUrl: `${OFFICIAL}/details/${t.templeNameId}?lang=eng`,
    wikidata: w?.qid || null,
    wikipedia: w?.wikipedia || null,
    orgId: t.templeOrgId,
  });
}
saveCache();

temples.sort((a, b) => (a.dedicated || '9999').localeCompare(b.dedicated || '9999') || (a.announced || '9999').localeCompare(b.announced || '9999') || a.name.localeCompare(b.name));

const counts = temples.reduce((c, t) => ((c[t.status] = (c[t.status] || 0) + 1), c), {});
const out = {
  name: 'Temples of The Church of Jesus Christ of Latter-day Saints',
  generated: new Date().toISOString().slice(0, 10),
  count: temples.length,
  byStatus: counts,
  sources: [
    { name: 'The Church of Jesus Christ of Latter-day Saints: temple list and temple pages', url: `${OFFICIAL}/list?lang=eng`, use: 'names, status, locations, addresses, milestone dates' },
    { name: 'Wikidata', url: 'https://www.wikidata.org/', license: 'CC0 1.0', use: 'coordinates and Wikipedia links where available' },
    { name: 'OpenStreetMap contributors (Nominatim)', url: 'https://www.openstreetmap.org/copyright', license: 'ODbL 1.0', use: 'coordinates geocoded from addresses for the rest' },
  ],
  fields: {
    status: 'operating | opening-soon | under-construction | under-renovation | announced | closed',
    coordPrecision: 'site (temple itself) | address | city | country: how exact lat/lng is',
    coordSource: 'wikidata | openstreetmap | manual (scripts/temple-overrides.json)',
  },
  temples,
};

// Refuse to replace a good file with a broken scrape.
if (temples.length < 300 || temples.filter((t) => t.lat != null).length < temples.length * 0.9) {
  console.error('Refusing to write: too few temples or coordinates.', temples.length);
  process.exit(1);
}
fs.writeFileSync(OUT_JSON, JSON.stringify(out, null, 1) + '\n');

const COLS = ['id', 'name', 'status', 'city', 'region', 'country', 'lat', 'lng', 'coordPrecision', 'announced', 'groundbreaking', 'dedicated', 'rededicated', 'address', 'officialUrl', 'wikidata', 'wikipedia'];
const cell = (v) => { const s = Array.isArray(v) ? v.join(';') : v == null ? '' : String(v); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
fs.writeFileSync(OUT_CSV, [COLS.join(','), ...temples.map((t) => COLS.map((c) => cell(t[c])).join(','))].join('\n') + '\n');

const prec = temples.reduce((c, t) => ((c[t.coordPrecision || 'none'] = (c[t.coordPrecision || 'none'] || 0) + 1), c), {});
console.log('wrote', path.relative(ROOT, OUT_JSON), JSON.stringify(counts), 'coords:', JSON.stringify(prec));
