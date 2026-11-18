// Owner-only API behind the /admin dashboard (ticket 0.4).
//   GET /api/admin/dashboard -> { summary, deploys, uptime, errors }
//
// summary  public.admin_dashboard_summary() (latter-day-stats migration 0062): donations,
//          premium, accounts and ticket counts, aggregates only, owner only.
// deploys  latest Vercel deployment per project. Needs VERCEL_TOKEN (a read-only token
//          is enough) and optionally VERCEL_TEAM (team slug or id) on samuelbaird-com.
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

async function deploys() {
  if (!VERCEL_TOKEN) throw new Error('no_vercel_token');
  const team = /^team_/.test(VERCEL_TEAM) ? `teamId=${encodeURIComponent(VERCEL_TEAM)}` : `slug=${encodeURIComponent(VERCEL_TEAM)}`;
  const t = withTimeout(8000);
  try {
    const r = await fetch(`https://api.vercel.com/v6/deployments?limit=100&${team}`, {
      headers: { authorization: `Bearer ${VERCEL_TOKEN}` }, signal: t.signal,
    });
    if (!r.ok) throw new Error(`vercel_${r.status}`);
    const { deployments = [] } = await r.json();
    return SITES.map((s) => {
      const mine = deployments.filter((d) => d.name === s.project);
      const pick = (d) => d && {
        state: d.state || d.readyState,
        target: d.target || 'preview',
        created: d.created || d.createdAt,
        url: d.url ? `https://${d.url}` : null,
        inspector: d.inspectorUrl || null,
        branch: d.meta?.githubCommitRef || null,
        message: (d.meta?.githubCommitMessage || '').split('\n')[0].slice(0, 140) || null,
      };
      return {
        project: s.project,
        name: s.name,
        production: pick(mine.find((d) => d.target === 'production')),
        latest: pick(mine[0]),
        failing: mine.slice(0, 5).filter((d) => (d.state || d.readyState) === 'ERROR').length,
      };
    });
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
    vercelTeam: VERCEL_TEAM,
    errors,
  });
};
