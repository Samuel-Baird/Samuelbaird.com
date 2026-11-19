// The hosted MCP (api/mcp.js on Vercel, src/mcp-core.mjs shared with the Cloudflare Worker). Run: npm test
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { Readable } from 'node:stream';

const require = createRequire(import.meta.url);
const handler = require('../api/mcp.js');

async function call(method, body) {
  const req = Readable.from(body === undefined ? [] : [Buffer.from(typeof body === 'string' ? body : JSON.stringify(body))]);
  req.method = method;
  const res = { headers: {}, statusCode: 200, setHeader(k, v) { this.headers[k.toLowerCase()] = v; } };
  await new Promise((resolve) => { res.end = (b) => { res.body = b; resolve(); }; handler(req, res); });
  return { status: res.statusCode, headers: res.headers, json: res.body ? JSON.parse(res.body) : undefined };
}
const rpc = (id, method, params) => ({ jsonrpc: '2.0', id, method, params });
const tool = async (name, args) => JSON.parse((await call('POST', rpc(9, 'tools/call', { name, arguments: args }))).json.result.content[0].text);

test('initialize, tools/list and CORS', async () => {
  const init = await call('POST', rpc(1, 'initialize', { protocolVersion: '2025-06-18' }));
  assert.equal(init.status, 200);
  assert.equal(init.headers['access-control-allow-origin'], '*');
  assert.equal(init.json.result.protocolVersion, '2025-06-18');
  assert.equal(init.json.result.serverInfo.name, 'urim');
  const list = await call('POST', rpc(2, 'tools/list'));
  assert.deepEqual(list.json.result.tools.map((t) => t.name), ['lookup_term', 'match_glossary', 'earliest_usage', 'to_deseret', 'search_concepts', 'find_variants']);
});

test('HTTP edges: OPTIONS, GET, bad JSON, notification, batch', async () => {
  assert.equal((await call('OPTIONS')).status, 204);
  const get = await call('GET');
  assert.equal(get.status, 405);
  assert.equal(get.headers.allow, 'POST, OPTIONS');
  const bad = await call('POST', '{nope');
  assert.equal(bad.status, 400);
  assert.equal(bad.json.error.code, -32700);
  assert.equal((await call('POST', { jsonrpc: '2.0', method: 'notifications/initialized' })).status, 202);
  const batch = await call('POST', [rpc(1, 'ping'), rpc(2, 'nope')]);
  assert.equal(batch.json.length, 2);
  assert.equal(batch.json[1].error.code, -32601);
});

test('tools answer from the atlas and the Deseret engine', async () => {
  const look = await tool('lookup_term', { term: 'endowment', lang: 'pt' });
  assert.ok(look.results.length > 0);
  assert.ok(look.results[0].pt.preferred);
  const ds = await tool('to_deseret', { text: 'The Book of Mormon' });
  assert.match(ds.deseret, /[\u{10400}-\u{1044F}]/u);
  assert.equal(ds.words, 4);
  const strict = await tool('to_deseret', { text: 'Zxqvbn read', confident_only: true });
  assert.deepEqual(strict.left_in_latin.includes('zxqvbn'), true);
});
