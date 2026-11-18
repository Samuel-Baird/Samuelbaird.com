// Family single sign-on for samuelbaird.com functions.
//
// Every app under samuelbaird.com/* shares one origin, so the Supabase session
// cookie that the Latter-day Stats Google login sets (sb-<ref>-auth-token, path /)
// reaches these functions too. We read the access token out of it and forward it
// to Supabase as the user, so Postgres RLS decides what they may touch.
//
// Sign-in:  /latter-day-stats/login?return_to=<path on samuelbaird.com>
// Refresh:  any request to /latter-day-stats/* runs its proxy, which refreshes an
//           expired session and re-sets the cookie (see refreshSession in admin pages).
//
// Env (Vercel, samuelbaird-com project): SUPABASE_URL, SUPABASE_ANON_KEY
// (the same public values as NEXT_PUBLIC_SUPABASE_* on latter-day-stats).
// Files under api/_lib are helpers, not routes.

const SUPABASE_URL = (process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL || '').replace(/\/+$/, '');
const ANON = process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

function configured() { return Boolean(SUPABASE_URL && ANON); }

function parseCookies(header) {
  const out = {};
  for (const part of String(header || '').split(';')) {
    const i = part.indexOf('=');
    if (i < 0) continue;
    const k = part.slice(0, i).trim();
    let v = part.slice(i + 1).trim();
    try { v = decodeURIComponent(v); } catch { /* keep raw */ }
    out[k] = v;
  }
  return out;
}

// @supabase/ssr stores the session as JSON, optionally "base64-"-prefixed
// base64url, and splits values over 3180 bytes into name.0, name.1, ...
function readSession(cookieHeader) {
  if (!SUPABASE_URL) return null;
  const ref = new URL(SUPABASE_URL).hostname.split('.')[0];
  const name = `sb-${ref}-auth-token`;
  const jar = parseCookies(cookieHeader);
  let raw = jar[name];
  if (raw == null) {
    const chunks = [];
    for (let i = 0; jar[`${name}.${i}`] != null; i++) chunks.push(jar[`${name}.${i}`]);
    if (!chunks.length) return null;
    raw = chunks.join('');
  }
  try {
    const json = raw.startsWith('base64-')
      ? Buffer.from(raw.slice(7).replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8')
      : raw;
    const s = JSON.parse(json);
    return s && typeof s.access_token === 'string' ? s : null;
  } catch { return null; }
}

// Calls Supabase as the signed-in user. path is e.g. "/rest/v1/admin_tickets?select=*".
async function asUser(token, path, { method = 'GET', body, prefer } = {}) {
  const r = await fetch(SUPABASE_URL + path, {
    method,
    headers: {
      apikey: ANON,
      authorization: `Bearer ${token}`,
      accept: 'application/json',
      ...(body !== undefined ? { 'content-type': 'application/json' } : {}),
      ...(prefer ? { prefer } : {}),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const text = await r.text();
  let json = null;
  try { json = text ? JSON.parse(text) : null; } catch { json = { message: text }; }
  return { status: r.status, json };
}

// Resolves the request to { token } for the site owner, or an { status, error } to send.
async function requireOwner(req) {
  if (!configured()) return { status: 503, error: 'not_configured' };
  const session = readSession(req.headers.cookie);
  if (!session) return { status: 401, error: 'signed_out' };
  const r = await asUser(session.access_token, '/rest/v1/rpc/is_site_owner', { method: 'POST', body: {} });
  if (r.status === 401 || r.status === 403) return { status: 401, error: 'expired' };
  if (r.status === 404) return { status: 503, error: 'migration_missing' };
  if (r.status !== 200) return { status: 502, error: 'auth_check_failed' };
  if (r.json !== true) return { status: 403, error: 'not_owner' };
  return { token: session.access_token };
}

module.exports = { configured, readSession, asUser, requireOwner };
