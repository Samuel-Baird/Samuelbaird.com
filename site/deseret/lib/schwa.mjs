// Vendored from pulpit-vault scripts/deseret/schwa.mjs @ f57f3ff446.
// Do not edit here: regenerate with `python -m pipeline.deseret_data`. See deseret/README.md.
// Decides which unstressed *reduced-vowel* occurrences in a word's ARPAbet
// pronunciation -- CMUdict marks these AH0 or IH0, somewhat inconsistently
// relative to spelling -- should render as 𐐮 vs 𐐲 in Deseret. John Jenkins'
// rule treats both as the same underlying phenomenon: the reduced vowel is
// written with the i/y-spelling variant (𐐮) when the corresponding
// syllable is spelled with i or y, except immediately before /r/, and as
// schwa (𐐲) otherwise -- regardless of which of AH0/IH0 CMUdict happened to
// choose. Confirmed against the oracle: CMUdict gives "behold"/"because"/
// "before"/"began"/"even" an IH0 in their unstressed non-i/y-spelled
// syllable, but Jenkins writes schwa there just as for an AH0 case like
// "people"; "iniquity"'s IH0 *is* i/y-spelled and both CMUdict and Jenkins
// agree on 𐐮 there, so it needs no override either way. See
// schema/deseret/conventions.md and indexes/deseret/bom-oracle.tsv.
//
// METHOD: positionally align the word's vowel *letter* groups
// (/[aeiouy]+/g) against its vowel *phonemes*, syllable by syllable. This
// only works when the counts match, which is common but not universal for
// English spelling -- silent letters and letter/phoneme count mismatches
// break it. A handful of suffixes (-tion, -sion, ...) reliably represent a
// single trailing schwa with a letter group that *looks* like it should
// trigger the i/y variant but must not (the i/y is consumed by the
// preceding consonant's /sh/ or /ch/ sound) -- those are special-cased by
// stripping the suffix from both sides before alignment, not by exempting
// individual words.
import { ARPABET_VOWELS } from "./arpabet.mjs";

const REDUCED_VOWELS = new Set(["AH0", "IH0"]);

// Suffixes whose spelled i/y does not belong to the schwa that follows it
// (it's part of the preceding consonant's SH/CH/ZH sound). Longest first so
// "-tious" isn't half-matched by a hypothetical shorter overlap.
const SUFFIX_CONSUMPTION = ["tious", "cious", "geous", "gious", "tion", "sion", "tial", "cial", "tian"]
  .sort((a, b) => b.length - a.length);

const VOWEL_LETTERS_RE = /[aeiouy]+/g;

function bareStress(phoneme) {
  return phoneme.replace(/[012]$/, "");
}

function vowelIndices(phonemes) {
  return phonemes.map((p, i) => [i, p]).filter(([, p]) => ARPABET_VOWELS.has(bareStress(p))).map(([i]) => i);
}

/**
 * @param {string} word lowercase Latin spelling
 * @param {string[]} phonemes ARPAbet symbols with stress digits
 * @returns {{ overrides: Map<number, "i" | "schwa">, aligned: boolean }}
 *   overrides: for every reduced-vowel (AH0/IH0) index this rule could
 *     decide, "i" (use 𐐮) or "schwa" (use 𐐲) -- pass straight to
 *     arpabetToDeseret(phonemes, { overrides }).
 *   aligned: whether the letter/phoneme vowel-group counts matched (false
 *     means no decision could be made and every reduced vowel falls back to
 *     its ARPABET_TO_DESERET table default -- useful as a curation-queue
 *     flag when the word also contains i/y, since that's exactly the case
 *     this rule exists to get right).
 */
export function decideSchwa(word, phonemes) {
  const overrides = new Map();
  let remainingLetters = word;
  let remainingPhonemeIdx = vowelIndices(phonemes);

  // Suffix special-case: the word's *last* vowel phoneme is reduced and the
  // spelling ends in one of the SH/CH/ZH-then-schwa suffixes -> that one
  // occurrence is forced to plain schwa and excluded from alignment.
  const lastVowelIdx = remainingPhonemeIdx[remainingPhonemeIdx.length - 1];
  if (lastVowelIdx !== undefined && REDUCED_VOWELS.has(phonemes[lastVowelIdx])) {
    const suffix = SUFFIX_CONSUMPTION.find((s) => word.endsWith(s));
    if (suffix) {
      overrides.set(lastVowelIdx, "schwa");
      remainingLetters = word.slice(0, -suffix.length);
      remainingPhonemeIdx = remainingPhonemeIdx.slice(0, -1);
    }
  }

  let letterGroups = remainingLetters.match(VOWEL_LETTERS_RE) ?? [];

  // Trailing silent -e (before, because, believe, ...) is common enough to
  // handle generally rather than word-by-word: if there's exactly one extra
  // letter-group beyond the phoneme count, the word ends in "e", and that
  // final "e" is its own group (i.e. preceded by a consonant, not itself
  // part of the preceding vowel's spelling), drop it and re-check alignment.
  if (
    letterGroups.length === remainingPhonemeIdx.length + 1 &&
    remainingLetters.endsWith("e") &&
    letterGroups[letterGroups.length - 1] === "e"
  ) {
    letterGroups = letterGroups.slice(0, -1);
  }

  const aligned = letterGroups.length === remainingPhonemeIdx.length;
  if (!aligned) return { overrides, aligned };

  remainingPhonemeIdx.forEach((idx, pos) => {
    if (!REDUCED_VOWELS.has(phonemes[idx])) return; // raw compare: AH0/IH0 only, never stressed
    const group = letterGroups[pos];
    const hasIY = /[iy]/.test(group);
    const nextIsR = bareStress(phonemes[idx + 1] ?? "") === "R";
    overrides.set(idx, hasIY && !nextIsR ? "i" : "schwa");
  });

  return { overrides, aligned };
}
