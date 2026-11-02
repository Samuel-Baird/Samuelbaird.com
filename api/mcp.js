// Urim hosted MCP: read-only access to the atlas over streamable HTTP (stateless, JSON responses).
// Data comes from data/api.json, built by pipeline/build.py. No auth, no state, no user data.
const DATA = require('../data/api.json').concepts;

const SITE = 'https://urim.samuelbaird.com';
const LANGS = ['pt', 'es'];
const VERSIONS = ['2025-11-25', '2025-06-18', '2025-03-26', '2024-11-05'];

// ---- text helpers (mirror pipeline/textutil.py)
const fold = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const tokens = (s) => {
  const out = [];
  const re = /[\p{L}\p{N}_]+/gu;
  let m;
  while ((m = re.exec(s))) out.push([m[0], m.index]);
  return out;
};
const variants = (w) => {
  const v = new Set([w, w + 's', w + 'es']);
  if (w.endsWith('y')) v.add(w.slice(0, -1) + 'ies');
  return v;
};

// ---- index (built once per cold start)
const bucket = new Map(); // first-token form -> [{sets, c}]
for (const c of DATA) {
  for (const form of c.en) {
    const toks = tokens(fold(form)).map((t) => t[0]);
    if (!toks.length) continue;
    const sets = toks.map(variants);
    for (const f of sets[0]) {
      if (!bucket.has(f)) bucket.set(f, []);
      bucket.get(f).push({ sets, c });
    }
  }
}
for (const b of bucket.values()) b.sort((a, z) => z.sets.length - a.sets.length);

function matchText(text) {
  const toks = tokens(fold(text));
  const seen = new Set();
  const out = [];
  let i = 0;
  while (i < toks.length) {
    let hit = 0;
    for (const { sets, c } of bucket.get(toks[i][0]) || []) {
      const L = sets.length;
      if (i + L <= toks.length && sets.every((s, k) => s.has(toks[i + k][0]))) {
        if (!seen.has(c.slug)) {
          seen.add(c.slug);
          out.push(c);
        }
        hit = L;
        break;
      }
    }
    i += hit || 1;
  }
  return out;
}

const url = (c) => `${SITE}/c/${c.slug}`;
const langName = { pt: 'Portuguese (Brazil)', es: 'Spanish' };

function brief(c, lang) {
  const d = c[lang];
  if (!d) return null;
  const o = { use: d.preferred, confidence: d.confidence };
  if (d.variants.length) o.also = d.variants.map((v) => v.term);
  return o;
}

function detail(c, langs) {
  const o = { concept: c.en[0], category: c.category, url: url(c) };
  for (const l of langs) {
    const d = c[l];
    if (!d) continue;
    o[l] = {
      preferred: d.preferred,
      confidence: d.confidence,
      renderings: d.renderings.map((r) => ({
        term: r.term,
        evidence: r.evidence,
        ...(r.evidence.length
          ? {
              talk_paragraphs: r.talk_paragraphs,
              scripture_verses: r.scripture_verses,
              years: r.years[0] ? `${r.years[0]}-${r.years[1]}` : undefined,
              share: r.share,
            }
          : {}),
      })),
    };
  }
  if (c.flags.length) o.notes = c.flags;
  return o;
}

// ---- tools
const langProp = {
  type: 'string',
  enum: LANGS,
  description: "Target language: 'pt' (Brazilian Portuguese) or 'es' (Spanish).",
};

const TOOLS = [
  {
    name: 'lookup_term',
    description:
      'Look up a Latter-day Saint term in English, Portuguese or Spanish (reverse lookup works: searching "investidura" finds "endowment"). ' +
      'Returns every Church-published rendering with evidence type (approved_term, attested), usage counts, years and a link to the source page. ' +
      'Evidence comes only from official Church translations; counts show usage, not correctness.',
    inputSchema: {
      type: 'object',
      properties: {
        term: { type: 'string', description: 'Term in English, Portuguese or Spanish.' },
        lang: { ...langProp, description: 'Optional: limit output to one language.' },
        limit: { type: 'integer', minimum: 1, maximum: 10, description: 'Max concepts (default 5).' },
      },
      required: ['term'],
    },
    run({ term, lang, limit }) {
      const q = fold(String(term || '')).trim();
      if (!q) throw new Error('term is required');
      const scored = [];
      for (const c of DATA) {
        const keys = c.en.map(fold);
        for (const l of LANGS) if (c[l]) keys.push(...c[l].renderings.map((r) => fold(r.term)));
        let s = 0;
        if (keys.includes(q)) s = 3;
        else if (keys.some((k) => k.startsWith(q))) s = 2;
        else if (keys.some((k) => k.includes(q))) s = 1;
        if (s) scored.push([s, c]);
      }
      scored.sort((a, b) => b[0] - a[0] || a[1].en[0].length - b[1].en[0].length);
      const langs = lang ? [lang] : LANGS;
      return { query: term, results: scored.slice(0, limit || 5).map(([, c]) => detail(c, langs)) };
    },
  },
  {
    name: 'match_glossary',
    description:
      'Given English text, return only the Church terminology it contains, with the required rendering in the target language. ' +
      'Use this before translating a passage so you apply the Church\'s own vocabulary without loading a whole glossary. ' +
      'confidence: approved (Church approved-terms list), attested (found in official Church text), hint (suggested, unconfirmed).',
    inputSchema: {
      type: 'object',
      properties: { text: { type: 'string', description: 'English text (up to ~20,000 characters).' }, lang: langProp },
      required: ['text', 'lang'],
    },
    run({ text, lang }) {
      if (!LANGS.includes(lang)) throw new Error("lang must be 'pt' or 'es'");
      const terms = matchText(String(text || '').slice(0, 20000))
        .map((c) => ({ en: c.en[0], ...brief(c, lang), url: url(c) }))
        .filter((t) => t.use);
      return { lang, language: langName[lang], terms };
    },
  },
  {
    name: 'search_concepts',
    description: 'List atlas concepts by English name or topic category. With no query, returns the category list.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Substring of an English term or a category name.' },
        limit: { type: 'integer', minimum: 1, maximum: 50, description: 'Default 20.' },
      },
    },
    run({ query, limit }) {
      const q = fold(String(query || '')).trim();
      if (!q) {
        const cats = {};
        for (const c of DATA) cats[c.category] = (cats[c.category] || 0) + 1;
        return { categories: Object.entries(cats).map(([name, concepts]) => ({ name, concepts })) };
      }
      const hits = DATA.filter((c) => fold(c.category).includes(q) || c.en.some((e) => fold(e).includes(q)));
      return {
        total: hits.length,
        concepts: hits.slice(0, limit || 20).map((c) => ({
          en: c.en[0],
          category: c.category,
          pt: c.pt && c.pt.preferred,
          es: c.es && c.es.preferred,
          url: url(c),
        })),
      };
    },
  },
  {
    name: 'find_variants',
    description:
      'Find where Church translations are inconsistent: "varies" = one English term with several Church renderings; ' +
      '"collisions" = several English terms sharing one rendering. Observations from published text, not judgments.',
    inputSchema: {
      type: 'object',
      properties: {
        kind: { type: 'string', enum: ['varies', 'collisions'] },
        lang: { ...langProp, description: 'Optional filter.' },
      },
      required: ['kind'],
    },
    run({ kind, lang }) {
      const tag = kind === 'varies' ? 'varies in ' : 'shares ';
      const rows = [];
      for (const c of DATA) {
        for (const f of c.flags) {
          if (!f.startsWith(tag)) continue;
          if (lang && !f.includes(`(${lang})`) && !f.includes(`in ${lang}:`)) continue;
          rows.push({ en: c.en[0], note: f, url: url(c) });
        }
      }
      return { kind, count: rows.length, results: rows.slice(0, 60) };
    },
  },
];

// ---- JSON-RPC / MCP plumbing
const ok = (id, result) => ({ jsonrpc: '2.0', id, result });
const err = (id, code, message) => ({ jsonrpc: '2.0', id, error: { code, message } });

function handle(msg) {
  const { id, method, params } = msg;
  if (id === undefined || id === null) return null; // notification
  switch (method) {
    case 'initialize': {
      const want = params && params.protocolVersion;
      return ok(id, {
        protocolVersion: VERSIONS.includes(want) ? want : VERSIONS[0],
        capabilities: { tools: {} },
        serverInfo: { name: 'urim', title: 'Urim: Mormon Translation Atlas', version: '1.0.0', websiteUrl: SITE },
        instructions:
          'Read-only atlas of how the Church of Jesus Christ of Latter-day Saints translates its own vocabulary into Portuguese and Spanish. ' +
          'Evidence is limited to official Church translations. Independent project, not affiliated with the Church.',
      });
    }
    case 'ping':
      return ok(id, {});
    case 'tools/list':
      return ok(id, { tools: TOOLS.map(({ name, description, inputSchema }) => ({ name, description, inputSchema, annotations: { readOnlyHint: true, openWorldHint: false } })) });
    case 'tools/call': {
      const tool = TOOLS.find((t) => t.name === (params && params.name));
      if (!tool) return err(id, -32602, `Unknown tool: ${params && params.name}`);
      try {
        const result = tool.run((params && params.arguments) || {});
        return ok(id, { content: [{ type: 'text', text: JSON.stringify(result) }] });
      } catch (e) {
        return ok(id, { isError: true, content: [{ type: 'text', text: String(e.message || e) }] });
      }
    }
    default:
      return err(id, -32601, `Method not found: ${method}`);
  }
}

async function readBody(req) {
  if (req.body !== undefined && req.body !== null) return typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
  const chunks = [];
  for await (const ch of req) chunks.push(ch);
  return Buffer.concat(chunks).toString('utf8');
}

module.exports = async function mcp(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept, Authorization, Mcp-Session-Id, Mcp-Protocol-Version');
  res.setHeader('Access-Control-Expose-Headers', 'Mcp-Session-Id');
  if (req.method === 'OPTIONS') {
    res.statusCode = 204;
    return res.end();
  }
  if (req.method !== 'POST') {
    res.statusCode = 405;
    res.setHeader('Allow', 'POST, OPTIONS');
    return res.end();
  }
  let body;
  try {
    body = JSON.parse(await readBody(req));
  } catch {
    res.statusCode = 400;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify(err(null, -32700, 'Parse error')));
  }
  const batch = Array.isArray(body);
  const replies = (batch ? body : [body]).map((m) => handle(m || {})).filter(Boolean);
  if (!replies.length) {
    res.statusCode = 202;
    return res.end();
  }
  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(batch ? replies : replies[0]));
};
