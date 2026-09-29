"use client";

import { useMemo, useState } from "react";
import { ChoroplethMap } from "@/components/map/choropleth-map";
import type { WorldMap } from "@/lib/world-map";

export type CountryStats = {
  continent: string;
  year: number;
  members: number;
  congregations: number;
  wards: number;
  branches: number;
  stakes: number;
  districts: number;
  missions: number;
  temples: number;
  family_history_centers: number;
  source_url: string;
};

type CountKey =
  | "members"
  | "congregations"
  | "wards"
  | "branches"
  | "stakes"
  | "districts"
  | "missions"
  | "temples"
  | "family_history_centers";

type Metric = {
  id: string;
  label: string;
  /** Counts can be shown per 100,000 members; ratios cannot. */
  count?: CountKey;
  value: (c: CountryStats) => number | null;
  format: (v: number) => string;
};

const nf = new Intl.NumberFormat("en-US");
const nf1 = new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 });

const countMetric = (id: CountKey, label: string): Metric => ({
  id,
  label,
  count: id,
  value: (c) => c[id],
  format: (v) => nf.format(v),
});

const METRICS: Metric[] = [
  countMetric("members", "Members"),
  countMetric("congregations", "Congregations"),
  countMetric("wards", "Wards"),
  countMetric("branches", "Branches"),
  countMetric("stakes", "Stakes"),
  countMetric("districts", "Districts"),
  countMetric("missions", "Missions"),
  countMetric("temples", "Temples"),
  countMetric("family_history_centers", "Family history centers"),
  {
    id: "members_per_congregation",
    label: "Members per congregation",
    value: (c) => (c.congregations > 0 ? c.members / c.congregations : null),
    format: (v) => nf.format(Math.round(v)),
  },
  {
    id: "ward_share",
    label: "Wards as share of congregations",
    value: (c) => (c.congregations > 0 ? (100 * c.wards) / c.congregations : null),
    format: (v) => `${Math.round(v)}%`,
  },
];

const STAT_LINES: [CountKey, string][] = [
  ["members", "Members"],
  ["congregations", "Congregations"],
  ["wards", "Wards"],
  ["branches", "Branches"],
  ["stakes", "Stakes"],
  ["districts", "Districts"],
  ["missions", "Missions"],
  ["temples", "Temples"],
  ["family_history_centers", "Family history centers"],
];

const btn = (on: boolean) =>
  "rounded-[var(--radius)] border px-3 py-1.5 text-xs " +
  (on
    ? "border-[color:var(--accent)] bg-[color:var(--accent-soft)] text-[color:var(--accent)]"
    : "border-[color:var(--border)] hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]");

export function MapExplorer({
  map,
  countries,
  asOf,
}: {
  map: WorldMap;
  countries: Record<string, CountryStats>;
  asOf: string;
}) {
  const [metricId, setMetricId] = useState("members");
  const [perCapita, setPerCapita] = useState(false);

  const metric = METRICS.find((m) => m.id === metricId)!;
  // "Members per 100,000 members" is 100,000 everywhere, so it is not offered.
  const canScale = !!metric.count && metric.id !== "members";
  const per = perCapita && canScale;

  const values = useMemo(() => {
    const out: Record<string, number | null> = {};
    for (const [name, c] of Object.entries(countries)) {
      const v = metric.value(c);
      out[name] = v === null ? null : per ? (c.members > 0 ? (v / c.members) * 100000 : null) : v;
    }
    return out;
  }, [countries, metric, per]);

  const fmt = (v: number) => (per ? nf1.format(v) : metric.format(v));
  const label = per ? `${metric.label} per 100,000 members` : metric.label;
  const items = Object.keys(countries).map((name) => ({ name, value: values[name] }));
  const total = items.reduce((n, i) => n + (i.value ?? 0), 0);
  const showTotal = !per && !!metric.count;

  const tooltip = (name: string) => {
    const hc = countries[name];
    const hv = values[name];
    return (
      <>
        <p className="serif text-sm font-semibold">
          {name} <span className="font-normal text-[color:var(--muted)]">· {hc.continent}</span>
        </p>
        <p className="mt-1 tabular-nums">
          <span className="serif text-lg font-semibold">{hv === null ? "—" : fmt(hv)}</span>{" "}
          <span className="text-[color:var(--muted)]">{label.toLowerCase()}</span>
        </p>
        <dl className="mt-2 grid grid-cols-[1fr_auto] gap-x-3 gap-y-0.5 tabular-nums text-[color:var(--muted)]">
          {STAT_LINES.map(([k, l]) => (
            <div key={k} className="contents">
              <dt>{l}</dt>
              <dd className="text-right text-[color:var(--foreground)]">{nf.format(hc[k])}</dd>
            </div>
          ))}
        </dl>
        <p className="mt-2 text-[color:var(--muted)]">Data year {hc.year}</p>
      </>
    );
  };

  return (
    <div className="space-y-6">
      <section className="rounded-[var(--radius)] border border-[color:var(--border)] p-6 sm:p-7">
        <p className="small-caps text-[11px] font-medium text-[color:var(--muted)]">Show on the map</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {METRICS.map((m) => (
            <button
              key={m.id}
              type="button"
              aria-pressed={m.id === metricId}
              onClick={() => setMetricId(m.id)}
              className={btn(m.id === metricId)}
            >
              {m.label}
            </button>
          ))}
        </div>
        <label
          className={
            "mt-4 flex items-center gap-2 text-sm " +
            (canScale ? "" : "text-[color:var(--muted)] opacity-60")
          }
        >
          <input
            type="checkbox"
            checked={per}
            disabled={!canScale}
            onChange={(e) => setPerCapita(e.target.checked)}
            className="accent-[color:var(--accent)]"
          />
          Per 100,000 members (adjusts for how large the Church is in each country)
        </label>
      </section>

      <section className="rounded-[var(--radius)] border border-[color:var(--border)] p-4 sm:p-7">
        <ChoroplethMap
          map={map}
          items={items}
          format={fmt}
          title={`${label} by country`}
          subtitle={
            (showTotal ? `Worldwide total across the ${items.length} countries shown: ${nf.format(total)}. ` : "") +
            `Church-reported figures for ${asOf.split(" ")[0]}.`
          }
          source="Church facts and statistics, 2025"
          filename={`lds-${metric.id}${per ? "-per-100k" : ""}-by-country`}
          rankTitle={`Highest ${label.toLowerCase()}`}
          tooltip={tooltip}
        />
      </section>
    </div>
  );
}
