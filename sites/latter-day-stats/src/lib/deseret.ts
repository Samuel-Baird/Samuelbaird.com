/**
 * Shared Latin -> "Deseret" glyph mapping. Deseret is a phonemic alphabet, so
 * there is no true letter-for-letter transliteration of English — this picks
 * a plausible glyph per Latin letter for decorative use (the title reveal
 * animation, the donate modal). It is not a real transliteration and nothing
 * meaningful is ever encoded in it.
 */
const DESERET_LOWER: Record<string, string> = {
  a: "\u{10430}",
  b: "\u{1043A}",
  c: "\u{1043F}",
  d: "\u{1043C}",
  e: "\u{1042F}",
  f: "\u{10441}",
  g: "\u{10440}",
  h: "\u{10438}",
  i: "\u{1042E}",
  j: "\u{1043E}",
  k: "\u{1043F}",
  l: "\u{1044A}",
  m: "\u{1044B}",
  n: "\u{1044C}",
  o: "\u{1042C}",
  p: "\u{10439}",
  q: "\u{1043F}",
  r: "\u{10449}",
  s: "\u{10445}",
  t: "\u{1043B}",
  u: "\u{10433}",
  v: "\u{10442}",
  w: "\u{10436}",
  x: "\u{10446}",
  y: "\u{10437}",
  z: "\u{10446}",
};

/** Deseret capitals sit 0x28 below their lowercase counterparts. */
const CASE_OFFSET = 0x28;

export function toDeseretChar(char: string): string {
  const lower = DESERET_LOWER[char.toLowerCase()];
  if (!lower) return char;
  if (char === char.toLowerCase()) return lower;
  return String.fromCodePoint(lower.codePointAt(0)! - CASE_OFFSET);
}

export function toDeseretText(text: string): string {
  return Array.from(text).map(toDeseretChar).join("");
}
