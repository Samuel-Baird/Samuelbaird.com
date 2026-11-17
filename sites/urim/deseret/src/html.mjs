// Vendored from pulpit-vault scripts/deseret/html.mjs @ f57f3ff446.
// Do not edit here: regenerate with `python -m pipeline.deseret_data`. See deseret/README.md.
// Markdown-safe(-enough) HTML text-node walker. Transliterates ONLY the
// text between tags -- never tag names, attributes (href, id, class,
// data-*, aria-*), or HTML entities -- and never the contents of
// code/pre/script/style elements (their contents are not prose, so
// shouldn't be walked as words at all).
//
// WHY OPERATE ON RENDERED HTML, NOT MARKDOWN: see the header comment in
// site/scripts/build-deseret.mjs. Short version -- CR/JD talks have raw
// `<a class="supplied-ref">` HTML injected into their markdown before
// render, and this vault's paragraph-anchor scheme (#pN) must mean the
// same thing in every edition (site/scripts/lib/render.mjs), which is only
// guaranteed if literally nothing but text nodes changes.
import { eachWord } from "./tokens.mjs";

const SKIP_TAGS = new Set(["code", "pre", "script", "style"]);

// Some eras of this vault's source markdown carry the apostrophe in
// contractions as a literal HTML numeric/named entity (`didn&#39;t`)
// instead of a Unicode character (`didn’t`) -- an ingestion-era artifact,
// confirmed directly against site/src/data/generated/talks.json (e.g.
// 1869-12-pratt-revelations-and-manifestations-of-god-and-of-wicked-spirits
// renders "didn&#39;t"). Because an entity is its own opaque SEGMENT_RE
// match, "didn" and "t" land in two separate text runs with nothing
// joining them, so eachWord's WORD_RE tokenizes them as two unrelated
// words -- "didn" becomes real OOV noise (found via
// progress/translations/deseret/oov.yaml's frequency ranking, not by inspection) even
// though "didn't" itself is a perfectly ordinary, resolvable contraction.
// Normalizing these to a literal apostrophe BEFORE segmenting fixes
// tokenization for every downstream consumer (wordlist build, stage B) in
// one place. This only changes TEXT CONTENT, never tag/attribute markup
// (entities never appear inside a tag by construction -- SEGMENT_RE's tag
// alternative consumes the whole `<...>` span first), so it can't affect
// the href/id structural invariants scripts/deseret-html.test.mjs checks.
const APOSTROPHE_ENTITY_RE = /&(?:#0*39|#x0*27|apos|#0*8217|#x0*2019|rsquo);/gi;
export function normalizeApostropheEntities(html) {
  return html.replace(APOSTROPHE_ENTITY_RE, "’");
}

// Splits into: an HTML comment, a tag, an entity, or a plain-text run (up to
// the next < or &). Comment/tag/entity are consumed whole and never handed
// to eachWord. Named groups so adding an alternative later can't silently
// shift the others (this file's history: an earlier version had no comment
// branch at all -- <!-- ... --> matched none of the alternatives, so the
// global-exec loop just skipped forward over it, silently DROPPING every
// HTML comment in the corpus, including in-body editorial markers like
// "<!-- HEAVYWEIGHT REVIEW ... -->". Caught by the identity-property test
// in scripts/deseret-html.test.mjs, not by inspection.).
const SEGMENT_RE = /(?<comment><!--[\s\S]*?-->)|(?<tag><\/?(?<tagName>[a-zA-Z][a-zA-Z0-9-]*)[^>]*>)|(?<entity>&[#a-zA-Z0-9]+;)|(?<text>[^<&]+)/g;

/**
 * @param {string} html
 * @param {(word: string, ctx: { prev: string | undefined, next: string | undefined }) => string | void} transliterateWord
 *   called for every Latin word token found in a text run outside a skip
 *   element; return a replacement or void to leave it unchanged. `ctx.prev`
 *   is the nearest preceding word anywhere earlier in `html` (tracked
 *   across tag/entity/comment boundaries, so it survives e.g. "<em>close</em>
 *   the door"); `ctx.next` is the nearest following word WITHIN THE SAME
 *   text run only (no lookahead across a tag boundary). Both feed
 *   schema/deseret/heteronyms.yaml's "prev in [...]" / "next in [...]"
 *   rules (scripts/deseret/heteronyms.mjs) -- prev for trailing triggers
 *   ("we have read"), next for leading ones ("blessed are the poor", where
 *   the trigger word follows the ambiguous one). Neither crosses a
 *   skip-element boundary (code/pre/script/style) -- those contents are
 *   never scanned for words at all.
 * @returns {string}
 */
export function mapHtmlText(rawHtml, transliterateWord) {
  const html = normalizeApostropheEntities(rawHtml);
  let out = "";
  const skipStack = [];
  let prevWord;
  let m;
  SEGMENT_RE.lastIndex = 0;
  while ((m = SEGMENT_RE.exec(html))) {
    const { comment, tag, tagName, entity, text } = m.groups;
    if (comment) {
      out += comment;
      continue;
    }
    if (tag) {
      out += tag;
      if (tagName) {
        const lower = tagName.toLowerCase();
        if (SKIP_TAGS.has(lower)) {
          if (tag[1] === "/") {
            // Pop the nearest matching skip tag, tolerating unbalanced/malformed
            // markup rather than throwing -- this is a display projection, not
            // a validator.
            const idx = skipStack.lastIndexOf(lower);
            if (idx !== -1) skipStack.splice(idx, 1);
          } else if (!tag.endsWith("/>")) {
            skipStack.push(lower);
          }
        }
      }
      continue;
    }
    if (entity) {
      out += entity;
      continue;
    }
    if (skipStack.length > 0) {
      out += text;
      continue;
    }
    out += eachWord(text, (word, start, end, prev, next) => transliterateWord(word, { prev, next }), prevWord);
    const words = text.match(/[A-Za-z]+(?:['’-][A-Za-z]+)*/g);
    if (words && words.length) prevWord = words[words.length - 1];
  }
  return out;
}
