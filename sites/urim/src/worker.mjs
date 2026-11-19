// Urim on Cloudflare Workers: the hosted MCP (same tools as api/mcp.js, via src/mcp-core.mjs) plus the
// static site/ through the ASSETS binding, with vercel.json's rewrites and old-host redirect.
// Workers have no filesystem, so the data is bundled in (wrangler.jsonc "rules": .tsv as Text, JSON natively).
import { createMcp, respond } from './mcp-core.mjs';
import { parseWords } from '../deseret/src/index.mjs';
import api from '../data/api.json';
import wordsTsv from '../deseret/data/words.tsv';
import heteronyms from '../deseret/data/heteronyms.json';
import overrides from '../deseret/data/overrides.json';

// Parse the Deseret word list at startup (global scope, ~140 ms of CPU) rather than inside a request.
const words = parseWords(wordsTsv);
const handle = createMcp({ concepts: api.concepts, deseretData: () => ({ words, heteronyms, overrides }) });

const OLD_HOST = 'urim.samuelbaird.com';
const CANONICAL = 'https://samuelbaird.com/urim/';
const PREFIX = '/urim';

async function mcp(request) {
  const out = await respond(handle, request.method, () => request.text());
  return new Response(out.body, { status: out.status, headers: out.headers });
}

const redirect = (location, status) => new Response(null, { status, headers: { Location: location } });

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // vercel.json "redirects": the old host 301s every page to samuelbaird.com/urim, except /urim/* and /api/*.
    // (Only reaches the Worker for paths in assets.run_worker_first; see CLAUDE.md "Cloudflare".)
    if (url.hostname === OLD_HOST && !/^(urim(\/|$)|api\/)/.test(path.slice(1))) {
      return redirect(CANONICAL + path.slice(1) + url.search, 301);
    }

    if (path === '/mcp' || path === '/api/mcp') return mcp(request);

    // vercel.json "rewrites": /urim -> /, /urim/:path* -> /:path* (samuelbaird.com proxies /urim/* here).
    if (path === PREFIX || path.startsWith(PREFIX + '/')) {
      // trailingSlash: false
      if (path.length > PREFIX.length && path.endsWith('/')) return redirect(path.replace(/\/+$/, '') + url.search, 308);
      const inner = path.slice(PREFIX.length) || '/';
      if (inner === '/mcp' || inner === '/api/mcp') return mcp(request); // /urim/mcp is canonical
      const res = await env.ASSETS.fetch(new Request(new URL(inner + url.search, url), request));
      // Asset redirects (cleanUrls: /about.html -> /about) must keep the /urim prefix.
      const loc = res.headers.get('Location');
      if (loc && res.status >= 300 && res.status < 400) {
        const target = new URL(loc, new URL(inner, url));
        if (target.origin === url.origin && !target.pathname.startsWith(PREFIX + '/')) {
          const headers = new Headers(res.headers);
          headers.set('Location', PREFIX + (target.pathname === '/' ? '' : target.pathname) + target.search);
          return new Response(res.body, { status: res.status, headers });
        }
      }
      return res;
    }

    return env.ASSETS.fetch(request); // other /api/* paths: 404 from assets, as on Vercel
  },
};
