"use client";

import { CONTEXT_GRAY, SERIES_PAINT } from "./palette";
import { linearScale } from "./scales";

export type DotPlotRow = {
  label: string;
  value: number;
  /** Confidence-interval bounds; whiskers are drawn capless, per Burge. */
  lo?: number;
  hi?: number;
  paint?: string;
  /** Drawn in CONTEXT_GRAY and pulled toward the reference line's opacity —
   * the house convention for a row whose interval includes the reference
   * value (e.g. a CI spanning zero), following the shipped Pew PNG's own
   * "faded when the interval includes zero" rule. */
  deEmphasized?: boolean;
};

type Props = {
  rows: DotPlotRow[];
  reference?: { value: number; label: string };
  domain?: [number, number];
  /** A named formatter rather than a function prop — figures are server
   * components, and a function can't cross the server/client boundary.
   * "signedPercent": "+13%"/"-9%". "percent": "13%". "number": "1.5". */
  format?: "signedPercent" | "percent" | "number";
  height?: number;
};

const FORMATTERS: Record<NonNullable<Props["format"]>, (n: number) => string> = {
  signedPercent: (n) => `${n >= 0 ? "+" : ""}${n.toFixed(0)}%`,
  percent: (n) => `${n.toFixed(0)}%`,
  number: (n) => n.toFixed(1),
};

const W = 800;
const PAD_L = 4;
const PAD_R = 64;
const ROW_H = 34;

export function DotPlot({ rows: rawRows, reference, domain, format = "number" }: Props) {
  const formatValue = FORMATTERS[format];
  const rows = [...rawRows].sort((a, b) => b.value - a.value);
  const H = rows.length * ROW_H + 16;

  const allX = rows.flatMap((r) => [r.value, r.lo, r.hi].filter((v): v is number => v != null));
  if (reference) allX.push(reference.value);
  const [dLo, dHi] = domain ?? [Math.min(...allX), Math.max(...allX)];
  const pad = (dHi - dLo) * 0.08 || 1;
  const x = (v: number) => linearScale(v, [dLo - pad, dHi + pad], [PAD_L, W - PAD_R]);
  const y = (i: number) => 8 + i * ROW_H + ROW_H / 2;

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="none"
        role="img"
        aria-label={`Dot plot: ${rows.map((r) => `${r.label} ${formatValue(r.value)}`).join(", ")}`}
        className="w-full"
        style={{ height: H }}
      >
        {reference && (
          <line
            x1={x(reference.value)}
            x2={x(reference.value)}
            y1={0}
            y2={H}
            stroke="var(--muted)"
            strokeWidth={1}
            strokeDasharray="4 3"
            vectorEffect="non-scaling-stroke"
          />
        )}
        {rows.map((r, i) => {
          const paint = r.deEmphasized ? CONTEXT_GRAY : r.paint ?? SERIES_PAINT[0];
          const opacity = r.deEmphasized ? 0.5 : 1;
          return (
            <g key={r.label}>
              {r.lo != null && r.hi != null && (
                <line
                  x1={x(r.lo)}
                  x2={x(r.hi)}
                  y1={y(i)}
                  y2={y(i)}
                  stroke={paint}
                  strokeOpacity={opacity * 0.6}
                  strokeWidth={1.5}
                  vectorEffect="non-scaling-stroke"
                />
              )}
              <circle cx={x(r.value)} cy={y(i)} r={6} fill="var(--surface)" />
              <circle
                cx={x(r.value)}
                cy={y(i)}
                r={5}
                fill={paint}
                fillOpacity={opacity}
                stroke="var(--foreground)"
                strokeOpacity={opacity}
                strokeWidth={1.5}
              />
            </g>
          );
        })}
      </svg>

      {/* Row + value labels, HTML overlay per the house text rule */}
      {rows.map((r, i) => (
        <div
          key={r.label}
          className="absolute inset-x-0 flex items-center justify-between text-xs"
          style={{ top: `${((y(i) - ROW_H / 2) / H) * 100}%`, height: `${(ROW_H / H) * 100}%` }}
        >
          <span
            className={
              "truncate pr-2 font-medium " +
              (r.deEmphasized ? "text-[color:var(--muted)]" : "text-[color:var(--foreground)]")
            }
            style={{ maxWidth: `${((x(r.value) - 6) / W) * 100}%` }}
          >
            {r.label}
          </span>
          <span
            className="tabular-nums absolute"
            style={{ left: `${((x(r.value) + 12) / W) * 100}%` }}
          >
            {formatValue(r.value)}
          </span>
        </div>
      ))}

      {reference && (
        <div
          className="absolute -top-4 -translate-x-1/2 text-[11px] text-[color:var(--muted)]"
          style={{ left: `${(x(reference.value) / W) * 100}%` }}
        >
          {reference.label}
        </div>
      )}
    </div>
  );
}
