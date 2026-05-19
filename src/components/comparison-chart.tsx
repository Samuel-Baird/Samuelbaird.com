"use client";

import { useMemo, useState } from "react";
import { fmtCompact, fmtDate } from "@/lib/format";

export type ComparisonSeries = {
  label: string;
  color: string;
  data: { captured_at: string; subscribers: number }[];
};

type Props = {
  series: ComparisonSeries[];
  height?: number;
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
      v: d.subscribers,
    }))
    .filter((p) => Number.isFinite(p.t) && Number.isFinite(p.v));
  if (pts.length === 0) return [];
  if (mode === "absolute") return pts;
  const base = pts[0].v || 1;
  return pts.map((p) => ({ ...p, v: (p.v / base) * 100 }));
}

export function ComparisonChart({ series, height = 280 }: Props) {
  const [mode, setMode] = useState<"absolute" | "indexed">("indexed");

  const normalized = useMemo(
    () => series.map((s) => ({ ...s, points: normalizeSeries(s, mode) })),
    [series, mode],
  );

  const validSeries = normalized.filter((s) => s.points.length >= 2);

  if (validSeries.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-[color:var(--border)] bg-white p-10 text-center text-sm text-[color:var(--muted)]">
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
  const tSpan = Math.max(1, tMax - tMin);
  const vSpan = Math.max(1, vMax - vMin);

  const W = 800;
  const H = height;
  const padL = 8;
  const padR = 8;
  const padT = 8;
  const padB = 24;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;
  const x = (t: number) => padL + ((t - tMin) / tSpan) * innerW;
  const y = (v: number) => padT + innerH - ((v - vMin) / vSpan) * innerH;

  return (
    <div className="rounded-2xl border border-[color:var(--border)] bg-white p-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
            Subscribers — comparison
          </div>
          <div className="mt-1 text-xs text-[color:var(--muted)]">
            {fmtDate(new Date(tMin).toISOString())} →{" "}
            {fmtDate(new Date(tMax).toISOString())}
          </div>
        </div>
        <div className="inline-flex rounded-full border border-[color:var(--border)] bg-[color:var(--muted-soft)] p-0.5 text-xs">
          <button
            type="button"
            onClick={() => setMode("indexed")}
            className={
              "rounded-full px-3 py-1.5 " +
              (mode === "indexed"
                ? "bg-white text-[color:var(--foreground)] shadow-sm"
                : "text-[color:var(--muted)]")
            }
          >
            Indexed (=100)
          </button>
          <button
            type="button"
            onClick={() => setMode("absolute")}
            className={
              "rounded-full px-3 py-1.5 " +
              (mode === "absolute"
                ? "bg-white text-[color:var(--foreground)] shadow-sm"
                : "text-[color:var(--muted)]")
            }
          >
            Absolute
          </button>
        </div>
      </div>

      <svg
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="none"
        role="img"
        aria-label="Channel comparison chart"
        className="mt-4 h-64 w-full sm:h-72"
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
              <circle cx={x(last.t)} cy={y(last.v)} r={3.5} fill={s.color} />
            </g>
          );
        })}
      </svg>

      <ul className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs">
        {validSeries.map((s) => {
          const last = s.points[s.points.length - 1];
          const first = s.points[0];
          const delta = last.v - first.v;
          const pct = first.v > 0 ? (delta / first.v) * 100 : 0;
          return (
            <li key={s.label} className="flex items-center gap-2">
              <span
                className="inline-block h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: s.color }}
                aria-hidden="true"
              />
              <span className="font-medium text-[color:var(--foreground)]">
                {s.label}
              </span>
              <span
                className={
                  "tabular-nums " +
                  (delta >= 0 ? "text-emerald-700" : "text-red-700")
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
