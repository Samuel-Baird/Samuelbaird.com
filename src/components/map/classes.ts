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

export type MapClass = { fill: string; min: number; max: number };

export type Classing = {
  classes: MapClass[];
  hasZero: boolean;
  fillFor: (v: number | null) => string;
};

/** Splits the positive values into up to five quantile classes. Ties can
 * merge classes, so a metric with few distinct values gets fewer swatches. */
export function classify(values: (number | null)[]): Classing {
  const nums = values.filter((v): v is number => v !== null);
  const positive = nums.filter((v) => v > 0).sort((a, b) => a - b);
  const hasZero = nums.some((v) => v === 0);

  const n = RAMP.length;
  const groups: number[][] = Array.from({ length: n }, () => []);
  positive.forEach((v, i) => {
    let g = Math.min(n - 1, Math.floor((i / positive.length) * n));
    // Equal values must share a class.
    const prev = positive[i - 1];
    if (i > 0 && v === prev) {
      const pg = groups.findIndex((arr) => arr.includes(v));
      if (pg >= 0) g = pg;
    }
    groups[g].push(v);
  });

  const used = groups.filter((g) => g.length > 0);
  const classes: MapClass[] = used.map((g, i) => ({
    // Spread the surviving classes across the whole ramp.
    fill: RAMP[used.length === 1 ? n - 1 : Math.round((i / (used.length - 1)) * (n - 1))],
    min: g[0],
    max: g[g.length - 1],
  }));

  const fillFor = (v: number | null) => {
    if (v === null) return NO_DATA_FILL;
    if (v <= 0) return ZERO_FILL;
    const c = classes.find((k) => v >= k.min && v <= k.max) ?? classes[classes.length - 1];
    return c ? c.fill : ZERO_FILL;
  };
  return { classes, hasZero, fillFor };
}
