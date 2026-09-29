"use client";

import { useMemo, useState } from "react";
import { ChoroplethMap } from "@/components/map/choropleth-map";
import { DataTable } from "./data-table";
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

export type StateStats = Omit<CountryStats, "continent"> & { capital: string };

export type ContinentStats = Omit<CountryStats, "continent" | "source_url"> & {
  countries_with_data: number;
};

const US = "United States";

const COUNT_COLUMNS = METRICS.filter((m) => m.count).map((m) => ({ key: m.count!, label: m.label }));

export function MapExplorer({
  map,
  usMap,
  countries,
  states,
  continents,
  asOf,
}: {
  map: WorldMap;
  usMap: WorldMap;
  countries: Record<string, CountryStats>;
  /** Published state records per country name; only the United States has any so far. */
  states: Record<string, Record<string, StateStats>>;
  /** The Church's own continent totals, keyed by continent name. */
  continents: Record<string, ContinentStats>;
  asOf: string;
}) {
  const [metricId, setMetricId] = useState("members");
  const [perCapita, setPerCapita] = useState(false);
  const [focus, setFocus] = useState<string | null>(null);
  const [group, setGroup] = useState<"countries" | "continents">("countries");
  const inContinents = group === "continents";

  const stateRecords = states[US] ?? {};
  const publishedStates = Object.keys(stateRecords).length;
  const inStates = !inContinents && focus === US && publishedStates > 0;

  // One record set per level, so the rest of the component doesn't care which is showing.
  const records = useMemo<Record<string, CountryStats>>(() => {
    if (inContinents) {
      const out: Record<string, CountryStats> = {};
      for (const [name, c] of Object.entries(continents)) {
        out[name] = { ...c, continent: `${c.countries_with_data} countries`, source_url: "" };
      }
      return out;
    }
    if (!inStates) return countries;
    const out: Record<string, CountryStats> = {};
    for (const name of Object.keys(usMap.shapes)) {
      const st = stateRecords[name];
      if (st) out[name] = { ...st, continent: st.capital ? `capital ${st.capital}` : "state" };
    }
    return out;
  }, [inContinents, inStates, countries, continents, stateRecords, usMap]);

  const metrics = METRICS;
  const metric = metrics.find((m) => m.id === metricId) ?? METRICS[0];
  // "Members per 100,000 members" is 100,000 everywhere, so it is not offered.
  const canScale = !!metric.count && metric.id !== "members";
  const per = perCapita && canScale;

  const values = useMemo(() => {
    const out: Record<string, number | null> = {};
    for (const [name, c] of Object.entries(records)) {
      const v = metric.value(c);
      out[name] = v === null ? null : per ? (c.members > 0 ? (v / c.members) * 100000 : null) : v;
    }
    return out;
  }, [records, metric, per]);

  const fmt = (v: number) => (per ? nf1.format(v) : metric.format(v));
  const label = per ? `${metric.label} per 100,000 members` : metric.label;
  const shownMap = inStates ? usMap : map;
  // On the continent view every country takes its continent's value.
  const items = Object.keys(shownMap.shapes).map((name) => ({
    name,
    value: inContinents ? (values[countries[name]?.continent ?? ""] ?? null) : (values[name] ?? null),
  }));
  const continentItems = inContinents
    ? Object.keys(records).map((name) => ({ name, value: values[name] ?? null }))
    : undefined;
  const total = (continentItems ?? items).reduce((n, i) => n + (i.value ?? 0), 0);
  const showTotal = !per && !!metric.count;
  const withData = (continentItems ?? items).filter((i) => i.value !== null).length;

  const tooltip = (rawName: string) => {
    const name = inContinents ? (countries[rawName]?.continent ?? rawName) : rawName;
    const hc = records[name];
    const hv = values[name];
    if (!hc) {
      return (
        <>
          <p className="serif text-sm font-semibold">{name}</p>
          <p className="mt-1 text-[color:var(--muted)]">
            No statistics from the Church for this {inStates ? "state" : "country"}.
          </p>
        </>
      );
    }
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

  function onItemClick(name: string) {
    if (inStates || inContinents) return;
    setFocus((f) => (f === name ? null : name));
  }

  const level = inStates ? "U.S. state" : inContinents ? "continent" : "country";
  const focusedRecord = focus && !inStates && !inContinents ? records[focus] : null;

  const tableRows = Object.entries(records).map(([name, c]) => ({
    name,
    cells: Object.fromEntries(COUNT_COLUMNS.map((col) => [col.key, c[col.key as CountKey]])),
  }));

  return (
    <div className="space-y-6">
      <section className="rounded-[var(--radius)] border border-[color:var(--border)] p-6 sm:p-7">
        <p className="small-caps text-[11px] font-medium text-[color:var(--muted)]">Group by</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {(["countries", "continents"] as const).map((g) => (
            <button
              key={g}
              type="button"
              aria-pressed={group === g}
              onClick={() => {
                setGroup(g);
                setFocus(null);
              }}
              className={btn(group === g)}
            >
              {g === "countries" ? "Countries" : "Continents"}
            </button>
          ))}
        </div>
        <p className="small-caps mt-6 text-[11px] font-medium text-[color:var(--muted)]">Show on the map</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {metrics.map((m) => (
            <button
              key={m.id}
              type="button"
              aria-pressed={m.id === metric.id}
              onClick={() => setMetricId(m.id)}
              className={btn(m.id === metric.id)}
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
          Per 100,000 members (adjusts for how large the Church is in each {level})
        </label>
      </section>

      <section className="rounded-[var(--radius)] border border-[color:var(--border)] p-4 sm:p-7">
        <div className="mb-4 flex flex-wrap items-center gap-3 text-sm">
          {focus ? (
            <button
              type="button"
              onClick={() => setFocus(null)}
              className="inline-flex h-10 items-center gap-2 rounded-[var(--radius)] border border-[color:var(--border)] px-3 hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]"
            >
              <span aria-hidden="true">←</span> World map
            </button>
          ) : null}
          <p className="text-[color:var(--muted)]">
            {inContinents
              ? "Each country is shaded with its continent's total. Hover for the continent's figures."
              : inStates
              ? `All ${publishedStates} states and D.C., from the Church's statistics pages.`
              : focus
                ? `Zoomed to ${focus}. Click it again, or use the button, to go back.`
                : publishedStates > 0
                  ? "Click any country to zoom in. Click the United States to explore it by state."
                  : "Click any country to zoom in."}
          </p>
        </div>
        <ChoroplethMap
          map={shownMap}
          items={items}
          format={fmt}
          title={inStates ? `${label} by U.S. state` : inContinents ? `${label} by continent` : `${label} by country`}
          subtitle={
            (showTotal
              ? inStates
                ? `Total across the ${withData} states and D.C.: ${nf.format(total)}. `
                : inContinents
                  ? `Total across the ${withData} continents: ${nf.format(total)}. `
                  : `Total across the ${items.length} countries shown: ${nf.format(total)}. `
              : "") +
            (inContinents
              ? `Each country is shaded with its continent's total. Church-reported figures for ${asOf.split(" ")[0]}.`
              : `Church-reported figures for ${asOf.split(" ")[0]}.`)
          }
          source={inStates ? "Church facts and statistics state pages, 2025" : "Church facts and statistics, 2025"}
          filename={`lds-${inStates ? "us-states-" : ""}${metric.id}${per ? "-per-100k" : ""}-by-${inStates ? "state" : inContinents ? "continent" : "country"}`}
          rankTitle={inContinents ? `By continent: ${label.toLowerCase()}` : `Top 10: ${label.toLowerCase()}`}
          rankItems={continentItems}
          tooltip={tooltip}
          focusName={inStates ? null : focus}
          onItemClick={onItemClick}
          exportCrop={inStates ? 1 : 0.88}
          noDataLabel="No data"
        />
        {focusedRecord ? (
          <div className="mt-4 rounded-[var(--radius)] border border-[color:var(--border)] p-4 text-sm">
            {tooltip(focus!)}
          </div>
        ) : null}
      </section>

      <section className="rounded-[var(--radius)] border border-[color:var(--border)] p-6 sm:p-7">
        <p className="small-caps text-[11px] font-medium text-[color:var(--muted)]">
          {inStates ? "By state" : inContinents ? "By continent" : "By country"}
        </p>
        <div className="mt-4">
          <DataTable
            key={inStates ? "states" : inContinents ? "continents" : "countries"}
            rows={tableRows}
            columns={COUNT_COLUMNS}
            nameLabel={inStates ? "State" : inContinents ? "Continent" : "Country"}
            highlight={metric.count}
          />
        </div>
      </section>
    </div>
  );
}
