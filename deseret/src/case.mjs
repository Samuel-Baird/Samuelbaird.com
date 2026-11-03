// Vendored from pulpit-vault scripts/deseret/case.mjs @ f57f3ff446.
// Do not edit here: regenerate with `python -m pipeline.deseret_data`. See deseret/README.md.
// Code-point-aware case handling for Deseret text.
//
// Deseret has real upper/lowercase pairs (capital = lowercase - 0x28), but
// every codepoint is outside the BMP (a UTF-16 surrogate pair), so plain
// JS `.length`/`[i]` indexing is wrong. Use `Array.from`/`for...of`, which
// iterate by Unicode code point, everywhere in this module and its callers.

import {
  DESERET_LOWER_MIN,
  DESERET_LOWER_MAX,
  DESERET_UPPER_MIN,
  DESERET_UPPER_MAX,
  DESERET_CASE_OFFSET,
} from "./arpabet.mjs";

/** @param {string} ch a single Deseret lowercase codepoint (as a string) */
export function toDeseretUpper(ch) {
  const cp = ch.codePointAt(0);
  if (cp < DESERET_LOWER_MIN || cp > DESERET_LOWER_MAX) return ch;
  return String.fromCodePoint(cp - DESERET_CASE_OFFSET);
}

/** @param {string} ch a single Deseret capital codepoint (as a string) */
export function toDeseretLower(ch) {
  const cp = ch.codePointAt(0);
  if (cp < DESERET_UPPER_MIN || cp > DESERET_UPPER_MAX) return ch;
  return String.fromCodePoint(cp + DESERET_CASE_OFFSET);
}

/** Lowercase every codepoint in a Deseret string, leaving non-Deseret characters untouched. */
export function lowerDeseretWord(word) {
  return Array.from(word).map(toDeseretLower).join("");
}

/**
 * Classify a Latin word's letter casing so Deseret output can match it.
 * @param {string} latin
 * @returns {"lower" | "title" | "upper" | "mixed"}
 */
export function classifyCase(latin) {
  const letters = latin.match(/\p{L}/gu) ?? [];
  if (letters.length === 0) return "lower";
  const upperCount = letters.filter((c) => c === c.toUpperCase() && c !== c.toLowerCase()).length;
  if (upperCount === 0) return "lower";
  if (upperCount === letters.length) return "upper";
  // Title case: exactly the first letter is uppercase, everything else lower.
  const first = letters[0];
  const restLower = letters.slice(1).every((c) => c === c.toLowerCase() || c === c.toUpperCase());
  const firstIsUpper = first === first.toUpperCase() && first !== first.toLowerCase();
  if (firstIsUpper && upperCount === 1) return "title";
  return "mixed";
}

/**
 * Apply `latin`'s case pattern to a (lowercase) Deseret glyph string.
 * "mixed" (e.g. an interior capital, "McKay") falls back to title-casing
 * just the first glyph -- Deseret has no per-syllable case convention to
 * fall back on, and this is the least-wrong default.
 * @param {string} deseretLower
 * @param {string} latin
 */
export function applyCase(deseretLower, latin) {
  const pattern = classifyCase(latin);
  const cps = Array.from(deseretLower);
  if (cps.length === 0) return deseretLower;
  if (pattern === "lower") return deseretLower;
  if (pattern === "upper") return cps.map(toDeseretUpper).join("");
  // title or mixed
  return [toDeseretUpper(cps[0]), ...cps.slice(1)].join("");
}
