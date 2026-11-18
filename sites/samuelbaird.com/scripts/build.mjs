// Static build for samuelbaird.com. Run: node scripts/build.mjs
// - Reads the site's own data (sacred-sites/data.js, books/data.js) and pre-renders it as plain HTML,
//   CSV and JSON, so people, search engines and AI crawlers see the content without running JavaScript.
// - Regenerates shared fragments (nav, footer, SEO/JSON-LD head) inside marker comments on every page.
// - Writes /about, /faq, /data, /sacred-sites/sites, /wishlist, robots.txt, sitemap.xml, llms.txt, llms-full.txt.
// - /wishlist merges wishlist/data.json (synced from Amazon by scripts/fetch-wishlist.mjs) with your
//   hand-set priorities in wishlist/priorities.json.
// Idempotent: safe to run repeatedly. Commit the output (Vercel serves the repo as-is).
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { renderHead, renderTop, renderFoot, PROJECTS as FAMILY, ALL_PROJECTS } from '../../../packages/family/render.mjs';
import { AMAZON_TAG } from '../../../packages/family/referrals.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const R = (...p) => path.join(ROOT, ...p);
const read = (f) => fs.readFileSync(R(f), 'utf8');
const write = (f, s) => { fs.mkdirSync(path.dirname(R(f)), { recursive: true }); fs.writeFileSync(R(f), s); };

/* ---------- constants you may want to edit ---------- */
const BASE = 'https://samuelbaird.com';
const NAME = 'Samuel Baird';
const EMAIL = 'ithinksamofficial@gmail.com';
const LICENSE_URL = 'https://creativecommons.org/licenses/by/4.0/';
const LICENSE_NAME = 'CC BY 4.0';
const NOW = new Date().toISOString();
const TODAY = NOW.slice(0, 10);
const MONTH_YEAR = new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric', timeZone: 'UTC' });
const YEAR = new Date().getUTCFullYear();
// Figures for the two sister sites, read from the live sites on the date below. Update when you rebuild.
const EXT = {
  asOf: 'November 2026',
  lds: { channels: 328, subs: '16.6M', studies: 73, graphics: 58 },
  pulpit: { discourses: 12201, verbatim: 4292, authoritative: 5474, contemporaneous: 2225, reconstructed: 2, fragmentary: 208 },
};
// Project URLs come from packages/family/projects.json (one registry for every site).
const projectUrl = (id) => FAMILY.find((p) => p.id === id).url;
const LDS = projectUrl('latter-day-stats');
const PULPIT = 'https://pulpit.restorationcommons.org';
const DESERET = 'https://deseret.wiki';
const YT = 'https://www.youtube.com/@ithinkthereforeisam?sub_confirmation=1';
const SUBSTACK = 'https://ithinkisam.substack.com/';
const IG = 'https://www.instagram.com/ithinkisam/';
const GH = 'https://github.com/Samuel-Baird';
// sameAs entries are identity links, so use the plain channel URL (YT carries ?sub_confirmation=1 for visible links).
const YT_CHANNEL = 'https://www.youtube.com/@ithinkthereforeisam';
const SAMEAS = [YT_CHANNEL, SUBSTACK, IG, GH];

/* ---------- load data ---------- */
const sandbox = vm.createContext({ window: {}, console });
vm.runInContext(read('books/data.js'), sandbox);
const BOOKS = sandbox.window.BOOKS.map((b) => ({
  ...b, type: b.type || (/amazon\./.test(b.link) ? 'book' : 'article'),
}));
const sites = vm.runInNewContext(
  read('sacred-sites/data.js') + '\n' + read('sacred-sites/links.js') + '\n' + read('sacred-sites/lib.js') +
  '\n;({SITES,WISH,COMMUNITIES,labelOf,isService,categoryLabel,mapsUrl,NO_MAPS,ALL_PHOTOS,COUNTRY,photoUrl});',
  { console },
);
const { SITES, WISH, COMMUNITIES, labelOf, isService, categoryLabel, mapsUrl, NO_MAPS, ALL_PHOTOS, photoUrl } = sites;

/* ---------- wishlist: Amazon data + local priorities ---------- */
// Referral tags live in one place for every site (packages/family/referrals.mjs).
const AFFILIATE_TAG = AMAZON_TAG;
const readJson = (f, fallback) => (fs.existsSync(R(f)) ? JSON.parse(read(f)) : fallback);
const WL_DATA = readJson('wishlist/data.json', { items: [] });
const WL_PRI = readJson('wishlist/priorities.json', { items: {} }).items || {};
const WL_URL = WL_DATA.url || 'https://www.amazon.com/hz/wishlist/ls/3ECBMMP7G2LZ4';
const TIERS = [
  ['highest', 'Most wanted'], ['high', 'High priority'], ['medium', 'Wanted'], ['low', 'Nice to have'], ['lowest', 'Someday'],
];
const TIER_ORDER = Object.fromEntries(TIERS.map(([k], i) => [k, i]));
const WISHLIST = WL_DATA.items.map((it, i) => {
  const o = (it.asin && WL_PRI[it.asin]) || WL_PRI[it.itemId] || {};
  const priority = TIER_ORDER[o.priority] != null ? o.priority : TIER_ORDER[it.amazonPriority] != null ? it.amazonPriority : 'medium';
  // Product link keeps the list context (colid/coliid) so Amazon offers my gift address and marks it bought.
  const link = it.asin
    ? `https://www.amazon.com/dp/${it.asin}?colid=${WL_DATA.list}&coliid=${it.itemId}&tag=${AFFILIATE_TAG}`
    : it.href || WL_URL;
  return { ...it, priority, rank: Number.isFinite(o.rank) ? o.rank : Infinity, note: o.note ?? it.comment ?? '', hide: !!o.hide, link, order: i };
}).filter((x) => !x.hide).sort((a, b) => TIER_ORDER[a.priority] - TIER_ORDER[b.priority] || a.rank - b.rank || (b.added || '').localeCompare(a.added || '') || a.order - b.order);
const WL_UPDATED = WL_DATA.updated ? WL_DATA.updated.slice(0, 10) : null;

const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const j = (o) => JSON.stringify(o);
const longDate = (iso) => new Date(iso + 'T12:00:00Z').toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
const shortDate = (iso) => new Date(iso + 'T12:00:00Z').toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' });
const plural = (n, w, pl) => `${n.toLocaleString('en-US')} ${n === 1 ? w : (pl || w + 's')}`;
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

/* ---------- derived facts ---------- */
const allVisits = SITES.flatMap((s) => s.visits.map((v) => ({ ...v, site: s })));
const traditionsOf = (list) => [...new Set(list.map((s) => labelOf(s.denom)))];
const F = {
  sites: SITES.length,
  traditions: traditionsOf(SITES).length,
  countries: new Set(SITES.map((s) => s.country)).size,
  visits: allVisits.length,
  services: allVisits.filter((v) => isService(v.type)).length,
  photos: ALL_PHOTOS.length,
  wishlist: WISH.length,
  firstVisit: allVisits.map((v) => v.date).sort()[0],
  lastVisit: allVisits.map((v) => v.date).sort().slice(-1)[0],
  ldsTemples: SITES.filter((s) => s.denom === 'LDS' && /temple/i.test(s.name)).length,
  books: BOOKS.filter((b) => b.type === 'book').length,
  articles: BOOKS.filter((b) => b.type === 'article').length,
  read: BOOKS.length,
  lastRead: BOOKS[0],
};
const FACT = {
  sites: F.sites, traditions: F.traditions, countries: F.countries, photos: F.photos, visits: F.visits,
  services: F.services, ldsTemples: F.ldsTemples, read: F.read, books: F.books, articles: F.articles,
  channels: EXT.lds.channels, subs: EXT.lds.subs, studies: EXT.lds.studies, graphics: EXT.lds.graphics,
  discourses: EXT.pulpit.discourses.toLocaleString('en-US'),
  bookcount: `${plural(F.books, 'book')} and ${plural(F.articles, 'article')}, newest first, with the date I finished each one.`,
};
// Every LDS temple (data/lds-temples.json, built by scripts/fetch-temples.mjs from official + Wikidata + OSM data).
const TEMPLE_DATA = JSON.parse(read('data/lds-temples.json'));
const TEMPLES = TEMPLE_DATA.temples;
// Keep in step with temples/app.js.
const TEMPLE_STATUS = {
  'operating': ['Operating', '#D9B46A'], 'opening-soon': ['Opening soon', '#8DA27A'], 'under-renovation': ['Under renovation', '#C98A5A'],
  'under-construction': ['Under construction', '#7E9BBB'], 'announced': ['Announced', '#B9AE96'], 'closed': ['Closed', '#9A4446'],
};
const T = {
  all: TEMPLES.length,
  operating: TEMPLES.filter((t) => ['operating', 'under-renovation'].includes(t.status)).length,
  building: TEMPLES.filter((t) => ['under-construction', 'opening-soon'].includes(t.status)).length,
  announced: TEMPLES.filter((t) => t.status === 'announced').length,
  countries: new Set(TEMPLES.map((t) => t.country).filter(Boolean)).size,
  thisYear: TEMPLES.filter((t) => (t.dedicated || '').startsWith(TODAY.slice(0, 4))).length,
};
FACT.temples = T.all;
const templePlace = (t) => [t.city, t.region, t.country].filter(Boolean).join(', ') || t.location;
const templeStatus = (s) => `<span class="t-st"><i style="background:${(TEMPLE_STATUS[s] || [0, '#B9AE96'])[1]}"></i>${esc((TEMPLE_STATUS[s] || [s])[0])}</span>`;
const templeRow = (t) => `<tr data-id="${esc(t.id)}"><td>${esc(t.name)}</td><td>${esc(templePlace(t))}</td><td>${templeStatus(t.status)}</td>`
  + `<td class="hide-sm">${t.announced ? `<time datetime="${t.announced}">${shortDate(t.announced)}</time>` : ''}</td>`
  + `<td>${t.dedicated ? `<time datetime="${t.dedicated}">${shortDate(t.dedicated)}</time>` : ''}</td>`
  + `<td class="t-links"><a href="${esc(t.officialUrl)}" rel="noopener">Official</a>${t.wikipedia ? `<a href="${esc(t.wikipedia)}" rel="noopener">Wikipedia</a>` : ''}</td></tr>`;
const templeStats = () => [
  [T.all, 'temples'], [T.operating, 'operating'], [T.building, 'under construction'], [T.announced, 'announced'],
  [T.countries, 'countries &amp; territories'], [T.thisYear, `dedicated in ${TODAY.slice(0, 4)}`],
].map(([n, l]) => `<li><b>${n}</b><span>${l}</span></li>`).join('');
function templeDecades() {
  const counts = {};
  for (const t of TEMPLES) if (t.dedicated) { const d = t.dedicated.slice(0, 3) + '0'; counts[d] = (counts[d] || 0) + 1; }
  const decades = [];
  for (let d = +Object.keys(counts).sort()[0]; d <= +TODAY.slice(0, 3) * 10; d += 10) decades.push(String(d));
  const max = Math.max(...Object.values(counts));
  return `<div class="t-dec" role="img" aria-label="Temples dedicated per decade: ${decades.map((d) => `${d}s ${counts[d] || 0}`).join(', ')}">${decades.map((d) => `<div style="height:${((counts[d] || 0) / max * 100).toFixed(1)}%"><span>${counts[d] || 0}</span></div>`).join('')}</div>`
    + `<div class="t-dec-x" aria-hidden="true">${decades.map((d) => `<span>${d.slice(2)}s</span>`).join('')}</div>`;
}

// Church history sites (data/lds-historic-sites.json, built by scripts/fetch-historic-sites.mjs from the Church's pages + OSM).
const HIST_DATA = JSON.parse(read('data/lds-historic-sites.json'));
const HIST = HIST_DATA.sites;
// Keep in step with historic-sites/app.js.
const HIST_CAT = { 'Historic site': '#D9B46A', "Visitors' center": '#7E9BBB', Monument: '#8DA27A', Museum: '#C98A5A' };
const H = {
  all: HIST.length,
  historic: HIST.filter((x) => x.category === 'Historic site').length,
  centers: HIST.filter((x) => x.category === "Visitors' center" || x.category === 'Museum').length,
  monuments: HIST.filter((x) => x.category === 'Monument').length,
  states: new Set(HIST.filter((x) => x.country === 'United States').map((x) => x.region).filter(Boolean)).size,
  countries: new Set(HIST.map((x) => x.country).filter(Boolean)).size,
};
FACT.historicSites = H.all;
const histPlace = (x) => [x.city, x.region, x.country === 'United States' ? '' : x.country].filter(Boolean).join(', ');
const histCat = (c) => `<span class="t-st"><i style="background:${HIST_CAT[c] || '#B9AE96'}"></i>${esc(c)}</span>`;
const histRow = (x) => `<tr data-id="${esc(x.id)}"><td>${esc(x.name)}</td><td>${esc(histPlace(x))}</td><td>${histCat(x.category)}</td><td class="hide-sm">${esc(x.area || '')}</td>`
  + `<td class="t-links"><a href="${esc(x.officialUrl)}" rel="noopener">Official</a>${x.wikipedia ? `<a href="${esc(x.wikipedia)}" rel="noopener">Wikipedia</a>` : ''}</td></tr>`;
const histStats = () => [
  [H.all, 'sites'], [H.historic, 'historic sites'], [H.centers, 'visitors&rsquo; centers &amp; museums'], [H.monuments, 'monuments'],
  [H.states, 'U.S. states'], [H.countries, H.countries === 1 ? 'country' : 'countries'],
].map(([n, l]) => `<li><b>${n}</b><span>${l}</span></li>`).join('');

// Hymnbooks (data/lds-hymns.json, built by scripts/fetch-hymns.mjs from the Joseph Smith Papers + the Church's Gospel Library).
const HYMN_DATA = JSON.parse(read('data/lds-hymns.json'));
const HYMNS = HYMN_DATA.hymns;
const HYMN_ED = Object.fromEntries(HYMN_DATA.editions.map((e) => [e.id, e]));
// Newest edition first. Keep CHANGE in step with hymns/app.js.
const HYMN_ORDER = HYMN_DATA.editions.map((e) => e.id).reverse();
const HYMN_CHANGE = { added: ['Added', '#8DA27A'], kept: ['Kept', '#7E9BBB'], removed: ['Removed', '#C98A5A'] };
const hymnIn = (ed) => HYMNS.filter((h) => h.edition === ed && h.change !== 'removed');
const keysIn = (ed) => new Set(hymnIn(ed).map((h) => h.hymnKey));
const HY = {
  editions: HYMN_DATA.editions.length,
  records: HYMNS.length,
  texts: new Set(HYMNS.map((h) => h.hymnKey)).size,
  first: HYMN_DATA.editions[0],
  y1835in1985: [...keysIn('1835')].filter((k) => keysIn('1985').has(k)).length,
  y1835: hymnIn('1835').length,
  newHfhc: hymnIn('hfhc').filter((h) => h.change === 'added').length,
};
FACT.hymns = HY.records;
const hymnCount = (ed) => HYMN_ED[ed].hymns;
const hymnChange = (c) => c ? `<span class="t-st"><i style="background:${HYMN_CHANGE[c][1]}"></i>${HYMN_CHANGE[c][0]}</span>` : '';
const hymnRow = (h) => `<tr data-id="${esc(h.id)}"><td class="h-no">${h.number ?? (h.previousNumber != null ? `<s title="Number in the previous edition">${h.previousNumber}</s>` : '')}</td>`
  + `<td><b>${esc(h.title || h.firstLine)}</b>${h.title && h.firstLine ? `<span class="h-fl">${esc(h.firstLine)}</span>` : ''}</td>`
  + `<td>${esc(HYMN_ED[h.edition].short)}</td><td class="hide-sm">${esc(h.text || '')}</td><td>${hymnChange(h.change)}</td>`
  + `<td class="t-links"><a href="${esc(h.source)}" rel="noopener">Source</a></td></tr>`;
const hymnRows = () => HYMN_ORDER.flatMap((ed) => HYMNS.filter((h) => h.edition === ed)
  .sort((a, b) => (a.number ?? 1e6) - (b.number ?? 1e6) || (a.previousNumber ?? 0) - (b.previousNumber ?? 0))).map(hymnRow).join('\n');
const hymnStats = () => [
  ...HYMN_DATA.editions.map((e) => [e.hymns, `${esc(e.short)}${e.partial ? ' (so far)' : ''}`]),
  [HY.texts, 'distinct texts'], [`${HY.y1835in1985}/${HY.y1835}`, '1835 hymns still in 1985'],
].map(([n, l]) => `<li><b>${n}</b><span>${l}</span></li>`).join('');

// Sites grouped by tradition (listed communities first, in the order they are defined).
const byTradition = [];
for (const c of COMMUNITIES) {
  const list = SITES.filter((s) => c.match.includes(s.denom)).sort((a, b) => a.name.localeCompare(b.name));
  if (list.length) byTradition.push({ name: c.name, sites: list });
}
const covered = new Set(byTradition.flatMap((t) => t.sites.map((s) => s.id)));
const other = SITES.filter((s) => !covered.has(s.id));
if (other.length) byTradition.push({ name: 'Other traditions', sites: other });

const siteRow = (s) => {
  const dates = s.visits.map((v) => v.date).sort();
  const cats = [...new Set(s.visits.map((v) => categoryLabel(v.cat)))];
  return {
    name: s.name, tradition: labelOf(s.denom), denomination: s.denom, city: s.city, state: s.state, country: s.country,
    latitude: s.lat, longitude: s.lon, website: s.site || '', wikipedia: s.wikiUrl || '', visits: s.visits.length, first_visit: dates[0], last_visit: dates[dates.length - 1],
    visit_types: cats.join('; '),
    google_maps: NO_MAPS.has(s.id) ? '' : mapsUrl(s),
  };
};
const SITE_ROWS = SITES.map(siteRow).sort((a, b) => a.tradition.localeCompare(b.tradition) || a.name.localeCompare(b.name));
const csvCell = (v) => { const s = String(v ?? ''); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
const toCsv = (rows) => { const cols = Object.keys(rows[0]); return [cols.join(','), ...rows.map((r) => cols.map((c) => csvCell(r[c])).join(','))].join('\n') + '\n'; };
const BOOK_ROWS = BOOKS.map((b) => ({ title: b.title, type: b.type, date_finished: b.read, url: b.link }));

/* ---------- shared fragments ---------- */
const NAV_ITEMS = [
  ['/#projects', 'Projects'], ['/sacred-sites', 'Sacred Sites'], ['/books', 'Reading'], ['/collection', 'Collection'],
  ['/data', 'Data'], ['/faq', 'FAQ'], ['/about', 'About'],
];
// Shared family chrome (sidebar, top bar, panorama) from packages/family.
const nav = (p) => renderTop('samuelbaird.com', p);
// samuelbaird.com links stay root-relative on this site.
const rel = (u) => (u.startsWith(BASE) ? u.slice(BASE.length) || '/' : u + (/^https?:\/\/[^/]+$/.test(u) ? '/' : ''));
const foot = () => `<footer class="sitefoot"><div class="rail">
  <div class="cols">
    <div><h2 class="small-caps">Projects</h2><ul>
      ${FAMILY.map((x) => `<li><a href="${rel(x.url)}">${esc(x.name)}</a>${x.role === 'contributor' ? ' <small>(contributor)</small>' : ''}</li>`).join('')}
      <li><a href="/projects">All projects</a></li></ul></div>
    <div><h2 class="small-caps">Learn</h2><ul>
      <li><a href="/about">About</a></li><li><a href="/faq">FAQ</a></li><li><a href="/data">Open data</a></li>
      <li><a href="/sacred-sites/sites">Sacred sites directory</a></li><li><a href="/llms.txt">llms.txt</a></li></ul></div>
    <div><h2 class="small-caps">Elsewhere</h2><ul>
      <li><a href="${YT}" rel="me noopener">YouTube</a></li><li><a href="${SUBSTACK}" rel="me noopener">Substack</a></li>
      <li><a href="${IG}" rel="me noopener">Instagram</a></li><li><a href="${GH}" rel="me noopener">GitHub</a></li></ul></div>
    <div><h2 class="small-caps">Contact &amp; support</h2><ul>
      <li><a href="mailto:${EMAIL}?subject=Samuel%20Baird">${EMAIL}</a></li><li><a href="/donate">Donate</a></li>
      <li><a href="/wishlist">Wishlist</a></li></ul></div>
  </div>
  <p class="legal">Original data on this site is released under <a href="${LICENSE_URL}" rel="license noopener">${LICENSE_NAME}</a>.</p>
</div></footer>
${renderFoot('samuelbaird.com')}`;

/* ---------- structured data ---------- */
const PERSON = {
  '@type': 'Person', '@id': BASE + '/#person', name: NAME, url: BASE + '/', sameAs: SAMEAS,
  description: 'Builds public data tools and makes videos about religion, history and ideas. Creator of Latter-day Stats, the Deseret Wiki, Urim and MCP servers for Latter-day Saint research (Peepstone, Deseret MCP); contributor to Pulpit; keeper of the Sacred Sites Visited map.',
  knowsAbout: ['Latter-day Saint history', 'Religious demographics', 'Survey data', 'General Conference', 'Deseret Alphabet', 'Translation', 'Model Context Protocol', 'Comparative religion', 'Data visualization'],
  email: 'mailto:' + EMAIL,
};
const WEBSITE = { '@type': 'WebSite', '@id': BASE + '/#website', url: BASE + '/', name: NAME, description: 'Data tools and videos about religion, history and ideas.', inLanguage: 'en', publisher: { '@id': BASE + '/#person' }, license: LICENSE_URL };
// One schema.org node per external project (on-site pages get their own CollectionPage nodes).
const projectNodeId = (x) => (x.kind === 'page' ? x.url + '#page' : x.url + '/#' + (x.schemaType === 'SoftwareApplication' ? 'app' : 'website'));
const projectNode = (x) => ({
  '@type': x.schemaType, '@id': projectNodeId(x), name: x.name, url: x.url + '/', description: x.description,
  ...(x.schemaType === 'SoftwareApplication' ? { applicationCategory: 'DeveloperApplication', operatingSystem: 'Any (Model Context Protocol client)', offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' } } : { inLanguage: 'en' }),
  [x.role === 'contributor' ? 'contributor' : 'creator']: { '@id': BASE + '/#person' },
  keywords: x.topics.join(', '), subjectOf: { '@type': 'AboutPage', '@id': BASE + '/projects/' + x.id + '#page', url: BASE + '/projects/' + x.id, name: `About ${x.name}` },
});
const PROJECTS = FAMILY.filter((x) => x.kind !== 'page').map(projectNode);
const pageId = (path) => BASE + (path === '/' ? '/' : path) + '#page';
const crumbs = (items) => {
  const last = items[items.length - 1][1];
  return { '@type': 'BreadcrumbList', '@id': BASE + last + '#breadcrumb', itemListElement: items.map(([name, url], i) => ({ '@type': 'ListItem', position: i + 1, name, item: BASE + url })) };
};
// Standard page node. Every page links to the shared WebSite/Person nodes, which seo() adds to each graph.
const webPage = (p, type, extra = {}) => {
  const url = BASE + (p.path === '/' ? '/' : p.path);
  const img = BASE + (p.image || '/img/og-card.png');
  return {
    '@type': type, '@id': url + '#page', url, name: p.title, description: p.desc, inLanguage: 'en',
    isPartOf: { '@id': BASE + '/#website' }, author: { '@id': BASE + '/#person' }, publisher: { '@id': BASE + '/#person' },
    primaryImageOfPage: { '@type': 'ImageObject', url: img }, dateModified: NOW,
    ...(p.path === '/' ? {} : { breadcrumb: { '@id': url + '#breadcrumb' } }), ...extra,
  };
};
const PERSON_REF = { '@id': BASE + '/#person' };
const CATALOG = { '@type': 'DataCatalog', name: `${NAME}: open data`, url: BASE + '/data' };

// Places of worship: pick the most specific schema.org type the tradition supports.
const placeType = (s) => (s.denom === 'Catholic' ? 'CatholicChurch'
  : ['Anglican', 'Episcopalian', 'Lutheran', 'Greek Orthodox', 'SDA'].includes(s.denom) ? 'Church'
  : /jewish/i.test(s.denom) ? 'Synagogue' : /islam|muslim/i.test(s.denom) ? 'Mosque' : 'PlaceOfWorship');
const placeId = (s) => BASE + '/sacred-sites/sites#' + slug(s.name);
const placeNode = (s) => ({
  '@type': placeType(s), '@id': placeId(s), name: s.name,
  address: { '@type': 'PostalAddress', addressLocality: s.city, addressRegion: s.state, addressCountry: s.country === 'USA' ? 'US' : s.country },
  geo: { '@type': 'GeoCoordinates', latitude: s.lat, longitude: s.lon },
  ...(NO_MAPS.has(s.id) ? {} : { hasMap: mapsUrl(s) }),
  description: `${labelOf(s.denom)} place of worship in ${s.city}, ${s.state}, visited ${plural(s.visits.length, 'time')} by ${NAME}.`,
});
const photoNodes = () => ALL_PHOTOS.map((x, i) => ({
  '@type': 'ImageObject', '@id': BASE + '/sacred-sites/photos#photo-' + (i + 1),
  name: `${x.site.name}, ${shortDate(x.date)}`, contentUrl: photoUrl(x.p, 1600), thumbnailUrl: photoUrl(x.p, 400),
  width: x.p[1], height: x.p[2], dateCreated: x.date, encodingFormat: 'image/jpeg',
  contentLocation: { '@id': placeId(x.site) }, creator: PERSON_REF, creditText: NAME,
  copyrightNotice: `© ${x.date.slice(0, 4)} ${NAME}. ${LICENSE_NAME}`, copyrightHolder: PERSON_REF,
  license: LICENSE_URL, acquireLicensePage: BASE + '/data#cite',
}));

// Keep in sync with collection/index.html (titles are read from there for llms-full.txt).
const COLLECTION = [
  { '@type': 'Book', name: 'The Deseret First Book', datePublished: '1868', publisher: { '@type': 'Organization', name: 'Regents of the Deseret University' }, locationCreated: { '@type': 'Place', name: 'Salt Lake City, Utah' }, inLanguage: 'dsr', description: 'First edition of one of only four books ever printed in the Deseret Alphabet.' },
  { '@type': 'Book', name: '1908 Northern States Mission Book of Mormon', datePublished: '1908', publisher: { '@type': 'Organization', name: 'Northern States Mission of The Church of Jesus Christ of Latter-day Saints' }, locationCreated: { '@type': 'Place', name: 'Chicago, Illinois' }, description: 'Early 20th-century hardcover edition of the Book of Mormon published by the Northern States Mission.' },
  { '@type': 'PublicationIssue', name: 'The Latter-day Saints\u2019 Millennial Star, January 2, 1864', datePublished: '1864-01-02', isPartOf: { '@type': 'Periodical', name: 'The Latter-day Saints\u2019 Millennial Star' }, locationCreated: { '@type': 'Place', name: 'Liverpool, England' }, description: 'Original 1864 issue of the Millennial Star, the first for 1864, during the presidency of Brigham Young.' },
  { '@type': 'CreativeWork', name: 'Vintage LDS Glass Sacrament Cup', material: 'glass', description: 'Early 1900s vintage glass individual sacrament cup from the transition away from shared communion cups in Latter-day Saint worship.' },
];
const collectionList = () => ({ '@type': 'ItemList', '@id': BASE + '/collection#items', name: 'Collection', numberOfItems: COLLECTION.length, itemListElement: COLLECTION.map((c, i) => ({ '@type': 'ListItem', position: i + 1, item: { ...c, owner: PERSON_REF } })) });

const bookNode = (b, i) => {
  const isbn = (b.cover.match(/\/(\d{9}[\dX])\.jpg$/) || [])[1];
  return { '@type': b.type === 'book' ? 'Book' : 'Article', '@id': BASE + '/books#item-' + (i + 1), name: b.title, url: b.link, ...(isbn ? { isbn } : {}), ...(b.cover ? { image: BASE + b.cover } : {}) };
};
const DATASETS = {
  sites: {
    '@type': 'Dataset', '@id': BASE + '/data#sacred-sites', name: 'Sacred Sites Visited: churches, temples and houses of worship',
    description: `${F.sites} sacred sites across ${F.traditions} traditions visited in person by Samuel Baird between ${longDate(F.firstVisit)} and ${longDate(F.lastVisit)}, with coordinates, visit counts and visit types. Each site is counted once.`,
    url: BASE + '/data', license: LICENSE_URL, isAccessibleForFree: true, creator: { '@type': 'Person', name: NAME, url: BASE + '/' }, inLanguage: 'en', dateModified: NOW, includedInDataCatalog: CATALOG,
    keywords: ['sacred sites', 'places of worship', 'churches', 'LDS temples', 'religion', 'Utah'],
    temporalCoverage: `${F.firstVisit}/${F.lastVisit}`, spatialCoverage: { '@type': 'Place', name: 'United States' },
    variableMeasured: ['name', 'tradition', 'city', 'state', 'latitude', 'longitude', 'visits', 'first_visit', 'last_visit', 'visit_types'],
    distribution: [
      { '@type': 'DataDownload', encodingFormat: 'text/csv', contentUrl: BASE + '/data/sacred-sites.csv' },
      { '@type': 'DataDownload', encodingFormat: 'application/json', contentUrl: BASE + '/data/sacred-sites.json' },
    ],
  },
  temples: {
    '@type': 'Dataset', '@id': BASE + '/data#lds-temples', name: TEMPLE_DATA.name,
    description: `All ${T.all} temples of The Church of Jesus Christ of Latter-day Saints (operating, under construction and announced) with status, location, coordinates and announcement, groundbreaking and dedication dates. Compiled from the Church's official temple pages, Wikidata and OpenStreetMap.`,
    url: BASE + '/temples', isAccessibleForFree: true, creator: { '@type': 'Person', name: NAME, url: BASE + '/' }, inLanguage: 'en', dateModified: NOW, includedInDataCatalog: CATALOG,
    keywords: ['LDS temples', 'Latter-day Saint temples', 'temples of The Church of Jesus Christ of Latter-day Saints', 'temple dedications', 'open data'],
    spatialCoverage: { '@type': 'Place', name: 'Worldwide' },
    variableMeasured: ['name', 'status', 'city', 'region', 'country', 'latitude', 'longitude', 'announced', 'groundbreaking', 'dedicated', 'rededicated'],
    distribution: [
      { '@type': 'DataDownload', encodingFormat: 'text/csv', contentUrl: BASE + '/data/lds-temples.csv' },
      { '@type': 'DataDownload', encodingFormat: 'application/json', contentUrl: BASE + '/data/lds-temples.json' },
    ],
  },
  historic: {
    '@type': 'Dataset', '@id': BASE + '/data#lds-historic-sites', name: HIST_DATA.name,
    description: `The ${H.all} Church history sites, visitors' centers, monuments and museums operated by The Church of Jesus Christ of Latter-day Saints, with category, address and coordinates. Compiled from the Church's official historic sites pages and OpenStreetMap.`,
    url: BASE + '/historic-sites', isAccessibleForFree: true, creator: { '@type': 'Person', name: NAME, url: BASE + '/' }, inLanguage: 'en', dateModified: NOW, includedInDataCatalog: CATALOG,
    keywords: ['Church history sites', 'LDS historic sites', 'Latter-day Saint historic sites', 'Nauvoo', 'Kirtland', 'Palmyra', 'Mormon Trail', 'open data'],
    spatialCoverage: [...new Set(HIST.map((x) => x.country).filter(Boolean))].map((c) => ({ '@type': 'Place', name: c })),
    variableMeasured: ['name', 'category', 'operator', 'area', 'street', 'city', 'region', 'country', 'latitude', 'longitude', 'coordPrecision'],
    distribution: [
      { '@type': 'DataDownload', encodingFormat: 'text/csv', contentUrl: BASE + '/data/lds-historic-sites.csv' },
      { '@type': 'DataDownload', encodingFormat: 'application/json', contentUrl: BASE + '/data/lds-historic-sites.json' },
    ],
  },
  hymns: {
    '@type': 'Dataset', '@id': BASE + '/data#lds-hymns', name: HYMN_DATA.name,
    description: `Every hymn in ${HY.editions} Latter-day Saint hymnbooks (${HYMN_DATA.editions.map((e) => `${e.short}: ${e.hymns}`).join('; ')}), one record per hymn per edition, with number, title, first line, text and music credits as printed, and whether each hymn was added, kept or removed from the edition before. Facts only, no lyrics. Compiled from the Joseph Smith Papers transcriptions and the Church's Gospel Library, with authors' religion from Wikidata.`,
    url: BASE + '/hymns', isAccessibleForFree: true, creator: { '@type': 'Person', name: NAME, url: BASE + '/' }, inLanguage: 'en', dateModified: NOW, includedInDataCatalog: CATALOG,
    keywords: ['LDS hymns', 'Latter-day Saint hymnbook', 'Hymns for Home and Church', '1985 hymnbook', 'Emma Smith hymnal', 'hymnody', 'open data'],
    temporalCoverage: `${HY.first.year}/..`,
    variableMeasured: ['edition', 'number', 'title', 'firstLine', 'text', 'music', 'tune', 'yearWritten', 'authorDenomination', 'change', 'previousNumber'],
    distribution: [
      { '@type': 'DataDownload', encodingFormat: 'text/csv', contentUrl: BASE + '/data/lds-hymns.csv' },
      { '@type': 'DataDownload', encodingFormat: 'application/json', contentUrl: BASE + '/data/lds-hymns.json' },
    ],
  },
  reading: {
    '@type': 'Dataset', '@id': BASE + '/data#reading-list', name: 'Reading log: books and articles with date finished',
    description: `${F.books} books and ${F.articles} articles read by Samuel Baird, with the date each was finished and a link to the source.`,
    url: BASE + '/data', license: LICENSE_URL, isAccessibleForFree: true, creator: { '@type': 'Person', name: NAME, url: BASE + '/' }, inLanguage: 'en', dateModified: NOW, includedInDataCatalog: CATALOG,
    keywords: ['reading list', 'books', 'religion', 'theology', 'church history'],
    temporalCoverage: `${BOOKS.map((b) => b.read).sort()[0]}/${BOOKS[0].read}`,
    variableMeasured: ['title', 'type', 'date_finished', 'url'],
    distribution: [
      { '@type': 'DataDownload', encodingFormat: 'text/csv', contentUrl: BASE + '/data/reading-list.csv' },
      { '@type': 'DataDownload', encodingFormat: 'application/json', contentUrl: BASE + '/data/reading-list.json' },
    ],
  },
};

/* ---------- FAQ (also feeds FAQPage JSON-LD and llms-full.txt) ---------- */
const recent3 = BOOKS.slice(0, 3).map((b) => b.title);
const ldsTempleNames = SITES.filter((s) => s.denom === 'LDS' && /temple/i.test(s.name)).map((s) => s.name).sort();
const FAQ = [
  ['Who is Samuel Baird?', `Samuel Baird builds public data tools and makes videos about religion, history and ideas. He created <a href="${rel(LDS)}">Latter-day Stats</a>, a public hub for statistics, research and creator data on the Latter-day Saint community; the <a href="${DESERET}/">Deseret Wiki</a>, a library and primer of the 1854 Deseret Alphabet; <a href="${rel(projectUrl('urim'))}">Urim</a>, an atlas of how the Church translates its own vocabulary; and AI tools for Latter-day Saint research (<a href="/projects/peepstone">Peepstone</a> and <a href="/projects/deseret-mcp">Deseret MCP</a>). He contributed to <a href="${PULPIT}/">Pulpit</a>, a critical edition of every General Conference discourse since 1830; he keeps a map of the sacred places he has visited; and he makes videos on the YouTube channel <a href="${YT}" rel="me noopener">@ithinkthereforeisam</a>. Everything is free, independent and ad-free. See <a href="/about">About</a>.`],
  ['What projects has Samuel Baird made?', `${FAMILY.filter((x) => x.role === 'creator').length} public projects, all free: ${FAMILY.filter((x) => x.role === 'creator').map((x) => `<a href="${rel(x.url)}">${esc(x.name)}</a> (${esc(x.tagline.replace(/\.$/, '').replace(/^./, (c) => c.toLowerCase()))})`).join('; ')}. He also contributed to <a href="${PULPIT}/">Pulpit</a>. Every project has a page under <a href="/projects">Projects</a>.`],
  ['What is Latter-day Stats?', `Latter-day Stats is a public, independent hub for statistics, research and creator data on the Latter-day Saint community. As of ${EXT.asOf} it tracks ${EXT.lds.channels} LDS YouTube channels with ${EXT.lds.subs} combined subscribers, ${EXT.lds.studies} academic studies and ${EXT.lds.graphics} survey-data graphics (Pew and other surveys). Its Data Explorer lets you chart public survey datasets, Studies is a curated research library, and Channels is a directory of LDS YouTube creators. It lives at <a href="${LDS}/">latterdaystats.samuelbaird.com</a>.`],
  ['How many LDS YouTube channels are there?', `There is no official count. The most complete public list is the directory at <a href="${LDS}/channels">Latter-day Stats Channels</a>, which tracked ${EXT.lds.channels} LDS-related YouTube channels with ${EXT.lds.subs} combined subscribers as of ${EXT.asOf}. The directory is refreshed regularly, so check it for the current figure.`],
  ['What is Pulpit?', `Pulpit is a critical digital edition of every General Conference discourse since 1830: ${EXT.pulpit.discourses.toLocaleString('en-US')} discourses as of ${EXT.asOf}, each traced to its best surviving witness and graded for fidelity (${EXT.pulpit.verbatim.toLocaleString('en-US')} verbatim, ${EXT.pulpit.authoritative.toLocaleString('en-US')} authoritative print, ${EXT.pulpit.contemporaneous.toLocaleString('en-US')} contemporaneous report, ${EXT.pulpit.reconstructed} reconstructed, ${EXT.pulpit.fragmentary} fragmentary). It is a Restoration Commons project that Samuel Baird contributed to: <a href="${PULPIT}/">pulpit.restorationcommons.org</a>.`],
  ['Which sacred sites has Samuel Baird visited?', `Since January 2025 he has visited ${F.sites} sacred sites in ${F.traditions} traditions (Catholic, Greek Orthodox, Anglican, Presbyterian, Lutheran, Episcopal, Seventh-day Adventist, Jehovah's Witnesses and The Church of Jesus Christ of Latter-day Saints), most recently on ${longDate(F.lastVisit)}. Each site is counted once. Browse the <a href="/sacred-sites/sites">full directory</a>, the <a href="/sacred-sites">interactive map</a>, the <a href="/sacred-sites/photos">photo gallery</a> or the <a href="/sacred-sites/traditions">traditions page</a>.`],
  ['How many LDS temples has Samuel Baird visited?', `${F.ldsTemples} distinct Latter-day Saint temples as of ${MONTH_YEAR}: ${ldsTempleNames.map(esc).join(', ')}. Repeat visits to the same temple are counted once. Details are in the <a href="/sacred-sites/sites#the-church-of-jesus-christ-of-latter-day-saints-lds">sacred sites directory</a>.`],
  ['What has Samuel Baird read recently?', `He has logged ${plural(F.books, 'book')} and ${plural(F.articles, 'article')}, newest first. The three most recent are ${recent3.map((t) => '<i>' + esc(t) + '</i>').join(', ')}; the latest was finished on ${longDate(F.lastRead.read)}. See <a href="/books">My Reading</a>.`],
  ['Is the data on this site free to use?', `Yes. The original datasets and photographs on this site (the sacred sites list, the reading log and the <a href="/sacred-sites/photos">sacred sites photos</a>) are released under <a href="${LICENSE_URL}" rel="license noopener">${LICENSE_NAME}</a>: reuse them with attribution to Samuel Baird and a link to samuelbaird.com. Download them as CSV or JSON from <a href="/data">Open data</a>. Latter-day Stats publishes its own datasets, each with sources.`],
  ['How should I cite this site?', `For the sacred sites data: Baird, Samuel. "Sacred Sites Visited." samuelbaird.com, ${F.firstVisit.slice(0, 4)}–${F.lastVisit.slice(0, 4)}. ${BASE}/data. For Latter-day Stats, cite the specific study, dataset or graphic page and its listed source.`],
  ['Can AI assistants and search engines use this site?', `Yes. <a href="/robots.txt">robots.txt</a> explicitly allows the major search and AI crawlers (including GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchBot, PerplexityBot, Google-Extended and Applebot-Extended), and a plain-text summary for language models is at <a href="/llms.txt">/llms.txt</a>. Please attribute and link back when you use the content.`],
  ['How can I contact Samuel Baird?', `Email <a href="mailto:${EMAIL}?subject=Samuel%20Baird">${EMAIL}</a> for questions, corrections, collaboration or press. Corrections to any figure on this site are welcome.`],
  ['How can I support the projects?', `The projects are free and ad-free. You can chip in toward hosting by <a href="/donate">donating via PayPal or Venmo</a>, or send something from the <a href="/wishlist">wishlist</a> of books and equipment for the channel, sorted with the most-wanted items first.`],
];
const stripTags = (h) => h.replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"');

/* ---------- build-time schema check ---------- */
function checkLd(path, graph) {
  const ids = new Set(graph.map((n) => n['@id']).filter(Boolean));
  const bad = [];
  const walk = (o, where) => {
    if (Array.isArray(o)) return o.forEach((x) => walk(x, where));
    if (!o || typeof o !== 'object') return;
    const keys = Object.keys(o);
    if (keys.length === 1 && keys[0] === '@id') { if (o['@id'].startsWith(BASE) && !ids.has(o['@id'])) bad.push(`${where}: dangling ${o['@id']}`); return; }
    if (!o['@type']) bad.push(`${where}: node without @type (${keys.slice(0, 3).join(',')})`);
    for (const k of keys) walk(o[k], where + '.' + k);
  };
  graph.forEach((n, i) => walk(n, `${path}[${i}:${n['@type']}]`));
  if (bad.length) { console.error('JSON-LD check failed:\n  ' + bad.slice(0, 20).join('\n  ')); process.exit(1); }
}

/* ---------- head / SEO ---------- */
// Vercel Web Analytics (cookie-free). Needs "Web Analytics" enabled for the project in the Vercel dashboard;
// until then /_vercel/insights/script.js 404s harmlessly. Gives referrers such as chatgpt.com and perplexity.ai.
const ANALYTICS = `<script>window.va=window.va||function(){(window.vaq=window.vaq||[]).push(arguments)}</script>
<script defer src="/_vercel/insights/script.js"></script>`;
function seo(p) {
  const url = BASE + (p.path === '/' ? '/' : p.path);
  const img = BASE + (p.image || '/img/og-card.png');
  const seen = new Set();
  const graph = [WEBSITE, PERSON, ...(p.ld || [])].filter((n) => !n['@id'] || (!seen.has(n['@id']) && seen.add(n['@id'])));
  checkLd(p.path, graph);
  const ld = graph.length ? `\n<script type="application/ld+json">${j({ '@context': 'https://schema.org', '@graph': graph })}</script>` : '';
  return `<title>${esc(p.title)}</title>
<meta name="description" content="${esc(p.desc)}">
<link rel="canonical" href="${url}">
<meta name="author" content="${NAME}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta property="og:site_name" content="${NAME}">
<meta property="og:type" content="${p.ogType || 'website'}">
<meta property="og:title" content="${esc(p.title)}">
<meta property="og:description" content="${esc(p.desc)}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${img}">
<meta property="og:locale" content="en_US">
${p.image && p.image !== '/img/og-card.png' ? '' : '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'}<meta property="og:image:alt" content="${esc(p.imageAlt || 'Samuel Baird: screenshots of Latter-day Stats, Pulpit and the Sacred Sites map')}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(p.title)}">
<meta name="twitter:description" content="${esc(p.desc)}">
<meta name="twitter:image" content="${img}">
<link rel="alternate" type="text/plain" href="/llms.txt" title="LLM-readable summary">
${ANALYTICS}${ld}`;
}

const PAGES = {
  '/': { file: 'index.html', title: `${NAME}: Data Tools and Videos on Religion, History and Ideas`, desc: `${NAME} builds Latter-day Stats (${EXT.lds.channels} LDS YouTube channels, ${EXT.lds.studies} studies), the Deseret Wiki, the Urim translation atlas and AI tools for Latter-day Saint research, and maps ${F.sites} sacred sites he has visited.`,
    ld: (p) => [webPage(p, 'WebPage', { '@id': BASE + '/#webpage', about: PERSON_REF, mainEntity: { '@id': BASE + '/#projects' } }), ...PROJECTS,
      { '@type': 'ItemList', '@id': BASE + '/#projects', name: 'Projects', numberOfItems: FAMILY.length, itemListElement: FAMILY.map((x, i) => ({ '@type': 'ListItem', position: i + 1, item: { '@id': projectNodeId(x) } })) },
      webPage({ path: '/sacred-sites', title: 'Sacred Sites Visited', desc: `Map, photos and statistics of the churches, temples and houses of worship ${NAME} has visited since January 2025.`, image: '/img/sacred-sites-map.webp' }, 'CollectionPage', { breadcrumb: undefined }),
      webPage({ path: '/books', title: 'My Reading', desc: `Books and articles ${NAME} has read, with the date he finished each one.` }, 'CollectionPage', { breadcrumb: undefined }),
      webPage({ path: '/collection', title: 'Collection', desc: `Historical Latter-day Saint books, periodicals and artifacts owned by ${NAME}.` }, 'CollectionPage', { breadcrumb: undefined })] },
  '/about': { title: `About ${NAME}: Creator of Latter-day Stats`, desc: `${NAME} builds public data tools and makes videos about religion, history and ideas. What he has made, how the projects connect, how to cite them and how to get in touch.`,
    ld: (p) => [webPage(p, 'ProfilePage', { mainEntity: PERSON_REF }), crumbs([['Home', '/'], ['About', '/about']])] },
  '/faq': { title: `FAQ: ${NAME}, Latter-day Stats, Pulpit and Sacred Sites`, desc: 'Direct answers: how many LDS YouTube channels are tracked, what Pulpit is, which sacred sites and temples Samuel Baird has visited, what he reads, and how to cite or reuse the data.',
    ld: (p) => [webPage(p, 'FAQPage', { mainEntity: FAQ.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: stripTags(a) } })) }), crumbs([['Home', '/'], ['FAQ', '/faq']])] },
  '/data': { title: 'Open Data: Sacred Sites and Reading Log (CSV, JSON) · Samuel Baird', desc: `Download original datasets under ${LICENSE_NAME}: ${F.sites} sacred sites with coordinates and visit dates, and a ${F.read}-item reading log. CSV and JSON, with field descriptions and a citation.`,
    ld: (p) => [webPage(p, 'CollectionPage', { about: [{ '@id': DATASETS.sites['@id'] }, { '@id': DATASETS.reading['@id'] }, { '@id': DATASETS.temples['@id'] }, { '@id': DATASETS.historic['@id'] }, { '@id': DATASETS.hymns['@id'] }], hasPart: [{ '@id': DATASETS.sites['@id'] }, { '@id': DATASETS.reading['@id'] }, { '@id': DATASETS.temples['@id'] }, { '@id': DATASETS.historic['@id'] }, { '@id': DATASETS.hymns['@id'] }] }), DATASETS.sites, DATASETS.reading, DATASETS.temples, DATASETS.historic, DATASETS.hymns, crumbs([['Home', '/'], ['Open data', '/data']])] },
  '/sacred-sites': { file: 'sacred-sites/index.html', title: `Sacred Sites Visited: Interactive Map of ${F.sites} Churches and Temples · ${NAME}`, desc: `An interactive map of the ${F.sites} churches, temples and houses of worship ${NAME} has visited since January 2025, filterable by tradition, place and year.`, image: '/img/sacred-sites-map.webp', imageAlt: 'Map of sacred sites visited, mostly in Utah',
    ld: (p) => [webPage(p, 'CollectionPage', { about: { '@id': DATASETS.sites['@id'] }, mainEntity: { '@id': BASE + '/sacred-sites/sites#list' } }), DATASETS.sites, sitesList(), ...SITES.map(placeNode), crumbs([['Home', '/'], ['Sacred Sites', '/sacred-sites']])] },
  '/sacred-sites/photos': { file: 'sacred-sites/photos/index.html', title: `Sacred Sites Photos: ${F.photos} Photos of Churches and Temples · ${NAME}`, desc: `${F.photos} photographs from the churches, temples and houses of worship ${NAME} has visited, filterable by tradition, newest first. Free to reuse under ${LICENSE_NAME}.`, image: '/img/sacred-sites-photos.webp', imageAlt: 'Photo gallery of Greek Orthodox church interiors',
    ld: (p) => [webPage(p, 'ImageGallery', { associatedMedia: photoNodes().map((n) => ({ '@id': n['@id'] })) }), ...photoNodes(), ...SITES.filter((s) => (ALL_PHOTOS.some((x) => x.site === s))).map(placeNode), crumbs([['Home', '/'], ['Sacred Sites', '/sacred-sites'], ['Photos', '/sacred-sites/photos']])] },
  '/sacred-sites/traditions': { file: 'sacred-sites/traditions/index.html', title: `Sacred Sites Traditions: ${F.traditions} Traditions Visited · ${NAME}`, desc: `Every faith tradition in the Sacred Sites project, which ones ${NAME} has visited (${F.traditions} so far, across ${F.sites} sites), and the nearest places to Provo, Utah to visit the rest.`, image: '/img/sacred-sites-stats.webp', imageAlt: 'Traditions page for sacred sites visited',
    ld: (p) => [webPage(p, 'WebPage', { about: { '@id': DATASETS.sites['@id'] }, mainEntity: { '@id': DATASETS.sites['@id'] } }), DATASETS.sites, crumbs([['Home', '/'], ['Sacred Sites', '/sacred-sites'], ['Traditions', '/sacred-sites/traditions']])] },
  '/sacred-sites/sites': { title: `Every Sacred Site I've Visited: ${F.sites} Churches, Temples and Houses of Worship`, desc: `A complete directory of the ${F.sites} sacred sites ${NAME} has visited, grouped by tradition, with city, state, number of visits, dates and map links.`, image: '/img/sacred-sites-map.webp',
    ld: (p) => [webPage(p, 'CollectionPage', { about: { '@id': DATASETS.sites['@id'] }, mainEntity: { '@id': BASE + '/sacred-sites/sites#list' } }), DATASETS.sites, sitesList(), ...SITES.map(placeNode), crumbs([['Home', '/'], ['Sacred Sites', '/sacred-sites'], ['Directory', '/sacred-sites/sites']])] },
  '/books': { file: 'books/index.html', title: `My Reading: ${F.books} Books and ${F.articles} Articles Read · ${NAME}`, desc: `${plural(F.books, 'book')} and ${plural(F.articles, 'article')} ${NAME} has read on religion, theology and church history, newest first, with the date he finished each one.`, image: '/img/og-card.png',
    ld: (p) => [webPage(p, 'CollectionPage', { about: { '@id': DATASETS.reading['@id'] }, mainEntity: { '@id': BASE + '/books#list' } }), DATASETS.reading,
      { '@type': 'ItemList', '@id': BASE + '/books#list', name: 'Reading log', numberOfItems: BOOKS.length, itemListElement: BOOKS.map((b, i) => ({ '@type': 'ListItem', position: i + 1, item: bookNode(b, i) })) },
      crumbs([['Home', '/'], ['My Reading', '/books']])] },
  '/temples': { file: 'temples/index.html', title: `Every Latter-day Saint Temple: Map, Status and Dedication Dates (${T.all}) · ${NAME}`, desc: `Map and open dataset of all ${T.all} temples of The Church of Jesus Christ of Latter-day Saints in ${T.countries} countries and territories: ${T.operating} operating, ${T.building} under construction and ${T.announced} announced, with announcement, groundbreaking and dedication dates. CSV and JSON.`,
    ld: (p) => [webPage(p, 'CollectionPage', { about: { '@id': DATASETS.temples['@id'] } }), DATASETS.temples, crumbs([['Home', '/'], ['Temples', '/temples']])] },
  '/historic-sites': { file: 'historic-sites/index.html', title: `Church History Sites: Map of ${H.all} Latter-day Saint Historic Sites · ${NAME}`, desc: `Map and open dataset of the ${H.all} Church history sites, visitors' centers, monuments and museums operated by The Church of Jesus Christ of Latter-day Saints, from Palmyra and Kirtland to Nauvoo, Missouri and the Mormon Trail, with addresses and coordinates. CSV and JSON.`,
    ld: (p) => [webPage(p, 'CollectionPage', { about: { '@id': DATASETS.historic['@id'] } }), DATASETS.historic, crumbs([['Home', '/'], ['Historic sites', '/historic-sites']])] },
  '/hymns': { file: 'hymns/index.html', title: `Latter-day Saint Hymnbooks: Every Hymn in Every Edition, 1835 to Today · ${NAME}`, desc: `Search ${HY.records} records of every hymn in ${HY.editions} Latter-day Saint hymnbooks, from Emma Smith's 1835 collection to Hymns (1985) and Hymns—For Home and Church: numbers, first lines, authors and composers, and which hymns were added or dropped. CSV and JSON.`,
    ld: (p) => [webPage(p, 'CollectionPage', { about: { '@id': DATASETS.hymns['@id'] } }), DATASETS.hymns, crumbs([['Home', '/'], ['Hymns', '/hymns']])] },
  '/collection': { file: 'collection/index.html', title: `Collection: Historic Latter-day Saint Books, Periodicals and Artifacts · ${NAME}`, desc: `Historical Latter-day Saint items owned by ${NAME}, including a first edition of the Deseret First Book (1868), an 1864 Millennial Star and a 1908 Northern States Mission Book of Mormon.`,
    ld: (p) => [webPage(p, 'CollectionPage', { mainEntity: { '@id': BASE + '/collection#items' } }), collectionList(), crumbs([['Home', '/'], ['Collection', '/collection']])] },
  '/wishlist': { title: `Wishlist: Books and Equipment for the Channel · ${NAME}`, desc: `${WISHLIST.length ? plural(WISHLIST.length, 'book and piece of equipment', 'books and pieces of equipment') : 'Books and equipment'} ${NAME} would like for his YouTube channel, most wanted first. Bought through Amazon, shipped directly to him.`,
    ld: (p) => [webPage(p, 'CollectionPage', { mainEntity: { '@id': BASE + '/wishlist#list' } }),
      { '@type': 'ItemList', '@id': BASE + '/wishlist#list', name: 'Wishlist', itemListOrder: 'https://schema.org/ItemListOrderDescending', numberOfItems: WISHLIST.length, itemListElement: WISHLIST.map((w, i) => ({ '@type': 'ListItem', position: i + 1, name: w.title, url: w.link })) },
      crumbs([['Home', '/'], ['Donate', '/donate'], ['Wishlist', '/wishlist']])] },
  '/donate': { file: 'donate/index.html', title: `Donate · ${NAME}`, desc: `Support ${NAME}'s free, independent, ad-free projects and videos with a donation toward hosting, or send books or equipment for the channel from the wishlist.`,
    ld: (p) => [webPage(p, 'WebPage', { potentialAction: [
      { '@type': 'DonateAction', name: 'Donate via PayPal', recipient: PERSON_REF, target: 'https://paypal.me/Baird90' },
      { '@type': 'DonateAction', name: 'Donate via Venmo', recipient: PERSON_REF, target: 'https://venmo.com/Samuel-J-Baird' }] }), crumbs([['Home', '/'], ['Donate', '/donate']])] },
};
const sitesList = () => ({ '@type': 'ItemList', '@id': BASE + '/sacred-sites/sites#list', name: 'Sacred sites visited', numberOfItems: F.sites, itemListElement: SITES.map((s, i) => ({ '@type': 'ListItem', position: i + 1, item: { '@id': placeId(s) } })) });
const seoFor = (path) => { const p = { path, ...PAGES[path] }; if (typeof p.ld === 'function') p.ld = p.ld(p); p.ld = (p.ld || []).filter(Boolean); return seo(p); };

/* ---------- page shell for generated pages ---------- */
const FAVICON = `<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='4' fill='%2316161A'/%3E%3Crect x='5' y='5' width='90' height='90' rx='2' fill='none' stroke='%23BF9A55' stroke-width='3'/%3E%3Ctext x='50' y='67' font-size='46' text-anchor='middle' fill='%23E8DCC0' font-family='Georgia,serif'%3ESB%3C/text%3E%3C/svg%3E">`;
// Shared head links, also stamped into hand-written pages between <!--famhead--> markers.
const FAMHEAD = `${renderHead()}\n${FAVICON}`;
const HEAD_COMMON = `<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#16161A">
<link rel="stylesheet" href="/tokens.css">
<link rel="stylesheet" href="/style.css">
<link rel="stylesheet" href="/bg/bg.css">
<!--famhead-->${FAMHEAD}<!--/famhead-->
<script src="/bg/glyphwind.js" charset="utf-8" defer></script><script src="/bg/bg.js" defer></script>`;
const shell = (path, body, extraHead = '') => `<!doctype html>
<html lang="en">
<head>
${HEAD_COMMON}${extraHead}
<!--seo-->${seoFor(path)}<!--/seo-->
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<!--nav-->${nav(path)}<!--/nav-->
<main id="main" class="rail">
${body}
</main>
<!--foot-->${foot()}<!--/foot-->
<script src="/deseret.js" defer></script>
</body>
</html>
`;
const crumbHtml = (items) => `<nav class="crumbs" aria-label="Breadcrumb">${items.map(([n, u], i) => i === items.length - 1 ? `<span aria-current="page">${n}</span>` : `<a href="${u}">${n}</a>`).join('<span aria-hidden="true">/</span>')}</nav>`;
const pagehead = (crumb, eyebrow, h1, lede) => `<div class="pagehead">
  ${crumbHtml(crumb)}
  <p class="eyebrow small-caps">${eyebrow}</p>
  <h1>${h1}</h1>
  ${lede ? `<p class="lede">${lede}</p>` : ''}
</div>`;


/* ---------- projects: one page per project, from packages/family/projects.json ---------- */
const KIND = { site: 'Website', tool: 'AI tool (MCP server)', page: 'On this site' };
const hostOf = (u) => u.replace(/^https?:\/\//, '').replace(/\/$/, '');
const related = (x) => FAMILY.filter((y) => y.id !== x.id && y.kind !== 'page' && y.topics.some((t) => x.topics.includes(t)));
const projectFaq = (x) => [
  [`What is ${x.name}?`, x.description],
  [`Who made ${x.name}?`, x.role === 'contributor' ? `${x.name} is a Restoration Commons project. ${NAME} is a contributor; see <a href="/about">About</a>.` : `${NAME} built and maintains ${x.name}. It is independent and not affiliated with The Church of Jesus Christ of Latter-day Saints. See <a href="/about">About ${NAME}</a>.`],
  [`Is ${x.name} free?`, `Yes. ${x.name} is free to use, ad-free and needs no account${x.id === 'latter-day-stats' ? ' for browsing' : ''}.`],
  [`Where is ${x.name}?`, `At <a href="${rel(x.url)}">${hostOf(x.url)}</a>.${x.formerUrl ? ` It used to live at ${hostOf(x.formerUrl)}, which now redirects there.` : ''}`],
  ...(x.kind === 'tool' ? [[`How do I use ${x.name} with Claude or another AI assistant?`, `Add it as a custom connector using its MCP endpoint (${esc(x.facts.find((f) => f.startsWith('MCP endpoint') || f.startsWith('One endpoint'))?.replace(/^[^:]+:\s*/, '') || x.url)}). In Claude: Settings, Connectors, Add custom connector.`]] : []),
];
const projectPage = (x) => {
  const path = '/projects/' + x.id;
  const visit = rel(x.url);
  const rels = related(x);
  return shell(path, `${pagehead([['Home', '/'], ['Projects', '/projects'], [x.name, path]], `${KIND[x.kind]}${x.role === 'contributor' ? ' &middot; Contributor' : ''}`, esc(x.name), esc(x.tagline))}
<div class="prose project">
  <p class="visit"><a class="btn" href="${visit}">Visit ${esc(hostOf(x.url))} &rarr;</a></p>
  <h2 id="what">What is ${esc(x.name)}?</h2>
  <p>${esc(x.description)}</p>
  ${x.facts.length ? `<h2 id="facts">At a glance</h2>\n  <ul>${x.facts.map((f) => `<li>${esc(f)}</li>`).join('')}</ul>` : ''}
  ${x.links.length ? `<h2 id="start">Start here</h2>\n  <ul>${x.links.map(([t, u]) => `<li><a href="${rel(x.url) + (u === '/' ? '' : u)}">${esc(t)}</a></li>`).join('')}</ul>` : ''}
  <h2 id="topics">Topics</h2>
  <p class="topics">${x.topics.map((t) => `<span class="smallcaps">${esc(t)}</span>`).join(' ')}</p>
  ${rels.length ? `<h2 id="related">Related projects</h2>\n  <ol class="register">${rels.map((y) => `<li><a class="reg-title" href="/projects/${y.id}">${esc(y.name)}</a><p class="reg-note">${esc(y.tagline)}</p></li>`).join('')}</ol>` : ''}
  <h2 id="questions">Questions</h2>
  <dl class="qa">${projectFaq(x).map(([q, a]) => `<dt>${esc(q)}</dt><dd>${/</.test(a) ? a : esc(a)}</dd>`).join('')}</dl>
  <p class="small">Part of <a href="/projects">${NAME}&rsquo;s projects</a>. Figures dated ${EXT.asOf}.</p>
</div>`);
};
function projectsIndex() {
  return shell('/projects', `${pagehead([['Home', '/'], ['Projects', '/projects']], 'Projects', 'Projects', `Everything ${NAME} has built or contributed to: websites, open data and AI tools for research on religion and Latter-day Saint history. All free and independent.`)}
<div class="prose">
  ${['site', 'tool', 'page'].map((k) => `<h2>${{ site: 'Websites', tool: 'AI tools', page: 'On this site' }[k]}</h2>
  <ol class="register">${FAMILY.filter((x) => x.kind === k).map((x) => `<li id="${x.id}"><a class="reg-title" href="${x.kind === 'page' ? rel(x.url) : '/projects/' + x.id}">${esc(x.name)}</a><p class="reg-note">${esc(x.tagline)}${x.role === 'contributor' ? ' (contributor)' : ''}</p><p class="reg-note"><a href="${rel(x.url)}">${esc(hostOf(x.url))}</a></p></li>`).join('')}</ol>`).join('\n  ')}
</div>`);
}
for (const x of FAMILY.filter((y) => y.kind !== 'page')) {
  PAGES['/projects/' + x.id] = { title: `${x.name}: ${x.tagline.replace(/\.$/, '')} · ${NAME}`, desc: x.description.split('. ').slice(0, 2).join('. ').replace(/\.?$/, '.'),
    ld: (p) => [webPage(p, 'AboutPage', { about: { '@id': projectNodeId(x) }, mainEntity: { '@id': projectNodeId(x) } }), projectNode(x),
      { '@type': 'FAQPage', '@id': BASE + p.path + '#faq', isPartOf: { '@id': BASE + p.path + '#page' }, mainEntity: projectFaq(x).map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: stripTags(a) } })) },
      crumbs([['Home', '/'], ['Projects', '/projects'], [x.name, p.path]])] };
}
PAGES['/projects'] = { title: `Projects by ${NAME}: Latter-day Stats, Deseret Wiki, Urim and More`, desc: `All ${FAMILY.length} projects by ${NAME}: ${FAMILY.map((x) => x.name).join(', ')}. Websites, open data and AI tools for research on religion and Latter-day Saint history.`,
  ld: (p) => [webPage(p, 'CollectionPage', { mainEntity: { '@id': BASE + '/#projects' } }), ...PROJECTS,
    ...FAMILY.filter((x) => x.kind === 'page').map((x) => webPage({ path: x.url.slice(BASE.length), title: x.name, desc: x.description }, 'CollectionPage', { breadcrumb: undefined })),
    { '@type': 'ItemList', '@id': BASE + '/#projects', name: 'Projects', numberOfItems: FAMILY.length, itemListElement: FAMILY.map((x, i) => ({ '@type': 'ListItem', position: i + 1, item: { '@id': projectNodeId(x) } })) },
    crumbs([['Home', '/'], ['Projects', '/projects']])] };
const projectRegister = () => `<ol class="register project-index">${FAMILY.map((x) => `<li><a class="reg-title" href="${x.kind === 'page' ? rel(x.url) : '/projects/' + x.id}">${esc(x.name)}</a><p class="reg-note">${esc(x.tagline)}${x.role === 'contributor' ? ' (contributor)' : ''}</p><p class="reg-note"><a href="${rel(x.url)}">${esc(hostOf(x.url))}</a></p></li>`).join('')}</ol>`;

/* ---------- generated pages ---------- */
function aboutPage() {
  return shell('/about', `${pagehead([['Home', '/'], ['About', '/about']], 'About', `About ${NAME}`, `I build public data tools and make videos about what people believe and why. Everything here is free, independent and ad-free.`)}
<div class="prose">
  <h2>What I make</h2>
  <ul class="plain">
    ${FAMILY.map((x) => `<li><a href="${rel(x.url)}"><b>${esc(x.name)}</b></a>: ${esc(x.tagline)}${x.role === 'contributor' ? ' I contributed to it.' : ''} <a href="/projects/${x.id}">More</a>.</li>`).join('\n    ')}
    <li><a href="${YT}" rel="me noopener"><b>YouTube</b></a> and <a href="${SUBSTACK}" rel="me noopener"><b>Substack</b></a>: videos and written pieces on history, belief and data.</li>
  </ul>
  <h2>How the projects fit together</h2>
  <p>Latter-day Stats answers questions about the Latter-day Saint community with numbers. Pulpit answers questions about what was actually said from the General Conference pulpit. Urim shows how those words are translated, and the Deseret Wiki preserves the alphabet the early Church designed to write them. Peepstone and Deseret MCP let AI assistants search all of it with citations. Sacred Sites Visited is first-hand fieldwork across many traditions, and My Reading and the Collection list the printed sources I read and own. Every project lives at samuelbaird.com or links back to it, shares one design and one menu, and the datasets are published openly on <a href="/data">Open data</a>.</p>
  <h2 id="cite">How to cite</h2>
  <p>Baird, Samuel. &ldquo;Sacred Sites Visited.&rdquo; samuelbaird.com, ${F.firstVisit.slice(0, 4)}&ndash;${F.lastVisit.slice(0, 4)}. <code>${BASE}/data</code><br>For Latter-day Stats, cite the individual study, dataset or graphic page and its stated source. Original data is released under <a href="${LICENSE_URL}" rel="license noopener">${LICENSE_NAME}</a>.</p>
  <h2 id="contact">Contact</h2>
  <p>Questions, corrections, collaboration or press: <a href="mailto:${EMAIL}?subject=Samuel%20Baird">${EMAIL}</a>. Also on <a href="${IG}" rel="me noopener">Instagram</a> and <a href="${GH}" rel="me noopener">GitHub</a>.</p>
  <h2>Corrections</h2>
  <p>If a figure here is wrong, email me and I will fix it. Figures for Latter-day Stats and Pulpit are read from the live sites and dated (last checked ${EXT.asOf}).</p>
</div>`);
}

function faqPage() {
  return shell('/faq', `${pagehead([['Home', '/'], ['FAQ', '/faq']], 'FAQ', 'Questions and direct answers', `Short, sourced answers about ${NAME}, Latter-day Stats, Pulpit and the sacred sites map. Figures are dated; last updated ${longDate(TODAY)}.`)}
<div class="faq">
${FAQ.map(([q, a]) => `<section class="qa" id="${slug(q)}"><h2>${esc(q)}</h2><p>${a}</p></section>`).join('\n')}
</div>`);
}

function dataPage() {
  const fields = (rows) => `<dl class="fields">${rows.map(([k, v]) => `<dt><code>${k}</code></dt><dd>${v}</dd>`).join('')}</dl>`;
  const preview = SITE_ROWS.slice(0, 6);
  return shell('/data', `${pagehead([['Home', '/'], ['Open data', '/data']], 'Open data', 'Original datasets you can download', `Free datasets to download: two first-hand ones under ${LICENSE_NAME}, and compiled lists of every Latter-day Saint temple, Church history site and hymnbook hymn. Updated ${longDate(TODAY)}.`)}
<div class="prose wide">
  <section class="dataset" id="sacred-sites">
    <h2>Sacred sites visited</h2>
    <p>${plural(F.sites, 'site')} in ${plural(F.traditions, 'tradition')}, visited in person between ${longDate(F.firstVisit)} and ${longDate(F.lastVisit)}. Each site is one row; repeat visits are counted in the <code>visits</code> column. Coordinates are approximate building locations.</p>
    <div class="btns"><a class="primary" href="/data/sacred-sites.csv" download>Download CSV</a><a class="secondary" href="/data/sacred-sites.json" download>Download JSON</a><a class="secondary" href="/sacred-sites/sites">Browse as a directory</a></div>
    ${fields([['name', 'Name of the place of worship'], ['tradition', 'Tradition or community, as listed on the map'], ['denomination', 'Short denomination key used in the source data'], ['city, state, country', 'Location'], ['latitude, longitude', 'Decimal degrees (WGS84)'], ['website, wikipedia', 'Official website and English Wikipedia article for the place, blank when none'], ['visits', 'Number of recorded visits'], ['first_visit, last_visit', 'ISO dates (YYYY-MM-DD)'], ['visit_types', 'Attended worship, toured interior, visited grounds or historical site'], ['google_maps', 'Map search link, blank for events held outside a church building or on private property']])}
    <div class="tablewrap"><table class="tbl"><caption>Preview: first ${preview.length} of ${F.sites} rows</caption><thead><tr><th>name</th><th>tradition</th><th>city</th><th>state</th><th>visits</th><th>last_visit</th></tr></thead><tbody>
    ${preview.map((r) => `<tr><td>${esc(r.name)}</td><td>${esc(r.tradition)}</td><td>${esc(r.city)}</td><td>${esc(r.state)}</td><td>${r.visits}</td><td>${r.last_visit}</td></tr>`).join('')}
    </tbody></table></div>
    <p class="note">Maps and photos built from this data: <a href="/sacred-sites">map</a>, <a href="/sacred-sites/photos">photos</a>, <a href="/sacred-sites/traditions">traditions</a>.</p>
  </section>
  <section class="dataset" id="lds-temples">
    <h2>Every Latter-day Saint temple</h2>
    <p>All ${T.all} temples of The Church of Jesus Christ of Latter-day Saints in ${T.countries} countries and territories (${T.operating} operating, ${T.building} under construction, ${T.announced} announced), with coordinates and milestone dates. Facts compiled from the Church&rsquo;s official temple pages; coordinates from Wikidata (CC0) and OpenStreetMap (&copy; OpenStreetMap contributors, ODbL). <code>coordPrecision</code> says whether a location is the temple itself, its address, or only its city or country.</p>
    <div class="btns"><a class="primary" href="/data/lds-temples.csv" download>Download CSV</a><a class="secondary" href="/data/lds-temples.json" download>Download JSON</a><a class="secondary" href="/temples">Map and list</a></div>
    ${fields([['name, status', 'Official temple name; operating, opening-soon, under-construction, under-renovation or announced'], ['city, region, country, address', 'Location as published by the Church'], ['lat, lng, coordPrecision', 'Decimal degrees; precision is site, address, city or country'], ['announced, groundbreaking, dedicated', 'ISO dates (YYYY-MM-DD), blank if not reached'], ['rededicated', 'Semicolon-separated ISO dates'], ['officialUrl, wikidata, wikipedia', 'Links to the official page, Wikidata item and English Wikipedia article']])}
  </section>
  <section class="dataset" id="lds-historic-sites">
    <h2>Church history sites</h2>
    <p>The ${H.all} historic sites, visitors&rsquo; centers, monuments and museums operated by The Church of Jesus Christ of Latter-day Saints (${H.historic} historic sites, ${H.centers} visitors&rsquo; centers and museums, ${H.monuments} monuments), with addresses and coordinates. The list, names, categories and addresses come from the Church&rsquo;s official <a href="https://www.churchofjesuschrist.org/learn/history/sites?lang=eng" rel="noopener">Historic Sites and Museums</a> pages. Coordinates use the Church&rsquo;s published map pins where available, with OpenStreetMap as the fallback (&copy; OpenStreetMap contributors, ODbL). Every record links to its official source.</p>
    <div class="btns"><a class="primary" href="/data/lds-historic-sites.csv" download>Download CSV</a><a class="secondary" href="/data/lds-historic-sites.json" download>Download JSON</a><a class="secondary" href="/historic-sites">Map and list</a></div>
    ${fields([['name, category', 'Official name; Historic site, Visitors&rsquo; center, Monument or Museum (the Church&rsquo;s own label where it gives one)'], ['operator', 'Who runs the site today'], ['area', 'Group of sites on the Church pages (Ohio, Missouri, Illinois&hellip;), blank for stand-alone sites'], ['street, city, region, postalCode, country', 'Physical address as published by the Church'], ['lat, lng, coordPrecision', 'Decimal degrees; precision is site, address, street or city'], ['coordSource', 'church for published map pins, openstreetmap for geocoded locations, or manual for a documented override'], ['officialUrl, source', 'The site&rsquo;s official page, and the official list it appears on'], ['wikidata, wikipedia', 'From the matched OpenStreetMap feature, when it has them']])}
  </section>
  <section class="dataset" id="lds-hymns">
    <h2>Latter-day Saint hymnbooks</h2>
    <p>Every hymn in ${HY.editions} hymnbooks, one record per hymn per edition: ${HYMN_DATA.editions.map((e) => `${esc(e.short)} (${e.hymns}${e.partial ? ' so far' : ''})`).join(', ')}. Numbers, titles, first lines and the text and music credits as printed, with whether each hymn was added, kept or removed from the edition before. The 1835 and 1841 lists come from the <a href="https://www.josephsmithpapers.org/paper-summary/collection-of-sacred-hymns-1835/1" rel="noopener">Joseph Smith Papers</a> transcriptions; Hymns (1985) and Hymns&mdash;For Home and Church from the Church&rsquo;s <a href="https://www.churchofjesuschrist.org/study/manual/hymns?lang=eng" rel="noopener">Gospel Library</a>; authors&rsquo; religion from Wikidata (CC0), only where name and life dates match. Facts only: no lyrics.</p>
    <div class="btns"><a class="primary" href="/data/lds-hymns.csv" download>Download CSV</a><a class="secondary" href="/data/lds-hymns.json" download>Download JSON</a><a class="secondary" href="/hymns">Search the hymns</a></div>
    ${fields([['edition, editionYear, number, section', 'Which book, and the hymn&rsquo;s number and section in it'], ['title, firstLine', 'As printed (1835 and 1841 have no titles)'], ['text, music, tune', 'Credits as printed, without copyright notices'], ['authors, composers', 'Names parsed from the credits (translators and arrangers left out)'], ['yearWritten', 'Year in the text credit, where the book gives one'], ['authorDenomination', 'Authors&rsquo; religion from Wikidata, blank when unknown'], ['hymnKey', 'Links the same text across editions'], ['change, previousNumber', 'added, kept or removed against the previous edition in the dataset, and its number there'], ['source', 'Page the record comes from']])}
  </section>
  <section class="dataset" id="reading-list">
    <h2>Reading log</h2>
    <p>${plural(F.books, 'book')} and ${plural(F.articles, 'article')}, each with the date finished and a link to the source. Newest first.</p>
    <div class="btns"><a class="primary" href="/data/reading-list.csv" download>Download CSV</a><a class="secondary" href="/data/reading-list.json" download>Download JSON</a><a class="secondary" href="/books">Browse with covers</a></div>
    ${fields([['title', 'Title of the book or article'], ['type', '<code>book</code> or <code>article</code>'], ['date_finished', 'ISO date (YYYY-MM-DD)'], ['url', 'Link to the source (book links are Amazon affiliate links)']])}
  </section>
  <section class="dataset" id="more">
    <h2>More data from the network</h2>
    <ul class="plain">
      <li><a href="${LDS}/data-explorer"><b>Latter-day Stats Data Explorer</b></a>: ${EXT.lds.graphics} graphics and public survey datasets (Pew, CCES and others) with downloadable charts.</li>
      <li><a href="${LDS}/studies"><b>Latter-day Stats Studies</b></a>: ${EXT.lds.studies} curated academic studies.</li>
      <li><a href="${LDS}/channels"><b>Latter-day Stats Channels</b></a>: ${EXT.lds.channels} LDS YouTube channels with subscriber counts.</li>
      <li><a href="${PULPIT}/"><b>Pulpit</b></a>: ${EXT.pulpit.discourses.toLocaleString('en-US')} General Conference discourses, each graded for fidelity to the original words.</li>
    </ul>
  </section>
  <section class="dataset" id="cite">
    <h2>License and citation</h2>
    <p>Released under <a href="${LICENSE_URL}" rel="license noopener">${LICENSE_NAME}</a>: share and adapt with attribution. This also covers the <a href="/sacred-sites/photos">sacred sites photographs</a>; credit &ldquo;${NAME}, samuelbaird.com&rdquo;.</p>
    <p><code>Baird, Samuel. &ldquo;Sacred Sites Visited.&rdquo; samuelbaird.com, ${F.firstVisit.slice(0, 4)}&ndash;${F.lastVisit.slice(0, 4)}. ${BASE}/data</code></p>
  </section>
</div>`);
}

function sitesPage() {
  const sections = byTradition.map((t) => `<section class="trad" id="${slug(t.name)}">
  <h2>${esc(t.name)} <small>${plural(t.sites.length, 'site')}</small></h2>
  <ul class="sitelist">
  ${t.sites.map((s) => {
    const d = s.visits.map((v) => v.date).sort();
    const range = d[0] === d[d.length - 1] ? shortDate(d[0]) : `${shortDate(d[0])} to ${shortDate(d[d.length - 1])}`;
    const link = [s.site && `<a href="${esc(s.site)}" rel="noopener">Website</a>`, s.wikiUrl && `<a href="${esc(s.wikiUrl)}" rel="noopener">Wikipedia</a>`, !NO_MAPS.has(s.id) && `<a href="${mapsUrl(s)}" rel="noopener">Map</a>`].filter(Boolean).map((a) => ' ' + a).join('');
    return `<li><b>${esc(s.name)}</b><span>${esc(s.city)}, ${esc(s.state)} &middot; ${plural(s.visits.length, 'visit')} &middot; ${range}${link}</span></li>`;
  }).join('\n  ')}
  </ul></section>`).join('\n');
  return shell('/sacred-sites/sites', `${pagehead([['Home', '/'], ['Sacred Sites', '/sacred-sites'], ['Directory', '/sacred-sites/sites']], 'Directory', `Every sacred site I&rsquo;ve visited`, `${plural(F.sites, 'site')} across ${plural(F.traditions, 'tradition')} since ${longDate(F.firstVisit)}, grouped by tradition. Each site is counted once; most recent visit ${longDate(F.lastVisit)}.`)}
<div class="btns" style="margin:0 0 28px"><a class="primary" href="/sacred-sites">Open the map</a><a class="secondary" href="/sacred-sites/photos">Photos</a><a class="secondary" href="/sacred-sites/traditions">Traditions</a><a class="secondary" href="/data#sacred-sites">Download CSV / JSON</a></div>
<nav class="jump" aria-label="Jump to tradition">${byTradition.map((t) => `<a href="#${slug(t.name)}">${esc(t.name.replace(/ \(.*\)$/, '').replace('The Church of Jesus Christ of Latter-day Saints', 'LDS'))}</a>`).join('')}</nav>
<div class="prose wide">
${sections}
</div>`);
}

function wishlistPage() {
  const card = (w) => `<li>
    <a class="cover" href="${esc(w.link)}" target="_blank" rel="noopener sponsored" tabindex="-1" aria-hidden="true">${w.image ? `<img src="${esc(w.image)}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">` : ''}</a>
    <h3><a href="${esc(w.link)}" target="_blank" rel="noopener sponsored">${esc(w.title)}</a></h3>
    ${w.byline ? `<p class="by">${esc(w.byline)}</p>` : ''}${w.priceText ? `<p class="price">${esc(w.priceText)}</p>` : ''}${w.note ? `<p class="why">${esc(w.note)}</p>` : ''}
  </li>`;
  const tiers = TIERS.map(([k, label]) => [k, label, WISHLIST.filter((w) => w.priority === k)]).filter(([, , l]) => l.length);
  const body = WISHLIST.length
    ? tiers.map(([k, label, list]) => `<section class="wl-tier" id="${k}"><h2>${label} <small>${plural(list.length, 'item')}</small></h2>
<ul class="wl">
  ${list.map(card).join('\n  ')}
</ul></section>`).join('\n')
    : `<p class="wl-empty">The list is syncing from Amazon. In the meantime, <a href="${WL_URL}" target="_blank" rel="noopener">view it on amazon.com</a>.</p>`;
  return shell('/wishlist', `${pagehead([['Home', '/'], ['Donate', '/donate'], ['Wishlist', '/wishlist']], 'Wishlist', 'Books and equipment for the channel', `${WISHLIST.length ? `${plural(WISHLIST.length, 'item')}, most wanted first. ` : ''}Research books and gear that go into making the videos.${WL_UPDATED ? ` Synced from Amazon ${longDate(WL_UPDATED)}.` : ''}`)}
<div class="wl-how">
  <div class="btns"><a class="primary" href="${WL_URL}" target="_blank" rel="noopener">Open the list on Amazon &rarr;</a><a class="secondary" href="/donate">Donate instead</a></div>
  <p class="note disclosure">Buying from these links or the Amazon list ships to me directly and marks the item as bought. Links are Amazon affiliate links; I may earn a commission. Thank you!</p>
</div>
${body}`, '\n<link rel="stylesheet" href="/wishlist/wishlist.css">');
}

/* ---------- marker patching for hand-written pages ---------- */
const region = (html, tag, content) => {
  const re = new RegExp(`<!--${tag}-->[\\s\\S]*?<!--/${tag}-->`);
  if (!re.test(html)) return html;
  return html.replace(re, () => `<!--${tag}-->${content}<!--/${tag}-->`);
};
const patch = (file, path, extra = {}) => {
  let h = read(file);
  const before = h;
  h = region(h, 'seo', seoFor(path));
  h = region(h, 'nav', nav(path));
  h = region(h, 'foot', foot());
  h = region(h, 'famhead', FAMHEAD);
  for (const [tag, content] of Object.entries(extra)) h = region(h, tag, content);
  // numbers that must match the data: <b data-b="sites">34</b>
  h = h.replace(/(<([a-z0-9]+)[^>]*\sdata-b="(\w+)"[^>]*>)[^<]*(<\/\2>)/g, (m, open, t, key, close) => (key in FACT ? open + FACT[key] + close : m));
  if (h !== before) write(file, h);
};

const bookLi = (b) => `<li class="book" data-type="${b.type}"><a href="${esc(b.link)}" target="_blank" rel="noopener${/amazon\./.test(b.link) ? ' sponsored' : ''}">${b.cover ? `<img src="${esc(b.cover)}" alt="Cover of ${esc(b.title)}" loading="lazy" decoding="async">` : '<div class="blank" role="img" aria-label="No cover"></div>'}<h3>${esc(b.title)}</h3><time datetime="${b.read}">${longDate(b.read)}</time></a></li>`;
const coverWall = BOOKS.filter((b) => b.cover).slice(0, 12).map((b) => `<li><a href="/books" title="${esc(b.title)}"><img src="${esc(b.cover)}" alt="Cover of ${esc(b.title)}" loading="lazy" decoding="async"></a></li>`).join('');
const collectionItems = [...read('collection/index.html').matchAll(/<span class="label[^>]*>([^<]*)<\/span>\s*<h2>(.*?)<\/h2>/g)].map((m) => ({ label: m[1].replace(/&middot;/g, '·'), title: m[2] }));
const collectionChips = collectionItems.map((c) => `<li><span class="small-caps">${c.label}</span><b>${c.title}</b></li>`).join('');

/* ---------- 404 ---------- */
function notFoundPage() {
  const html = shell('/404', `${pagehead([['Home', '/']], '404', 'Page not found', 'That page does not exist or has moved. Try one of these instead.')}
<div class="prose"><ul class="plain">${NAV_ITEMS.map(([h, t]) => `<li><a href="${h}">${t}</a></li>`).join('')}</ul></div>`);
  return html.replace(/<!--seo-->[\s\S]*?<!--\/seo-->/, () => `<!--seo--><title>Page not found · ${NAME}</title>\n<meta name="robots" content="noindex,follow">\n<link rel="canonical" href="${BASE}/">\n<!--/seo-->`);
}

/* ---------- run ---------- */
write('404.html', notFoundPage());
write('about/index.html', aboutPage());
write('faq/index.html', faqPage());
write('data/index.html', dataPage());
write('sacred-sites/sites/index.html', sitesPage());
write('wishlist/index.html', wishlistPage());
write('projects/index.html', projectsIndex());
for (const x of FAMILY.filter((y) => y.kind !== 'page')) write(`projects/${x.id}/index.html`, projectPage(x));
write('data/sacred-sites.csv', toCsv(SITE_ROWS));
write('data/sacred-sites.json', JSON.stringify({ name: DATASETS.sites.name, license: LICENSE_URL, source: BASE + '/data', generated: TODAY, records: SITE_ROWS }, null, 2) + '\n');
write('data/reading-list.csv', toCsv(BOOK_ROWS));
write('data/reading-list.json', JSON.stringify({ name: DATASETS.reading.name, license: LICENSE_URL, source: BASE + '/data', generated: TODAY, records: BOOK_ROWS }, null, 2) + '\n');

patch('index.html', '/', { covers: coverWall, 'collection-items': collectionChips, 'project-index': projectRegister() });
patch('books/index.html', '/books', { books: BOOKS.map(bookLi).join('\n') });
patch('collection/index.html', '/collection');
patch('temples/index.html', '/temples', { 'temple-stats': templeStats(), 'temple-decades': templeDecades(), 'temple-rows': TEMPLES.map(templeRow).join('\n') });
patch('historic-sites/index.html', '/historic-sites', { 'hist-stats': histStats(), 'hist-rows': HIST.map(histRow).join('\n') });
patch('hymns/index.html', '/hymns', { 'hymn-stats': hymnStats(), 'hymn-rows': hymnRows() });
patch('donate/index.html', '/donate');
patch('sacred-sites/index.html', '/sacred-sites');
patch('sacred-sites/photos/index.html', '/sacred-sites/photos');
patch('sacred-sites/traditions/index.html', '/sacred-sites/traditions');

// robots.txt: allow everything, and say so explicitly for the crawlers that feed AI search and assistants.
const BOTS = ['Googlebot', 'Bingbot', 'GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-User', 'Claude-SearchBot', 'anthropic-ai', 'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Applebot', 'Applebot-Extended', 'DuckAssistBot', 'Amazonbot', 'MistralAI-User', 'cohere-ai', 'Meta-ExternalAgent', 'CCBot', 'YouBot'];
// Apps served under samuelbaird.com/<project> can only be steered from here (robots.txt is per host).
const DISALLOW = FAMILY.filter((x) => x.basePath).flatMap((x) => (x.privatePaths || []).map((q) => `Disallow: ${x.basePath}${q}\n`)).join('');
write('robots.txt', `# ${BASE}: all crawlers welcome, including search and AI assistants. Please attribute and link back.
${BOTS.map((b) => `User-agent: ${b}\nAllow: /\n${DISALLOW}`).join('\n')}
User-agent: *
Allow: /
${DISALLOW}
Sitemap: ${BASE}/sitemap.xml
${FAMILY.filter((x) => x.basePath && x.sitemap).map((x) => `Sitemap: ${x.url}${x.sitemap}\n`).join('')}`);

// sitemap.xml
const urls = [['/', 1.0, 'weekly'], ['/projects', 0.9, 'weekly'], ...FAMILY.filter((x) => x.kind !== 'page').map((x) => ['/projects/' + x.id, 0.8, 'monthly']), ['/about', 0.8, 'monthly'], ['/faq', 0.9, 'weekly'], ['/data', 0.9, 'weekly'], ['/sacred-sites', 0.8, 'weekly'], ['/sacred-sites/sites', 0.8, 'weekly'], ['/sacred-sites/photos', 0.6, 'weekly'], ['/sacred-sites/traditions', 0.6, 'weekly'], ['/books', 0.7, 'weekly'], ['/collection', 0.6, 'monthly'], ['/temples', 0.9, 'weekly'], ['/data/lds-temples.csv', 0.4, 'weekly'], ['/data/lds-temples.json', 0.4, 'weekly'], ['/historic-sites', 0.8, 'monthly'], ['/data/lds-historic-sites.csv', 0.4, 'monthly'], ['/data/lds-historic-sites.json', 0.4, 'monthly'], ['/hymns', 0.8, 'monthly'], ['/data/lds-hymns.csv', 0.4, 'monthly'], ['/data/lds-hymns.json', 0.4, 'monthly'], ['/donate', 0.3, 'yearly'], ['/wishlist', 0.3, 'weekly'], ['/data/sacred-sites.csv', 0.4, 'weekly'], ['/data/sacred-sites.json', 0.4, 'weekly'], ['/data/reading-list.csv', 0.4, 'weekly'], ['/data/reading-list.json', 0.4, 'weekly'], ['/llms.txt', 0.3, 'monthly']];
write('sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(([u, pr, cf]) => `  <url><loc>${BASE}${u === '/' ? '/' : u}</loc><lastmod>${TODAY}</lastmod><changefreq>${cf}</changefreq><priority>${pr.toFixed(1)}</priority></url>`).join('\n')}
</urlset>
`);

// llms.txt (llmstxt.org) and llms-full.txt
write('llms.txt', `# ${NAME}

> ${NAME} builds public data tools and makes videos about religion, history and ideas. He created Latter-day Stats (statistics, research and creator data on the Latter-day Saint community), contributed to Pulpit (every General Conference discourse since 1830), and keeps a map of ${F.sites} sacred sites he has visited. Everything is free, independent and ad-free. Original data is ${LICENSE_NAME}: attribute and link to ${BASE}.

Figures for external sites are dated ${EXT.asOf}.

## Projects
All projects: [${BASE}/projects](${BASE}/projects). Every project except the Deseret Wiki lives at ${BASE}/<project>.

${FAMILY.map((x) => `- [${x.name}](${x.url}${x.kind === 'page' ? '' : '/'}): ${x.tagline}${x.role === 'contributor' ? ' Samuel Baird is a contributor.' : ''}${x.kind === 'page' ? '' : ` [About](${BASE}/projects/${x.id})`}${x.facts.length ? '\n' + x.facts.map((f) => `  - ${f}`).join('\n') : ''}${x.links.length ? '\n' + x.links.map(([t, u]) => `  - [${t}](${x.url}${u === '/' ? '/' : u})`).join('\n') : ''}`).join('\n')}
  - Sacred sites: [directory of every site](${BASE}/sacred-sites/sites), [photos](${BASE}/sacred-sites/photos) and [traditions](${BASE}/sacred-sites/traditions).
- [Wishlist](${BASE}/wishlist): books and equipment he would like for the YouTube channel, most wanted first.

## Answers and data
- [FAQ](${BASE}/faq): direct answers with dated figures.
- [Open data](${BASE}/data): CSV and JSON downloads, field descriptions, license and citation.
  - [sacred-sites.csv](${BASE}/data/sacred-sites.csv), [sacred-sites.json](${BASE}/data/sacred-sites.json)
  - [reading-list.csv](${BASE}/data/reading-list.csv), [reading-list.json](${BASE}/data/reading-list.json)
- [About](${BASE}/about): who he is, how the projects connect, how to cite.

## Elsewhere
- [YouTube @ithinkthereforeisam](${YT})
- [Substack](${SUBSTACK})
- [GitHub](${GH})
- Contact: ${EMAIL}

## Optional
- [Full text version of this site](${BASE}/llms-full.txt)
- [Sitemap](${BASE}/sitemap.xml)
`);

const md = (h) => stripTags(h.replace(/<a [^>]*href="([^"]+)"[^>]*>(.*?)<\/a>/g, (m, u, t) => `[${stripTags(t)}](${u.startsWith('/') ? BASE + u : u})`));
write('llms-full.txt', `# ${NAME}: full text

> Plain-text copy of the key pages of ${BASE}. Updated ${TODAY}. Original data licensed ${LICENSE_NAME}.

## Projects

${FAMILY.map((x) => `### ${x.name}\n\n${x.url}${x.kind === 'page' ? '' : '/'}${x.role === 'contributor' ? ' (Samuel Baird is a contributor)' : ''}\n\n${x.description}${x.facts.length ? '\n\n' + x.facts.map((f) => `- ${f}`).join('\n') : ''}\n\nTopics: ${x.topics.join(', ')}.`).join('\n\n')}

## FAQ

${FAQ.map(([q, a]) => `### ${q}\n\n${md(a)}`).join('\n\n')}

## Sacred sites visited (${F.sites} sites, ${F.traditions} traditions, ${longDate(F.firstVisit)} to ${longDate(F.lastVisit)})

${byTradition.map((t) => `### ${t.name} (${t.sites.length})\n\n${t.sites.map((s) => { const d = s.visits.map((v) => v.date).sort(); return `- ${s.name}, ${s.city}, ${s.state}: ${plural(s.visits.length, 'visit')}, ${d[0]}${d[0] === d[d.length - 1] ? '' : ' to ' + d[d.length - 1]}`; }).join('\n')}`).join('\n\n')}

## Reading log (${F.books} books, ${F.articles} articles; newest first)

${BOOKS.map((b) => `- ${b.read}: ${b.title} (${b.type})`).join('\n')}

## Collection

${collectionItems.map((c) => `- ${c.title.replace(/&rsquo;/g, "'").replace(/&ndash;/g, '-').replace(/&amp;/g, '&')} (${c.label})`).join('\n')}
`);

// Deseret title reveal: every word in a page title needs a phonetic entry in /deseret.js.
{
  const { pageTitles, readTable, WORD_RE, wordKey } = await import('./deseret-words.mjs');
  const table = readTable();
  const gaps = pageTitles().flatMap((t) => (t.text.match(WORD_RE) || []).filter((w) => !table[wordKey(w)]).map((w) => `${w} (${t.file})`));
  if (gaps.length) console.warn(`deseret.js has no entry for: ${gaps.join(', ')}. Run node scripts/deseret-words.mjs.`);
}

console.log(`built: ${F.sites} sites, ${F.traditions} traditions, ${F.read} reading items, ${F.ldsTemples} LDS temples, ${F.photos} photos`);
