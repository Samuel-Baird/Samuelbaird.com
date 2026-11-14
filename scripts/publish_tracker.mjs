// Validate courses/<course>/tracker.json and copy it to the site repo.
// usage: node scripts/publish_tracker.mjs me3410 [../Samuelbaird.com]
import fs from 'node:fs';
import path from 'node:path';

const course = process.argv[2] || 'me3410';
const site = path.resolve(process.argv[3] || '../Samuelbaird.com');
const src = path.resolve('courses', course, 'tracker.json');
const dst = path.join(site, 'learn', course, 'tracker.json');
const d = JSON.parse(fs.readFileSync(src, 'utf8'));
const fail = (m) => { console.error('INVALID:', m); process.exit(1); };

const STATUSES = new Set(['todo', 'in_progress', 'pdf_ready', 'submitted', 'graded', 'blocked']);
if (!d.items?.length) fail('no items');
const ids = new Set();
for (const it of d.items) {
  for (const k of ['id', 'title', 'group', 'pts', 'due_iso', 'due_local', 'plan', 'status', 'deliver', 'url'])
    if (it[k] === undefined || it[k] === '') fail(`${it.id}: missing ${k}`);
  if (ids.has(it.id)) fail(`duplicate ${it.id}`);
  ids.add(it.id);
  if (!STATUSES.has(it.status)) fail(`${it.id}: bad status ${it.status}`);
  if (!/^https:\/\/uvu\.instructure\.com\/courses\/\d+\/assignments\/\d+$/.test(it.url)) fail(`${it.id}: bad url`);
}
const txt = JSON.stringify(d);
if (/\bNaN\b|undefined/.test(txt)) fail('NaN/undefined in data');
// The public tracker carries status and deliverable names only: no solutions, answers or handout text.
if (/solution manual|answer key/i.test(txt)) fail('mentions answer material');
fs.mkdirSync(path.dirname(dst), { recursive: true });
fs.copyFileSync(src, dst);
console.log(`ok: ${d.items.length} items -> ${dst}`);
