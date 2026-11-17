/**
 * Map shading. Countries are sorted into equal-sized classes (quantiles) and
 * each class gets a clearly different color, so highs and lows read at a
 * glance instead of having to compare two shades of one hue.
 *
 * The ramp is hardcoded rather than token-based on purpose: the PNG export
 * has to render on its own white canvas, off-site, so the on-screen map and
 * the download share these exact colors (same reasoning as the Python PNG
 * pipeline's own palette - see docs/CHARTS.md).
 */

/** Pale yellow -> amber -> orange -> red -> dark plum: ordered by lightness
 * as well as hue, so it survives grayscale and color-blindness. */
export const RAMP = ["#fde9a9", "#f6b95b", "#e4762f", "#b7372b", "#5b1230"] as const;
/** Countries with data whose value is zero. */
export const ZERO_FILL = "#e4e1da";
/** Countries with no data / not in the dataset. */
export const NO_DATA_FILL = "#efece5";

export type MapClass = { fill: string; label: string };

export type Classing = {
  classes: MapClass[];
  hasZero: boolean;
  fillFor: (v: number | null) => string;
};

/** Leading digits ordered from roundest to least round. */
const DIGITS = [1, 5, 2, 2.5, 3, 4, 6, 8, 1.5, 7.5];

/** The roundest number in (lo, hi] (1, 5, 2, 2.5, ... times a power of ten),
 * preferring the larger on a tie; `hi` itself if nothing rounder fits. Any
 * number in that interval splits the data identically, so rounding never moves
 * a country between bands. */
function roundest(lo: number, hi: number, integer: boolean): { n: number; rank: number } {
  let best: { n: number; rank: number } | null = null;
  const top = Math.ceil(Math.log10(hi));
  for (let m = top; m >= Math.floor(Math.log10(lo)) - 2; m--) {
    DIGITS.forEach((d, rank) => {
      const n = Number((d * 10 ** m).toPrecision(12));
      if (n <= lo || n > hi || (integer && !Number.isInteger(n))) return;
      if (!best || rank < best.rank || (rank === best.rank && n > best.n)) best = { n, rank };
    });
  }
  return best ?? { n: hi, rank: DIGITS.length };
}

/** Splits the positive values into up to five bands with round boundaries,
 * placed so the bands hold roughly equal numbers of countries, and every
 * color is used whenever there are enough distinct values (fewer than five
 * distinct values get one band each). Zero gets its own swatch. Labels read "1,000–4,999" for counts, "10%–15%" for rates, with
 * the last band open-ended ("100,000+"). */
export function classify(values: (number | null)[], format: (v: number) => string): Classing {
  const nums = values.filter((v): v is number => v !== null);
  const positive = nums.filter((v) => v > 0).sort((a, b) => a - b);
  const hasZero = nums.some((v) => v === 0);
  const integer = positive.every(Number.isInteger);
  const n = RAMP.length;

  // Distinct positive values and how many countries sit below each.
  const uniq: number[] = [];
  const before: number[] = [];
  positive.forEach((v, idx) => {
    if (uniq[uniq.length - 1] !== v) {
      uniq.push(v);
      before.push(idx);
    }
  });

  // Every band is used whenever the data allows: pick four cut points at
  // distinct values. Each may drift up to 30% of an ideal band's size from an
  // equal split to land on a rounder number (1,000 beats 1,137); ties can't be
  // split, so this can't be a plain quintile.
  const cutIdx: number[] = [];
  if (uniq.length <= n) {
    for (let idx = 1; idx < uniq.length; idx++) cutIdx.push(idx);
  } else {
    let prev = 0;
    for (let j = 1; j < n; j++) {
      const target = (j * positive.length) / n;
      const tol = (0.3 * positive.length) / n;
      const maxIdx = uniq.length - (n - j); // leave room for the cuts still to come
      let bestIdx = prev + 1;
      let bestScore = Infinity;
      for (let idx = prev + 1; idx <= maxIdx; idx++) {
        const dev = Math.abs(before[idx] - target);
        // Outside the tolerance only the closest cut wins; inside it, roundness does.
        const score =
          dev <= tol ? roundest(uniq[idx - 1], uniq[idx], integer).rank * 1e6 + dev : 1e12 + dev;
        if (score < bestScore) {
          bestScore = score;
          bestIdx = idx;
        }
      }
      cutIdx.push(bestIdx);
      prev = bestIdx;
    }
  }
  const breaks = cutIdx.map((idx) => roundest(uniq[idx - 1], uniq[idx], integer).n);
  const min = positive[0];

  const k = breaks.length + 1;
  const fills = Array.from({ length: k }, (_, i) =>
    RAMP[k === 1 ? n - 1 : Math.round((i / (k - 1)) * (n - 1))],
  );

  const labels = Array.from({ length: k }, (_, i) => {
    if (k === 1) return positive.length ? format(min) : "";
    const lo = i === 0 ? null : breaks[i - 1];
    const hi = i === k - 1 ? null : breaks[i];
    if (lo === null) {
      if (integer) return hi! - 1 <= 1 ? "1" : `1–${format(hi! - 1)}`;
      return `Under ${format(hi!)}`;
    }
    if (hi === null) return `${format(lo)}+`;
    if (integer) return hi - 1 === lo ? format(lo) : `${format(lo)}–${format(hi - 1)}`;
    return `${format(lo)}–${format(hi)}`;
  });

  const classes: MapClass[] = fills.map((fill, i) => ({ fill, label: labels[i] }));

  const fillFor = (v: number | null) => {
    if (v === null) return NO_DATA_FILL;
    if (v <= 0) return ZERO_FILL;
    let idx = 0;
    while (idx < breaks.length && v >= breaks[idx]) idx++;
    return classes[idx]?.fill ?? ZERO_FILL;
  };
  return { classes, hasZero, fillFor };
}
