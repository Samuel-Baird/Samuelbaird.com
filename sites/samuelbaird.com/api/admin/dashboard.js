// Owner-only API behind the /admin dashboard (ticket 0.4).
//   GET /api/admin/dashboard -> { summary, deploys, uptime, errors }
//
// summary  public.admin_dashboard_summary() (latter-day-stats migration 0062): donations,
//          premium, accounts and ticket counts, aggregates only, owner only.
// deploys  latest Cloudflare Workers deployment and version per Worker. Needs CLOUDFLARE_API_TOKEN
//          (Account > Workers Scripts > Read is enough) and CLOUDFLARE_ACCOUNT_ID on samuelbaird-com.
// uptime   a live GET of every public site's home page, with status and timing.
// Each part fails on its own: a missing env var or a slow site only empties that panel.
const { asUser, requireOwner } = require('../_lib/session');

const VERCEL_TOKEN = process.env.VERCEL_TOKEN || '';
const VERCEL_TEAM = process.env.VERCEL_TEAM || 'samuel-bairds-projects';

// Vercel project name -> where it is served. Hidden projects (Omni) are fine here: owner only.
const SITES = [
  { project: 'samuelbaird-com', name: 'samuelbaird.com', url: 'https://samuelbaird.com/' },
  { project: 'latter-day-stats', name: 'Latter-day Stats', url: 'https://samuelbaird.com/latter-day-stats' },
  { project: 'urim', name: 'Urim', url: 'https://samuelbaird.com/urim' },
  { project: 'peepstone', name: 'Peepstone', url: 'https://samuelbaird.com/peepstone' },
  { project: 'omni', name: 'Omni (hidden)', url: 'https://samuelbaird.com/omni' },
  { project: 'deseret-wiki', name: 'Deseret Wiki', url: 'https://deseret.wiki/' },
  { project: 'deseret-mcp', name: 'Deseret MCP', url: 'https://mcp.deseret.wiki/' },
];

function withTimeout(ms) {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), ms);
  return { signal: c.signal, done: () => clearTimeout(t) };
}

async function summary(token) {
  const r = await asUser(token, '/rest/v1/rpc/admin_dashboard_summary', { method: 'POST', body: {} });
  if (r.status === 404) throw new Error('migration_missing');
  if (r.status !== 200) throw new Error((r.json && (r.json.message || r.json.code)) || 'summary_failed');
  return r.json;
}

async function cf(path, signal) {
  const r = await fetch(`https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT}/workers/scripts/${path}`, {
    headers: { authorization: `Bearer ${CF_TOKEN}` }, signal,
  });
  if (r.status === 404) return null; // Worker not deployed yet
  if (!r.ok) throw new Error(`cloudflare_${r.status}`);
  return (await r.json()).result;
}

// CI deploys with --tag <sha> --message "<branch>: <commit subject>" (see .github/workflows/deploy.yml).
function describe(v, created) {
  if (!v) return null;
  const a = v.annotations || {};
  const msg = a['workers/message'] || '';
  const m = msg.match(/^([^:\s]+): ([\s\S]*)$/);
  return {
    state: 'READY',
    target: 'production',
    created: Date.parse(created || (v.metadata && v.metadata.created_on) || '') || null,
    url: null,
    inspector: null,
    branch: m ? m[1] : null,
    message: (m ? m[2] : msg).split('\n')[0].slice(0, 140) || a['workers/tag'] || null,
  };
}

async function deploys() {
  if (!CF_TOKEN || !CF_ACCOUNT) throw new Error('no_cloudflare_token');
  const t = withTimeout(8000);
  try {
    return await Promise.all(SITES.map(async (s) => {
      const [dep, vers] = await Promise.all([
        cf(`${s.project}/deployments`, t.signal),
        cf(`${s.project}/versions?per_page=5`, t.signal),
      ]);
      const versions = (vers && vers.items) || [];
      const current = dep && dep.deployments && dep.deployments[0];
      const liveId = current && current.versions && current.versions[0] && current.versions[0].version_id;
      const live = versions.find((v) => v.id === liveId) || (liveId ? { id: liveId, annotations: current.annotations, metadata: {} } : null);
      const latest = versions[0] || null;
      return {
        project: s.project,
        name: s.name,
        production: describe(live, current && current.created_on),
        latest: latest && { ...describe(latest), target: latest.id === liveId ? 'production' : 'preview' },
        failing: 0, // failed builds show in GitHub Actions, not here
      };
    }));
  } finally { t.done(); }
}

async function uptime() {
  return Promise.all(SITES.map(async (s) => {
    const t = withTimeout(6000);
    const start = Date.now();
    try {
      const r = await fetch(s.url, { method: 'GET', redirect: 'follow', signal: t.signal, headers: { 'user-agent': 'samuelbaird-admin-uptime' } });
      return { name: s.name, url: s.url, status: r.status, ok: r.ok, ms: Date.now() - start };
    } catch (e) {
      return { name: s.name, url: s.url, status: 0, ok: false, ms: Date.now() - start, error: e.name === 'AbortError' ? 'timeout' : 'unreachable' };
    } finally { t.done(); }
  }));
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  if (req.method !== 'GET') { res.setHeader('Allow', 'GET'); return res.status(405).json({ error: 'method_not_allowed' }); }

  const auth = await requireOwner(req);
  if (!auth.token) return res.status(auth.status).json({ error: auth.error });

  const [s, d, u] = await Promise.allSettled([summary(auth.token), deploys(), uptime()]);
  const errors = {};
  if (s.status === 'rejected') errors.summary = s.reason.message;
  if (d.status === 'rejected') errors.deploys = d.reason.message;
  if (u.status === 'rejected') errors.uptime = u.reason.message;
  return res.status(200).json({
    summary: s.status === 'fulfilled' ? s.value : null,
    deploys: d.status === 'fulfilled' ? d.value : null,
    uptime: u.status === 'fulfilled' ? u.value : null,
    cloudflareAccount: CF_ACCOUNT || null,
    errors,
  });
};
