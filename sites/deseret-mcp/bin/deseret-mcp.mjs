#!/usr/bin/env node
// Deseret MCP, local: stdio transport (newline-delimited JSON-RPC), no dependencies.
// Everything the hosted server does, plus deseret_file for whole files on this computer.
//   claude mcp add deseret -- node /path/to/deseret-mcp/bin/deseret-mcp.mjs
// Also a small CLI:  deseret-mcp to "some text"  |  deseret-mcp from "𐐔𐐯𐑆𐐲𐑉𐐯𐐻"  |  deseret-mcp file notes.md
import readline from 'node:readline';
import { createHandler } from '../src/tools.mjs';

const [cmd, ...rest] = process.argv.slice(2);
const handle = createHandler({ local: true });

if (cmd && cmd !== 'serve') {
  const tool = { to: 'to_deseret', from: 'from_deseret', word: 'deseret_word', file: 'deseret_file', search: 'search_wiki', read: 'read_wiki' }[cmd];
  if (!tool) {
    console.error('usage: deseret-mcp [serve] | to <text> | from <text> | word <word> | file <path> | search <query> | read <id>');
    process.exit(2);
  }
  const arg = rest.join(' ');
  const key = { to_deseret: 'text', from_deseret: 'text', deseret_word: 'word', deseret_file: 'path', search_wiki: 'query', read_wiki: 'id' }[tool];
  const reply = await handle({ jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: tool, arguments: { [key]: arg } } });
  const r = reply.result;
  if (r.isError) { console.error(r.content[0].text); process.exit(1); }
  const s = r.structuredContent;
  if (tool === 'to_deseret') { console.log(s.deseret); if (s.unknown.length) console.error(`not transliterated: ${s.unknown.map((u) => u.word).join(', ')}`); }
  else if (tool === 'from_deseret') console.log(s.latin);
  else console.log(JSON.stringify(s, null, 2));
} else {
  const rl = readline.createInterface({ input: process.stdin, terminal: false });
  const send = (o) => process.stdout.write(JSON.stringify(o) + '\n');
  rl.on('line', async (line) => {
    if (!line.trim()) return;
    let msg;
    try { msg = JSON.parse(line); } catch { return send({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Parse error' } }); }
    const batch = Array.isArray(msg);
    const replies = (await Promise.all((batch ? msg : [msg]).map((m) => handle(m)))).filter(Boolean);
    if (replies.length) send(batch ? replies : replies[0]);
  });
}
