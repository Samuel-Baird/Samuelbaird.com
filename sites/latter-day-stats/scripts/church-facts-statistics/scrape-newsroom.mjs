// Scrapes newsroom.churchofjesuschrist.org/facts-and-statistics: every country and every
// U.S. state, which is a fuller list than churchofjesuschrist.org/learn/facts-statistics
// (that site had 116 countries and nine states when this was written; this one has
// 160 countries and all 50 states plus D.C.). Canada's provinces live on its own
// Newsroom (news-ca.churchofjesuschrist.org); no other country Newsroom has subdivisions.
//
// The site lists every country and state in its own menu, so nothing is hard-coded: the
// script reads the menu from one page, then fetches each page. Figures are read from the
// visible "value / label" pairs (Total Church Membership, Stakes, Congregations, Wards,
// Branches, FamilySearch Centers, Temples, Missions, Districts). The pages carry no "as
// of" date, only charts that end at 2025, so every row is recorded as 2025.
//
// Usage: node scripts/church-facts-statistics/scrape-newsroom.mjs
// Output: newsroom-countries.csv, newsroom-states.csv, newsroom-provinces.csv
//         (next to this script)

import { writeFileSync } from 'node:fs';

const BASE = 'https://newsroom.churchofjesuschrist.org';
const CA_BASE = 'https://news-ca.churchofjesuschrist.org';
const OUT = new URL('./', import.meta.url);
const DELAY_MS = 250;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function fetchHtml(path, base = BASE) {
  for (let attempt = 1; attempt <= 4; attempt++) {
    try {
      const res = await fetch(`${base}${path}`, { headers: { 'user-agent': 'Mozilla/5.0 latter-day-stats-scraper/1.0' } });
      if (res.status === 404) return null;
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.text();
    } catch (e) {
      if (attempt === 4) throw new Error(`${path}: ${e.message}`);
      await sleep(2000 * 2 ** (attempt - 1));
    }
  }
}

/** Visible text of the statistics block as a "|"-separated token list. */
function tokens(html) {
  // Start at the map controls, or (Canada's template has none) at the first stat, so
  // the page <title> ("... | Total Church Membership") isn't mistaken for the figure.
  const at = html.indexOf('Show map');
  const start = at >= 0 ? at : Math.max(html.indexOf('class="stat-value"') - 600, 0);
  const tail = html.slice(start);
  // "Family History Centers" also contains the word, so match the heading tag; some
  // pages use a different wrapper, so fall back to a fixed window.
  const found = tail.search(/<h\d[^>]*>\s*History\s*</);
  const block = tail
    .slice(0, found > 0 ? found : 12000)
    .replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>|<svg[\s\S]*?<\/svg>|<!--[\s\S]*?-->/g, '')
    // Tags, allowing '>' inside quoted attribute values.
    .replace(/<(?:"[^"]*"|'[^']*'|[^'">])*>/g, '|')
    .replace(/&amp;/g, '&')
    .replace(/&nbsp;|&#160;|&#8239;/g, ' ');
  return block.split('|').map((t) => t.trim()).filter(Boolean);
}

// Canada's pages group thousands with a (non-breaking) space: "85 916".
const toNum = (s) => {
  const t = s?.replace(/[\s,  ]/g, '');
  return t && /^\d+$/.test(t) ? Number(t) : null;
};

/** The number immediately before a label, e.g. ["647", "Stakes"] -> 647. */
function before(toks, label) {
  const i = toks.indexOf(label);
  return i > 0 ? toNum(toks[i - 1]) : null;
}

function parse(html, code, path, base = BASE) {
  let t = tokens(html);
  // A state or province page shows its own block and then its country's; keep only
  // the first so a missing figure can't be filled from the country's.
  const firstMembership = t.indexOf('Total Church Membership');
  const secondMembership = t.indexOf('Total Church Membership', firstMembership + 1);
  if (secondMembership > 0) t = t.slice(0, secondMembership - 1);
  const mi = t.indexOf('Total Church Membership');
  return {
    name: nameOf.get(path) ?? (mi > 1 ? t[mi - 2] : code),
    slug: code,
    continent: continentOf.get(code) ?? '',
    year: 2025,
    membership: before(t, 'Total Church Membership'),
    congregations: before(t, 'Congregations'),
    wards: before(t, 'Wards'),
    branches: before(t, 'Branches'),
    stakes: before(t, 'Stakes'),
    districts: before(t, 'Districts'),
    missions: before(t, 'Missions'),
    // Pages with no temples still show a stray number before the label; no country has
    // anywhere near this many operating temples (the U.S. has 101).
    temples: (() => { const n = before(t, 'Temples'); return n !== null && n > 150 ? 0 : n; })(),
    // Canada's pages still say "Family History Centers".
    family_history_centers: before(t, 'FamilySearch Centers') ?? before(t, 'Family History Centers'),
    url: `${base}/facts-and-statistics/${path}`,
  };
}

const menu = await fetchHtml('/facts-and-statistics/state/utah');
const CONTINENT_NAMES = {
  'north-america': 'North America',
  'south-america': 'South America',
  europe: 'Europe',
  asia: 'Asia',
  oceania: 'Oceania (Pacific)',
  africa: 'Africa',
};
// Display names come from the menu links: a page's own heading is sometimes a
// "Click here for the ... Newsroom" banner instead of the country name.
const nameOf = new Map();
for (const m of menu.matchAll(/href="\/facts-and-statistics\/((?:country|state)\/[a-z0-9-]+)"[^>]*>([^<]+)</g)) {
  if (!nameOf.has(m[1])) nameOf.set(m[1], m[2].trim());
}
// The menu groups countries under <ul id="fas-countries-<continent>">.
const continentOf = new Map();
for (const m of menu.matchAll(/id="fas-countries-([a-z-]+)"([\s\S]*?)<\/ul>/g)) {
  for (const l of m[2].matchAll(/\/facts-and-statistics\/country\/([a-z0-9-]+)"/g)) {
    continentOf.set(l[1], CONTINENT_NAMES[m[1]] ?? m[1]);
  }
}
const links = [...new Set([...menu.matchAll(/href="\/facts-and-statistics\/(country|state)\/([a-z0-9-]+)"/g)].map((m) => `${m[1]}/${m[2]}`))];
const countrySlugs = links.filter((l) => l.startsWith('country/'));
const stateSlugs = links.filter((l) => l.startsWith('state/'));
// Canada's provinces come from the Canadian Newsroom's own menu.
const caMenu = await fetchHtml('/facts-and-statistics/province/alberta', CA_BASE);
// Nunavut is not in the menu. Its URL loads, but shows Canada's totals (no figures of
// its own), so it is deliberately left out and stays grey on the map.
const provinceSlugs = [...new Set([...caMenu.matchAll(/href="\/facts-and-statistics\/(province\/[a-z0-9-]+)"/g)].map((m) => m[1]))];
for (const m of caMenu.matchAll(/href="\/facts-and-statistics\/(province\/[a-z0-9-]+)"[^>]*>([^<]+)</g)) {
  if (!nameOf.has(m[1])) nameOf.set(m[1], m[2].trim());
}
console.log(`${countrySlugs.length} countries, ${stateSlugs.length} states, ${provinceSlugs.length} provinces in the menus`);

const scrape = async (paths, base = BASE) => {
  const rows = [];
  for (const p of paths) {
    await sleep(DELAY_MS);
    const html = await fetchHtml(`/facts-and-statistics/${p}`, base);
    if (!html) {
      console.warn(`skip ${p} (404)`);
      continue;
    }
    const row = parse(html, p.split('/')[1], p, base);
    if (row.membership === null) {
      console.warn(`skip ${p} (no membership found)`);
      continue;
    }
    rows.push(row);
    console.log(`${p}: ${row.name} ${row.membership}`);
  }
  return rows;
};

const csv = (rows) => {
  const cols = Object.keys(rows[0]);
  const esc = (v) => {
    const s = v === null || v === undefined ? '' : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [cols.join(','), ...rows.map((r) => cols.map((c) => esc(r[c])).join(','))].join('\n') + '\n';
};

const countries = (await scrape(countrySlugs)).sort((a, b) => a.name.localeCompare(b.name));
const states = (await scrape(stateSlugs)).sort((a, b) => a.name.localeCompare(b.name));
if (!countries.length || !states.length) throw new Error('nothing scraped; refusing to overwrite output');
writeFileSync(new URL('newsroom-countries.csv', OUT), csv(countries));
writeFileSync(new URL('newsroom-states.csv', OUT), csv(states));
const provinces = (await scrape(provinceSlugs, CA_BASE)).sort((a, b) => a.name.localeCompare(b.name));
if (provinces.length) writeFileSync(new URL('newsroom-provinces.csv', OUT), csv(provinces));
console.log(`\n${countries.length} countries, ${states.length} states, ${provinces.length} provinces`);
