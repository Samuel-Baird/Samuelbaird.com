// Vercel function behind the private /scout page.
//   GET  /api/scout  -> { keys: [...] }  normalized URLs the owner has dismissed (no titles; same data leads.json already exposes)
//   GET  /api/scout?list=1 -> { text }   the scout's master search list (search-list.txt)
//   POST /api/scout  -> body { list: "..." } replaces search-list.txt
//   POST /api/scout  -> body { url, title }: adds the URL to state/dismissed.json in
//                       Samuel-Baird/collector-items so future scout runs skip it.
// No login: the /scout page is unlinked and noindex, so nothing protects this endpoint beyond that.
// Env (set in Vercel): SCOUT_GITHUB_TOKEN = fine-grained token, Contents read/write on collector-items only.
// No dependencies. The repo and file path are fixed here and never taken from the request.
const MAX_ITEMS = 2000; // keeps dismissed.json from growing without bound if the URL is ever found

const OWNER = 'Samuel-Baird';
const REPO = 'collector-items';
const FILE = 'state/dismissed.json';
const API = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${FILE}`;

// Same rule as the scout runs and the page: host + path + query, no scheme, no www., no tracking params.
function normalize(u) {
  try {
    const x = new URL(String(u));
    if (!/^https?:$/.test(x.protocol)) return '';
    const drop = /^(utm_|_trk|hash$|fbclid|gclid|mkcid|mkevt|mkrid|campid|customid|toolid|ssspo|sssrc|ssuid|widget_ver|media$)/i;
    for (const k of [...x.searchParams.keys()]) if (drop.test(k)) x.searchParams.delete(k);
    const host = x.hostname.toLowerCase().replace(/^www\./, '');
    const path = x.pathname.replace(/\/+$/, '') || '/';
    const q = x.searchParams.toString();
    return host + path + (q ? '?' + q : '');
  } catch { return ''; }
}

const LIST_API = `https://api.github.com/repos/${OWNER}/${REPO}/contents/search-list.txt`;
const MAX_LIST = 20000;

function gh(method, body) { return ghFile(API, method, body); }

async function ghFile(url, method, body) {
  const r = await fetch(url + (method === 'GET' ? '?ref=main' : ''), {
    method,
    headers: {
      authorization: `Bearer ${process.env.SCOUT_GITHUB_TOKEN}`,
      accept: 'application/vnd.github+json',
      'x-github-api-version': '2022-11-28',
      'user-agent': 'scout-dismiss',
      ...(body ? { 'content-type': 'application/json' } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  return { status: r.status, json: await r.json().catch(() => ({})) };
}

function decode(file) {
  try { return JSON.parse(Buffer.from(file.content || '', 'base64').toString('utf8')); }
  catch { return { items: {} }; }
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  if (!process.env.SCOUT_GITHUB_TOKEN) {
    return res.status(503).json({ error: 'Not configured' });
  }

  // Editable search list (search-list.txt): GET ?list=1 reads it, POST {list} replaces it.
  const wantsList = req.method === 'GET' ? req.query && req.query.list : (typeof req.body === 'object' && req.body && 'list' in req.body);
  if (wantsList) {
    if (req.method === 'GET') {
      const cur = await ghFile(LIST_API, 'GET');
      if (cur.status !== 200) return res.status(502).json({ error: 'GitHub read failed' });
      return res.status(200).json({ text: Buffer.from(cur.json.content || '', 'base64').toString('utf8') });
    }
    const text = String(req.body.list).replace(/\r\n/g, '\n');
    if (text.length > MAX_LIST) return res.status(413).json({ error: 'List too long' });
    for (let attempt = 0; attempt < 3; attempt++) {
      const cur = await ghFile(LIST_API, 'GET');
      if (cur.status !== 200) return res.status(502).json({ error: 'GitHub read failed' });
      const put = await ghFile(LIST_API, 'PUT', {
        message: 'Update search list from /scout',
        content: Buffer.from(text.replace(/\n*$/, '\n')).toString('base64'),
        sha: cur.json.sha,
        branch: 'main',
      });
      if (put.status === 200 || put.status === 201) return res.status(200).json({ ok: true });
      if (put.status !== 409 && put.status !== 422) return res.status(502).json({ error: 'GitHub write failed' });
    }
    return res.status(503).json({ error: 'Busy, try again' });
  }

  if (req.method === 'GET') {
    const { status, json } = await gh('GET');
    if (status !== 200) return res.status(502).json({ error: 'GitHub read failed' });
    return res.status(200).json({ keys: Object.keys(decode(json).items || {}) });
  }

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'GET, POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const body = typeof req.body === 'string' ? (() => { try { return JSON.parse(req.body); } catch { return {}; } })() : (req.body || {});
  const key = normalize(body.url);
  if (!key || key.length > 1500) return res.status(400).json({ error: 'Bad url' });
  const title = String(body.title || '').replace(/\s+/g, ' ').slice(0, 200);

  for (let attempt = 0; attempt < 3; attempt++) {
    const cur = await gh('GET');
    if (cur.status !== 200) return res.status(502).json({ error: 'GitHub read failed' });
    const data = decode(cur.json);
    data.items = data.items || {};
    if (data.items[key]) return res.status(200).json({ ok: true, already: true });
    if (Object.keys(data.items).length >= MAX_ITEMS) return res.status(507).json({ error: 'Dismissed list is full' });
    data.items[key] = { title, dismissed_at: new Date().toISOString().slice(0, 10) };
    const put = await gh('PUT', {
      message: 'Dismiss lead from /scout',
      content: Buffer.from(JSON.stringify(data, null, 2) + '\n').toString('base64'),
      sha: cur.json.sha,
      branch: 'main',
    });
    if (put.status === 200 || put.status === 201) return res.status(200).json({ ok: true });
    if (put.status !== 409 && put.status !== 422) return res.status(502).json({ error: 'GitHub write failed' });
  }
  return res.status(503).json({ error: 'Busy, try again' });
};
