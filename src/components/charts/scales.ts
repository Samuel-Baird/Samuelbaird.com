/**
 * Pure geometry shared by every chart in the kit: linear scales, tick
 * generation, and percent formatting. Nothing here touches React or the
 * DOM, so it's safe to import from server components building figure props.
 *
 * `axisBounds`, `tickYears`, `stackOffset`, and `rowHeight` are hoisted
 * verbatim from the eternal-increase timeline's `graph-shared.ts`, comments
 * included — that file re-exports them so its two consumers need no
 * changes. See docs/CHARTS.md "Axis-domain honesty" for why the reasoning
 * below matters, not just the math.
 */

export function linearScale(
  value: number,
  domain: [number, number],
  range: [number, number],
): number {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  const span = d1 - d0 || 1;
  return r0 + ((value - d0) / span) * (r1 - r0);
}

/** A handful of "nice" tick values spanning a domain — never more than
 * `maxTicks`, so a chart's value axis never turns into a ladder. */
export function niceTicks(domain: [number, number], maxTicks = 5): number[] {
  const [lo, hi] = domain;
  if (lo === hi) return [lo];
  const rawStep = (hi - lo) / Math.max(1, maxTicks - 1);
  const magnitude = 10 ** Math.floor(Math.log10(rawStep));
  const residual = rawStep / magnitude;
  const step =
    (residual >= 5 ? 10 : residual >= 2 ? 5 : residual >= 1 ? 2 : 1) * magnitude;
  const ticks: number[] = [];
  const start = Math.ceil(lo / step) * step;
  for (let t = start; t <= hi + step / 1000; t += step) {
    ticks.push(Math.round(t / step) * step);
  }
  return ticks;
}

/** `42%`, not `42.0%` — the house rule for chart labels. Pass `decimals`
 * only when the spread genuinely needs the extra digit. */
export function fmtPctLabel(value: number, decimals = 0): string {
  return `${value.toFixed(decimals)}%`;
}

// --- Hoisted from eternal-increase-timeline/graph-shared.ts ---

/**
 * Decade-rounded bounds for layout, kept separate from the true data range.
 * Padding the plot to round decades keeps edge dots off the border and puts
 * tick labels on readable numbers, but the caption reports the real first and
 * last years — rounding up would otherwise advertise a year with no source in
 * it (a 2025 source must not make the axis claim 2030).
 */
export function axisBounds(years: number[]): {
  min: number;
  max: number;
  dataMin: number;
  dataMax: number;
} {
  const dataMin = Math.min(...years);
  const dataMax = Math.max(...years);
  const min = Math.floor(dataMin / 10) * 10;
  const max = Math.ceil(dataMax / 10) * 10;
  return { min, max: max === min ? min + 10 : max, dataMin, dataMax };
}

/**
 * Two tick densities. Labelled years get a full-height gridline; the decades
 * between them get a short mark on the axis rule only. A single density
 * either ruled the plot with twenty lines or left a two-century span with
 * four labels.
 */
export function tickYears(
  min: number,
  max: number,
): { grid: number[]; minor: number[] } {
  const span = max - min;
  const labelStep = span <= 60 ? 10 : span <= 300 ? 20 : 50;
  const grid: number[] = [];
  for (let y = Math.ceil(min / labelStep) * labelStep; y <= max; y += labelStep) {
    grid.push(y);
  }
  const minorStep = span <= 300 ? 10 : 50;
  const minor: number[] = [];
  for (let y = Math.ceil(min / minorStep) * minorStep; y <= max; y += minorStep) {
    if (!grid.includes(y)) minor.push(y);
  }
  return { grid, minor };
}

const DOT_PITCH = 11; // vertical gap between dots stacked on one year
const ROW_MIN = 30;
const ROW_PAD = 15;

/**
 * Stack dots that share a column around a row's centre line, so a row holding
 * one dot still reads as a single row rather than a top-aligned pile.
 */
export function stackOffset(indexInColumn: number, columnSize: number): number {
  return (indexInColumn - (columnSize - 1) / 2) * DOT_PITCH;
}

/** Height a row needs to hold its deepest column. */
export function rowHeight(maxStack: number): number {
  return Math.max(ROW_MIN, maxStack * DOT_PITCH + ROW_PAD);
}
