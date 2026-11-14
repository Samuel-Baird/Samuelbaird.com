// Sync the public Amazon wishlist into wishlist/data.json. Run: node scripts/fetch-wishlist.mjs
// - Reads the list's public "list view" page and follows its "show more" pagination.
// - Only rewrites data.json when the items actually changed, so scheduled runs make no empty commits.
// - Refuses to overwrite good data with an empty result. Pass --allow-empty if the list really is empty now.
// - Amazon sometimes serves a CAPTCHA to bots. If it still does after retries, the run keeps the
//   current data.json and exits 0 with a warning (the next scheduled run tries again); it only fails
//   when there is no data on file yet.
// No dependencies. Runs on a schedule in .github/workflows/wishlist.yml; also safe to run by hand.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const LIST_ID = process.env.WISHLIST_ID || '3ECBMMP7G2LZ4';
const ORIGIN = 'https://www.amazon.com';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(ROOT, 'wishlist', 'data.json');
const MAX_PAGES = 40;
const ALLOW_EMPTY = process.argv.includes('--allow-empty');
// --file <path> parses a saved copy of the page instead of fetching (for testing the parser).
const FILE = process.argv.includes('--file') ? process.argv[process.argv.indexOf('--file') + 1] : null;

const HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en-US,en;q=0.9',
};

const decode = (s) => String(s ?? '')
  .replace(/<[^>]+>/g, '')
  .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
  .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(+d))
  .replace(/&nbsp;/g, ' ').replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&')
  .replace(/\s+/g, ' ').trim();
const attr = (tag, name) => { const m = tag.match(new RegExp(`\\s${name}\\s*=\\s*(["'])([\\s\\S]*?)\\1`, 'i')); return m ? m[2] : null; };
// Inner HTML of the first element whose id is `${prefix}${itemId}` (Amazon keys every field this way).
const byId = (html, id) => {
  const m = html.match(new RegExp(`<([a-z0-9]+)[^>]*\\sid=["']${id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}["'][^>]*>([\\s\\S]*?)</\\1>`, 'i'));
  return m ? m[2] : null;
};
const openTagById = (html, id) => (html.match(new RegExp(`<[a-z0-9]+[^>]*\\sid=["']${id}["'][^>]*>`, 'i')) || [])[0] || null;

const PRIORITY_BY_NUM = { 2: 'highest', 1: 'high', 0: 'medium', '-1': 'low', '-2': 'lowest' };
const parsePriority = (block, id) => {
  const label = decode(byId(block, 'itemPriorityLabel_' + id) || '').toLowerCase().match(/\b(highest|high|medium|low|lowest)\b/);
  if (label) return label[1];
  const num = decode(byId(block, 'itemPriority_' + id) || '');
  return PRIORITY_BY_NUM[num] || null;
};
const parseDate = (s) => {
  const m = decode(s).match(/([A-Z][a-z]+ \d{1,2}, \d{4})/);
  if (!m) return null;
  const d = new Date(m[1] + ' 12:00 UTC');
  return Number.isNaN(+d) ? null : d.toISOString().slice(0, 10);
};
const bigImage = (src) => src && src.replace(/\._[^/]*?_\.(jpe?g|png|webp)$/i, '._SL500_.$1');

function parseItems(html) {
  // Each wishlist entry is an <li ... data-itemId="I..."> element.
  const starts = [...html.matchAll(/<li\b[^>]*\bdata-itemid=["']([A-Z0-9]+)["'][^>]*>/gi)];
  return starts.map((m, i) => {
    const id = m[1];
    const tag = m[0];
    const block = html.slice(m.index, i + 1 < starts.length ? starts[i + 1].index : undefined);
    const nameTag = openTagById(block, 'itemName_' + id);
    const href = nameTag ? decode(attr(nameTag, 'href')) : '';
    const params = decode(attr(tag, 'data-reposition-action-params') || '');
    const asin = (params.match(/ASIN:([A-Z0-9]{10})/) || href.match(/\/dp\/([A-Z0-9]{10})/) || [])[1] || null;
    const imgBlock = byId(block, 'itemImage_' + id) || '';
    const imgTag = (imgBlock.match(/<img\b[^>]*>/i) || [])[0];
    const priceBlock = byId(block, 'itemPrice_' + id) || '';
    const priceText = decode((priceBlock.match(/class=["'][^"']*a-offscreen[^"']*["'][^>]*>([^<]*)</) || [])[1] || '') || null;
    const dataPrice = parseFloat(attr(tag, 'data-price'));
    const price = Number.isFinite(dataPrice) && dataPrice > 0 ? dataPrice
      : priceText ? parseFloat(priceText.replace(/[^0-9.]/g, '')) || null : null;
    const num = (pfx) => { const v = parseInt(decode(byId(block, pfx + id) || ''), 10); return Number.isFinite(v) ? v : null; };
    return {
      itemId: id,
      asin,
      title: decode(nameTag ? attr(nameTag, 'title') || byId(block, 'itemName_' + id) : '') || null,
      byline: decode(byId(block, 'item-byline-' + id) || '').replace(/^by\s+/i, '') || null,
      price,
      priceText: priceText || (price ? `$${price.toFixed(2)}` : null),
      image: bigImage(imgTag ? attr(imgTag, 'src') : null),
      amazonPriority: parsePriority(block, id),
      comment: decode(byId(block, 'itemComment_' + id) || '') || null,
      requested: num('itemRequested_'),
      purchased: num('itemPurchased_'),
      added: parseDate(byId(block, 'itemAddedDate_' + id) || ''),
      href: href ? new URL(href, ORIGIN).href : null,
    };
  }).filter((x) => x.title);
}

const nextUrl = (html) => {
  const tag = (html.match(/<input\b[^>]*\bname=["']showMoreUrl["'][^>]*>/i) || [])[0];
  const v = tag && decode(attr(tag, 'value'));
  return v ? new URL(v, ORIGIN).href : null;
};

class BlockedError extends Error {}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
// Pause between pages, with jitter, so the crawl looks less like a bot burst.
const PAGE_DELAY_MS = 1500;

async function get(url) {
  for (let attempt = 1; ; attempt++) {
    const res = await fetch(url, { headers: HEADERS, redirect: 'follow' });
    const body = await res.text();
    const blocked = /captcha|Type the characters you see|api-services-support@amazon\.com/i.test(body);
    if (res.ok && !blocked) return body;
    if (attempt >= 4) {
      const msg = `${url}: ${blocked ? 'Amazon served a CAPTCHA / bot check' : 'HTTP ' + res.status}`;
      throw blocked || res.status === 503 ? new BlockedError(msg) : new Error(msg);
    }
    await sleep(2000 * 2 ** attempt + Math.random() * 2000);
  }
}

async function main() {
  const listUrl = `${ORIGIN}/hz/wishlist/ls/${LIST_ID}?viewType=list&filter=unpurchased&sort=default`;
  let html = FILE ? fs.readFileSync(FILE, 'utf8') : await get(listUrl);
  const name = decode(byId(html, 'profile-list-name') || '') || null;
  const seen = new Map();
  for (let page = 1; ; page++) {
    for (const it of parseItems(html)) if (!seen.has(it.itemId)) seen.set(it.itemId, it);
    const next = FILE ? null : nextUrl(html);
    if (!next || page >= MAX_PAGES || /id=["']endOfListMarker["']/.test(html)) break;
    await sleep(PAGE_DELAY_MS + Math.random() * PAGE_DELAY_MS);
    html = await get(next);
  }
  // Drop items that are fully bought (Amazon's "unpurchased" filter normally already does this).
  const items = [...seen.values()].filter((x) => !(x.requested && x.purchased != null && x.purchased >= x.requested));

  const prev = fs.existsSync(OUT) ? JSON.parse(fs.readFileSync(OUT, 'utf8')) : null;
  if (!items.length && !ALLOW_EMPTY && prev?.items?.length) {
    console.error(`Parsed 0 items but ${prev.items.length} are on file; leaving data.json alone (rerun with --allow-empty if the list is really empty).`);
    process.exit(1);
  }
  const data = { list: LIST_ID, name: name || prev?.name || null, url: `${ORIGIN}/hz/wishlist/ls/${LIST_ID}`, items };
  if (prev && JSON.stringify({ ...prev, updated: undefined }) === JSON.stringify({ ...data, updated: undefined })) {
    console.log(`wishlist unchanged (${items.length} items)`);
    return;
  }
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify({ ...data, updated: new Date().toISOString() }, null, 2) + '\n');
  console.log(`wishlist updated: ${items.length} items${prev ? ` (was ${prev.items.length})` : ''}`);
}

main().catch((e) => {
  // Blocked by Amazon but we already have data: keep it and let the next scheduled run retry.
  if (e instanceof BlockedError && fs.existsSync(OUT)) {
    console.log(`::warning title=Wishlist sync skipped::${e.message.split(': ').pop()}; keeping the current wishlist/data.json.`);
    return;
  }
  console.error(e.message || e);
  process.exit(1);
});
