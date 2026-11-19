import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { load } from '../src/load.mjs';
import { phonesToDeseret, applyCase, PHONE, LETTERS, historical1868 } from '../src/dsrt.mjs';

const { engine } = load();

test('the whole CMU dictionary is loaded', () => {
  assert.ok(engine.size > 120000, `only ${engine.size} words`);
});

test('ARPAbet maps to the wiki table, with Y+UW as 𐑏', () => {
  assert.equal(phonesToDeseret('B OY1'), '𐐺𐑎');
  assert.equal(phonesToDeseret('F Y UW1'), '𐑁𐑏');
  assert.equal(phonesToDeseret('B ER1 D'), '𐐺𐐲𐑉𐐼');
  assert.throws(() => phonesToDeseret('Q'), /unknown ARPAbet phone/);
  assert.equal(Object.keys(PHONE).length, 40);
  assert.equal(LETTERS.length, 40);
});

test('case is kept: lower, Title, UPPER', () => {
  assert.equal(engine.word('god').deseret, '𐑀𐐪𐐼');
  assert.equal(engine.word('God').deseret, '𐐘𐐪𐐼');
  assert.equal(engine.word('GOD').deseret, '𐐘𐐂𐐔');
  assert.equal(applyCase('I', '𐐴'), '𐐌');
});

test('the wiki overrides win over CMUdict', () => {
  assert.equal(engine.word('Deseret').deseret, '𐐔𐐯𐑆𐐲𐑉𐐯𐐻');
  assert.equal(engine.word('and').deseret, '𐐰𐑌𐐼');
  assert.equal(engine.word('not').deseret, '𐑌𐐱𐐻');
});

test('agrees with the Deseret Wiki word table (when a checkout is next to this repo)', { skip: !fs.existsSync(new URL('../../deseret/src/data/deseret-words.json', import.meta.url)) }, () => {
  const table = JSON.parse(fs.readFileSync(new URL('../../deseret/src/data/deseret-words.json', import.meta.url), 'utf8'));
  // the heteronyms are deliberate: the wiki takes CMUdict's first reading, we take the common one
  const expected = new Set(['lead', 'read', 'use', 'wind', 'live', 'tear', 'close', 'wound', 'bow', 'minute']);
  const diff = Object.entries(table).filter(([w, d]) => !expected.has(w) && engine.word(w)?.deseret !== d);
  assert.ok(diff.length <= 3, `differs from the wiki on: ${diff.map(([w]) => w).join(', ')}`);
});

test('words outside the dictionary are built from their parts and reported', () => {
  const r = engine.text('Their unfaithfulness grieved the gatekeepers.');
  const d = r.derived.find((x) => x.word === 'unfaithfulness');
  assert.ok(d, 'unfaithfulness should be derived');
  assert.match(d.from, /faithful/);
  assert.equal(r.stats.derived, 1);
  assert.equal(r.unknown.length, 0);
});

test('unknown words stay in Latin and are listed with counts', () => {
  const r = engine.text('Zxqvb said zxqvb twice; Qwrtp once.');
  assert.match(r.deseret, /Zxqvb/);
  assert.match(r.deseret, /Qwrtp/);
  assert.deepEqual(r.unknown.map((u) => u.word).sort(), ['Qwrtp', 'Zxqvb', 'zxqvb']);
  assert.equal(r.stats.unknown, 3);
});

test('strict mode leaves derived words in Latin and lists them as unknown', () => {
  const r = engine.text('unfaithfulness', { strict: true });
  assert.equal(r.deseret, 'unfaithfulness');
  assert.equal(r.unknown[0].word, 'unfaithfulness');
  assert.equal(r.derived[0].kept_in_latin, true);
});

test('names are not split into nonsense compounds', () => {
  for (const w of ['Shavian', 'covenantal', 'zarahemlites']) assert.equal(engine.word(w), null, w);
});

test('Book of Mormon names come from the overrides', () => {
  assert.equal(engine.word('Nephi').deseret, '𐐤𐐨𐑁𐐴');
  assert.equal(engine.word('Nephites').source, 'derived');
});

test('heteronyms follow the word before them and are reported', () => {
  const r = engine.text('I will read it. I have read it.');
  const [a, b] = r.deseret.match(/𐑉𐐨𐐼|𐑉𐐯𐐼/gu);
  assert.equal(a, '𐑉𐐨𐐼');
  assert.equal(b, '𐑉𐐯𐐼');
  assert.equal(r.heteronyms[0].word, 'read');
});

test('per-call spellings override everything', () => {
  const r = engine.text('I read it.', { spellings: { read: 'R EH1 D', Zxqvb: '𐑆𐐮𐐿' } });
  assert.match(r.deseret, /𐑉𐐯𐐼/);
  assert.throws(() => engine.text('x', { spellings: { x: 'QQ' } }), /unknown ARPAbet/);
});

test('digits, URLs, emails and IPA are untouched', () => {
  const r = engine.text('In 1854, see https://deseret.wiki/fonts/ or mail a@b.org; the 2nd /ˈdɛzərɛt/.');
  assert.match(r.deseret, /1854/);
  assert.match(r.deseret, /https:\/\/deseret\.wiki\/fonts\//);
  assert.match(r.deseret, /a@b\.org/);
  assert.match(r.deseret, /2nd/);
  assert.match(r.deseret, /ˈdɛzərɛt/);
});

test('markdown: frontmatter, code, link targets and footnotes are kept', () => {
  const md = '---\ntitle: Hello world\n---\n\n# The alphabet\n\nSee [the fonts](https://deseret.wiki/fonts/ "Fonts page") and `code here`.[^1]\n\n```js\nconst letters = 38;\n```\n\n[^1]: A note.\n';
  const r = engine.text(md, { format: 'markdown' });
  assert.ok(r.deseret.startsWith('---\ntitle: Hello world\n---'));
  assert.match(r.deseret, /\]\(https:\/\/deseret\.wiki\/fonts\/ "Fonts page"\)/);
  assert.match(r.deseret, /`code here`/);
  assert.match(r.deseret, /const letters = 38;/);
  assert.match(r.deseret, /\[\^1\]/);
  assert.match(r.deseret, /# 𐐜 𐐰𐑊𐑁𐐲𐐺𐐯𐐻/);
  assert.match(r.deseret, /\[𐑄 𐑁𐐪𐑌𐐻𐑅\]/);
});

test('html: only text nodes change', () => {
  const r = engine.text('<p class="lead">The <a href="/fonts/">fonts</a> &amp; <code>code</code></p>', { format: 'html' });
  assert.equal(r.deseret, '<p class="lead">𐐜 <a href="/fonts/">𐑁𐐪𐑌𐐻𐑅</a> &amp; <code>code</code></p>');
});

test('explain gives letters and alternatives', () => {
  const e = engine.explain('read');
  assert.equal(e.letters.length, 3);
  assert.equal(e.letters[0].name, 'Er');
  assert.equal(e.alternatives.length, 2);
  assert.ok(e.note);
  assert.equal(engine.explain('zxqvb').found, false);
});

test('Deseret back to Latin, with homophones and respellings reported', () => {
  const r = engine.fromDeseret('𐐜 𐐔𐐯𐑆𐐲𐑉𐐯𐐻 𐐈𐑊𐑁𐐲𐐺𐐯𐐻 𐐶𐐪𐑆 𐐺𐐴 𐑄 𐐡𐐨𐐾𐐲𐑌𐐻𐑅. 𐑆𐐿𐑅𐑅!');
  assert.equal(r.latin.split('.')[0], 'The Deseret Alphabet was by the Regents');
  assert.ok(r.ambiguous.some((a) => a.chose === 'by' && a.also.includes('buy')));
  assert.equal(r.respelled[0].respelled, 'zkss');
});

test('round trip of ordinary prose', () => {
  const src = 'The Regents of the University approved a new alphabet for the territory';
  const back = engine.fromDeseret(engine.text(src).deseret).latin;
  assert.equal(back, src);
});

test('historical1868 matches the printed examples the wiki cites', () => {
  const h = (s) => engine.text(s, historical1868).deseret;
  assert.equal(h('Holiness to the Lord'), '𐐐𐐬𐑊𐐨𐑌𐐮𐑅 𐐻𐐭 𐑄 𐐢𐐫𐑉𐐼');
  assert.equal(h('while'), '𐐸𐐶𐐴𐑊');
  assert.equal(h('While'), '𐐐𐐶𐐴𐑊');
  assert.equal(h('of the'), '𐐱𐑂 𐑄');
  assert.equal(h('who'), engine.text('who').deseret, 'wh- words that start with an h sound are left alone');
  assert.notEqual(h('Holiness'), engine.text('Holiness').deseret, '-ness is 𐐮𐑅 only in the 1868 forms');
  assert.equal(h('Deseret'), '𐐔𐐯𐑅𐐨𐑉𐐯𐐻', 'DeSEEret, as in the primers');
  assert.equal(engine.text('of').deseret, '𐐲𐑂', 'modern spelling is unchanged without the option');
});

test('"the" is 𐑄 and Deseret is DeZUret by default', () => {
  assert.equal(engine.text('the The THE').deseret, '𐑄 𐐜 𐐜');
  assert.equal(engine.text('Deseret').deseret, '𐐔𐐯𐑆𐐲𐑉𐐯𐐻');
  assert.equal(engine.text('Encyclopædia').deseret, '𐐇𐑌𐑅𐐴𐐿𐑊𐐲𐐹𐐨𐐼𐐨𐐲');
  // every spelling of Deseret, and the two-letter "the", still read back
  assert.equal(engine.fromDeseret('𐐔𐐯𐑅𐐨𐑉𐐯𐐻 𐐔𐐯𐑅𐐲𐑉𐐯𐐻 𐐔𐐯𐑆𐐲𐑉𐐯𐐻 𐑄𐐲 𐑄').latin, 'Deseret Deseret Deseret the the');
});

test('1868 forms and hand corrections read back to Latin', () => {
  assert.equal(engine.fromDeseret('𐐐𐐬𐑊𐐨𐑌𐐮𐑅 𐐻𐐭 𐑄 𐐢𐐫𐑉𐐼').latin, 'Holiness to the Lord');
  assert.equal(engine.fromDeseret('𐐸𐐶𐐴𐑊 𐐱𐑂').latin, 'while of');
  assert.equal(engine.fromDeseret(engine.text('Mormon').deseret).latin, 'Mormon');
});

test('syllabic values: a word that sounds like a letter name is that one letter', () => {
  const t = (s) => engine.text(s).deseret;
  assert.equal(t('be bee tea tee pea gay thee ye gee woo ha'), '𐐺 𐐺 𐐻 𐐻 𐐹 𐑀 𐑄 𐐷 𐐾 𐐶 𐐸');
  assert.equal(t('Be BE'), '𐐒 𐐒');
  assert.equal(t('bees beat teas'), '𐐺𐐨𐑆 𐐺𐐨𐐻 𐐻𐐨𐑆', 'never inside a longer word');
  assert.equal(engine.explain('bee').deseret, '𐐺');
  assert.ok(engine.explain('bee').syllabic);
  const back = engine.fromDeseret('𐐒 𐑀 𐐺 𐐻 𐑄');
  assert.equal(back.latin, 'Be gay be tea the');
  assert.ok(back.ambiguous.some((a) => a.chose === 'be' && a.also.includes('bee')));
  assert.ok(back.ambiguous.some((a) => a.chose === 'the' && a.also.includes('thee')));
});
