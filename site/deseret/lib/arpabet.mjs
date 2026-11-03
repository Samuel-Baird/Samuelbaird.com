// Vendored from pulpit-vault scripts/deseret/arpabet.mjs @ f57f3ff446.
// Do not edit here: regenerate with `python -m pipeline.deseret_data`. See deseret/README.md.
// ARPAbet (CMUdict phoneme set) <-> Deseret Alphabet glyph mapping.
//
// Conventions (see schema/deseret/conventions.md for the full rationale,
// adopted from John H. Jenkins' modern-Deseret style guide):
//   - 38-letter inventory: the two "extra" 40-letter-chart glyphs, OI
//     (U+1044E) and EW (U+1044F), are never emitted. /oi/ is written as the
//     two-letter sequence OW+IH (falls out of ARPAbet OY mapping to two
//     Deseret letters); /juː/ falls out naturally from a Y phoneme followed
//     by a UW phoneme -- no special case needed.
//   - SHORT AH (U+10431) is never emitted -- CMU/General American has no
//     LOT/PALM contrast distinct from AA, and Jenkins' usage confirms this
//     (verified against his Deseret Book of Mormon).
//   - Stress digits (0/1/2) on the input ARPAbet symbols never change the
//     glyph chosen here. The one place stress matters -- whether an
//     unstressed AH0 becomes schwa (𐐲) or the i/y-spelling variant (𐐮) --
//     is decided by schwa.mjs *before* a phoneme reaches this table, by
///    substituting the phoneme string itself ("AH0" vs the synthetic
//     "AH0_IY" key below). This file has no stress logic.
//
// This module is a pure function of a phoneme list; it does no dictionary
// lookup and no linguistic guessing. Every entry below was checked against
// worked examples from Jenkins' Deseret Book of Mormon during development
// (see indexes/deseret/bom-oracle.tsv once scripts/build-deseret-oracle.ts
// has run).

const S = (cps) => cps.map((cp) => String.fromCodePoint(cp)).join("");

// Deseret lowercase letters, U+10428-U+1044F. Capitals are lowercase - 0x28.
const D = {
  longI: 0x10428, // 𐐨  IY
  longE: 0x10429, // 𐐩  EY
  longA: 0x1042a, // 𐐪  AA
  longAh: 0x1042b, // 𐐫  AO
  longO: 0x1042c, // 𐐬  OW
  longOo: 0x1042d, // 𐐭  UW
  shortI: 0x1042e, // 𐐮  IH
  shortE: 0x1042f, // 𐐯  EH
  shortA: 0x10430, // 𐐰  AE
  shortAh: 0x10431, // 𐐱  (reserved -- never emitted)
  shortO: 0x10432, // 𐐲  AH / schwa
  shortOo: 0x10433, // 𐐳  UH
  ay: 0x10434, // 𐐴  AY
  ow: 0x10435, // 𐐵  AW
  wu: 0x10436, // 𐐶  W
  yee: 0x10437, // 𐐷  Y
  h: 0x10438, // 𐐸  HH
  pee: 0x10439, // 𐐹  P
  bee: 0x1043a, // 𐐺  B
  tee: 0x1043b, // 𐐻  T
  dee: 0x1043c, // 𐐼  D
  chee: 0x1043d, // 𐐽  CH
  jee: 0x1043e, // 𐐾  JH
  kay: 0x1043f, // 𐐿  K
  gay: 0x10440, // 𐑀  G
  ef: 0x10441, // 𐑁  F
  vee: 0x10442, // 𐑂  V
  eth: 0x10443, // 𐑃  TH
  thee: 0x10444, // 𐑄  DH
  es: 0x10445, // 𐑅  S
  zee: 0x10446, // 𐑆  Z
  esh: 0x10447, // 𐑇  SH
  zhee: 0x10448, // 𐑈  ZH
  er: 0x10449, // 𐑉  R
  el: 0x1044a, // 𐑊  L
  em: 0x1044b, // 𐑋  M
  en: 0x1044c, // 𐑌  N
  eng: 0x1044d, // 𐑍  NG
  oi: 0x1044e, // 𐑎  (reserved -- never emitted)
  ew: 0x1044f, // 𐑏  (reserved -- never emitted)
};

// The 15 ARPAbet vowel phonemes (stress-stripped), for schwa.mjs's
// vowel-letter/vowel-phoneme positional alignment.
export const ARPABET_VOWELS = new Set([
  "AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW",
]);

export const DESERET_LOWER_MIN = 0x10428;
export const DESERET_LOWER_MAX = 0x1044f;
export const DESERET_UPPER_MIN = 0x10400;
export const DESERET_UPPER_MAX = 0x10427;
export const DESERET_CASE_OFFSET = 0x28;

// Glyphs this project's 38-letter convention must never emit. Guarded by a
// unit test over every table entry below, and by a corpus-wide assertion in
// the wordlist build.
export const RESERVED_UNUSED_CODEPOINTS = new Set([D.shortAh, D.oi, D.ew]);

// Stress-stripped ARPAbet phoneme -> Deseret glyph(s).
export const ARPABET_TO_DESERET = Object.freeze({
  // Vowels
  AA: S([D.longA]),
  AE: S([D.shortA]),
  AH: S([D.shortO]),
  AO: S([D.longAh]),
  AW: S([D.ow]),
  AY: S([D.ay]),
  EH: S([D.shortE]),
  ER: S([D.shortO, D.er]), // digraph: schwa + r-glyph, never U+10421-style single letter
  EY: S([D.longE]),
  IH: S([D.shortI]),
  IY: S([D.longI]),
  OW: S([D.longO]),
  OY: S([D.longO, D.shortI]), // digraph: OW + IH, never U+1044E (oi)
  UH: S([D.shortOo]),
  UW: S([D.longOo]),

  // Consonants
  B: S([D.bee]),
  CH: S([D.chee]),
  D: S([D.dee]),
  DH: S([D.thee]),
  F: S([D.ef]),
  G: S([D.gay]),
  HH: S([D.h]),
  JH: S([D.jee]),
  K: S([D.kay]),
  L: S([D.el]),
  M: S([D.em]),
  N: S([D.en]),
  NG: S([D.eng]),
  P: S([D.pee]),
  R: S([D.er]),
  S: S([D.es]),
  SH: S([D.esh]),
  T: S([D.tee]),
  TH: S([D.eth]),
  V: S([D.vee]),
  W: S([D.wu]),
  Y: S([D.yee]),
  Z: S([D.zee]),
  ZH: S([D.zhee]),
});

// Every emitted glyph must fall in the lowercase Deseret range and never be
// one of the three reserved/unused codepoints. Checked once at module load
// so a bad table edit fails immediately, not just in tests.
for (const [phoneme, glyphs] of Object.entries(ARPABET_TO_DESERET)) {
  for (const ch of glyphs) {
    const cp = ch.codePointAt(0);
    if (cp < DESERET_LOWER_MIN || cp > DESERET_LOWER_MAX) {
      throw new Error(`ARPABET_TO_DESERET[${phoneme}] contains a non-Deseret-lowercase codepoint`);
    }
    if (RESERVED_UNUSED_CODEPOINTS.has(cp)) {
      throw new Error(`ARPABET_TO_DESERET[${phoneme}] emits a reserved 40-letter-chart glyph`);
    }
  }
}

// Inverse table for the oracle round-trip check. Longest-glyph-sequence
// first (2-codepoint ER/OY digraphs) so decoding is self-consistent with
// encoding. NOTE: this is a lossy, best-effort inverse over *arbitrary*
// Deseret text (e.g. Jenkins' corpus) -- 𐐲𐑉 could in principle arise from
// two separately-motivated phonemes rather than our ER digraph, and 𐐬𐐮
// likewise for OY vs. a genuine OW+IH sequence. It is exact, by
// construction, for any string this module itself produced.
const DIGRAPH_ENTRIES = [
  [ARPABET_TO_DESERET.ER, ["ER"]],
  [ARPABET_TO_DESERET.OY, ["OY"]],
];
const SINGLE_ENTRIES = Object.entries(ARPABET_TO_DESERET)
  .filter(([phoneme]) => phoneme !== "ER" && phoneme !== "OY")
  .map(([phoneme, glyph]) => [glyph, [phoneme]]);

// The two reduced-vowel phonemes CMUdict marks unstressed -- AH0 and IH0 --
// are treated by Jenkins' convention as ONE class ("does this syllable's
// *spelling* have i/y?") rather than two: an override at a given index
// forces the i/y-glyph (𐐮) or the schwa-glyph (𐐲) regardless of which of
// the two CMUdict happened to use. schwa.mjs is the only producer of these
// overrides, and only ever for indices where phonemes[i] is exactly "AH0"
// or "IH0" -- never for a stressed vowel or a consonant.
const REDUCED_VOWEL_OVERRIDE_GLYPH = { i: ARPABET_TO_DESERET.IH, schwa: ARPABET_TO_DESERET.AH };

/**
 * @param {string[]} phonemes ARPAbet symbols, stress digits allowed (stripped internally).
 * @param {{ overrides?: Map<number, "i" | "schwa"> }} [opts] indices into
 *   `phonemes` (must be "AH0" or "IH0" at that index) whose reduced-vowel
 *   glyph is decided by schwa.mjs rather than the default per-phoneme table.
 * @returns {string} Deseret glyphs, all lowercase.
 */
export function arpabetToDeseret(phonemes, opts = {}) {
  const overrides = opts.overrides ?? new Map();
  let out = "";
  phonemes.forEach((raw, i) => {
    const override = overrides.get(i);
    if (override !== undefined) {
      if (raw !== "AH0" && raw !== "IH0") {
        throw new Error(`overrides[${i}] set on non-reduced-vowel phoneme "${raw}"`);
      }
      out += REDUCED_VOWEL_OVERRIDE_GLYPH[override];
      return;
    }
    const bare = raw.replace(/[012]$/, "");
    const glyph = ARPABET_TO_DESERET[bare];
    if (glyph === undefined) {
      throw new Error(`No Deseret mapping for ARPAbet phoneme "${raw}" (bare "${bare}")`);
    }
    out += glyph;
  });
  return out;
}

/**
 * Best-effort inverse of arpabetToDeseret, for oracle comparison and the
 * lexicon round-trip invariant. Returns null if `glyphs` contains anything
 * outside the mapped consonant/vowel set (e.g. punctuation slipped in by a
 * caller that should have stripped it first).
 * @param {string} glyphs
 * @returns {string[] | null}
 */
export function deseretToArpabet(glyphs) {
  const cps = Array.from(glyphs);
  const out = [];
  let i = 0;
  outer: while (i < cps.length) {
    for (const [glyph, phonemes] of DIGRAPH_ENTRIES) {
      const glyphCps = Array.from(glyph);
      if (cps.slice(i, i + glyphCps.length).join("") === glyph) {
        out.push(...phonemes);
        i += glyphCps.length;
        continue outer;
      }
    }
    const single = cps[i];
    const match = SINGLE_ENTRIES.find(([glyph]) => glyph === single);
    if (!match) return null;
    out.push(...match[1]);
    i += 1;
  }
  return out;
}
