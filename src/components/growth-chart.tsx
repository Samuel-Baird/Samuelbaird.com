"use client";

import { useState } from "react";
import { fmtCompact, fmtDate } from "@/lib/format";

type Point = { captured_at: string; subscribers?: number; value?: number };

type Props = {
  data: Point[];
  height?: number;
  label?: string;
};

type HoverPoint = { xPct: number; yPct: number; date: string; value: number };

export function GrowthChart({ data, height = 200, label = "Subscribers" }: Props) {
  const [hover, setHover] = useState<HoverPoint | null>(null);
  if (!data || data.length < 2) {
    return (
      <div className="rounded-[var(--radius)] border border-dashed border-[color:var(--border)] bg-white p-6 text-center text-sm text-[color:var(--muted)]">
        {label} history will appear here once at least two snapshots have
        been collected.
      </div>
    );
  }

  const points = data
    .map((d) => ({
      iso: d.captured_at,
      t: new Date(d.captured_at).getTime(),
      v: d.value ?? d.subscribers ?? 0,
    }))
    .filter((p) => Number.isFinite(p.t) && Number.isFinite(p.v));

  const tMin = points[0].t;
  const tMax = points[points.length - 1].t;
  const vMin = Math.min(...points.map((p) => p.v));
  const vMax = Math.max(...points.map((p) => p.v));
  const vSpan = Math.max(1, vMax - vMin);
  const tSpan = Math.max(1, tMax - tMin);

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

  const path = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${x(p.t).toFixed(1)} ${y(p.v).toFixed(1)}`)
    .join(" ");

  const area =
    `M ${x(points[0].t).toFixed(1)} ${(padT + innerH).toFixed(1)} ` +
    points.map((p) => `L ${x(p.t).toFixed(1)} ${y(p.v).toFixed(1)}`).join(" ") +
    ` L ${x(points[points.length - 1].t).toFixed(1)} ${(padT + innerH).toFixed(1)} Z`;

  const first = points[0];
  const last = points[points.length - 1];
  const delta = last.v - first.v;
  const pct = first.v > 0 ? (delta / first.v) * 100 : 0;
  const up = delta >= 0;

  function handleMouseMove(e: React.MouseEvent<SVGSVGElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const svgX = ((e.clientX - rect.left) / rect.width) * W;
    let nearest = points[0];
    let minDist = Infinity;
    for (const p of points) {
      const d = Math.abs(svgX - x(p.t));
      if (d < minDist) { minDist = d; nearest = p; }
    }
    setHover({
      xPct: (x(nearest.t) / W) * 100,
      yPct: (y(nearest.v) / H) * 100,
      date: nearest.iso,
      value: nearest.v,
    });
  }

  return (
    <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5">
      <div className="flex items-end justify-between gap-3">
        <div>
          <div className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
            {label} over time
          </div>
          <div className="mt-1 text-xs text-[color:var(--muted)]">
            {fmtDate(first.iso)} → {fmtDate(last.iso)}
          </div>
        </div>
        <div className="text-right">
          <div className="serif text-2xl font-semibold tabular-nums">
            {fmtCompact(last.v)}
          </div>
          <div
            className={
              "text-xs tabular-nums " +
              (up ? "text-[color:var(--accent)]" : "text-[color:var(--oxblood)]")
            }
          >
            {up ? "+" : ""}
            {fmtCompact(delta)} ({up ? "+" : ""}
            {pct.toFixed(1)}%)
          </div>
        </div>
      </div>
      <div className="relative mt-4">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          preserveAspectRatio="none"
          role="img"
          aria-label={`${label} from ${fmtDate(first.iso)} to ${fmtDate(last.iso)}`}
          className="h-44 w-full sm:h-52"
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHover(null)}
        >
          <path
            d={area}
            fill="var(--accent)"
            fillOpacity={0.08}
          />
          <path
            d={path}
            fill="none"
            stroke="var(--accent)"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            vectorEffect="non-scaling-stroke"
          />
          <circle cx={x(last.t)} cy={y(last.v)} r={3.5} fill="var(--accent)" />
          {hover && (() => {
            const hx = (hover.xPct / 100) * W;
            const hy = (hover.yPct / 100) * H;
            return (
              <>
                <line
                  x1={hx} y1={padT}
                  x2={hx} y2={padT + innerH}
                  stroke="var(--border)"
                  strokeWidth={1}
                  strokeDasharray="4 2"
                  vectorEffect="non-scaling-stroke"
                />
                <circle cx={hx} cy={hy} r={5} fill="var(--accent)" />
              </>
            );
          })()}
        </svg>
        {hover && (
          <div
            className="pointer-events-none absolute z-10 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 py-2 text-xs"
            style={{
              left: `${hover.xPct}%`,
              top: `${hover.yPct}%`,
              transform: `translate(${hover.xPct > 75 ? "-100%" : "8px"}, -110%)`,
            }}
          >
            <div className="font-medium text-[color:var(--foreground)]">{fmtDate(hover.date)}</div>
            <div className="tabular-nums text-[color:var(--accent)]">{fmtCompact(hover.value)} {label.toLowerCase()}</div>
          </div>
        )}
      </div>
    </div>
  );
}
