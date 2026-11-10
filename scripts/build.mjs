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
const LDS = 'https://latterdaystats.samuelbaird.com';
const PULPIT = 'https://pulpit.restorationcommons.org';
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
const AFFILIATE_TAG = 'ithinkthereforeisam-20';
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
const nav = (p) => {
  const links = NAV_ITEMS.map(([h, t]) => `<a href="${h}"${h.split('#')[0] === p && !h.includes('#') || (h === '/sacred-sites' && p.startsWith('/sacred-sites')) ? ' aria-current="page"' : ''}>${t}</a>`).join('');
  return `<div class="netbar"><div class="rail"><span>Also by ${NAME}</span><a href="${LDS}/">Latter-day Stats</a><a href="${PULPIT}/">Pulpit</a><a href="${YT}" rel="me noopener">YouTube</a><a href="${SUBSTACK}" rel="me noopener">Substack</a></div></div>
<header class="topbar"><div class="rail">
  <a class="wordmark" href="/" aria-label="${NAME}, home"><span class="mono" aria-hidden="true">SB</span>${NAME}</a>
  <nav class="nav" aria-label="Main">${links}<a class="nav-cta" href="/donate"${p === '/donate' ? ' aria-current="page"' : ''}>Donate</a></nav>
</div></header>`;
};
const foot = () => `<footer class="sitefoot"><div class="rail">
  <div class="cols">
    <div><h2 class="small-caps">Projects</h2><ul>
      <li><a href="${LDS}/">Latter-day Stats</a></li><li><a href="${PULPIT}/">Pulpit</a> <small>(contributor)</small></li>
      <li><a href="/sacred-sites">Sacred Sites Visited</a></li><li><a href="/books">My Reading</a></li><li><a href="/collection">Collection</a></li></ul></div>
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
  <p class="legal">&copy; ${YEAR} ${NAME}. Free, independent and ad-free. Original data on this site is released under <a href="${LICENSE_URL}" rel="license noopener">${LICENSE_NAME}</a>.</p>
</div></footer>`;

/* ---------- structured data ---------- */
const PERSON = {
  '@type': 'Person', '@id': BASE + '/#person', name: NAME, url: BASE + '/', sameAs: SAMEAS,
  description: 'Builds public data tools and makes videos about religion, history and ideas. Creator of Latter-day Stats, contributor to Pulpit, and keeper of the Sacred Sites Visited map.',
  knowsAbout: ['Latter-day Saint history', 'Religious demographics', 'Survey data', 'General Conference', 'Comparative religion', 'Data visualization'],
  email: 'mailto:' + EMAIL,
};
const WEBSITE = { '@type': 'WebSite', '@id': BASE + '/#website', url: BASE + '/', name: NAME, description: 'Data tools and videos about religion, history and ideas.', inLanguage: 'en', publisher: { '@id': BASE + '/#person' }, license: LICENSE_URL };
const PROJECTS = [
  { '@type': 'WebSite', '@id': LDS + '/#website', name: 'Latter-day Stats', url: LDS + '/', description: 'A public, independent hub for statistics, research and creator data on the Latter-day Saint community.', creator: { '@id': BASE + '/#person' } },
  { '@type': 'WebSite', '@id': PULPIT + '/#website', name: 'Pulpit', url: PULPIT + '/', description: 'Every General Conference discourse since 1830, each traced to its best surviving witness and graded for fidelity. A Restoration Commons project.', contributor: { '@id': BASE + '/#person' } },
];
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
  ['Who is Samuel Baird?', `Samuel Baird builds public data tools and makes videos about religion, history and ideas. He created <a href="${LDS}/">Latter-day Stats</a>, a public hub for statistics, research and creator data on the Latter-day Saint community; he contributed to <a href="${PULPIT}/">Pulpit</a>, a critical edition of every General Conference discourse since 1830; he keeps a map of the sacred places he has visited; and he makes videos on the YouTube channel <a href="${YT}" rel="me noopener">@ithinkthereforeisam</a>. Everything is free, independent and ad-free. See <a href="/about">About</a>.`],
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
<link rel="alternate" type="text/plain" href="/llms.txt" title="LLM-readable summary">${ld}`;
}

const PAGES = {
  '/': { file: 'index.html', title: `${NAME}: Data Tools and Videos on Religion, History and Ideas`, desc: `${NAME} builds Latter-day Stats (${EXT.lds.channels} LDS YouTube channels, ${EXT.lds.studies} studies), contributed to Pulpit (every General Conference talk since 1830), and maps ${F.sites} sacred sites he has visited. See the projects.`,
    ld: (p) => [webPage(p, 'WebPage', { '@id': BASE + '/#webpage', about: PERSON_REF, mainEntity: { '@id': BASE + '/#projects' } }), ...PROJECTS,
      { '@type': 'ItemList', '@id': BASE + '/#projects', name: 'Projects', numberOfItems: 5, itemListElement: [
        { '@type': 'ListItem', position: 1, item: { '@id': LDS + '/#website' } }, { '@type': 'ListItem', position: 2, item: { '@id': PULPIT + '/#website' } },
        { '@type': 'ListItem', position: 3, item: { '@id': pageId('/sacred-sites') } }, { '@type': 'ListItem', position: 4, item: { '@id': pageId('/books') } },
        { '@type': 'ListItem', position: 5, item: { '@id': pageId('/collection') } }] },
      webPage({ path: '/sacred-sites', title: 'Sacred Sites Visited', desc: `Map, photos and statistics of the churches, temples and houses of worship ${NAME} has visited since January 2025.`, image: '/img/sacred-sites-map.webp' }, 'CollectionPage', { breadcrumb: undefined }),
      webPage({ path: '/books', title: 'My Reading', desc: `Books and articles ${NAME} has read, with the date he finished each one.` }, 'CollectionPage', { breadcrumb: undefined }),
      webPage({ path: '/collection', title: 'Collection', desc: `Historical Latter-day Saint books, periodicals and artifacts owned by ${NAME}.` }, 'CollectionPage', { breadcrumb: undefined })] },
  '/about': { title: `About ${NAME}: Creator of Latter-day Stats`, desc: `${NAME} builds public data tools and makes videos about religion, history and ideas. What he has made, how the projects connect, how to cite them and how to get in touch.`,
    ld: (p) => [webPage(p, 'ProfilePage', { mainEntity: PERSON_REF }), crumbs([['Home', '/'], ['About', '/about']])] },
  '/faq': { title: `FAQ: ${NAME}, Latter-day Stats, Pulpit and Sacred Sites`, desc: 'Direct answers: how many LDS YouTube channels are tracked, what Pulpit is, which sacred sites and temples Samuel Baird has visited, what he reads, and how to cite or reuse the data.',
    ld: (p) => [webPage(p, 'FAQPage', { mainEntity: FAQ.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: stripTags(a) } })) }), crumbs([['Home', '/'], ['FAQ', '/faq']])] },
  '/data': { title: 'Open Data: Sacred Sites and Reading Log (CSV, JSON) · Samuel Baird', desc: `Download original datasets under ${LICENSE_NAME}: ${F.sites} sacred sites with coordinates and visit dates, and a ${F.read}-item reading log. CSV and JSON, with field descriptions and a citation.`,
    ld: (p) => [webPage(p, 'CollectionPage', { about: [{ '@id': DATASETS.sites['@id'] }, { '@id': DATASETS.reading['@id'] }], hasPart: [{ '@id': DATASETS.sites['@id'] }, { '@id': DATASETS.reading['@id'] }] }), DATASETS.sites, DATASETS.reading, crumbs([['Home', '/'], ['Open data', '/data']])] },
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
const HEAD_COMMON = `<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0f1115">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='6' fill='%230f1115'/%3E%3Crect x='4' y='4' width='92' height='92' rx='4' fill='none' stroke='%23d9a441' stroke-width='3'/%3E%3Ctext x='50' y='66' font-size='46' text-anchor='middle' fill='%23d9a441' font-family='Georgia,serif' font-weight='600'%3ESB%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="/tokens.css">
<link rel="stylesheet" href="/style.css">
<link rel="stylesheet" href="/bg/bg.css">
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

/* ---------- generated pages ---------- */
function aboutPage() {
  return shell('/about', `${pagehead([['Home', '/'], ['About', '/about']], 'About', `About ${NAME}`, `I build public data tools and make videos about what people believe and why. Everything here is free, independent and ad-free.`)}
<div class="prose">
  <h2>What I make</h2>
  <ul class="plain">
    <li><a href="${LDS}/"><b>Latter-day Stats</b></a>: a public hub for statistics, research and creator data on the Latter-day Saint community. As of ${EXT.asOf} it tracks ${EXT.lds.channels} YouTube channels (${EXT.lds.subs} combined subscribers), ${EXT.lds.studies} studies and ${EXT.lds.graphics} survey graphics.</li>
    <li><a href="${PULPIT}/"><b>Pulpit</b></a>: a Restoration Commons critical edition of all ${EXT.pulpit.discourses.toLocaleString('en-US')} General Conference discourses since 1830, each traced to its best surviving witness. I contributed to it.</li>
    <li><a href="/sacred-sites"><b>Sacred Sites Visited</b></a>: a map, photo gallery and statistics of the ${F.sites} places of worship I have visited in person since January 2025, across ${F.traditions} traditions.</li>
    <li><a href="/books"><b>My Reading</b></a>: ${plural(F.books, 'book')} and ${plural(F.articles, 'article')} with the date I finished each.</li>
    <li><a href="/collection"><b>Collection</b></a>: historic Latter-day Saint books, periodicals and artifacts I own.</li>
    <li><a href="${YT}" rel="me noopener"><b>YouTube</b></a> and <a href="${SUBSTACK}" rel="me noopener"><b>Substack</b></a>: videos and written pieces on history, belief and data.</li>
  </ul>
  <h2>How the projects fit together</h2>
  <p>Latter-day Stats answers questions about the Latter-day Saint community with numbers. Pulpit answers questions about what was actually said from the General Conference pulpit. Sacred Sites Visited is first-hand fieldwork across many traditions, and My Reading and the Collection list the printed sources I read and own. Each site links to the others, and the datasets are published openly on <a href="/data">Open data</a>.</p>
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
  return shell('/data', `${pagehead([['Home', '/'], ['Open data', '/data']], 'Open data', 'Original datasets you can download', `Two small first-hand datasets, free to reuse under ${LICENSE_NAME}. Updated ${longDate(TODAY)}.`)}
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
write('data/sacred-sites.csv', toCsv(SITE_ROWS));
write('data/sacred-sites.json', JSON.stringify({ name: DATASETS.sites.name, license: LICENSE_URL, source: BASE + '/data', generated: TODAY, records: SITE_ROWS }, null, 2) + '\n');
write('data/reading-list.csv', toCsv(BOOK_ROWS));
write('data/reading-list.json', JSON.stringify({ name: DATASETS.reading.name, license: LICENSE_URL, source: BASE + '/data', generated: TODAY, records: BOOK_ROWS }, null, 2) + '\n');

patch('index.html', '/', { covers: coverWall, 'collection-items': collectionChips });
patch('books/index.html', '/books', { books: BOOKS.map(bookLi).join('\n') });
patch('collection/index.html', '/collection');
patch('donate/index.html', '/donate');
patch('sacred-sites/index.html', '/sacred-sites');
patch('sacred-sites/photos/index.html', '/sacred-sites/photos');
patch('sacred-sites/traditions/index.html', '/sacred-sites/traditions');

// robots.txt: allow everything, and say so explicitly for the crawlers that feed AI search and assistants.
const BOTS = ['Googlebot', 'Bingbot', 'GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-User', 'Claude-SearchBot', 'anthropic-ai', 'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Applebot', 'Applebot-Extended', 'DuckAssistBot', 'Amazonbot', 'MistralAI-User', 'cohere-ai', 'Meta-ExternalAgent', 'CCBot', 'YouBot'];
write('robots.txt', `# ${BASE}: all crawlers welcome, including search and AI assistants. Please attribute and link back.
${BOTS.map((b) => `User-agent: ${b}\nAllow: /\n`).join('\n')}
User-agent: *
Allow: /

Sitemap: ${BASE}/sitemap.xml
`);

// sitemap.xml
const urls = [['/', 1.0, 'weekly'], ['/about', 0.8, 'monthly'], ['/faq', 0.9, 'weekly'], ['/data', 0.9, 'weekly'], ['/sacred-sites', 0.8, 'weekly'], ['/sacred-sites/sites', 0.8, 'weekly'], ['/sacred-sites/photos', 0.6, 'weekly'], ['/sacred-sites/traditions', 0.6, 'weekly'], ['/books', 0.7, 'weekly'], ['/collection', 0.6, 'monthly'], ['/donate', 0.3, 'yearly'], ['/wishlist', 0.3, 'weekly'], ['/data/sacred-sites.csv', 0.4, 'weekly'], ['/data/sacred-sites.json', 0.4, 'weekly'], ['/data/reading-list.csv', 0.4, 'weekly'], ['/data/reading-list.json', 0.4, 'weekly'], ['/llms.txt', 0.3, 'monthly']];
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
- [Latter-day Stats](${LDS}/): ${EXT.lds.channels} LDS YouTube channels (${EXT.lds.subs} combined subscribers), ${EXT.lds.studies} studies, ${EXT.lds.graphics} survey graphics.
  - [Data Explorer](${LDS}/data-explorer): public survey datasets (Pew, CCES and others) with charts.
  - [Studies](${LDS}/studies): curated academic research library.
  - [Channels](${LDS}/channels): directory of LDS YouTube creators.
- [Pulpit](${PULPIT}/): ${EXT.pulpit.discourses.toLocaleString('en-US')} General Conference discourses since 1830, each traced to its best surviving witness and graded for fidelity. A Restoration Commons project Samuel Baird contributed to.
- [Sacred Sites Visited](${BASE}/sacred-sites): interactive map of ${F.sites} churches, temples and houses of worship visited since January 2025.
  - [Directory of every site](${BASE}/sacred-sites/sites): grouped by tradition, with dates and map links.
  - [Photos](${BASE}/sacred-sites/photos) and [Traditions](${BASE}/sacred-sites/traditions).
- [My Reading](${BASE}/books): ${F.books} books and ${F.articles} articles with the date finished.
- [Collection](${BASE}/collection): historic Latter-day Saint books, periodicals and artifacts.
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

## FAQ

${FAQ.map(([q, a]) => `### ${q}\n\n${md(a)}`).join('\n\n')}

## Sacred sites visited (${F.sites} sites, ${F.traditions} traditions, ${longDate(F.firstVisit)} to ${longDate(F.lastVisit)})

${byTradition.map((t) => `### ${t.name} (${t.sites.length})\n\n${t.sites.map((s) => { const d = s.visits.map((v) => v.date).sort(); return `- ${s.name}, ${s.city}, ${s.state}: ${plural(s.visits.length, 'visit')}, ${d[0]}${d[0] === d[d.length - 1] ? '' : ' to ' + d[d.length - 1]}`; }).join('\n')}`).join('\n\n')}

## Reading log (${F.books} books, ${F.articles} articles; newest first)

${BOOKS.map((b) => `- ${b.read}: ${b.title} (${b.type})`).join('\n')}

## Collection

${collectionItems.map((c) => `- ${c.title.replace(/&rsquo;/g, "'").replace(/&ndash;/g, '-').replace(/&amp;/g, '&')} (${c.label})`).join('\n')}
`);

console.log(`built: ${F.sites} sites, ${F.traditions} traditions, ${F.read} reading items, ${F.ldsTemples} LDS temples, ${F.photos} photos`);
