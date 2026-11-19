// Urim hosted MCP on Vercel: read-only access to the atlas over streamable HTTP (stateless, JSON responses).
// The tools live in src/mcp-core.mjs, shared with the Cloudflare Worker (src/worker.mjs); this file only
// reads the data from disk and adapts Node's req/res. No auth, no state, no user data.
const fs = require('fs');
const path = require('path');
const DATA = require('../data/api.json').concepts;

const DESERET_DIR = path.join(__dirname, '..', 'deseret', 'data');
const readDeseret = (f) => fs.readFileSync(path.join(DESERET_DIR, f), 'utf8');

const core = import('../src/mcp-core.mjs').then((m) => ({
  respond: m.respond,
  handle: m.createMcp({
    concepts: DATA,
    deseretData: () => ({ words: readDeseret('words.tsv'), heteronyms: readDeseret('heteronyms.json'), overrides: readDeseret('overrides.json') }),
  }),
}));

async function readBody(req) {
  if (req.body !== undefined && req.body !== null) return typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
  const chunks = [];
  for await (const ch of req) chunks.push(ch);
  return Buffer.concat(chunks).toString('utf8');
}

module.exports = async function mcp(req, res) {
  const { respond, handle } = await core;
  const out = await respond(handle, req.method, () => readBody(req));
  res.statusCode = out.status;
  for (const [k, v] of Object.entries(out.headers)) res.setHeader(k, v);
  res.end(out.body === null ? undefined : out.body);
};
