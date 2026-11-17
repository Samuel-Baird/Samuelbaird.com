// Local preview: serves site/ with clean URLs (as vercel.json does) and the MCP at /api/mcp.
// Run: npm run dev   (PORT, default 4321)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import mcp from '../api/mcp.js';

const SITE = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'site');
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript; charset=utf-8', '.svg': 'image/svg+xml', '.txt': 'text/plain' };
const port = Number(process.env.PORT) || 4321;
http.createServer((req, res) => {
  const url = new URL(req.url, 'http://x');
  if (url.pathname === '/api/mcp') return mcp(req, res);
  let p = path.join(SITE, decodeURIComponent(url.pathname));
  if (!p.startsWith(SITE)) { res.statusCode = 403; return res.end(); }
  if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, 'index.html');
  if (!fs.existsSync(p) && fs.existsSync(p + '.html')) p += '.html';
  if (!fs.existsSync(p)) { res.statusCode = 404; return res.end('Not found'); }
  res.setHeader('Content-Type', TYPES[path.extname(p)] || 'application/octet-stream');
  fs.createReadStream(p).pipe(res);
}).listen(port, () => console.log(`http://localhost:${port}`));
