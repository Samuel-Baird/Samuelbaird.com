/**
 * One-axis gridlines and explicit wave-year ticks — Burge's "gray48
 * gridlines, one axis only, no ticks" rule translated to the house
 * `--border` token. Gridlines are SVG (they must align pixel-for-pixel with
 * the plotted path); tick labels are HTML overlays per the house text rule
 * in docs/CHARTS.md ("chart text is percent-positioned HTML, never SVG
 * `<text>`", because `preserveAspectRatio="none"` distorts SVG text).
 */

export type GridLine = { pos: number; major: boolean };

/** Horizontal gridlines (a value axis) inside an SVG plot area. `pos` is in
 * SVG viewBox pixels already. */
export function GridLinesY({
  lines,
  x1,
  x2,
}: {
  lines: GridLine[];
  x1: number;
  x2: number;
}) {
  return (
    <>
      {lines.map((l, i) => (
        <line
          key={i}
          x1={x1}
          x2={x2}
          y1={l.pos}
          y2={l.pos}
          stroke="var(--border)"
          strokeWidth={1}
          strokeDasharray={l.major ? undefined : "4 2"}
          vectorEffect="non-scaling-stroke"
        />
      ))}
    </>
  );
}

/** Vertical gridlines (a category/time axis) inside an SVG plot area. */
export function GridLinesX({
  lines,
  y1,
  y2,
}: {
  lines: GridLine[];
  y1: number;
  y2: number;
}) {
  return (
    <>
      {lines.map((l, i) => (
        <line
          key={i}
          y1={y1}
          y2={y2}
          x1={l.pos}
          x2={l.pos}
          stroke="var(--border)"
          strokeWidth={1}
          strokeDasharray={l.major ? undefined : "4 2"}
          vectorEffect="non-scaling-stroke"
        />
      ))}
    </>
  );
}

/** Explicit wave-year (or other category) tick labels, as an HTML row below
 * the plot, positioned by percent so it survives `preserveAspectRatio="none"`
 * scaling without distortion. */
export function WaveTicks({
  ticks,
}: {
  ticks: { pct: number; label: string }[];
}) {
  return (
    <div className="relative mt-1.5 h-4 text-[11px] text-[color:var(--muted)]">
      {ticks.map((t) => (
        <span
          key={t.label}
          className="tabular-nums absolute -translate-x-1/2"
          style={{ left: `${t.pct}%` }}
        >
          {t.label}
        </span>
      ))}
    </div>
  );
}
