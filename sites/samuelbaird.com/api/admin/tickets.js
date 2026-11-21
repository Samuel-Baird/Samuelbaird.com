// Owner-only API behind /admin/tickets. Data: public.admin_tickets in the
// Latter-day Stats Supabase project (migration 0061); RLS allows the owner account only.
//   GET    /api/admin/tickets            -> { tickets: [...] }
//   POST   /api/admin/tickets            -> body: ticket fields, creates one
//   PATCH  /api/admin/tickets?ref=5.2    -> body: fields to change
//   DELETE /api/admin/tickets?ref=5.2
// Auth: the shared family session cookie (see ../_lib/session.js).
const { asUser, requireOwner } = require('../_lib/session');

const STATUS = ['idea', 'backlog', 'next', 'doing', 'review', 'blocked', 'done', 'dropped'];
const VISIBILITY = ['public', 'private', 'hidden'];
const SCORES = ['priority', 'impact', 'traffic', 'revenue', 'ease'];
const ALLOWED_ORIGINS = ['https://samuelbaird.com', 'https://www.samuelbaird.com'];

function str(v, max) { return typeof v === 'string' ? v.slice(0, max) : undefined; }
function list(v) {
  if (typeof v === 'string') v = v.split(',');
  return Array.isArray(v) ? v.map((x) => String(x).trim().toLowerCase()).filter(Boolean).slice(0, 20) : undefined;
}

// Whitelists and normalises fields; never trusts id/created_at/updated_at from the client.
function clean(b) {
  const t = {};
  const ref = str(b.ref, 20);
  if (ref !== undefined) t.ref = ref.trim();
  if ('parent_ref' in b) t.parent_ref = b.parent_ref ? String(b.parent_ref).trim().slice(0, 20) : null;
  for (const [k, max] of [['title', 200], ['summary', 2000], ['notes', 20000], ['category', 40]]) {
    const v = str(b[k], max);
    if (v !== undefined) t[k] = k === 'category' ? v.trim().toLowerCase() : v;
  }
  if (typeof b.ai_enabled === 'boolean') t.ai_enabled = b.ai_enabled;
  if ('ai_instructions' in b) {
    const v = b.ai_instructions === null ? '' : str(b.ai_instructions, 10000);
    if (v !== undefined) t.ai_instructions = v;
  }
  if (STATUS.includes(b.status)) t.status = b.status;
  if (VISIBILITY.includes(b.visibility)) t.visibility = b.visibility;
  for (const k of SCORES) {
    const n = Number(b[k]);
    if (Number.isInteger(n) && n >= 1 && n <= 5) t[k] = n;
  }
  for (const k of ['monetization', 'tags']) { const v = list(b[k]); if (v) t[k] = v; }
  if (Array.isArray(b.links)) {
    t.links = b.links
      .filter((l) => l && /^https?:\/\//i.test(String(l.url || '')))
      .slice(0, 30)
      .map((l) => ({ label: String(l.label || l.url).slice(0, 120), url: String(l.url).slice(0, 1000) }));
  }
  return t;
}

async function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') { try { return JSON.parse(req.body); } catch { return null; } }
  return null;
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');

  if (req.method !== 'GET') {
    // Cookie auth: refuse cross-site writes. (Supabase cookies are SameSite=Lax too.)
    const origin = req.headers.origin;
    if (origin && !ALLOWED_ORIGINS.includes(origin) && !/^http:\/\/localhost(:\d+)?$/.test(origin)) {
      return res.status(403).json({ error: 'bad_origin' });
    }
    if (!/^application\/json/i.test(req.headers['content-type'] || '') && req.method !== 'DELETE') {
      return res.status(415).json({ error: 'json_only' });
    }
  }

  const auth = await requireOwner(req);
  if (!auth.token) return res.status(auth.status).json({ error: auth.error });

  const ref = typeof req.query?.ref === 'string' ? req.query.ref : '';
  const byRef = `ref=eq.${encodeURIComponent(ref)}`;
  let r;

  switch (req.method) {
    case 'GET':
      r = await asUser(auth.token, '/rest/v1/admin_tickets?select=*&order=ref.asc&limit=1000');
      return r.status === 200
        ? res.status(200).json({ tickets: r.json })
        : res.status(502).json({ error: 'read_failed', detail: r.json });

    case 'POST': {
      const body = await readBody(req);
      if (!body) return res.status(400).json({ error: 'bad_json' });
      const t = clean(body);
      if (!t.ref || !t.title) return res.status(400).json({ error: 'ref_and_title_required' });
      r = await asUser(auth.token, '/rest/v1/admin_tickets', { method: 'POST', body: t, prefer: 'return=representation' });
      if (r.status === 409) return res.status(409).json({ error: 'ref_taken' });
      return r.status === 201
        ? res.status(201).json({ ticket: r.json[0] })
        : res.status(400).json({ error: 'create_failed', detail: r.json });
    }

    case 'PATCH': {
      if (!ref) return res.status(400).json({ error: 'ref_required' });
      const body = await readBody(req);
      if (!body) return res.status(400).json({ error: 'bad_json' });
      const t = clean(body);
      if (!Object.keys(t).length) return res.status(400).json({ error: 'nothing_to_change' });
      r = await asUser(auth.token, `/rest/v1/admin_tickets?${byRef}`, { method: 'PATCH', body: t, prefer: 'return=representation' });
      if (r.status === 409) return res.status(409).json({ error: 'ref_taken' });
      if (r.status !== 200) return res.status(400).json({ error: 'update_failed', detail: r.json });
      return r.json.length ? res.status(200).json({ ticket: r.json[0] }) : res.status(404).json({ error: 'not_found' });
    }

    case 'DELETE':
      if (!ref) return res.status(400).json({ error: 'ref_required' });
      r = await asUser(auth.token, `/rest/v1/admin_tickets?${byRef}`, { method: 'DELETE', prefer: 'return=representation' });
      if (r.status !== 200) return res.status(400).json({ error: 'delete_failed', detail: r.json });
      return r.json.length ? res.status(200).json({ deleted: ref }) : res.status(404).json({ error: 'not_found' });

    default:
      res.setHeader('Allow', 'GET, POST, PATCH, DELETE');
      return res.status(405).json({ error: 'method_not_allowed' });
  }
};
