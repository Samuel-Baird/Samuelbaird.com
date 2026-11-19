import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { Readable } from 'node:stream';
import { fileURLToPath } from 'node:url';
import handler from '../api/mcp.js';
import { createHandler } from '../src/tools.mjs';

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');

// minimal stand-ins for Vercel's req/res
async function post(body, method = 'POST') {
  const req = Readable.from([Buffer.from(typeof body === 'string' ? body : JSON.stringify(body))]);
  req.method = method;
  const res = { statusCode: 200, headers: {}, body: '', setHeader(k, v) { this.headers[k.toLowerCase()] = v; }, end(s) { this.body = s || ''; this.done = true; } };
  await handler(req, res);
  return { status: res.statusCode, headers: res.headers, json: res.body ? JSON.parse(res.body) : null };
}
const call = async (name, args) => (await post({ jsonrpc: '2.0', id: 9, method: 'tools/call', params: { name, arguments: args } })).json.result;

test('hosted: initialize, tools/list, CORS', async () => {
  const init = await post({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-06-18' } });
  assert.equal(init.status, 200);
  assert.equal(init.json.result.protocolVersion, '2025-06-18');
  assert.equal(init.json.result.serverInfo.name, 'deseret');
  assert.equal(init.headers['access-control-allow-origin'], '*');
  const list = await post({ jsonrpc: '2.0', id: 2, method: 'tools/list' });
  const names = list.json.result.tools.map((t) => t.name);
  assert.deepEqual(names, ['to_deseret', 'deseret_word', 'from_deseret', 'search_wiki', 'read_wiki', 'wiki_contents']);
  assert.ok(!names.includes('deseret_file'), 'no file access on the hosted server');
});

test('hosted: notifications, batches, bad JSON, GET', async () => {
  assert.equal((await post({ jsonrpc: '2.0', method: 'notifications/initialized' })).status, 202);
  const b = await post([{ jsonrpc: '2.0', id: 1, method: 'ping' }, { jsonrpc: '2.0', id: 2, method: 'nope' }]);
  assert.equal(b.json.length, 2);
  assert.equal(b.json[1].error.code, -32601);
  assert.equal((await post('{not json')).status, 400);
  assert.equal((await post('', 'GET')).status, 405);
});

test('hosted: to_deseret reports unknown words', async () => {
  const r = await call('to_deseret', { text: 'The Deseret Alphabet, Qwrtp.' });
  assert.ok(!r.isError);
  assert.equal(r.structuredContent.deseret, '𐐜 𐐔𐐯𐑆𐐲𐑉𐐯𐐻 𐐈𐑊𐑁𐐲𐐺𐐯𐐻, Qwrtp.');
  assert.deepEqual(r.structuredContent.unknown, [{ word: 'Qwrtp', count: 1 }]);
  assert.match(r.structuredContent.note, /left in Latin letters/);
  assert.equal(JSON.parse(r.content[0].text).deseret, r.structuredContent.deseret);
});

test('hosted: errors come back as tool errors', async () => {
  assert.equal((await call('to_deseret', { text: '' })).isError, true);
  assert.equal((await call('deseret_word', { word: 'two words' })).isError, true);
  assert.equal((await call('from_deseret', { text: 'latin only' })).isError, true);
  assert.equal((await call('read_wiki', { id: 'missing' })).isError, true);
  const r = await post({ jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'deseret_file', arguments: { path: 'x' } } });
  assert.equal(r.json.error.code, -32602);
});

test('hosted: search, read and Deseret-script queries', async () => {
  const s = (await call('search_wiki', { query: 'Who carved the type for the 1868 books?' })).structuredContent;
  assert.ok(s.results.length > 0);
  const rd = (await call('read_wiki', { id: s.results[0].id })).structuredContent;
  assert.ok(rd.citation.includes(rd.url));
  const d = (await call('search_wiki', { query: '𐑁𐐪𐑌𐐻𐑅', kind: 'article' })).structuredContent;
  assert.ok(d.results.length > 0, 'a Deseret query also searches its Latin reading');
  const c = (await call('wiki_contents', {})).structuredContent;
  assert.ok(c.kinds.length >= 9);
});

test('local: deseret_file writes beside the input and will not overwrite', async () => {
  const handle = createHandler({ local: true });
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'dm-'));
  const src = path.join(dir, 'talk.md');
  fs.writeFileSync(src, '---\ntitle: A talk\n---\n\nThe [alphabet](https://deseret.wiki/) is phonemic. Qwrtp.\n');
  const run = (args) => handle({ jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: 'deseret_file', arguments: args } });
  const r = (await run({ path: src })).result.structuredContent;
  assert.equal(r.output_path, path.join(dir, 'talk.dsrt.md'));
  assert.equal(r.format, 'markdown');
  const out = fs.readFileSync(r.output_path, 'utf8');
  assert.ok(out.startsWith('---\ntitle: A talk\n---'));
  assert.match(out, /\[𐐰𐑊𐑁𐐲𐐺𐐯𐐻\]\(https:\/\/deseret\.wiki\/\)/);
  assert.deepEqual(r.unknown.map((u) => u.word), ['Qwrtp']);
  assert.equal((await run({ path: src })).result.isError, true, 'refuses to overwrite');
  assert.ok(!(await run({ path: src, overwrite: true })).result.isError);
  assert.equal((await run({ path: src, output_path: src, overwrite: true })).result.isError, true, 'never writes over the input');
  assert.equal((await run({ path: path.join(dir, 'none.md') })).result.isError, true);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('local: stdio server speaks newline-delimited JSON-RPC', async () => {
  const child = spawn(process.execPath, [path.join(ROOT, 'bin', 'deseret-mcp.mjs')], { stdio: ['pipe', 'pipe', 'inherit'] });
  const lines = [];
  let buf = '';
  const got = new Promise((resolve) => child.stdout.on('data', (d) => {
    buf += d;
    let i;
    while ((i = buf.indexOf('\n')) >= 0) { lines.push(JSON.parse(buf.slice(0, i))); buf = buf.slice(i + 1); }
    if (lines.length === 3) resolve();
  }));
  for (const m of [
    { jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-11-25' } },
    { jsonrpc: '2.0', method: 'notifications/initialized' },
    { jsonrpc: '2.0', id: 2, method: 'tools/list' },
    { jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'deseret_word', arguments: { word: 'bee' } } },
  ]) child.stdin.write(JSON.stringify(m) + '\n');
  await got;
  child.kill();
  assert.equal(lines[0].result.protocolVersion, '2025-11-25');
  assert.ok(lines[1].result.tools.some((t) => t.name === 'deseret_file'));
  assert.equal(lines[2].result.structuredContent.deseret, '𐐺'); // syllabic value: the letter Bee alone
});
