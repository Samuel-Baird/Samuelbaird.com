// Deseret Alphabet transliteration for English text. Browser- and Node-safe (no I/O here).
//
// This is the lookup runtime of pulpit-vault's Deseret engine (docs/deseret.md in that repo):
// each English word is looked up in a prebuilt word list, heteronyms (read/live/use/...) are
// resolved from local context, and the Latin word's capitalization is reapplied. A word with
// no spelling is left in Latin script unchanged; nothing is ever invented at runtime.
// Output follows the 38-letter standard of the 1868-69 printings.
import { mapHtmlText } from "./html.mjs";
import { applyCase } from "./case.mjs";
import { arpabetToDeseret } from "./arpabet.mjs";
import { decideSchwa } from "./schwa.mjs";
import { createHeteronymResolver } from "./heteronyms.mjs";
import { eachWord, wordsOf } from "./tokens.mjs";

/**
 * Parse data/words.tsv ("word<TAB>deseret<TAB>confident(1|0)") into a Map.
 * @param {string} tsv
 * @returns {Map<string, { d: string, c: boolean }>}
 */
export function parseWords(tsv) {
  const map = new Map();
  for (const line of tsv.split("\n")) {
    if (!line) continue;
    const [word, d, c] = line.replace(/\r$/, "").split("\t");
    if (word && d) map.set(word, { d, c: c === "1" });
  }
  return map;
}

/**
 * @param {{
 *   words: Map<string, { d: string, c: boolean }>,
 *   heteronyms?: Record<string, any>,
 *   overrides?: Record<string, string[] | string>,
 *   confidentOnly?: boolean,
 * }} opts
 *   overrides: word -> ARPAbet phonemes, taking precedence over the word list (keys starting with "_" are ignored).
 *   confidentOnly: leave words whose spelling came from a G2P/stemming guess in Latin
 *   (default false, which matches pulpit-vault's published output).
 */
export function createTransliterator({ words, heteronyms = {}, overrides = {}, confidentOnly = false }) {
  const resolver = createHeteronymResolver(heteronyms);
  const curated = new Map(Object.entries(overrides).filter(([k, v]) => !k.startsWith("_") && Array.isArray(v)));

  /** Deseret spelling for one Latin word, or undefined if it has none. */
  function word(w, ctx = {}) {
    if (resolver.isHeteronym(w)) {
      const arpabet = resolver.resolve(w, ctx);
      const { overrides } = decideSchwa(w.toLowerCase(), arpabet);
      return applyCase(arpabetToDeseret(arpabet, { overrides }), w);
    }
    const fixed = curated.get(w.toLowerCase());
    if (fixed) return applyCase(arpabetToDeseret(fixed), w);
    // The list is keyed with typographic apostrophes (it was built from typographer-rendered text),
    // so a straight apostrophe in plain input must still find "lord’s" and "don’t".
    const hit = words.get(w.toLowerCase().replace(/'/g, "’"));
    if (!hit || (confidentOnly && !hit.c)) return undefined;
    return applyCase(hit.d, w);
  }

  /** Transliterate plain text. Punctuation, digits and unknown words are left as they are. */
  function text(s) {
    return eachWord(s, (w, _start, _end, prev, next) => word(w, { prev, next }));
  }

  /** Transliterate HTML text nodes only (never tags, attributes, entities, code/pre/script/style). */
  function html(s) {
    return mapHtmlText(s, (w, ctx) => word(w, ctx));
  }

  /** How much of `s` has a Deseret spelling. */
  function coverage(s) {
    const all = wordsOf(s);
    const left = [];
    let converted = 0;
    all.forEach((w, i) => {
      const ctx = { prev: all[i - 1], next: all[i + 1] };
      if (word(w, ctx) === undefined) left.push(w);
      else converted += 1;
    });
    return { words: all.length, converted, left_latin: [...new Set(left.map((w) => w.toLowerCase()))].sort() };
  }

  return { word, text, html, coverage };
}

export { applyCase, arpabetToDeseret, mapHtmlText, eachWord, wordsOf };
