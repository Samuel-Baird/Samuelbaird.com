import type { TagInk } from "@/components/tag";
import { ERAS } from "./constants";

/**
 * Geometry shared by the figures on this page.
 *
 * Both plots plant dots on the same year axis and differ only in what the
 * vertical direction means — claim axis in the distribution graph, stance in
 * the certainty graph. Keeping the axis maths in one place is what stops the
 * two figures from disagreeing about where 1900 falls or which decade an era
 * starts in, which would be a quiet and very confusing bug: the reader would
 * be comparing two pictures that do not share a ruler.
 *
 * Everything here is pure. The dot models, tooltips and pointer handling stay
 * with each figure, because they are entangled with what a dot *is* there.
 */

// SVG paint attributes take a CSS variable directly, so unlike Tailwind class
// strings these can be looked up from a table without tripping v4's inability
// to see constructed class names.
export const INK_PAINT: Record<TagInk, string> = {
  ink: "var(--foreground)",
  accent: "var(--accent)",
  oxblood: "var(--oxblood)",
  honey: "var(--honey)",
  muted: "var(--muted)",
};

export const ERA_STRIP = 15; // room for era labels above the first row
export const DOT_PITCH = 11; // vertical gap between dots stacked on one year
export const ROW_MIN = 30;
export const ROW_PAD = 15;
// Percent of the width held back at each end. A source landing exactly on the
// axis minimum would otherwise be drawn centred on x=0 and lose its left half
// to the edge of the SVG.
export const INSET = 1.5;

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

export type EraBand = {
  id: string;
  label: string;
  left: number;
  width: number;
};

export type Axis = {
  min: number;
  max: number;
  dataMin: number;
  dataMax: number;
  pctFor: (year: number) => number;
  ticks: { grid: number[]; minor: number[] };
  bands: EraBand[];
};

/**
 * The full horizontal model for a set of years: bounds, the year-to-percent
 * projection, both tick densities, and the era backdrop.
 *
 * `domainYears` fixes the axis to a span wider than the data — pass the whole
 * corpus and the plot keeps the same ruler however little is on it. That is
 * what makes an absence legible: a question last raised in 2013 should show
 * thirteen empty years, not quietly rescale until its final dot sits against
 * the right edge looking current. `dataMin`/`dataMax` still report the real
 * first and last year of what is actually plotted, so the caption never
 * inherits the padding.
 */
export function buildAxis(years: number[], domainYears?: number[]): Axis {
  const { min, max } = axisBounds(
    domainYears && domainYears.length > 0 ? domainYears : years,
  );
  const { dataMin, dataMax } = axisBounds(years);
  const span = max - min;
  const pctFor = (year: number) =>
    Math.round((INSET + ((year - min) / span) * (100 - 2 * INSET)) * 10) / 10;

  // Eras overlapping the axis, in order, for the alternating backdrop.
  const bands = ERAS.filter(
    (era) => era.startYear <= max && era.endYear >= min,
  ).map((era) => {
    const left = pctFor(Math.max(era.startYear, min));
    return {
      id: era.id,
      label: era.label,
      left,
      width: pctFor(Math.min(era.endYear, max)) - left,
    };
  });

  return { min, max, dataMin, dataMax, pctFor, ticks: tickYears(min, max), bands };
}

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

/**
 * Whichever dot the pointer is closest to, or null past the give-up radius.
 *
 * Pointer input is handled by one transparent layer over the whole plot rather
 * than by a hit circle per dot. A comfortable 24px target is wider than the
 * gap between adjacent years on a two-century axis, so per-dot targets
 * overlapped and whichever happened to paint last swallowed its neighbours'
 * clicks entirely. Nearest-wins keeps every dot reachable at any width and
 * still forgives an imprecise tap.
 */
export function nearestDot<T extends { pct: number; cy: number }>(
  dots: T[],
  box: DOMRect,
  clientX: number,
  clientY: number,
): T | null {
  const x = clientX - box.left;
  const y = clientY - box.top;
  let best: T | null = null;
  let bestDistance = Infinity;
  for (const dot of dots) {
    const dx = (dot.pct / 100) * box.width - x;
    const dy = dot.cy - y;
    const distance = dx * dx + dy * dy;
    if (distance < bestDistance) {
      bestDistance = distance;
      best = dot;
    }
  }
  return bestDistance <= 22 * 22 ? best : null;
}
