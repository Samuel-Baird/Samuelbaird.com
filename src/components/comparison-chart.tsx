"use client";

import { useMemo, useState } from "react";
import { fmtCompact, fmtDate } from "@/lib/format";
import { ChartTooltip } from "@/components/charts/chart-tooltip";
import { EndOfLineLabel } from "@/components/charts/direct-labels";
import { nearestByX, svgPointerX } from "@/components/charts/hover";
import { linearScale } from "@/components/charts/scales";

export type ComparisonSeries = {
  label: string;
  color: string;
  data: { captured_at: string; subscribers?: number; value?: number }[];
};

type Props = {
  series: ComparisonSeries[];
  height?: number;
  metricLabel?: string;
};

type NormalizedPoint = { t: number; v: number; iso: string };

function normalizeSeries(
  s: ComparisonSeries,
  mode: "absolute" | "indexed",
): NormalizedPoint[] {
  const pts = s.data
    .map((d) => ({
      iso: d.captured_at,
      t: new Date(d.captured_at).getTime(),
      v: d.value ?? d.subscribers ?? 0,
    }))
    .filter((p) => Number.isFinite(p.t) && Number.isFinite(p.v));
  if (pts.length === 0) return [];
  if (mode === "absolute") return pts;
  const base = pts[0].v || 1;
  return pts.map((p) => ({ ...p, v: (p.v / base) * 100 }));
}

type HoverState = {
  xPct: number;
  svgX: number;
  nearest: Array<{ label: string; color: string; value: number; iso: string }>;
};

export function ComparisonChart({ series, height = 280, metricLabel = "Subscribers" }: Props) {
  const [mode, setMode] = useState<"absolute" | "indexed">("indexed");
  const [hover, setHover] = useState<HoverState | null>(null);

  const normalized = useMemo(
    () => series.map((s) => ({ ...s, points: normalizeSeries(s, mode) })),
    [series, mode],
  );

  const validSeries = normalized.filter((s) => s.points.length >= 2);

  if (validSeries.length === 0) {
    return (
      <div className="rounded-[var(--radius)] border border-dashed border-[color:var(--border)] bg-white p-10 text-center text-sm text-[color:var(--muted)]">
        Pick two or more channels with sufficient history to compare.
      </div>
    );
  }

  const allTimes = validSeries.flatMap((s) => s.points.map((p) => p.t));
  const allValues = validSeries.flatMap((s) => s.points.map((p) => p.v));
  const tMin = Math.min(...allTimes);
  const tMax = Math.max(...allTimes);
  const vMin = Math.min(...allValues);
  const vMax = Math.max(...allValues);

  const W = 800;
  const H = height;
  const padL = 8;
  const padR = 88; // room for end-of-line labels
  const padT = 8;
  const padB = 24;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;
  const x = (t: number) => linearScale(t, [tMin, tMax], [padL, padL + innerW]);
  const y = (v: number) => linearScale(v, [vMin, vMax], [padT + innerH, padT]);

  function handleMouseMove(e: React.MouseEvent<SVGSVGElement>) {
    const svgX = svgPointerX(e, W);
    // Use the first valid series as the time anchor
    const anchor = validSeries[0];
    const anchorPoint = nearestByX(
      anchor.points.map((p) => ({ x: x(p.t), p })),
      svgX,
    );
    const anchorT = anchorPoint.p.t;
    // For each series find the point nearest to anchorT
    const nearest = validSeries.map((s) => {
      const best = nearestByX(
        s.points.map((p) => ({ x: p.t, p })),
        anchorT,
      ).p;
      return { label: s.label, color: s.color, value: best.v, iso: best.iso };
    });
    setHover({ xPct: (svgX / W) * 100, svgX, nearest });
  }

  return (
    <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
            {metricLabel} — comparison
          </div>
          <div className="mt-1 text-xs text-[color:var(--muted)]">
            {fmtDate(new Date(tMin).toISOString())} →{" "}
            {fmtDate(new Date(tMax).toISOString())}
          </div>
        </div>
        <div className="inline-flex rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)] p-0.5 text-xs">
          <button
            type="button"
            onClick={() => setMode("indexed")}
            className={
              "rounded-[var(--radius)] px-3 py-1.5 " +
              (mode === "indexed"
                ? "bg-white text-[color:var(--foreground)]"
                : "text-[color:var(--muted)]")
            }
          >
            Indexed (=100)
          </button>
          <button
            type="button"
            onClick={() => setMode("absolute")}
            className={
              "rounded-[var(--radius)] px-3 py-1.5 " +
              (mode === "absolute"
                ? "bg-white text-[color:var(--foreground)]"
                : "text-[color:var(--muted)]")
            }
          >
            Absolute
          </button>
        </div>
      </div>

      <div className="relative mt-4">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          preserveAspectRatio="none"
          role="img"
          aria-label="Channel comparison chart"
          className="h-64 w-full sm:h-72"
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHover(null)}
        >
          {validSeries.map((s) => {
            const path = s.points
              .map(
                (p, i) =>
                  `${i === 0 ? "M" : "L"} ${x(p.t).toFixed(1)} ${y(p.v).toFixed(1)}`,
              )
              .join(" ");
            const last = s.points[s.points.length - 1];
            return (
              <g key={s.label}>
                <path
                  d={path}
                  fill="none"
                  stroke={s.color}
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  vectorEffect="non-scaling-stroke"
                />
                {/* Donut marker on the last point, per the house line-chart spec */}
                <circle cx={x(last.t)} cy={y(last.v)} r={5} fill="var(--surface)" />
                <circle cx={x(last.t)} cy={y(last.v)} r={5} fill="none" stroke={s.color} strokeWidth={1.5} />
                <circle cx={x(last.t)} cy={y(last.v)} r={2} fill={s.color} />
              </g>
            );
          })}
          {hover && (
            <>
              <line
                x1={hover.svgX} y1={padT}
                x2={hover.svgX} y2={padT + innerH}
                stroke="var(--border)"
                strokeWidth={1}
                strokeDasharray="4 2"
                vectorEffect="non-scaling-stroke"
              />
              {hover.nearest.map((n) => {
                const s = validSeries.find((s) => s.label === n.label);
                if (!s) return null;
                const p = s.points.find((p) => p.iso === n.iso);
                if (!p) return null;
                return (
                  <circle
                    key={n.label}
                    cx={x(p.t)} cy={y(p.v)}
                    r={5}
                    fill={n.color}
                  />
                );
              })}
            </>
          )}
        </svg>

        {/* End-of-line labels, HTML overlay per the house text rule — direct
            labeling in place of relying solely on the legend below. */}
        {validSeries.map((s) => {
          const last = s.points[s.points.length - 1];
          return (
            <EndOfLineLabel
              key={s.label}
              xPct={(x(last.t) / W) * 100}
              yPct={(y(last.v) / H) * 100}
              color={s.color}
            >
              {s.label}
            </EndOfLineLabel>
          );
        })}

        {hover && (
          <ChartTooltip xPct={hover.xPct} yPct={8} anchor="top">
            <div className="mb-1.5 font-medium text-[color:var(--muted)]">
              {fmtDate(hover.nearest[0].iso)}
            </div>
            {hover.nearest.map((n) => (
              <div key={n.label} className="flex items-center gap-2 leading-5">
                <span
                  className="inline-block h-2 w-2 shrink-0 rounded-[var(--radius)]"
                  style={{ backgroundColor: n.color }}
                />
                <span className="truncate text-[color:var(--foreground)]">{n.label}</span>
                <span className="ml-auto tabular-nums text-[color:var(--foreground)]">
                  {mode === "indexed" ? `${n.value.toFixed(1)}` : fmtCompact(n.value)}
                </span>
              </div>
            ))}
          </ChartTooltip>
        )}
      </div>

      <ul className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs">
        {validSeries.map((s) => {
          const last = s.points[s.points.length - 1];
          const first = s.points[0];
          const delta = last.v - first.v;
          const pct = first.v > 0 ? (delta / first.v) * 100 : 0;
          return (
            <li key={s.label} className="flex items-center gap-2">
              <span
                className="inline-block h-2.5 w-2.5 rounded-[var(--radius)]"
                style={{ backgroundColor: s.color }}
                aria-hidden="true"
              />
              <span className="font-medium text-[color:var(--foreground)]">
                {s.label}
              </span>
              <span
                className={
                  "tabular-nums " +
                  (delta >= 0 ? "text-[color:var(--accent)]" : "text-[color:var(--oxblood)]")
                }
              >
                {delta >= 0 ? "+" : ""}
                {mode === "indexed"
                  ? `${pct.toFixed(1)}%`
                  : fmtCompact(delta)}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
