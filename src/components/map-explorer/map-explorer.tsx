"use client";

import { useMemo, useState } from "react";
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

function fill(t: number) {
  return `color-mix(in srgb, var(--accent) ${Math.round(8 + t * 92)}%, var(--surface))`;
}

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
  const [hover, setHover] = useState<{ name: string; x: number; y: number } | null>(null);

  const metric = METRICS.find((m) => m.id === metricId)!;
  const per = perCapita && !!metric.count;

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

  const ranked = Object.entries(values)
    .filter((e): e is [string, number] => e[1] !== null)
    .sort((a, b) => b[1] - a[1]);
  const sorted = ranked.map((r) => r[1]).sort((a, b) => a - b);
  // A single huge country (the United States, usually) shouldn't wash out the
  // rest: cap the scale at the 95th percentile and shade by square root.
  const cap = sorted.length ? sorted[Math.floor(sorted.length * 0.95)] || sorted[sorted.length - 1] : 1;
  const shade = (v: number) => Math.sqrt(Math.min(1, Math.max(0, v / (cap || 1))));

  const total = ranked.reduce((n, r) => n + r[1], 0);
  const showTotal = !per && !!metric.count;
  const drawn = Object.keys(countries).filter((n) => map.shapes[n]);

  function show(name: string, el: SVGElement, e?: React.MouseEvent) {
    const box = el.ownerSVGElement!.getBoundingClientRect();
    setHover({
      name,
      x: e ? e.clientX - box.left : box.width / 2,
      y: e ? e.clientY - box.top : box.height / 2,
    });
  }

  const hc = hover ? countries[hover.name] : null;
  const hv = hover ? values[hover.name] : null;

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
            (metric.count ? "" : "text-[color:var(--muted)] opacity-60")
          }
        >
          <input
            type="checkbox"
            checked={per}
            disabled={!metric.count}
            onChange={(e) => setPerCapita(e.target.checked)}
            className="accent-[color:var(--accent)]"
          />
          Per 100,000 members (adjusts for how large the Church is in each country)
        </label>
      </section>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_16rem]">
        <section className="rounded-[var(--radius)] border border-[color:var(--border)] p-6 sm:p-7">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <p className="serif text-lg font-semibold">{label}</p>
            {showTotal ? (
              <p className="text-sm tabular-nums text-[color:var(--muted)]">
                Total {nf.format(total)}
              </p>
            ) : null}
          </div>
          <div className="relative mt-4">
            <svg
              viewBox={`0 0 ${map.width} ${map.height}`}
              className="w-full"
              role="group"
              aria-label={`World map of ${label.toLowerCase()} by country`}
            >
              <path d={map.land} fill="var(--muted-soft)" stroke="var(--background)" strokeWidth="0.4" />
              {drawn.map((name) => {
                const s = map.shapes[name];
                const v = values[name];
                const f = v === null ? "var(--muted-soft)" : fill(shade(v));
                return (
                  <g key={name}>
                    <path
                      d={s.d}
                      fill={f}
                      stroke="var(--background)"
                      strokeWidth="0.4"
                      tabIndex={0}
                      aria-label={`${name}: ${v === null ? "no data" : fmt(v)}`}
                      className="outline-none focus-visible:stroke-[color:var(--foreground)]"
                      onMouseMove={(e) => show(name, e.currentTarget, e)}
                      onMouseLeave={() => setHover(null)}
                      onFocus={(e) => show(name, e.currentTarget)}
                      onBlur={() => setHover(null)}
                    />
                    {s.small ? (
                      <circle
                        cx={s.cx}
                        cy={s.cy}
                        r="3"
                        fill={f}
                        stroke="var(--foreground)"
                        strokeWidth="0.5"
                        onMouseMove={(e) => show(name, e.currentTarget, e)}
                        onMouseLeave={() => setHover(null)}
                      />
                    ) : null}
                  </g>
                );
              })}
            </svg>

            {hover && hc ? (
              <div
                role="status"
                className="pointer-events-none absolute z-10 w-60 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--surface)] p-3 text-xs"
                style={{ left: `min(${hover.x + 14}px, calc(100% - 15rem))`, top: hover.y + 14 }}
              >
                <p className="serif text-sm font-semibold">
                  {hover.name}{" "}
                  <span className="font-normal text-[color:var(--muted)]">· {hc.continent}</span>
                </p>
                <p className="mt-1 tabular-nums">
                  <span className="serif text-lg font-semibold">{hv === null ? "—" : fmt(hv!)}</span>{" "}
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
              </div>
            ) : null}
          </div>

          <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-[color:var(--muted)]">
            <span>0</span>
            <div
              className="h-2 w-40 border border-[color:var(--border)]"
              style={{
                background:
                  "linear-gradient(to right, color-mix(in srgb, var(--accent) 8%, var(--surface)), var(--accent))",
              }}
              aria-hidden="true"
            />
            <span>{fmt(cap)}+</span>
            <span className="ml-3 inline-flex items-center gap-1.5">
              <span
                className="inline-block h-2 w-4 border border-[color:var(--border)]"
                style={{ background: "var(--muted-soft)" }}
                aria-hidden="true"
              />
              No data
            </span>
          </div>
          <p className="mt-2 text-xs text-[color:var(--muted)]">
            Shading uses a square-root scale capped near the 95th percentile so one large country
            doesn&apos;t wash out the rest. As of {asOf}.
          </p>
        </section>

        <aside className="rounded-[var(--radius)] border border-[color:var(--border)] p-6">
          <p className="small-caps text-[11px] font-medium text-[color:var(--muted)]">Top 10</p>
          <ol className="mt-3 space-y-1.5 text-sm tabular-nums">
            {ranked.slice(0, 10).map(([name, v], i) => (
              <li key={name} className="flex justify-between gap-3">
                <span>
                  <span className="text-[color:var(--muted)]">{i + 1}.</span> {name}
                </span>
                <span>{fmt(v)}</span>
              </li>
            ))}
          </ol>
        </aside>
      </div>
    </div>
  );
}
