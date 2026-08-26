"use client";

import { useState } from "react";
import { CONTEXT_GRAY, CONTEXT_OPACITY, SERIES_PAINT } from "./palette";
import { linearScale, niceTicks } from "./scales";
import { svgPointerX, nearestByX } from "./hover";
import { GridLinesY } from "./axis";
import { EndOfLineLabel } from "./direct-labels";
import { ChartTooltip } from "./chart-tooltip";

export type WaveSeries = {
  label: string;
  /** One value per entry in `waves`, aligned by index; `null` where the
   * series wasn't fielded that wave (drawn as a dashed gap, per Burge). */
  values: (number | null)[];
  /** Explicit paint overrides the highlight/context default below. */
  paint?: string;
  /** The one series drawn in a house color; every other series is drawn in
   * CONTEXT_GRAY and doesn't count against the 4-series cap. */
  highlight?: boolean;
};

type Props = {
  /** Wave years, ascending, shared by every series. */
  waves: number[];
  series: WaveSeries[];
  yDomain?: [number, number];
  /** A named formatter rather than a function prop — figures are server
   * components, and a function can't cross the server/client boundary. */
  format?: "number" | "twoDecimal" | "percent";
  height?: number;
};

const FORMATTERS: Record<NonNullable<Props["format"]>, (n: number) => string> = {
  number: (n) => n.toFixed(1),
  twoDecimal: (n) => n.toFixed(2),
  percent: (n) => `${n.toFixed(0)}%`,
};

const W = 800;
const PAD_L = 8;
const PAD_R = 96; // room for end-of-line labels
const PAD_T = 12;
const PAD_B = 8;

export function WaveLineChart({
  waves,
  series,
  yDomain,
  format = "number",
  height = 260,
}: Props) {
  const formatValue = FORMATTERS[format];
  const H = height;
  const innerL = PAD_L;
  const innerR = W - PAD_R;
  const innerT = PAD_T;
  const innerB = H - PAD_B;

  const [hoverIdx, setHoverIdx] = useState<number | null>(null);

  const xDomain: [number, number] = [waves[0], waves[waves.length - 1]];
  const allValues = series.flatMap((s) => s.values.filter((v): v is number => v != null));
  const domain: [number, number] = yDomain ?? [
    Math.min(...allValues, 0) === 0 && Math.min(...allValues) > 0 ? 0 : Math.min(...allValues),
    Math.max(...allValues),
  ];

  const x = (year: number) => linearScale(year, xDomain, [innerL, innerR]);
  const y = (v: number) => linearScale(v, domain, [innerB, innerT]);

  const ticks = niceTicks(domain, 4);

  let paletteIdx = 0;
  const painted = series.map((s) => {
    const paint =
      s.paint ?? (s.highlight ? SERIES_PAINT[paletteIdx++ % SERIES_PAINT.length] : CONTEXT_GRAY);
    const opacity = !s.paint && !s.highlight ? CONTEXT_OPACITY : 1;
    return { ...s, paint, opacity };
  });

  function handleMouseMove(e: React.MouseEvent<SVGSVGElement>) {
    const svgX = svgPointerX(e, W);
    const points = waves.map((yr, i) => ({ x: x(yr), i }));
    const nearest = nearestByX(points, svgX);
    setHoverIdx(nearest.i);
  }

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="none"
        role="img"
        aria-label={`Line chart of ${series.map((s) => s.label).join(", ")} across ${waves[0]}–${waves[waves.length - 1]}`}
        className="h-56 w-full sm:h-64"
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setHoverIdx(null)}
      >
        <GridLinesY
          lines={ticks.map((t, i) => ({ pos: y(t), major: i === 0 }))}
          x1={innerL}
          x2={innerR}
        />
        {hoverIdx != null && (
          <line
            x1={x(waves[hoverIdx])}
            x2={x(waves[hoverIdx])}
            y1={innerT}
            y2={innerB}
            stroke="var(--border)"
            strokeWidth={1}
            strokeDasharray="4 2"
            vectorEffect="non-scaling-stroke"
          />
        )}
        {painted.map((s) => {
          const pts = waves
            .map((yr, i) => ({ yr, i, v: s.values[i] }))
            .filter((p) => p.v != null) as { yr: number; i: number; v: number }[];
          if (pts.length === 0) return null;

          // Split into contiguous runs (no missing wave between them) for a
          // solid path; bridge any gap with a dashed connector, per Burge's
          // "dashed segment across a gap" convention.
          const segments: typeof pts[] = [];
          let current: typeof pts = [pts[0]];
          for (let k = 1; k < pts.length; k++) {
            if (pts[k].i === pts[k - 1].i + 1) {
              current.push(pts[k]);
            } else {
              segments.push(current);
              current = [pts[k]];
            }
          }
          segments.push(current);

          const last = pts[pts.length - 1];

          return (
            <g key={s.label}>
              {segments.map((seg, si) => (
                <path
                  key={si}
                  d={seg
                    .map((p, i) => `${i === 0 ? "M" : "L"} ${x(p.yr).toFixed(1)} ${y(p.v).toFixed(1)}`)
                    .join(" ")}
                  fill="none"
                  stroke={s.paint}
                  strokeOpacity={s.opacity}
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  vectorEffect="non-scaling-stroke"
                />
              ))}
              {segments.length > 1 &&
                segments.slice(1).map((seg, si) => {
                  const prevEnd = segments[si][segments[si].length - 1];
                  const gapStart = seg[0];
                  return (
                    <line
                      key={`gap-${si}`}
                      x1={x(prevEnd.yr)}
                      y1={y(prevEnd.v)}
                      x2={x(gapStart.yr)}
                      y2={y(gapStart.v)}
                      stroke={s.paint}
                      strokeOpacity={s.opacity * 0.7}
                      strokeWidth={1.5}
                      strokeDasharray="4 3"
                      vectorEffect="non-scaling-stroke"
                    />
                  );
                })}
              {/* Donut markers at every plotted wave */}
              {pts.map((p) => (
                <g key={p.i}>
                  <circle cx={x(p.yr)} cy={y(p.v)} r={5} fill="var(--surface)" fillOpacity={s.opacity} />
                  <circle
                    cx={x(p.yr)}
                    cy={y(p.v)}
                    r={5}
                    fill="none"
                    stroke={s.paint}
                    strokeOpacity={s.opacity}
                    strokeWidth={1.5}
                  />
                  <circle cx={x(p.yr)} cy={y(p.v)} r={2} fill={s.paint} fillOpacity={s.opacity} />
                </g>
              ))}
              {/* End-of-line label anchor point, read by the HTML overlay below */}
              <circle cx={x(last.yr)} cy={y(last.v)} r={0} data-end-label />
            </g>
          );
        })}
      </svg>

      {/* End-of-line labels, HTML overlay per the house text rule */}
      {painted.map((s) => {
        const pts = waves
          .map((yr, i) => ({ yr, i, v: s.values[i] }))
          .filter((p) => p.v != null) as { yr: number; i: number; v: number }[];
        if (pts.length === 0) return null;
        const last = pts[pts.length - 1];
        return (
          <EndOfLineLabel
            key={s.label}
            xPct={(x(last.yr) / W) * 100}
            yPct={(y(last.v) / H) * 100}
            color={s.paint}
          >
            {s.label}
          </EndOfLineLabel>
        );
      })}

      {hoverIdx != null && (
        <ChartTooltip xPct={(x(waves[hoverIdx]) / W) * 100} yPct={8} align="auto">
          <div className="mb-1.5 font-medium text-[color:var(--muted)] tabular-nums">
            {waves[hoverIdx]}
          </div>
          {painted.map((s) => {
            const v = s.values[hoverIdx];
            if (v == null) return null;
            return (
              <div key={s.label} className="flex items-center gap-2 leading-5">
                <span
                  className="inline-block h-2 w-2 shrink-0 rounded-[var(--radius)]"
                  style={{ backgroundColor: s.paint, opacity: s.opacity }}
                />
                <span className="truncate text-[color:var(--foreground)]">{s.label}</span>
                <span className="ml-auto tabular-nums text-[color:var(--foreground)]">
                  {formatValue(v)}
                </span>
              </div>
            );
          })}
        </ChartTooltip>
      )}

      <div className="relative mt-1.5 h-4 text-[11px] text-[color:var(--muted)]">
        {waves.map((yr) => (
          <span
            key={yr}
            className="tabular-nums absolute -translate-x-1/2"
            style={{ left: `${(x(yr) / W) * 100}%` }}
          >
            {yr}
          </span>
        ))}
      </div>
    </div>
  );
}
