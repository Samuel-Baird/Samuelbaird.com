"use client";

import { useState } from "react";
import type { WorldMap } from "@/lib/world-map";
import type { CountryUnits, Estimate } from "./model";

export type MapRow = { name: string; units: CountryUnits; est: Estimate };

const nf = new Intl.NumberFormat("en-US");
const pct = (r: number) => `${Math.round(r * 100)}%`;

/** Fill saturation rises with implied rate; 0 is paper, `max` is full accent. */
function fill(rate: number, max: number) {
  const t = Math.min(1, Math.max(0, rate / max));
  return `color-mix(in srgb, var(--accent) ${Math.round(8 + t * 92)}%, var(--surface))`;
}

export function AttendanceMap({ map, rows }: { map: WorldMap; rows: MapRow[] }) {
  const [hover, setHover] = useState<{ row: MapRow; x: number; y: number } | null>(null);
  const max = Math.max(0.4, ...rows.map((r) => r.est.mid.rate));
  const drawn = rows.filter((r) => map.shapes[r.name]);

  function show(row: MapRow, el: SVGElement, e?: React.MouseEvent) {
    const box = el.ownerSVGElement!.getBoundingClientRect();
    const x = e ? e.clientX - box.left : box.width / 2;
    const y = e ? e.clientY - box.top : box.height / 2;
    setHover({ row, x, y });
  }

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${map.width} ${map.height}`}
        className="w-full"
        role="group"
        aria-label="World map of implied attendance rate by country"
      >
        <path d={map.land} fill="var(--muted-soft)" stroke="var(--background)" strokeWidth="0.4" />
        {drawn.map((r) => {
          const s = map.shapes[r.name];
          const label = `${r.name}: ${pct(r.est.mid.rate)} implied attendance`;
          return (
            <g key={r.name}>
              <path
                d={s.d}
                fill={fill(r.est.mid.rate, max)}
                stroke="var(--background)"
                strokeWidth="0.4"
                tabIndex={0}
                aria-label={label}
                className="outline-none focus-visible:stroke-[color:var(--foreground)]"
                onMouseMove={(e) => show(r, e.currentTarget, e)}
                onMouseLeave={() => setHover(null)}
                onFocus={(e) => show(r, e.currentTarget)}
                onBlur={() => setHover(null)}
              />
              {s.small ? (
                <circle
                  cx={s.cx}
                  cy={s.cy}
                  r="3"
                  fill={fill(r.est.mid.rate, max)}
                  stroke="var(--foreground)"
                  strokeWidth="0.5"
                  onMouseMove={(e) => show(r, e.currentTarget, e)}
                  onMouseLeave={() => setHover(null)}
                />
              ) : null}
            </g>
          );
        })}
      </svg>

      {hover ? (
        <div
          role="status"
          className="pointer-events-none absolute z-10 w-56 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--surface)] p-3 text-xs"
          style={{
            left: `min(${hover.x + 14}px, calc(100% - 14rem))`,
            top: hover.y + 14,
          }}
        >
          <p className="serif text-sm font-semibold">{hover.row.name}</p>
          <p className="mt-1 tabular-nums">
            <span className="serif text-lg font-semibold">{pct(hover.row.est.mid.rate)}</span>{" "}
            <span className="text-[color:var(--muted)]">
              ({pct(hover.row.est.low.rate)} – {pct(hover.row.est.high.rate)})
            </span>
          </p>
          <p className="mt-1 tabular-nums text-[color:var(--muted)]">
            {nf.format(Math.round(hover.row.est.mid.active))} attending of{" "}
            {nf.format(hover.row.units.members)} members
          </p>
          <p className="tabular-nums text-[color:var(--muted)]">
            {nf.format(hover.row.units.wards)} wards, {nf.format(hover.row.units.branches)} branches
          </p>
        </div>
      ) : null}

      <div className="mt-3 flex items-center gap-3 text-xs text-[color:var(--muted)]">
        <span>0%</span>
        <div
          className="h-2 w-40 border border-[color:var(--border)]"
          style={{
            background:
              "linear-gradient(to right, color-mix(in srgb, var(--accent) 8%, var(--surface)), var(--accent))",
          }}
          aria-hidden="true"
        />
        <span>{pct(max)}+</span>
        <span className="ml-3 inline-flex items-center gap-1.5">
          <span
            className="inline-block h-2 w-4 border border-[color:var(--border)]"
            style={{ background: "var(--muted-soft)" }}
            aria-hidden="true"
          />
          No data
        </span>
      </div>
    </div>
  );
}
