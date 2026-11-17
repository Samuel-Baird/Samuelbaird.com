// Deseret MCP, hosted: streamable HTTP, stateless, JSON responses. No auth, no state, no user data kept.
// Same tools as the local server except deseret_file (the hosted server never reads client paths).
import { createHandler } from '../src/tools.mjs';
import { load } from '../src/load.mjs';

const handle = createHandler({ local: false });

async function readBody(req) {
  if (req.body !== undefined && req.body !== null) return typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
  const chunks = [];
  for await (const ch of req) chunks.push(ch);
  return Buffer.concat(chunks).toString('utf8');
}

export default async function mcp(req, res) {
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
    return res.end(JSON.stringify({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Parse error' } }));
  }
  load(); // warm the dictionary on the first request of a cold start
  const batch = Array.isArray(body);
  const replies = (await Promise.all((batch ? body : [body]).map((m) => handle(m || {})))).filter(Boolean);
  if (!replies.length) {
    res.statusCode = 202;
    return res.end();
  }
  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(batch ? replies : replies[0]));
}
