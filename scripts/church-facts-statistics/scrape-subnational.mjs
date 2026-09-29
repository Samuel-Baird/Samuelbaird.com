// Scrapes state/province statistics from churchofjesuschrist.org/learn/facts-statistics.
//
// The Church is publishing these page by page (as of Sep 2026 only nine U.S. states
// exist; no Canadian provinces or anywhere else). So this script does not assume a
// list: it crawls every country page (slugs come from countries.csv, written by
// scrape.mjs) and follows every "The Church in ..." card that is not a country or
// continent, then keeps the pages that carry a `stateProvinceStatistics` record.
// U.S. state names are also probed directly, because a page can exist before any
// country page links to it. Re-run it whenever the Church adds states.
//
// Usage: node scripts/church-facts-statistics/scrape-subnational.mjs
// Output: states.csv and states.json (next to this script)

import { readFileSync, writeFileSync } from 'node:fs';

const BASE = 'https://www.churchofjesuschrist.org';
const OUT = new URL('./', import.meta.url);
const DELAY_MS = 350;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const csvRows = readFileSync(new URL('countries.csv', OUT), 'utf8').split('\n').slice(1).filter(Boolean);
const countrySlugs = new Set(
  csvRows.map((l) => l.split(',').find((c) => /^[a-z0-9-]+$/.test(c) && c.length > 1)),
);
const CONTINENT_SLUGS = new Set(['africa', 'asia', 'europe', 'north-america', 'south-america', 'oceania', 'central-america']);

const US_STATES = [
  'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware',
  'District of Columbia', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
  'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
  'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
  'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
  'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah',
  'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming',
];
const slugify = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-');

async function fetchPage(path) {
  const url = `${BASE}/learn/${path}?lang=eng`;
  for (let attempt = 1; attempt <= 4; attempt++) {
    try {
      const res = await fetch(url, { headers: { 'user-agent': 'latter-day-stats-scraper/1.0' } });
      if (res.status === 404) return null;
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const html = await res.text();
      const m = html.match(/<script id="__NEXT_DATA__"[^>]*>(.*?)<\/script>/s);
      if (!m) return null;
      return { url, html, json: JSON.parse(m[1]) };
    } catch (e) {
      if (attempt === 4) throw new Error(`${url}: ${e.message}`);
      await sleep(2000 * 2 ** (attempt - 1));
    }
  }
}

function findModel(node, model) {
  if (!node || typeof node !== 'object') return null;
  if (node.$model === model) return node;
  for (const v of Array.isArray(node) ? node : Object.values(node)) {
    const hit = findModel(v, model);
    if (hit) return hit;
  }
  return null;
}

/** Card links ("The Church in X") on a page, as learn/ paths. */
function cardPaths(html) {
  const out = new Set();
  for (const m of html.matchAll(/"linkText":"The Church in [^"]+","linkUrl":"([^"]+)"/g)) {
    const p = m[1].replace(BASE + '/learn/', '').replace(/\?.*$/, '');
    out.add(p);
  }
  return out;
}

const isKnown = (path) => {
  const slug = path.replace(/^facts-statistics\//, '').toLowerCase();
  return countrySlugs.has(slug) || CONTINENT_SLUGS.has(slug);
};

const candidates = new Set();
for (const slug of countrySlugs) {
  await sleep(DELAY_MS);
  const page = await fetchPage(`facts-statistics/${slug}`);
  if (!page) continue;
  for (const p of cardPaths(page.html)) if (!isKnown(p)) candidates.add(p);
}
for (const name of US_STATES) {
  candidates.add(`facts-statistics/${slugify(name)}`);
  candidates.add(`the-church-in-${slugify(name)}`);
}
console.log(`${candidates.size} candidate pages`);

const states = new Map();
const num = (v) => (v === undefined || v === null || v === '' || Number.isNaN(Number(v)) ? null : Number(v));
for (const path of candidates) {
  await sleep(DELAY_MS);
  const page = await fetchPage(path);
  const s = page && findModel(page.json, 'stateProvinceStatistics');
  if (!s) continue;
  const country = findModel(page.json, 'countryStatistics')?.country ?? '';
  const purpose = findModel(page.json, 'stateProvincePurpose');
  const key = `${country}|${s['State/Province']}`;
  if (states.has(key)) continue;
  states.set(key, {
    country,
    state: s['State/Province'],
    capital: purpose?.capitalCity ?? '',
    year: num(s.year),
    membership: num(s.churchMembership),
    congregations: num(s.congregations),
    wards: num(s.wards),
    branches: num(s.branches),
    stakes: num(s.stakes),
    districts: num(s.districts),
    missions: num(s.missions),
    temples: num(s.temples),
    // The CMS holds the literal string "fhcs" here: a template placeholder, not a count.
    family_history_centers: num(s.familyHistoryCenters),
    url: page.url,
  });
  console.log(`${country}: ${s['State/Province']} ${s.churchMembership}`);
}

const rows = [...states.values()].sort((a, b) => a.country.localeCompare(b.country) || a.state.localeCompare(b.state));
if (!rows.length) throw new Error('no state pages found; refusing to overwrite output');
const cols = Object.keys(rows[0]);
const esc = (v) => {
  const s = v === null || v === undefined ? '' : String(v);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
writeFileSync(new URL('states.csv', OUT), [cols.join(','), ...rows.map((r) => cols.map((c) => esc(r[c])).join(','))].join('\n') + '\n');
writeFileSync(new URL('states.json', OUT), JSON.stringify(rows, null, 2) + '\n');
console.log(`\n${rows.length} states/provinces across ${new Set(rows.map((r) => r.country)).size} countries`);
