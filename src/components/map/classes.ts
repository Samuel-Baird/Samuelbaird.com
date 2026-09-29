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

/** Round to a friendly number. Big counts snap to 1-2.5-5 (1,000 / 2,500 /
 * 5,000); smaller values and rates use a slightly finer set so they still
 * split into several bands. */
function nice(x: number): number {
  const mag = 10 ** Math.floor(Math.log10(x));
  const m = x / mag;
  const steps = x >= 1000 ? [1, 2.5, 5, 10] : [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10];
  const best = steps.reduce((a, b) => (Math.abs(b - m) < Math.abs(a - m) ? b : a));
  return best * mag;
}

/** Splits the positive values into up to five bands with round boundaries,
 * placed near the quintiles so the bands stay roughly balanced. Ties and
 * rounding can merge bands, so some metrics get fewer swatches. Zero gets its
 * own swatch. Labels read "1,000–4,999" for counts, "10%–15%" for rates, with
 * the last band open-ended ("100,000+"). */
export function classify(values: (number | null)[], format: (v: number) => string): Classing {
  const nums = values.filter((v): v is number => v !== null);
  const positive = nums.filter((v) => v > 0).sort((a, b) => a - b);
  const hasZero = nums.some((v) => v === 0);
  const integer = positive.every(Number.isInteger);
  const n = RAMP.length;

  const min = positive[0];
  const max = positive[positive.length - 1];
  const raw = [1, 2, 3, 4].map((q) => positive[Math.floor((q / n) * positive.length)]);
  const snap = (x: number) => (integer ? Math.max(1, Math.round(nice(x))) : nice(x));
  const inRange = (bs: number[]) =>
    [...new Set(bs)].filter((b) => b > min && b <= max).sort((a, b) => a - b);
  let breaks = inRange(raw.filter((x) => x !== undefined).map(snap));
  // Many tied low values (e.g. temples) collapse the quintiles into two bands;
  // spread the cut-offs evenly on a log scale instead.
  if (breaks.length < 3 && max / min >= 20) {
    breaks = inRange([1, 2, 3, 4].map((j) => snap(min * (max / min) ** (j / n))));
  }

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
