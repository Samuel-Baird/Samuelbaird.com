// Scrapes churchofjesuschrist.org/learn/facts-statistics for country + continent statistics.
//
// The pages are Next.js; every figure is in the embedded __NEXT_DATA__ JSON, so no HTML
// parsing is needed. Records are located by their `$model` (countryStatistics,
// continentStatistics, ...) rather than by path, so the script survives nesting changes.
//
// Usage: node scripts/church-facts-statistics/scrape.mjs
//        (behind a proxy: NODE_USE_ENV_PROXY=1 node ...)
// Output: countries.csv, continents.csv, worldwide.json, all.json (next to this script)

import { writeFileSync } from 'node:fs';

const BASE = 'https://www.churchofjesuschrist.org/learn/facts-statistics';
const OUT = new URL('./', import.meta.url);
// The index page does not link Africa, so it is seeded here.
const EXTRA_CONTINENT_SLUGS = ['africa'];
const DELAY_MS = 400;
// Sub-national pages that reuse their parent country's statistics record.
const SKIP_SLUGS = new Set(['hawaii']);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function fetchPageData(slug) {
  const url = `${BASE}${slug ? `/${slug}` : ''}?lang=eng`;
  for (let attempt = 1; attempt <= 4; attempt++) {
    try {
      const res = await fetch(url, { headers: { 'user-agent': 'latter-day-stats-scraper/1.0' } });
      if (res.status === 404) return null;
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const html = await res.text();
      const m = html.match(/<script id="__NEXT_DATA__"[^>]*>(.*?)<\/script>/s);
      if (!m) throw new Error('no __NEXT_DATA__');
      return { url, json: JSON.parse(m[1]) };
    } catch (e) {
      if (attempt === 4) throw new Error(`${url}: ${e.message}`);
      await sleep(2000 * 2 ** (attempt - 1));
    }
  }
}

/** Depth-first search for the first object whose `$model` matches. */
function findModel(node, model) {
  if (!node || typeof node !== 'object') return null;
  if (node.$model === model) return node;
  for (const v of Array.isArray(node) ? node : Object.values(node)) {
    const hit = findModel(v, model);
    if (hit) return hit;
  }
  return null;
}

/** Facts-statistics slugs linked anywhere in the page data. */
function linkedSlugs(json) {
  const s = JSON.stringify(json);
  return [...new Set([...s.matchAll(/\/learn\/facts-statistics\/([A-Za-z0-9-]+)/g)].map((m) => m[1]))];
}

const TZ = { EDT: '-04:00', EST: '-05:00' };
/** "Wed Apr 29 18:31:34 EDT 2026" -> ISO 8601 UTC. */
function toIso(s) {
  const m = s?.match(/^\w{3} (\w{3}) (\d{1,2}) ([\d:]{8}) (\w+) (\d{4})$/);
  if (!m) return '';
  const [, mon, day, time, tz, year] = m;
  const d = new Date(`${mon} ${day.padStart(2, '0')} ${year} ${time} GMT${TZ[tz] ?? '+00:00'}`);
  return Number.isNaN(d.getTime()) ? '' : d.toISOString();
}

const num = (v) => (v === undefined || v === null || v === '' ? null : Number(v));

function continentRow(stats, slug) {
  return {
    continent: stats.continent,
    slug,
    year: num(stats.year),
    last_updated: toIso(stats.$lastUpdatedDate),
    membership: num(stats.churchMembership),
    congregations: num(stats.congregations),
    stakes: num(stats.stakes),
    districts: num(stats.districts),
    missions: num(stats.missions),
    temples: num(stats.temples),
    family_history_centers: num(stats.familyHistoryCenters),
  };
}

const continents = [];
let worldwide = null;

const index = await fetchPageData('');
const continentSlugs = [
  ...new Set([...linkedSlugs(index.json), ...EXTRA_CONTINENT_SLUGS]),
];

const countrySlugs = new Map(); // country slug -> continent page it was found on
const continentPageSlugs = new Set();

for (const slug of continentSlugs) {
  await sleep(DELAY_MS);
  const page = await fetchPageData(slug);
  if (!page) {
    console.warn(`skip: ${slug} (404)`);
    continue;
  }
  const stats = findModel(page.json, 'continentStatistics');
  if (!stats) {
    console.warn(`skip: ${slug} (no continentStatistics)`);
    continue;
  }
  continentPageSlugs.add(slug.toLowerCase());
  continents.push(continentRow(stats, slug));
  worldwide ??= findModel(page.json, 'worldwideStatistics');
  for (const s of linkedSlugs(page.json)) {
    if (!continentSlugs.some((c) => c.toLowerCase() === s.toLowerCase()) && !countrySlugs.has(s)) {
      countrySlugs.set(s, stats.continent);
    }
  }
  console.log(`continent ${stats.continent}: ${stats.churchMembership} members`);
}

// Countries the user specifically named may not be linked from a continent page.
for (const s of ['mongolia']) if (!countrySlugs.has(s)) countrySlugs.set(s, null);

// Continent pages only feature a handful of countries. The Newsroom's facts-and-statistics
// menu lists every country the Church reports on, so seed from it (most of those slugs
// resolve to a page here). Slugs that don't resolve are covered by scrape-newsroom.mjs.
{
  const res = await fetch('https://newsroom.churchofjesuschrist.org/facts-and-statistics/state/utah', {
    headers: { 'user-agent': 'Mozilla/5.0 latter-day-stats-scraper/1.0' },
  });
  const html = res.ok ? await res.text() : '';
  for (const m of html.matchAll(/href="\/facts-and-statistics\/country\/([a-z0-9-]+)"/g)) {
    if (!countrySlugs.has(m[1])) countrySlugs.set(m[1], null);
  }
}

const countries = [];
const skipped = [];
const slugify = (name) =>
  name.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-');
for (const [slug, foundOn] of countrySlugs) {
  if (SKIP_SLUGS.has(slug)) {
    skipped.push(`${slug} (sub-national)`);
    continue;
  }
  await sleep(DELAY_MS);
  const page = await fetchPageData(slug);
  const stats = page && findModel(page.json, 'countryStatistics');
  const purpose = page && findModel(page.json, 'countryPurpose');
  if (!stats) {
    skipped.push(slug);
    continue;
  }
  const cont = findModel(page.json, 'continentStatistics');
  // The CMS occasionally links a page to another country's record (the Andorra page
  // returns Greece's). A page owns its record only if the slug matches the country name.
  const statsCountry = slugify(stats.country);
  const owns = slug.startsWith(statsCountry) || statsCountry.startsWith(slug);
  const title = page.json.props.pageProps.title ?? '';
  const pageName = title.replace(/^.*? in (the )?/, '').trim() || slug;
  const s = owns ? stats : {};
  countries.push({
    country: owns ? stats.country : pageName,
    slug,
    continent: cont?.continent ?? foundOn ?? '',
    capital: purpose?.capitalCity ?? '',
    official_languages: (purpose?.officalLanguages ?? []).map((l) => l.name).join('; '),
    year: num(s.year),
    last_updated: toIso(s.$lastUpdatedDate),
    membership: num(s.churchMembership),
    congregations: num(s.congregations),
    wards: num(s.wards),
    branches: num(s.branches),
    stakes: num(s.stakes),
    districts: num(s.districts),
    missions: num(s.missions),
    temples: num(s.temples),
    family_history_centers: num(s.familyHistoryCenters),
    data_note: owns ? '' : `source page returns ${stats.country}'s record; figures omitted`,
    url: page.url,
  });
  console.log(`country ${owns ? stats.country : `${pageName} (NO OWN STATS)`}`);
}

countries.sort((a, b) => a.continent.localeCompare(b.continent) || a.country.localeCompare(b.country));
continents.sort((a, b) => a.continent.localeCompare(b.continent));

const csv = (rows) => {
  const cols = Object.keys(rows[0]);
  const esc = (v) => {
    const s = v === null || v === undefined ? '' : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [cols.join(','), ...rows.map((r) => cols.map((c) => esc(r[c])).join(','))].join('\n') + '\n';
};

const worldRow = worldwide && {
  year: num(worldwide.year),
  last_updated: toIso(worldwide.$lastUpdatedDate),
  membership: num(worldwide.churchMembership),
  congregations: num(worldwide.congregations),
  stakes: num(worldwide.stakes),
  missions: num(worldwide.missions),
  temples: num(worldwide.temples),
};

writeFileSync(new URL('countries.csv', OUT), csv(countries));
writeFileSync(new URL('continents.csv', OUT), csv(continents));
writeFileSync(new URL('worldwide.json', OUT), JSON.stringify(worldRow, null, 2) + '\n');
writeFileSync(new URL('all.json', OUT), JSON.stringify({ worldwide: worldRow, continents, countries }, null, 2) + '\n');

console.log(`\n${countries.length} countries, ${continents.length} continents. Skipped: ${skipped.join(', ') || 'none'}`);
