"use client";

import { ChoroplethMap } from "@/components/map/choropleth-map";
import type { WorldMap } from "@/lib/world-map";
import type { Assumptions, CountryUnits, Estimate } from "./model";

export type MapRow = { name: string; units: CountryUnits; est: Estimate };

const nf = new Intl.NumberFormat("en-US");
const pct = (r: number) => `${Math.round(r * 100)}%`;

export function AttendanceMap({
  map,
  rows,
  assumptions,
}: {
  map: WorldMap;
  rows: MapRow[];
  assumptions: Assumptions;
}) {
  const byName = new Map(rows.map((r) => [r.name, r]));
  const items = rows.map((r) => ({ name: r.name, value: r.est.mid.rate }));

  const tooltip = (name: string) => {
    const r = byName.get(name)!;
    return (
      <>
        <p className="serif text-sm font-semibold">{r.name}</p>
        <p className="mt-1 tabular-nums">
          <span className="serif text-lg font-semibold">{pct(r.est.mid.rate)}</span>{" "}
          <span className="text-[color:var(--muted)]">
            ({pct(r.est.low.rate)} – {pct(r.est.high.rate)})
          </span>
        </p>
        <p className="mt-1 tabular-nums text-[color:var(--muted)]">
          {nf.format(Math.round(r.est.mid.active))} attending of {nf.format(r.units.members)} members
        </p>
        <p className="tabular-nums text-[color:var(--muted)]">
          {nf.format(r.units.wards)} wards, {nf.format(r.units.branches)} branches
        </p>
      </>
    );
  };

  return (
    <ChoroplethMap
      map={map}
      items={items}
      format={pct}
      title="Implied attendance rate by country"
      subtitle={`Estimated attenders as a share of reported members, assuming ${assumptions.ward.mid} people per ward and ${assumptions.branch.mid} per branch. Not a measured activity rate.`}
      source="Church facts and statistics, 2025; author's estimate"
      filename="lds-implied-attendance-by-country"
      rankTitle="Top 10: implied attendance"
      tooltip={tooltip}
    />
  );
}
