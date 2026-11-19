// samuelbaird.com on Cloudflare Workers.
//
// Static files are served straight from Workers static assets (see wrangler.jsonc, _headers, _redirects);
// this script only runs for the paths listed in assets.run_worker_first:
//   /api/*                          the Node-style handlers in ../api, run through a tiny req/res shim
//   /latter-day-stats, /urim,       the family apps, forwarded over service bindings (no extra HTTP hop,
//   /peepstone, /omni (+ /*)        Host stays samuelbaird.com). Without a binding (local dev, or before
//                                   an app is deployed) it falls back to proxying the app's public origin.
import process from 'node:process';

// The handlers read process.env when their module first evaluates, so they are imported only after
// the Worker's vars and secrets have been copied into process.env (first /api request).
const API = {
  '/api/scout': () => import('../api/scout.js'),
  '/api/admin/dashboard': () => import('../api/admin/dashboard.js'),
  '/api/admin/tickets': () => import('../api/admin/tickets.js'),
};

let envReady = false;
function loadEnv(env) {
  if (envReady) return;
  for (const [k, v] of Object.entries(env)) if (typeof v === 'string' && process.env[k] === undefined) process.env[k] = v;
  envReady = true;
}

// Keep in step with packages/family/projects.json (basePath, origin).
const APPS = [
  { base: '/latter-day-stats', binding: 'LATTER_DAY_STATS', origin: 'https://latterdaystats.samuelbaird.com' },
  { base: '/urim', binding: 'URIM', origin: 'https://urim.samuelbaird.com' },
  { base: '/peepstone', binding: 'PEEPSTONE', origin: 'https://peepstone.vercel.app' },
  { base: '/omni', binding: 'OMNI', origin: 'https://omni.samuelbaird.com', noindex: true },
];

const BASE_HEADERS = {
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
};

function withHeaders(res, extra) {
  const out = new Response(res.body, res);
  for (const [k, v] of Object.entries({ ...BASE_HEADERS, ...extra })) if (!out.headers.has(k)) out.headers.set(k, v);
  return out;
}

async function forward(app, request, env) {
  const svc = env[app.binding];
  let res;
  if (svc && typeof svc.fetch === 'function') {
    res = await svc.fetch(request);
  } else {
    const url = new URL(request.url);
    const target = new URL(url.pathname + url.search, app.origin);
    const headers = new Headers(request.headers);
    headers.set('x-forwarded-host', url.host);
    res = await fetch(target, { method: request.method, headers, body: request.body, redirect: 'manual' });
  }
  return withHeaders(res, app.noindex ? { 'X-Robots-Tag': 'noindex, nofollow, noarchive' } : {});
}

// --- Vercel-style (req, res) shim for the handlers in ../api ---------------------------------------

async function nodeRequest(request, url) {
  const headers = {};
  for (const [k, v] of request.headers) headers[k.toLowerCase()] = v;
  let body;
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    const text = await request.text();
    const type = headers['content-type'] || '';
    if (type.includes('application/json')) { try { body = text ? JSON.parse(text) : undefined; } catch { body = text; } }
    else if (type.includes('application/x-www-form-urlencoded')) body = Object.fromEntries(new URLSearchParams(text));
    else body = text || undefined;
  }
  return { method: request.method, url: url.pathname + url.search, headers, query: Object.fromEntries(url.searchParams), body };
}

function nodeResponse() {
  let resolve;
  const done = new Promise((r) => { resolve = r; });
  const headers = new Headers();
  const res = {
    statusCode: 200,
    headersSent: false,
    setHeader(k, v) { headers.set(k, Array.isArray(v) ? v.join(', ') : String(v)); return res; },
    getHeader(k) { return headers.get(k) ?? undefined; },
    removeHeader(k) { headers.delete(k); },
    status(code) { res.statusCode = code; return res; },
    json(obj) {
      if (!headers.has('content-type')) headers.set('content-type', 'application/json; charset=utf-8');
      return res.end(JSON.stringify(obj));
    },
    send(data) {
      if (data !== null && typeof data === 'object' && !(data instanceof Uint8Array)) return res.json(data);
      return res.end(data);
    },
    end(data) {
      if (res.headersSent) return res;
      res.headersSent = true;
      const noBody = res.statusCode === 204 || res.statusCode === 304;
      resolve(new Response(noBody ? null : (data ?? null), { status: res.statusCode, headers }));
      return res;
    },
  };
  return { res, done };
}

async function runApi(handler, request, url) {
  const req = await nodeRequest(request, url);
  const { res, done } = nodeResponse();
  try {
    await handler(req, res);
  } catch (err) {
    console.error(`api ${url.pathname} failed`, err);
    if (!res.headersSent) res.status(500).json({ error: 'internal_error' });
  }
  if (!res.headersSent) res.status(204).end(); // handler returned without responding
  return withHeaders(await done);
}

// ---------------------------------------------------------------------------------------------------

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    for (const app of APPS) {
      if (path === app.base || path.startsWith(app.base + '/')) return forward(app, request, env);
    }

    if (path.startsWith('/api/')) {
      // Vercel treated /api/foo.js as /api/foo; keep that, and keep trailing-slash URLs working.
      const key = path.replace(/\.js$/, '').replace(/\/+$/, '');
      if (API[key]) {
        loadEnv(env);
        const mod = await API[key]();
        return runApi(mod.default || mod, request, url);
      }
      return withHeaders(new Response(JSON.stringify({ error: 'not_found' }), {
        status: 404, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
      }));
    }

    return env.ASSETS.fetch(request);
  },
};
