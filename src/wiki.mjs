// Search and read over data/wiki.json (built by scripts/build-wiki.mjs from the Deseret Wiki).
// BM25 over title + text, with a bonus for the exact phrase; every hit carries its deseret.wiki URL.

export const KINDS = {
  article: 'Wiki article sections',
  page: 'Text of the site pages',
  letter: 'The letters of the alphabet (front-page chart)',
  library: 'Library: hosted PDFs, sermons and conference addresses, further reading',
  resource: 'Resources: communities, games, keyboards and tools',
  video: 'Videos',
  font: 'Fonts',
  book: 'Books & Prints in the Deseret Alphabet',
  quote: 'Quotes',
};

const fold = (s) => s.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase()
  .replace(/[\u{10400}-\u{10427}]/gu, (c) => String.fromCodePoint(c.codePointAt(0) + 0x28));
const STOP = new Set('a an and are as at be by for from has have in is it its of on or that the this to was were what which who with how why when where did does do about'.split(' '));
// light suffix stripping so designed/designing/designs/design meet; applied to both index and query
function stem(t) {
  if (/^[\u{10428}-\u{1044F}]/u.test(t) || /\d/.test(t)) return t;
  if (t.length > 4 && t.endsWith('ies')) return t.slice(0, -3) + 'y';
  for (const suf of ['ingly', 'ing', 'edly', 'ed', 'ers', 'er', 'ly', 'es', 's']) {
    if (!t.endsWith(suf) || t.length - suf.length < 4) continue;
    if ((suf === 's' || suf === 'es') && /(ss|us|is)$/.test(t)) return t;
    let s = t.slice(0, -suf.length);
    if (suf === 'es' && !/(s|x|z|ch|sh)$/.test(s)) s = t.slice(0, -1);
    if (/([b-df-hj-np-tv-z])\1$/.test(s) && !/(ll|ss|ff|zz)$/.test(s)) s = s.slice(0, -1); // stopped -> stop
    return s.replace(/e$/, '');
  }
  return t.replace(/e$/, '');
}
export const tokenize = (s) => (fold(String(s)).match(/[\p{L}\p{N}]+/gu) || []).filter((t) => !STOP.has(t)).map(stem);

const BACK_MATTER = /^(references|notes|bibliography|further reading|external links|see also|sources)$/i;

export function createWiki(corpus) {
  const records = corpus.records;
  const byId = new Map(records.map((r) => [r.id, r]));
  const docs = records.map((r) => {
    const title = tokenize(`${r.title} ${r.where || ''} ${r.author || ''}`);
    const body = tokenize(r.text || '');
    const tf = new Map();
    for (const t of title) tf.set(t, (tf.get(t) || 0) + 3);
    for (const t of body) tf.set(t, (tf.get(t) || 0) + 1);
    return { r, tf, len: title.length * 3 + body.length, hay: fold(`${r.title} ${r.text || ''}`) };
  });
  const df = new Map();
  for (const d of docs) for (const t of d.tf.keys()) df.set(t, (df.get(t) || 0) + 1);
  const avg = docs.reduce((a, d) => a + d.len, 0) / Math.max(docs.length, 1);
  const N = docs.length;

  function snippet(text, terms, size = 280) {
    if (!text) return '';
    const flat = text.replace(/\s+/g, ' ');
    const low = fold(flat);
    let at = -1;
    for (const t of terms) { const i = low.indexOf(t); if (i >= 0 && (at < 0 || i < at)) at = i; }
    if (at < 0 || flat.length <= size) return flat.length <= size ? flat : flat.slice(0, size).trimEnd() + '…';
    const start = Math.max(0, at - Math.floor(size / 3));
    const s = flat.slice(start, start + size).trim();
    return (start > 0 ? '…' : '') + s + (start + size < flat.length ? '…' : '');
  }

  function summary(r) {
    const o = { id: r.id, kind: r.kind, title: r.title };
    if (r.where && r.where !== r.title) o.where = r.where;
    o.url = r.url;
    if (r.source_url) o.source_url = r.source_url;
    return o;
  }

  function search(query, { kind, limit = 8 } = {}) {
    const q = String(query || '').trim();
    if (!q) throw new Error('query is required');
    const terms = [...new Set(tokenize(q))];
    const phrase = fold(q);
    const kinds = kind ? (Array.isArray(kind) ? kind : [kind]) : null;
    const scored = [];
    for (const d of docs) {
      if (kinds && !kinds.includes(d.r.kind)) continue;
      let s = 0;
      let hit = 0;
      for (const t of terms) {
        const f = d.tf.get(t);
        if (!f) continue;
        hit++;
        const idf = Math.log(1 + (N - df.get(t) + 0.5) / (df.get(t) + 0.5));
        s += idf * ((f * 2.2) / (f + 1.2 * (0.25 + 0.75 * (d.len / avg))));
      }
      if (!hit) continue;
      if (terms.length > 1) s *= 0.5 + (0.5 * hit) / terms.length;
      if (phrase.length > 3 && d.hay.includes(phrase)) s *= 1.6;
      if (d.r.kind === 'article' && BACK_MATTER.test(d.r.title)) s *= 0.4; // bibliographies match everything
      scored.push([s, d.r]);
    }
    scored.sort((a, b) => b[0] - a[0]);
    const max = Math.min(Math.max(1, Number(limit) || 8), 25);
    return {
      query: q,
      total: scored.length,
      results: scored.slice(0, max).map(([s, r]) => ({ ...summary(r), score: Math.round(s * 100) / 100, snippet: snippet(r.text, terms) })),
    };
  }

  function cite(r) {
    const parts = [`“${r.title}”`];
    if (r.where && r.where !== r.title) parts.push(r.where);
    parts.push(`Deseret Wiki, ${r.url}`);
    return parts.join(', ');
  }

  function read(id, { max_chars } = {}) {
    const r = byId.get(String(id || ''));
    if (!r) throw new Error(`No wiki record with id "${id}". Use search_wiki or wiki_contents to find ids.`);
    const { file, ...rest } = r;
    const out = { ...rest, citation: cite(r), source_file: `github.com/Samuel-Baird/deseret/blob/main/${file || ''}`.replace(/\/$/, '') };
    const cap = Math.min(Math.max(Number(max_chars) || 12000, 500), 60000);
    if (out.text && out.text.length > cap) {
      out.text = out.text.slice(0, cap).trimEnd() + '…';
      out.truncated = { shown: cap, total: r.text.length };
    }
    if (r.kind === 'article') {
      const base = r.id.split('#')[0];
      const secs = records.filter((x) => x.id.split('#')[0] === base);
      const i = secs.indexOf(r);
      if (secs[i - 1]) out.previous = summary(secs[i - 1]);
      if (secs[i + 1]) out.next = summary(secs[i + 1]);
    }
    return out;
  }

  function contents(kind) {
    if (!kind) {
      return {
        site: corpus.site,
        built: corpus.built,
        wiki_commit: corpus.commit,
        kinds: Object.entries(corpus.counts).map(([k, n]) => ({ kind: k, count: n, about: KINDS[k] || k })),
        note: 'Pass a kind to list its records, then read_wiki(id) for the full text.',
      };
    }
    const list = records.filter((r) => r.kind === kind);
    if (!list.length) throw new Error(`Unknown kind "${kind}". Kinds: ${Object.keys(corpus.counts).join(', ')}`);
    return { kind, about: KINDS[kind] || kind, count: list.length, records: list.map(summary) };
  }

  /** Word counts over the whole corpus (Latin words), for choosing between homophones. */
  function wordFreq() {
    const f = new Map();
    for (const r of records) for (const w of (`${r.title} ${r.text || ''}`.toLowerCase().match(/[a-z]+(?:'[a-z]+)?/g) || [])) f.set(w, (f.get(w) || 0) + 1);
    return f;
  }

  return { search, read, contents, wordFreq, size: records.length };
}
