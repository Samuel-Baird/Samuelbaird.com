import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { load } from '../src/load.mjs';
import { createWiki } from '../src/wiki.mjs';

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const { wiki, corpus } = load();

test('the corpus covers every kind of source on the wiki', () => {
  for (const k of ['article', 'page', 'letter', 'library', 'resource', 'video', 'font', 'book', 'quote']) assert.ok(corpus.counts[k] > 0, k);
  assert.equal(corpus.counts.letter, 38);
  for (const r of corpus.records) {
    assert.ok(r.url.startsWith('https://deseret.wiki/'), `${r.id} url ${r.url}`);
    assert.ok(r.id && r.title && r.kind, JSON.stringify(r).slice(0, 80));
  }
  assert.equal(new Set(corpus.records.map((r) => r.id)).size, corpus.records.length, 'ids are unique');
});

test('no links to the private research archive, and it is not named', () => {
  const raw = JSON.stringify(corpus);
  assert.doesNotMatch(raw, /corpus\.restorationcommons\.org/);
  assert.doesNotMatch(raw, /Gospel Scholar/i);
});

test('article anchors match the ids the built site gives its headings', { skip: !fs.existsSync(path.join(ROOT, '..', 'deseret', 'dist', 'wiki', 'deseret-alphabet', 'index.html')) }, () => {
  const html = fs.readFileSync(path.join(ROOT, '..', 'deseret', 'dist', 'wiki', 'deseret-alphabet', 'index.html'), 'utf8');
  const ids = new Set([...html.matchAll(/id="([^"]+)"/g)].map((m) => m[1]));
  for (const r of corpus.records.filter((x) => x.kind === 'article' && x.url.includes('#'))) {
    assert.ok(ids.has(decodeURIComponent(r.url.split('#')[1])), `missing anchor ${r.url}`);
  }
});

test('search finds the article section and returns citable urls', () => {
  const r = wiki.search('gold coin Holiness to the Lord');
  assert.ok(r.results.length);
  assert.ok(r.results.every((h) => h.url.startsWith('https://deseret.wiki/')));
  assert.ok(r.results.slice(0, 3).some((h) => h.kind === 'article'));
});

test('search by kind and for people', () => {
  const f = wiki.search('Noto Sans', { kind: 'font' });
  assert.equal(f.results[0].title, 'Noto Sans Deseret');
  const v = wiki.search('Saints Unscripted', { kind: 'video' });
  assert.match(v.results[0].source_url, /youtube\.com/);
  const t = wiki.search('Brigham Young 1868 conference', { kind: 'library' });
  assert.match(t.results[0].source_url, /pulpit\.restorationcommons\.org/);
});

test('read returns the full record, a citation and neighbours', () => {
  const id = corpus.records.find((r) => r.kind === 'article' && r.url.endsWith('#encodings')).id;
  const r = wiki.read(id);
  assert.match(r.citation, /Deseret Wiki, https:\/\/deseret\.wiki\/wiki\/deseret-alphabet\/#encodings/);
  assert.match(r.license, /CC BY-SA/);
  assert.ok(r.previous && r.next);
  assert.ok(r.text.length > 200);
  assert.throws(() => wiki.read('nope'), /No wiki record/);
});

test('contents lists kinds, then records', () => {
  const c = wiki.contents();
  assert.ok(c.kinds.find((k) => k.kind === 'article'));
  const l = wiki.contents('letter');
  assert.equal(l.records.length, 38);
  assert.throws(() => wiki.contents('nope'), /Unknown kind/);
});

test('build script reads quotes.json and new page lists from a wiki checkout', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'dw-'));
  const w = (p, s) => { fs.mkdirSync(path.dirname(path.join(dir, p)), { recursive: true }); fs.writeFileSync(path.join(dir, p), s); };
  w('src/pages/wiki/sample.md', '---\nheading: Sample\n---\n\nIntro text.\n\n## First part\n\nAlpha beta.\n\n## First part\n\nAgain.\n');
  w('src/pages/quotes.astro', '---\nimport Base from "../layouts/Base.astro";\nconst extra = [{ title: "A new list", note: "Something", url: "https://example.org" }];\n---\n<Base title="Quotes — Deseret Wiki"><h1>Quotes</h1><p>Words about the alphabet, gathered from sermons and letters.</p>{extra.map((x) => (<p>{x.title}</p>))}</Base>');
  w('src/data/quotes.json', JSON.stringify([{ id: 'by-1868', text: 'Teach the alphabet.', by: 'Someone', date: '1868', url: 'https://example.org/q' }]));
  const out = path.join(dir, 'wiki.json');
  execFileSync(process.execPath, [path.join(ROOT, 'scripts', 'build-wiki.mjs')], { env: { ...process.env, DESERET_WIKI: dir, DESERET_WIKI_OUT: out }, stdio: 'pipe' });
  const built = JSON.parse(fs.readFileSync(out, 'utf8'));
  const ids = built.records.map((r) => r.id);
  assert.ok(ids.includes('article:wiki:sample'));
  assert.ok(ids.includes('article:wiki:sample#first-part'));
  assert.ok(ids.includes('article:wiki:sample#first-part-1'), 'duplicate headings get -1');
  const q = built.records.find((r) => r.kind === 'quote');
  assert.equal(q.url, 'https://deseret.wiki/quotes/#by-1868');
  assert.equal(q.source_url, 'https://example.org/q');
  assert.equal(q.author, 'Someone');
  assert.ok(built.records.find((r) => r.id === 'quotes:extra:1'), 'unknown lists use the generic mapping');
  const page = built.records.find((r) => r.id === 'page:quotes');
  assert.match(page.text, /Words about the alphabet/);
  assert.doesNotMatch(page.text, /extra\.map/);
  const s = createWiki(built).search('teach alphabet');
  assert.equal(s.results[0].kind, 'quote');
  fs.rmSync(dir, { recursive: true, force: true });
});
