// Vendored from pulpit-vault scripts/deseret/tokens.mjs @ f57f3ff446.
// Do not edit here: regenerate with `python -m pipeline.deseret_data`. See deseret/README.md.
// Latin-word tokenizer shared by the wordlist build (whole talks) and the
// HTML transliterator (text nodes only, already isolated from markup by
// html.mjs). A "word" is a maximal run of letters, optionally with internal
// apostrophes or hyphens joining further letter runs -- this keeps
// "don't", "father's", "to-day", "self-existent" as single tokens while
// never swallowing a leading/trailing quote mark or dash.
const WORD_RE = /[A-Za-z]+(?:['’-][A-Za-z]+)*/g;

/**
 * @param {string} text
 * @param {(word: string, start: number, end: number, prevWord: string | undefined, nextWord: string | undefined) => string | void} cb
 *   Return a replacement string to substitute the match, or void/undefined
 *   to leave it unchanged. (Mirrors String.prototype.replace's callback
 *   contract so callers can use eachWord for both scanning and rewriting.)
 *   `prevWord`/`nextWord` are the nearest word tokens in `text` (not
 *   necessarily adjacent -- punctuation/whitespace between them is
 *   ignored). `prevWord` falls back to the caller-supplied `initialPrev`
 *   for the first word; `nextWord` is `undefined` for the last word in
 *   `text` even if more text follows in a later call (see html.mjs --
 *   next-word lookahead does not cross a text-run boundary, only prev does).
 * @param {string} [initialPrev] prevWord to report for the first match,
 *   e.g. the last word of the previous text run when the caller is
 *   threading context across multiple eachWord() calls (see html.mjs).
 * @returns {string} `text` with every callback replacement applied.
 */
export function eachWord(text, cb, initialPrev) {
  const matches = [...text.matchAll(WORD_RE)];
  if (matches.length === 0) return text;

  let out = "";
  let cursor = 0;
  matches.forEach((m, i) => {
    const word = m[0];
    const start = m.index;
    const end = start + word.length;
    out += text.slice(cursor, start);
    const prevWord = i === 0 ? initialPrev : matches[i - 1][0];
    const nextWord = i < matches.length - 1 ? matches[i + 1][0] : undefined;
    const replacement = cb(word, start, end, prevWord, nextWord);
    out += replacement === undefined ? word : replacement;
    cursor = end;
  });
  out += text.slice(cursor);
  return out;
}

/** Convenience: collect every word token without rewriting. */
export function wordsOf(text) {
  return text.match(WORD_RE) ?? [];
}
