// Builds data/wiki.json: every source on the Deseret Wiki as citable records.
// Run: npm run build:wiki   (reads a checkout of github.com/Samuel-Baird/deseret, never writes to it)
//   DESERET_WIKI=path/to/deseret   default ../deseret
//
// Sources: wiki articles (src/pages/wiki/*.md and src/content/**/*.md, one record per section), the
// visible text of every page, the lists in each page's frontmatter (library, resources, videos, the
// letter chart) and src/data/*.json (fonts, books & prints, quotes). Each record carries a deseret.wiki
// URL and, where the wiki links out, the original source URL.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const WIKI = path.resolve(process.env.DESERET_WIKI || path.join(ROOT, '..', 'deseret'));
const OUT = path.resolve(process.env.DESERET_WIKI_OUT || path.join(ROOT, 'data', 'wiki.json'));
const SITE = 'https://deseret.wiki';

if (!fs.existsSync(path.join(WIKI, 'src', 'pages'))) {
  console.error(`No Deseret Wiki checkout at ${WIKI} (set DESERET_WIKI).`);
  process.exit(1);
}

const rel = (p) => path.relative(WIKI, p).split(path.sep).join('/');
const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
// github-slugger, which Astro uses for heading ids
function slugger() {
  const seen = new Map();
  return (text) => {
    const base = text.toLowerCase().replace(/[^\p{L}\p{M}\p{N}\p{Pc} -]/gu, '').replace(/ /g, '-');
    let s = base;
    while (seen.has(s)) { seen.set(base, seen.get(base) + 1); s = `${base}-${seen.get(base)}`; }
    seen.set(s, 0);
    return s;
  };
}
const plainMd = (s) => s
  .replace(/<!--[\s\S]*?-->/g, ' ')
  .replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1')
  .replace(/\[([^\]]*)\]\((?:[^()]|\([^)]*\))*\)/g, '$1')
  .replace(/<[^>]+>/g, ' ')
  .replace(/^\s*\|?\s*-{3,}.*$/gm, ' ')
  .replace(/[*_`>#|]/g, ' ')
  .replace(/[ \t]+/g, ' ')
  .replace(/\n\s*\n+/g, '\n\n')
  .trim();
const routeOf = (file) => {
  let r = rel(file).replace(/^src\/pages\//, '/').replace(/\.(astro|md|mdx)$/, '');
  if (r.endsWith('/index')) r = r.slice(0, -'index'.length);
  return r === '/' ? '/' : r.replace(/\/?$/, '/');
};
const frontmatterOf = (s) => {
  const m = s.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return [{}, s];
  const fm = {};
  for (const line of m[1].split(/\r?\n/)) { const kv = line.match(/^(\w+):\s*(.*)$/); if (kv) fm[kv[1]] = kv[2].replace(/^["']|["']$/g, ''); }
  return [fm, s.slice(m[0].length)];
};
function walk(dir, re, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, re, out); else if (re.test(e.name)) out.push(p);
  }
  return out;
}

// The research archive behind some of the wiki's sources is not for public use: never pass its links on.
const PRIVATE_HOST = /corpus\.restorationcommons\.org/i;
const records = [];
const add = (r) => records.push(Object.fromEntries(Object.entries(r).filter(([, v]) => v !== undefined && v !== null && v !== '' && !(typeof v === 'string' && PRIVATE_HOST.test(v) && /^https?:/.test(v)))));

// ---- articles, one record per section
const articleFiles = [...walk(path.join(WIKI, 'src', 'pages'), /\.mdx?$/), ...walk(path.join(WIKI, 'src', 'content'), /\.mdx?$/)];
for (const file of articleFiles) {
  const [fm, body] = frontmatterOf(fs.readFileSync(file, 'utf8'));
  const url = SITE + (rel(file).startsWith('src/pages/') ? routeOf(file) : `/${rel(file).replace(/^src\/content\//, '').replace(/\.mdx?$/, '')}/`);
  const name = fm.heading || fm.title || path.basename(file).replace(/\.mdx?$/, '');
  const base = rel(file).replace(/^src\/(pages|content)\//, '').replace(/\.mdx?$/, '').replace(/\//g, ':');
  const attribution = (body.match(/^\*Text from \[([^\]]+)\]\(([^)]+)\)[^*]*licensed \[([^\]]+)\]/m) || []);
  const license = attribution.length ? `Text from ${attribution[1]} (${attribution[2]}), ${attribution[3]}` : undefined;
  const slug = slugger();
  const lines = body.split(/\r?\n/);
  const sections = [{ depth: 1, title: name, lines: [] }];
  let fence = false;
  for (const line of lines) {
    if (/^(```|~~~)/.test(line)) fence = !fence;
    const h = !fence && line.match(/^(#{2,4})\s+(.*)$/);
    if (h) sections.push({ depth: h[1].length, title: plainMd(h[2]).replace(/\s+/g, ' '), lines: [] });
    else sections.at(-1).lines.push(line);
  }
  const trail = [];
  for (const s of sections) {
    const anchor = s.depth === 1 ? '' : slug(s.title);
    trail.length = Math.max(0, s.depth - 1);
    trail[s.depth - 1] = s.title;
    const text = plainMd(s.lines.join('\n'));
    if (!text) continue; // a heading with only subsections under it
    add({
      id: `article:${base}${anchor ? '#' + anchor : ''}`,
      kind: 'article',
      title: s.depth === 1 ? name : s.title,
      where: trail.filter(Boolean).join(' › '),
      url: url + (anchor ? '#' + anchor : ''),
      text,
      description: s.depth === 1 ? fm.description : undefined,
      license,
      file: rel(file),
    });
  }
}

// ---- .astro pages: frontmatter lists and visible text
const dataDir = path.join(WIKI, 'src', 'data');
function evalFrontmatter(file, code) {
  const sandbox = { Astro: { props: {}, url: new URL(SITE) }, console: { log() {}, warn() {} } };
  const names = [];
  const body = code.replace(/^\s*import\s+(?:(\w+)|\{([^}]*)\}|\*\s+as\s+(\w+))\s+from\s+['"]([^'"]+)['"];?\s*$/gm, (m, def, named, star, spec) => {
    const target = path.resolve(path.dirname(file), spec);
    if (def && spec.endsWith('.json') && fs.existsSync(target)) { sandbox[def] = readJson(target); return ''; }
    for (const n of [def, star, ...(named ? named.split(',').map((x) => x.trim().split(/\s+as\s+/).pop()) : [])].filter(Boolean)) sandbox[n] = () => '';
    return '';
  }).replace(/^\s*import\s+['"][^'"]+['"];?\s*$/gm, '');
  for (const m of body.matchAll(/^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=/gm)) names.push(m[1]);
  try {
    return vm.runInNewContext(`${body}\n;({${names.join(',')}})`, sandbox, { timeout: 2000 });
  } catch (e) {
    console.warn(`  could not read the frontmatter of ${rel(file)}: ${e.message}`);
    return {};
  }
}
// drop {expressions} with their nesting (JSX inside .map callbacks), keeping the static text around them
const stripBraces = (s) => { let out = '', depth = 0; for (const c of s) { if (c === '{') depth++; else if (c === '}') { if (depth) depth--; } else if (!depth) out += c; } return out; };
const visibleText = (tpl) => stripBraces(tpl
  .replace(/<(script|style)[\s\S]*?<\/\1>/g, ' ')
  .replace(/<!--[\s\S]*?-->/g, ' '))
  .replace(/<[^>]*>/g, ' ')
  .replace(/&amp;/g, '&').replace(/&nbsp;/g, ' ').replace(/&[a-z]+;/g, ' ')
  .replace(/[ \t]+/g, ' ').replace(/\s*\n\s*/g, '\n').replace(/\n{2,}/g, '\n').trim();
const titleOf = (tpl, fallback) => (tpl.match(/<Title\s+text="([^"]+)"/) || tpl.match(/<Base\s+title="([^"—|]+)/) || [])[1]?.trim() || fallback;
const strings = (o) => Object.values(o).filter((v) => typeof v === 'string' && !/^(https?:|\/)/.test(v));

// how each known list becomes records; unknown lists fall back to a generic mapping
const MAPPERS = {
  'index.LETTERS': (l, page) => ({ kind: 'letter', title: `${l.glyph} ${l.name}`, text: `${l.name} (${l.glyph}): /${l.ipa}/ as in "${l.word}". One of the thirty-eight letters of the 1854 alphabet.`, url: page, glyph: l.glyph, ipa: l.ipa, key_word: l.word }),
  'index.CATEGORIES': null,
  'buy.sections': null,
  'library.pdfs': (p) => ({ kind: 'library', title: p.title, text: p.note, url: `${SITE}/library/${encodeURI(p.file)}`, source_url: p.cite, format: 'PDF (hosted on deseret.wiki)' }),
  'library.talks': (t, page) => ({ kind: 'library', title: `${t.who}, "${t.title}"`, text: `${t.date}. ${t.note}`, url: page, source_url: t.url, date: t.date, author: t.who, format: 'Sermon or conference address (Pulpit corpus)' }),
  'library.books': (b, page) => ({ kind: 'library', title: b.title, text: b.note, url: page, source_url: b.url, format: 'In copyright; linked to the publisher or a store' }),
  'resources.links': (l, page) => ({ kind: 'resource', title: l.title, text: l.note, url: page, source_url: l.url }),
  'videos.videos': (v, page) => ({ kind: 'video', title: v.title, text: `${v.title}. Video by ${v.by}.`, author: v.by, url: page, source_url: v.short ? `https://www.youtube.com/shorts/${v.id}` : `https://www.youtube.com/watch?v=${v.id}${v.list ? `&list=${v.list}` : ''}` }),
};
const pagesDir = path.join(WIKI, 'src', 'pages');
for (const file of walk(pagesDir, /\.astro$/)) {
  const r = rel(file);
  if (/404\.astro$/.test(r) || r.includes('/social/') || r.includes('[')) continue;
  const src = fs.readFileSync(file, 'utf8');
  const m = src.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  const tpl = m ? src.slice(m[0].length) : src;
  const page = SITE + routeOf(file);
  const pageKey = path.basename(file, '.astro');
  const pageTitle = titleOf(tpl, pageKey === 'index' ? 'Deseret Wiki' : pageKey);
  const text = visibleText(tpl);
  if (text.length > 40) add({ id: `page:${pageKey}`, kind: 'page', title: pageTitle, url: page, text, file: r });
  const vars = m ? evalFrontmatter(file, m[1]) : {};
  for (const [name, value] of Object.entries(vars)) {
    if (!Array.isArray(value) || !value.length || typeof value[0] !== 'object' || value[0] === null) continue;
    const key = `${pageKey}.${name}`;
    if (key in MAPPERS && MAPPERS[key] === null) continue;
    if (value === vars.fonts) continue; // src/data/fonts.json, handled below
    const map = MAPPERS[key] || ((o) => ({ kind: pageKey, title: o.title || o.name || strings(o)[0], text: strings(o).join('. '), url: page, source_url: o.url || o.href || o.cite }));
    value.forEach((o, i) => { const rec = map(o, page); if (rec) add({ id: `${pageKey}:${name}:${i + 1}`, where: pageTitle, file: r, ...rec }); });
  }
}

// ---- src/data/*.json
const buyFile = path.join(dataDir, 'buy.json');
if (fs.existsSync(buyFile)) {
  readJson(buyFile).forEach((b) => add({
    id: `book:${b.asin || b.title}`, kind: 'book', title: b.title, author: b.author, where: 'Books & Prints',
    text: `${b.title}, by ${b.author}.${b.price ? ` ${b.price}.` : ''}`, price: b.price, url: `${SITE}/buy/`, source_url: b.url, file: 'src/data/buy.json',
  }));
}
const fontsFile = path.join(dataDir, 'fonts.json');
if (fs.existsSync(fontsFile)) {
  readJson(fontsFile).forEach((f) => add({
    id: `font:${f.id}`, kind: 'font', title: f.name, where: 'Fonts', author: f.creator,
    text: `${f.name}: ${f.category} Deseret font, ${f.license} licence${f.creator ? `, by ${f.creator}` : ''}.${f.note ? ' ' + f.note : ''}`,
    license: f.license, url: `${SITE}/fonts/`, download_url: SITE + f.file, source_url: f.source, file: 'src/data/fonts.json',
  }));
}
// quotes: src/data/quotes.json (any of [..] or {quotes: [..]}) and the front-page quote
const quoteUrl = fs.existsSync(path.join(pagesDir, 'quotes.astro')) || fs.existsSync(path.join(pagesDir, 'quotes', 'index.astro')) ? `${SITE}/quotes/` : null;
const quoteRec = (q, i, file, url) => {
  const text = q.text || q.quote || q.body;
  if (!text) return null;
  const by = q.by || q.author || q.who || q.speaker;
  const ref = q.note || q.cite || q.citation || q.source || q.label;
  return { id: `quote:${q.id || q.slug || i + 1}`, kind: 'quote', title: `${by ? by + ': ' : ''}“${text.length > 70 ? text.slice(0, 67).trimEnd() + '…' : text}”`, text, author: by, date: q.date || q.year, citation: ref, where: 'Quotes', url: q.id && url ? `${url}#${q.id}` : url, source_url: q.url || q.link || q.href, file };
};
const seenQuotes = new Set();
const quotesFile = path.join(dataDir, 'quotes.json');
if (fs.existsSync(quotesFile)) {
  const raw = readJson(quotesFile);
  (Array.isArray(raw) ? raw : raw.quotes || []).forEach((q, i) => { const r = quoteRec(q, i, 'src/data/quotes.json', quoteUrl || `${SITE}/`); if (r) { seenQuotes.add(r.text.trim()); add(r); } });
}
const socialFile = path.join(dataDir, 'social-quote.json');
if (fs.existsSync(socialFile)) {
  const r = quoteRec(readJson(socialFile), 0, 'src/data/social-quote.json', `${SITE}/`);
  if (r && !seenQuotes.has(r.text.trim())) add({ ...r, id: 'quote:front-page', where: 'Front page' });
}

// ---- provenance
let commit = null;
try { commit = execFileSync('git', ['-C', WIKI, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(); } catch { /* not a git checkout */ }
const counts = {};
for (const r of records) counts[r.kind] = (counts[r.kind] || 0) + 1;
fs.writeFileSync(OUT, JSON.stringify({ site: SITE, built: new Date().toISOString().slice(0, 10), commit, counts, records }, null, 0) + '\n');
console.log(`${records.length} records written to ${path.relative(ROOT, OUT)} from ${WIKI}${commit ? ` @ ${commit.slice(0, 10)}` : ''}`);
console.log(counts);
