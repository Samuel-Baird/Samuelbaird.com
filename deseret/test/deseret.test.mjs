import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { loadTransliterator } from "../src/node.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const t = loadTransliterator();
const cps = (s) => Array.from(s).map((c) => c.codePointAt(0));
const isDeseret = (cp) => cp >= 0x10400 && cp <= 0x1044f;
const upper = (cp) => cp >= 0x10400 && cp <= 0x10427;
const RESERVED = new Set([0x10431, 0x1044e, 0x1044f]); // short ah, oi, ew: not used in the 38-letter standard

test("no word in the data uses the three reserved letters", () => {
  const rows = readFileSync(join(here, "..", "data", "words.tsv"), "utf8").split("\n").filter(Boolean);
  assert.ok(rows.length > 70000);
  for (const row of rows) {
    const [w, d] = row.split("\t");
    for (const cp of cps(d)) assert.ok(!RESERVED.has(cp), `${w} uses reserved U+${cp.toString(16)}`);
  }
});

test("letter-name words collapse to a single letter", () => {
  assert.equal(cps(t.word("the")).length, 1);
  assert.equal(cps(t.word("be")).length, 1);
});

test("output is Deseret letters for a known word and is lowercase by default", () => {
  const d = t.word("priesthood");
  assert.ok(d && cps(d).every(isDeseret));
  assert.ok(cps(d).every((cp) => !upper(cp)));
});

test("capitalization is carried over", () => {
  const lower = cps(t.word("god"));
  const title = cps(t.word("God"));
  const all = cps(t.word("GOD"));
  assert.equal(title.length, lower.length);
  assert.ok(upper(title[0]) && title.slice(1).every((cp) => !upper(cp)));
  assert.ok(all.every(upper));
  assert.ok(!upper(lower[0]));
});

test("unknown words, digits and punctuation are left unchanged", () => {
  assert.equal(t.text("Xyzzyqwfoo 1830, (ok)!").split(" ")[0], "Xyzzyqwfoo");
  assert.ok(t.text("1830, !?").startsWith("1830, !?"));
  assert.equal(t.word("Xyzzyqwfoo"), undefined);
});

test("straight and typographic apostrophes give the same spelling", () => {
  assert.ok(t.word("Lord's"));
  assert.equal(t.word("Lord's"), t.word("Lord’s"));
  assert.equal(t.word("don't"), t.word("don’t"));
});

test("curated overrides spell initialisms letter by letter and keep case", async () => {
  const { arpabetToDeseret } = await import("../src/index.mjs");
  assert.equal(t.word("ai"), arpabetToDeseret(["EY1", "AY1"]));
  assert.equal(cps(t.word("AI")).length, cps(t.word("ai")).length);
  assert.ok(cps(t.word("AI")).every(upper));
});

test("heteronyms are resolved from context", () => {
  const past = t.text("we have read the book");
  const present = t.text("we will read the book");
  const readPast = past.split(" ")[2];
  const readNow = present.split(" ")[2];
  assert.notEqual(readPast, readNow);
});

test("confidentOnly leaves guessed spellings in Latin", () => {
  const strict = loadTransliterator({ confidentOnly: true });
  const rows = readFileSync(join(here, "..", "data", "words.tsv"), "utf8").split("\n").filter(Boolean);
  const guess = rows.map((r) => r.split("\t")).find((r) => r[2] === "0" && /^[a-z]{6,}$/.test(r[0]));
  assert.ok(guess);
  assert.equal(strict.word(guess[0]), undefined);
  assert.equal(t.word(guess[0]), guess[1]);
});

test("html: only text nodes change", () => {
  const html = '<p class="priesthood" id="p1">The <a href="/c/priesthood">priesthood</a> &amp; <code>priesthood</code></p><!-- priesthood -->';
  const out = t.html(html);
  assert.ok(out.includes('class="priesthood"') && out.includes('href="/c/priesthood"'));
  assert.ok(out.includes("<code>priesthood</code>"));
  assert.ok(out.includes("&amp;") && out.includes("<!-- priesthood -->"));
  assert.ok(!/>priesthood</.test(out.replace("<code>priesthood</code>", "")));
  assert.ok(cps(out).some(isDeseret));
});

test("html: stripping tags from the output gives the plain-text rendering", () => {
  const plain = "The priesthood is the power of God.";
  const viaHtml = t.html(`<p>${plain}</p>`).replace(/<[^>]+>/g, "");
  assert.equal(viaHtml, t.text(plain));
});

test("coverage on the atlas vocabulary is high and reported", () => {
  const api = JSON.parse(readFileSync(join(here, "..", "..", "data", "api.json"), "utf8"));
  const terms = api.concepts.map((c) => c.en[0]).join(". ");
  const cov = t.coverage(terms);
  assert.ok(cov.words > 400);
  assert.ok(cov.converted / cov.words > 0.9, `coverage ${cov.converted}/${cov.words}; left: ${cov.left_latin.join(", ")}`);
});

test("parity with pulpit-vault's committed Deseret edition (when a checkout is present)", { skip: !existsSync(join(here, "..", "..", "..", "pulpit-vault", "talks", "deseret")) }, () => {
  const root = join(here, "..", "..", "..", "pulpit-vault", "talks");
  const id = "2024-04-alonso-jesus-christ-at-the-center-of-our-lives";
  const en = readFileSync(join(root, "english", "modern", "2024", `${id}.md`), "utf8");
  const ds = readFileSync(join(root, "deseret", "modern", "2024", `${id}.md`), "utf8");
  const enBody = en.slice(en.indexOf("\n---\n", 3) + 5);
  const dsBody = ds.slice(ds.indexOf("\n---\n", 3) + 5);
  const firstEn = enBody.split("\n").find((l) => l.trim().length > 80).replace(/\[\^\d+\]/g, "");
  const dsText = dsBody.replace(/<[^>]+>/g, "").replace(/\[\^\d+\]/g, "").replace(/&#39;|&rsquo;/g, "’");
  const mine = t.text(firstEn.trim());
  assert.ok(dsText.includes(mine.slice(0, 200)), "first paragraph differs from the Pulpit Deseret edition");
});
