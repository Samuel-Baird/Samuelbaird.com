import { INK_PAINT } from "@/components/charts/palette";
import { axisBounds, tickYears, stackOffset, rowHeight } from "@/components/charts/scales";
import { nearestDot } from "@/components/charts/hover";
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
 *
 * `INK_PAINT`, `axisBounds`, `tickYears`, `stackOffset`, `rowHeight`, and
 * `nearestDot` are hoisted into the shared chart kit
 * (src/components/charts/) and re-exported below, unchanged, so this
 * file's two consumers (stance-graph.tsx, timeline-graph.tsx) need no
 * changes. `buildAxis` stays here — it depends on this route's `ERAS`.
 */
export { INK_PAINT, stackOffset, rowHeight, nearestDot };

export const ERA_STRIP = 15; // room for era labels above the first row
// Percent of the width held back at each end. A source landing exactly on the
// axis minimum would otherwise be drawn centred on x=0 and lose its left half
// to the edge of the SVG.
export const INSET = 1.5;

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
