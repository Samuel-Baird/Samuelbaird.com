// Validate courses/<course>/course.json and copy it to the site repo.
// usage: node scripts/publish.mjs me3320 [../../sites/samuelbaird.com]  (run from projects/school in the monorepo)
import fs from 'node:fs';
import path from 'node:path';

const course = process.argv[2] || 'me3320';
const site = path.resolve(process.argv[3] || '../../sites/samuelbaird.com');
const src = path.resolve('courses', course, 'course.json');
const dst = path.join(site, 'learn', course, 'course.json');

const d = JSON.parse(fs.readFileSync(src, 'utf8'));
const fail = (m) => { console.error('INVALID:', m); process.exit(1); };

if (!d.units?.length) fail('no units');
const ids = new Set();
for (const u of d.units) {
  for (const k of ['id', 'title', 'tag', 'why', 'videos', 'know', 'eq', 'problems', 'book'])
    if (!u[k] || (Array.isArray(u[k]) && !u[k].length)) fail(`${u.id}: missing ${k}`);
  for (const v of u.videos) if (!/^[\w-]{11}$/.test(v.id)) fail(`${u.id}: bad video id ${v.id}`);
  for (const p of u.problems) {
    if (ids.has(p.id)) fail(`duplicate problem ${p.id}`);
    ids.add(p.id);
    if (!p.solution?.steps?.length || !p.solution?.answers?.length) fail(`${p.id}: empty solution`);
  }
}
for (const m of d.mocks || []) for (const p of m.problems) if (!ids.has(p)) fail(`mock ${m.id}: unknown problem ${p}`);
const txt = JSON.stringify(d);
if (txt.includes('<<')) fail('unfilled placeholder');
if (/\bNaN\b|undefined/.test(txt)) fail('NaN/undefined in data');
// the public page carries references and original writing only
if (/solution manual|instructor'?s manual/i.test(txt)) fail('mentions a solution manual');

fs.mkdirSync(path.dirname(dst), { recursive: true });
fs.copyFileSync(src, dst);
console.log(`ok: ${d.units.length} units, ${ids.size} problems, ${d.units.reduce((a, u) => a + u.videos.length, 0)} videos -> ${dst}`);
