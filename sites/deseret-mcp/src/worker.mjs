// Deseret MCP on Cloudflare Workers: the same hosted endpoint as api/mcp.js (streamable HTTP, stateless,
// JSON responses, no auth, no data kept) plus the static site/ through the ASSETS binding.
// Workers have no filesystem, so data/ is bundled in (wrangler.jsonc "rules": .tsv as Text, JSON natively).
import { createHandler } from './tools.mjs';
import { load, provideData } from './load.mjs';
import overrides from '../data/overrides.json';
import wiki from '../data/wiki.json';
import cmudict from '../data/cmudict.tsv';

provideData({ overrides, wiki, cmudict });
// Parse the dictionary at startup (global scope, ~150 ms of CPU) rather than inside the first request.
load();

const handle = createHandler({ local: false });

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Accept, Authorization, Mcp-Session-Id, Mcp-Protocol-Version',
  'Access-Control-Expose-Headers': 'Mcp-Session-Id',
};

const json = (status, body, extra = {}) =>
  new Response(JSON.stringify(body), { status, headers: { ...CORS, 'Content-Type': 'application/json', ...extra } });

async function mcp(request) {
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
  if (request.method !== 'POST') return new Response(null, { status: 405, headers: { ...CORS, Allow: 'POST, OPTIONS' } });
  let body;
  try {
    body = JSON.parse(await request.text());
  } catch {
    return json(400, { jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Parse error' } });
  }
  const batch = Array.isArray(body);
  const replies = (await Promise.all((batch ? body : [body]).map((m) => handle(m || {})))).filter(Boolean);
  if (!replies.length) return new Response(null, { status: 202, headers: CORS });
  return json(200, batch ? replies : replies[0], { 'Cache-Control': 'no-store' });
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (pathname === '/mcp' || pathname === '/api/mcp') return mcp(request); // /mcp is canonical; /api/mcp kept for existing connectors
    return env.ASSETS.fetch(request); // other /api/* paths: 404 from assets, as on Vercel
  },
};
