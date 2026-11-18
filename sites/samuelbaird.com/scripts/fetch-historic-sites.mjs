// Build the open dataset of the Church history sites operated by The Church of Jesus Christ of
// Latter-day Saints: data/lds-historic-sites.json and .csv. Run: node scripts/fetch-historic-sites.mjs [--refresh]
//
// Sources (facts only; no text or photos are copied from anywhere):
//   1. The Church's "Historic Sites and Museums" pages (churchofjesuschrist.org/learn/history/sites):
//      the landing page, each region page and each region's "All Locations" list give the sites and the
//      Church's own label for each (Historic Site, Visitors' Center, Monument...). Each site's official
//      page gives its name, physical address and (usually) a "View Map" link with the site's coordinates;
//      those coordinates are used as published (coordSource "church").
//   2. OpenStreetMap Nominatim (ODbL, attribution required): coordinates for pages whose map link has
//      none (a short link): the site itself when OSM has it mapped under its name, else the street
//      address, else the town. `coordPrecision` says which. Wikidata/Wikipedia links come from the OSM
//      feature's own tags when OSM has the site mapped under its official name near the official pin.
//      Map short links are not followed.
//   3. scripts/historic-site-overrides.json: hand corrections, each with a note and a source URL.
//
// Left out on purpose: entries the Church labels "Visitor Amenity" (picnic areas, stages, pavilions,
// rides, gift shops) or "Meetinghouse", and temples (they are in data/lds-temples.json).
//
// Official pages and geocodes are cached in scripts/cache/historic-sites.json so reruns only fetch what is
// new; --refresh refetches every official page. Polite: one request at a time, ~0.4 s between Church
// pages, 1.1 s between Nominatim calls. No dependencies. Refresh by hand; there is no scheduled workflow.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT_JSON = path.join(ROOT, 'data', 'lds-historic-sites.json');
const OUT_CSV = path.join(ROOT, 'data', 'lds-historic-sites.csv');
const CACHE = path.join(ROOT, 'scripts', 'cache', 'historic-sites.json');
const OVERRIDES = JSON.parse(fs.readFileSync(path.join(ROOT, 'scripts', 'historic-site-overrides.json'), 'utf8'));
const REFRESH = process.argv.includes('--refresh');
const CHURCH = 'https://www.churchofjesuschrist.org';
const LANDING = `${CHURCH}/learn/history/sites?lang=eng`;
const UA_BROWSER = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36';
const UA_BOT = 'lds-historic-sites-dataset/1.0 (open data script)';
const OPERATOR = 'The Church of Jesus Christ of Latter-day Saints';

// Region pages linked from the landing page, with the area name used in the dataset.
const AREAS = {
  'new-york-and-pennsylvania': 'New York and Pennsylvania',
  ohio: 'Ohio',
  missouri: 'Missouri',
  'historic-nauvoo': 'Illinois',
  'nebraska-and-iowa': 'Nebraska and Iowa',
  wyoming: 'Wyoming',
  'southwest-utah': 'Southwest Utah',
};
// The Church's labels we keep, mapped to the dataset's category.
const KEEP = { 'historic site': 'Historic site', "visitors' center": "Visitors' center", monument: 'Monument', museum: 'Museum' };

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const cache = fs.existsSync(CACHE) ? JSON.parse(fs.readFileSync(CACHE, 'utf8')) : { pages: {}, geocode: {} };
const saveCache = () => { fs.mkdirSync(path.dirname(CACHE), { recursive: true }); fs.writeFileSync(CACHE, JSON.stringify(cache, null, 1) + '\n'); };

async function get(url, { ua = UA_BROWSER, accept = 'text/html', tries = 3 } = {}) {
  for (let i = 1; ; i++) {
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(30000), headers: { 'User-Agent': ua, Accept: accept, 'Accept-Language': 'en-US,en;q=0.9' } });
      if (r.ok) return { text: await r.text(), url: r.url };
      if (r.status === 404) return null;
      throw new Error(`HTTP ${r.status}`);
    } catch (e) {
      if (i >= tries) throw new Error(`${url}: ${e.message}`);
      await sleep(1500 * i);
    }
  }
}

const decode = (s) => String(s || '').replace(/&amp;/g, '&').replace(/&#39;|&#x27;|&rsquo;|&#8217;/g, '’').replace(/&quot;/g, '"').replace(/&nbsp;/g, ' ').replace(/&ndash;/g, '–');
const text = (h) => decode(String(h || '').replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();
const clean = (s) => decode(s).replace(/\s+/g, ' ').trim();
const straight = (s) => s.replace(/[‘’]/g, "'");
const norm = (s) => straight(clean(s)).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/^the\s+/, '').replace(/[^a-z0-9]+/g, ' ').trim();
const slugOf = (url) => (url.match(/\/learn\/locations\/([a-z0-9-]+)/i) || [])[1]?.toLowerCase();
const locUrl = (slug) => `${CHURCH}/learn/locations/${slug}?lang=eng`;

// Cards on the Church's list pages: link, the Church's label for the place, and its name.
function cards(html) {
  const out = [];
  for (const m of html.matchAll(/<a href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g)) {
    const b = m[2];
    const title = text((b.match(/PagePromo-title">([\s\S]*?)<\/h\d>/) || [])[1]);
    if (!title) continue;
    out.push({ href: decode(m[1]).trim(), label: text((b.match(/PagePromo-category">([\s\S]*?)<\/div>/) || [])[1]), name: title });
  }
  return out;
}

// ---------- 1. the official list ----------
async function officialList() {
  const found = new Map(); // slug -> { slug, name, label, area, source }
  const add = (slug, rec) => { if (slug && !found.has(slug)) found.set(slug, { slug, ...rec }); else if (slug && rec.label && !found.get(slug).label) Object.assign(found.get(slug), rec); };
  const landing = await get(LANDING);
  if (!landing) throw new Error('Historic sites landing page not found');
  const regions = [...new Set([...landing.text.matchAll(/\/learn\/history\/sites\/([a-z0-9-]+)\?lang=eng/g)].map((m) => m[1]))].filter((r) => AREAS[r]);
  for (const r of Object.keys(AREAS)) if (!regions.includes(r)) console.warn(`  region no longer on the landing page: ${r}`);
  for (const r of regions) {
    // "All Locations" carries the Church's label for each place; regions without it link their sites directly.
    for (const page of [`${CHURCH}/learn/history/sites/${r}/all-locations?lang=eng`, `${CHURCH}/learn/history/sites/${r}?lang=eng`]) {
      const res = await get(page);
      await sleep(400);
      if (!res) continue;
      for (const c of cards(res.text)) {
        const slug = slugOf(c.href);
        if (slug) add(slug, { name: c.name, label: c.label, area: AREAS[r], source: page });
        else if (/^(visitor amenity|meetinghouse|wagon depot|temple|historic temple)$/i.test(c.label) || /\/temples\/details\//.test(c.href)) found.set('skip:' + c.name, { skip: c.label || 'Temple', name: c.name });
      }
      for (const m of res.text.matchAll(/\/learn\/locations\/([a-z0-9-]+)/gi)) add(m[1].toLowerCase(), { area: AREAS[r], source: page });
    }
  }
  // Sites linked straight from the landing page (birthplace, museum, forts, California, New Zealand...).
  for (const m of landing.text.matchAll(/\/learn\/locations\/([a-z0-9-]+)/gi)) add(m[1].toLowerCase(), { area: null, source: LANDING });
  // The Church History Museum's own page links its location page.
  const museum = await get(`${CHURCH}/learn/history/sites/church-history-museum?lang=eng`);
  if (museum) for (const m of museum.text.matchAll(/\/learn\/locations\/(church-history-museum)\b/g)) add(m[1], { area: null, label: 'Museum', source: `${CHURCH}/learn/history/sites/church-history-museum?lang=eng` });
  return found;
}

// Official location page: name, address and (for checking only) the map pin.
function parseLocation(html) {
  const name = text((html.match(/<h1[^>]*PageHeading[^>]*>([\s\S]*?)<\/h1>/) || html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/) || [])[1]);
  const a = html.match(/class="PostalAddress"([^>]*)>/);
  const attr = (k) => clean(((a && a[1]) || '').match(new RegExp(`data-${k}="([^"]*)"`))?.[1] || '');
  const pinM = html.match(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/) || html.match(/maps\?ll=(-?\d+\.\d+),(-?\d+\.\d+)/) || html.match(/\/maps\/place\/[^"]*@(-?\d+\.\d+),(-?\d+\.\d+)/);
  const addr = { street: attr('street-address'), city: attr('locality'), region: attr('region'), postalCode: attr('postal-code'), country: attr('country') };
  // Some pages give the address as rich text instead: "<b>Physical Address</b><br>street<br>City, State ZIP".
  const rt = !a && html.match(/<b>\s*Physical Address\s*<\/b>([\s\S]*?)(?:<span|<b>|<\/div>)/);
  if (rt) {
    const lines = rt[1].split(/<br\s*\/?>/i).map(text).filter(Boolean);
    const last = (lines.at(-1) || '').match(/^(.+?),\s*([A-Za-z .]+?)\s+(\d{5})(?:-\d{4})?$/);
    if (last) Object.assign(addr, { street: lines.slice(0, -1).join(', '), city: last[1], region: last[2], postalCode: last[3], country: 'USA' });
  }
  return {
    name,
    ...addr,
    pin: pinM ? [+pinM[1], +pinM[2]] : null,
    fetched: new Date().toISOString().slice(0, 10),
  };
}

// ---------- 2. Nominatim ----------
let lastGeo = 0;
async function geocode(query) {
  if (!query) return null;
  if (query in cache.geocode) return cache.geocode[query];
  const wait = 1100 - (Date.now() - lastGeo);
  if (wait > 0) await sleep(wait);
  lastGeo = Date.now();
  const res = await get('https://nominatim.openstreetmap.org/search?format=jsonv2&limit=3&extratags=1&accept-language=en&q=' + encodeURIComponent(query), { ua: UA_BOT, accept: 'application/json' });
  const hits = res ? JSON.parse(res.text) : [];
  cache.geocode[query] = hits.map((h) => ({
    lat: +(+h.lat).toFixed(5), lng: +(+h.lon).toFixed(5), kind: `${h.category}/${h.type}`, label: String(h.name || String(h.display_name || '').split(',')[0]),
    where: String(h.display_name || ''), wikidata: h.extratags?.wikidata || null, wikipedia: h.extratags?.wikipedia || null,
  }));
  return cache.geocode[query];
}

const km = (a, b) => {
  const r = Math.PI / 180, dLat = (b[0] - a[0]) * r, dLng = (b[1] - a[1]) * r;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(a[0] * r) * Math.cos(b[0] * r) * Math.sin(dLng / 2) ** 2;
  return 12742 * Math.asin(Math.sqrt(h));
};
const US_STATES = new Set(['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']);
const COUNTRY = { USA: 'United States', US: 'United States', 'United States of America': 'United States' };
const wikiUrl = (tag) => { const m = String(tag || '').match(/^en:(.+)$/); return m ? `https://en.wikipedia.org/wiki/${encodeURIComponent(m[1].replace(/ /g, '_'))}` : null; };
// Words that say what a place is rather than which one it is; a name match needs the rest to agree.
const GENERIC = new Set(['historic', 'site', 'sites', 'home', 'house', 'the', 'and', 'of', 'mormon', 'trail', 'center', 'centre', 'visitors', 'visitor', 's']);
const nameMatch = (osm, ours) => {
  const a = new Set(norm(osm).split(' ').filter((w) => !GENERIC.has(w)));
  const b = norm(ours).split(' ').filter((w) => !GENERIC.has(w));
  return b.length > 0 && a.size > 0 && b.every((w) => a.has(w)) && [...a].every((w) => b.includes(w));
};

// The place itself, if OSM has it mapped under (nearly) the official name near the official location.
async function findSite(names, place, near) {
  for (const n of names) {
    for (const h of (await geocode([n, place].filter(Boolean).join(', '))) || []) {
      if (/^(boundary|place|highway)\//.test(h.kind)) continue;
      if (!nameMatch(h.label, n)) continue;
      if (near && km(near, [h.lat, h.lng]) > 1.5) continue;
      return h;
    }
  }
  return null;
}

// ---------- main ----------
const found = await officialList();
const skipped = [...found.values()].filter((f) => f.skip);
const list = [...found.values()].filter((f) => !f.skip && !/virtual-tours/.test(f.slug));
console.log(`official list: ${list.length} locations (${skipped.length} amenities, meetinghouses and temples left out)`);

let fetched = 0;
for (const f of list) {
  if (cache.pages[f.slug] && !REFRESH) continue;
  const res = await get(locUrl(f.slug));
  cache.pages[f.slug] = res ? { ...parseLocation(res.text), url: res.url } : null;
  if (++fetched % 20 === 0) { console.log(`  pages: ${fetched}`); saveCache(); }
  await sleep(400);
}
saveCache();
console.log(`official pages fetched: ${fetched} (cached: ${list.length - fetched})`);

// Category from the Church's label; sites linked without one get it from their name.
const categoryOf = (f, name) => {
  const l = straight(f.label || '').toLowerCase();
  if (KEEP[l]) return KEEP[l];
  if (l) return null; // a label we don't keep (amenity, meetinghouse...)
  if (/museum|history (centre|center)/i.test(name)) return 'Museum';
  if (/visitors?['’]? (center|centre)|trail center/i.test(name)) return "Visitors' center";
  if (/monument|memorial/i.test(name)) return 'Monument';
  return 'Historic site';
};

const sites = [];
for (const f of list) {
  const p = cache.pages[f.slug];
  const o = OVERRIDES[f.slug] || {};
  if (!p && !o.name) { console.warn(`  no official page: ${f.slug}`); continue; }
  const name = clean(o.name || f.name || p.name);
  const category = o.category || categoryOf(f, name);
  if (!category) { skipped.push({ name, skip: f.label }); continue; }
  const street = o.street ?? p?.street ?? '', city = o.city ?? p?.city ?? '', region = o.region ?? p?.region ?? '';
  // A few official pages leave the country out of the address; a U.S. state implies it.
  const country = COUNTRY[o.country ?? p?.country] || o.country || p?.country || (US_STATES.has(region) ? 'United States' : '');
  const postalCode = o.postalCode ?? p?.postalCode ?? '';
  const place = [city, region, country].filter(Boolean).join(', ');
  const near = p?.pin || null;

  let lat = null, lng = null, precision = null, coordSource = null, wikidata = null, wikipedia = null;
  const names = [...new Set([name, p?.name, name.replace(/\s+(historic site|mormon trail site)$/i, '')].filter(Boolean).map(clean))];
  // The OSM feature (if mapped under the official name near the official pin) gives Wikidata/Wikipedia links.
  const hit = await findSite(names, place, near);
  if (hit) { wikidata = hit.wikidata; wikipedia = wikiUrl(hit.wikipedia); }
  // Coordinates: the map pin on the official page, else the OSM feature, else the geocoded address or town.
  if (near) { [lat, lng] = near.map((v) => +v.toFixed(5)); precision = 'site'; coordSource = 'church'; }
  else if (hit) { ({ lat, lng } = hit); precision = 'site'; coordSource = 'openstreetmap'; }
  if (lat == null && street && !/^(hc|po box|p\.o\.)/i.test(street)) {
    const g = ((await geocode([street, city, [region, postalCode].filter(Boolean).join(' '), country].filter(Boolean).join(', '))) || [])[0];
    if (g && (!near || km(near, [g.lat, g.lng]) < 5)) {
      const kind = /^(place\/house|building\/)/.test(g.kind) || /^\d/.test(street) && !/^highway\//.test(g.kind) && !/^(place|boundary)\//.test(g.kind) ? 'address' : /^highway\//.test(g.kind) ? 'street' : null;
      if (kind) { ({ lat, lng } = g); precision = kind; coordSource = 'openstreetmap'; }
    }
  }
  if (lat == null && place) {
    const g = ((await geocode(place)) || [])[0];
    if (g) { ({ lat, lng } = g); precision = 'city'; coordSource = 'openstreetmap'; }
  }
  if (o.lat != null) { lat = o.lat; lng = o.lng; precision = o.coordPrecision || 'city'; coordSource = 'manual'; }
  sites.push({
    id: f.slug,
    name,
    category,
    operator: OPERATOR,
    area: o.area ?? f.area ?? null,
    street, city, region, postalCode, country,
    lat, lng, coordPrecision: precision, coordSource,
    officialUrl: o.officialUrl || locUrl(f.slug),
    source: o.source || f.source,
    wikidata: o.wikidata ?? wikidata,
    wikipedia: o.wikipedia ?? wikipedia,
  });
}
saveCache();

// Hand-added sites with no /learn/locations page (each carries its own official source).
for (const [id, o] of Object.entries(OVERRIDES)) {
  if (id.startsWith('_') || !o.add || sites.some((s) => s.id === id)) continue;
  let { lat = null, lng = null, coordPrecision = null } = o, coordSource = lat != null ? 'manual' : null;
  if (lat == null) {
    const place = [o.city, o.region, o.country].filter(Boolean).join(', ');
    const hit = await findSite([o.name], place, null);
    const g = hit || ((await geocode([o.street, place].filter(Boolean).join(', '))) || [])[0];
    if (g) { ({ lat, lng } = g); coordPrecision = hit ? 'site' : /^(place\/house|building\/)/.test(g.kind) ? 'address' : 'street'; coordSource = 'openstreetmap'; }
  }
  sites.push({
    id, name: o.name, category: o.category, operator: OPERATOR, area: o.area ?? null,
    street: o.street || '', city: o.city || '', region: o.region || '', postalCode: o.postalCode || '', country: o.country || '',
    lat, lng, coordPrecision, coordSource, officialUrl: o.officialUrl, source: o.source, wikidata: o.wikidata || null, wikipedia: o.wikipedia || null,
  });
}
saveCache();

const AREA_ORDER = [...Object.values(AREAS), null];
sites.sort((a, b) => AREA_ORDER.indexOf(a.area) - AREA_ORDER.indexOf(b.area) || a.name.localeCompare(b.name));

const tally = (k) => sites.reduce((c, s) => ((c[s[k] || 'none'] = (c[s[k] || 'none'] || 0) + 1), c), {});
const out = {
  name: 'Church history sites of The Church of Jesus Christ of Latter-day Saints',
  generated: new Date().toISOString().slice(0, 10),
  count: sites.length,
  byCategory: tally('category'),
  sources: [
    { name: 'The Church of Jesus Christ of Latter-day Saints: Historic Sites and Museums and each location page', url: LANDING, use: 'which sites the Church operates, names, categories, addresses, map coordinates' },
    { name: 'OpenStreetMap contributors (Nominatim)', url: 'https://www.openstreetmap.org/copyright', license: 'ODbL 1.0', use: 'coordinates where the official page has none, and Wikidata/Wikipedia links from the matched feature' },
  ],
  fields: {
    category: "Historic site | Visitors' center | Monument | Museum (the Church's own label where it gives one)",
    operator: 'Who runs the site today',
    area: 'Group of sites on the Church pages (New York and Pennsylvania, Ohio, Missouri, Illinois, Nebraska and Iowa, Wyoming, Southwest Utah), blank for stand-alone sites',
    coordPrecision: 'site (the place itself) | address | street | city: how exact lat/lng is',
    coordSource: 'church (map link on the official page) | openstreetmap | manual (scripts/historic-site-overrides.json)',
    source: 'Official page that lists the site',
  },
  excluded: 'Entries the Church labels Visitor Amenity or Meetinghouse, and temples (see /data/lds-temples.json).',
  sites,
};

// Refuse to replace a good file with a broken scrape.
if (sites.length < 60 || sites.filter((s) => s.lat != null).length < sites.length * 0.95) {
  console.error('Refusing to write: too few sites or coordinates.', sites.length, sites.filter((s) => s.lat == null).map((s) => s.id).join(' '));
  process.exit(1);
}
fs.writeFileSync(OUT_JSON, JSON.stringify(out, null, 1) + '\n');

const COLS = ['id', 'name', 'category', 'operator', 'area', 'street', 'city', 'region', 'postalCode', 'country', 'lat', 'lng', 'coordPrecision', 'coordSource', 'officialUrl', 'source', 'wikidata', 'wikipedia'];
const cell = (v) => { const s = v == null ? '' : String(v); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
fs.writeFileSync(OUT_CSV, [COLS.join(','), ...sites.map((s) => COLS.map((c) => cell(s[c])).join(','))].join('\n') + '\n');

console.log('wrote', path.relative(ROOT, OUT_JSON), sites.length, JSON.stringify(out.byCategory), 'coords:', JSON.stringify(tally('coordPrecision')));
console.log('left out:', skipped.map((s) => `${s.name} (${s.skip})`).join('; '));
