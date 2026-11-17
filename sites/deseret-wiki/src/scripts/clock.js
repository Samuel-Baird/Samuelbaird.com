// The engraving's own day: one shared clock for the sky (sky.js) and the land (land.js).
// It runs on wall-clock time, so every page and every visitor sees the same hour of the same day.
export const SUN_CYCLE = 150_000; // ms for one day and night
export const DAY_SHARE = 0.62; // of the cycle the sun is above the ridge
export const LUNATION = 8; // days from one new moon to the next

export function sunPhase(now = Date.now()) {
  const p = (now % SUN_CYCLE) / SUN_CYCLE;
  if (p >= DAY_SHARE) return { up: false, p: (p - DAY_SHARE) / (1 - DAY_SHARE) };
  return { up: true, p: p / DAY_SHARE };
}

/** 0 new, 0.25 first quarter, 0.5 full, 0.75 last quarter */
export const moonPhase = (now = Date.now()) => (now / (SUN_CYCLE * LUNATION)) % 1;
/** share of the disc that is lit */
export const moonLit = (phase) => (1 - Math.cos(phase * 2 * Math.PI)) / 2;

export const dayIndex = (now = Date.now()) => Math.floor(now / SUN_CYCLE);

function hash(n) {
  let x = Math.imul(n ^ 0x9e3779b9, 0x85ebca6b);
  x ^= x >>> 13; x = Math.imul(x, 0xc2b2ae35); x ^= x >>> 16;
  return (x >>> 0) / 4294967296;
}

/** The crickets come every one to three days. */
export function swarmDay(n) {
  let d = n - (((n % 64) + 64) % 64);
  while (d < n) d += 1 + Math.floor(hash(d) * 3);
  return d === n;
}
/** how far into the day they come */
export const swarmAt = (n) => 0.12 + 0.22 * hash(n * 7 + 3);
