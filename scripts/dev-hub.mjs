// Local stand-in for samuelbaird.com's production routing (sites/samuelbaird.com/vercel.json rewrites).
//   node scripts/dev-hub.mjs [port=4310]
// /urim/*                      -> sites/urim/site (static)
// /latter-day-stats, /omni, /peepstone -> that app's `next dev` (start it with its base path; ports below)
// everything else              -> sites/samuelbaird.com (static, clean URLs)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PORT = Number(process.argv[2] || 4310);
const STATIC = [['/urim', 'sites/urim/site'], ['', 'sites/samuelbaird.com']];
const APPS = { '/latter-day-stats': 3050, '/omni': 3040, '/peepstone': 3060 };
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp', '.jpg': 'image/jpeg', '.ttf': 'font/ttf', '.txt': 'text/plain; charset=utf-8', '.xml': 'application/xml', '.csv': 'text/csv', '.pdf': 'application/pdf', '.woff2': 'font/woff2' };

function serveFile(res, dir, rel) {
  const base = path.join(ROOT, dir);
  const tries = [rel, rel + '.html', path.join(rel, 'index.html')];
  for (const t of tries) {
    const f = path.join(base, t);
    if (!f.startsWith(base)) break;
    if (fs.existsSync(f) && fs.statSync(f).isFile()) {
      res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' });
      return fs.createReadStream(f).pipe(res);
    }
  }
  const nf = path.join(base, '404.html');
  res.writeHead(404, { 'content-type': 'text/html; charset=utf-8' });
  res.end(fs.existsSync(nf) ? fs.readFileSync(nf) : 'Not found');
}

http.createServer((req, res) => {
  const url = new URL(req.url, 'http://x');
  const p = decodeURIComponent(url.pathname);
  const app = Object.keys(APPS).find((b) => p === b || p.startsWith(b + '/'));
  if (app) {
    const up = http.request({ host: '127.0.0.1', port: APPS[app], path: req.url, method: req.method, headers: req.headers }, (r) => { res.writeHead(r.statusCode, r.headers); r.pipe(res); });
    up.on('error', () => { res.writeHead(502); res.end(`${app} is not running on port ${APPS[app]}`); });
    return req.pipe(up);
  }
  const [prefix, dir] = STATIC.find(([b]) => b === '' || p === b || p.startsWith(b + '/'));
  serveFile(res, dir, p.slice(prefix.length) || '/');
}).listen(PORT, () => console.log(`dev hub on http://localhost:${PORT}`));
