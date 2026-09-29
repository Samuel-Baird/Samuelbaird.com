"use client";

import { Download } from "lucide-react";
import { useMemo, useState } from "react";
import { Tag } from "@/components/tag";
import {
  PRESETS,
  SCENARIOS,
  estimate,
  setScenario,
  totals,
  type Assumptions,
  type CountryUnits,
  type Scenario,
} from "./model";

export type Baseline = { self_id: number; members: number; ratio: number; year: number };

type Props = {
  asOf: string;
  worldwideMembers: number;
  countries: Record<string, CountryUnits>;
  order: string[];
  baselines: Record<string, Baseline>;
};

const nf = new Intl.NumberFormat("en-US");
const pct = (r: number) => `${Math.round(r * 100)}%`;

function Slider({
  label,
  value,
  min,
  max,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (v: number) => void;
}) {
  return (
    <label className="flex items-center gap-3 text-sm">
      <span className="w-12 shrink-0 capitalize text-[color:var(--muted)]">{label}</span>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="min-w-0 flex-1 accent-[color:var(--accent)]"
      />
      <input
        type="number"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Math.min(max, Math.max(min, Number(e.target.value) || min)))}
        className="w-16 rounded-[var(--radius)] border border-[color:var(--border)] bg-transparent px-2 py-1 text-right tabular-nums"
        aria-label={`${label} attendees`}
      />
    </label>
  );
}

const btn =
  "rounded-[var(--radius)] border border-[color:var(--border)] px-3 py-1.5 text-xs hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]";
const eyebrow = "small-caps text-[11px] font-medium text-[color:var(--muted)]";
const card = "rounded-[var(--radius)] border border-[color:var(--border)] p-6 sm:p-7";

export function ActivityEstimator({ asOf, worldwideMembers, countries, order, baselines }: Props) {
  const [a, setA] = useState<Assumptions>(PRESETS.Default);

  const rows = useMemo(
    () =>
      order.map((name) => ({
        name,
        units: countries[name],
        est: estimate(countries[name], a),
        baseline: baselines[name],
      })),
    [a, countries, order, baselines],
  );
  const total = totals(rows);

  function downloadCsv() {
    const head =
      "country,members,wards,branches,active_low,active_mid,active_high,rate_low,rate_mid,rate_high,survey_ratio,survey_year";
    const lines = rows.map((r) =>
      [
        r.name,
        r.units.members,
        r.units.wards,
        r.units.branches,
        ...SCENARIOS.map((s) => Math.round(r.est[s].active)),
        ...SCENARIOS.map((s) => r.est[s].rate.toFixed(4)),
        r.baseline?.ratio ?? "",
        r.baseline?.year ?? "",
      ].join(","),
    );
    const url = URL.createObjectURL(
      new Blob([[head, ...lines].join("\n")], { type: "text/csv" }),
    );
    const el = document.createElement("a");
    el.href = url;
    el.download = "activity-estimate.csv";
    el.click();
    URL.revokeObjectURL(url);
  }

  const chartRows = rows.slice(0, 15);
  const chartMax =
    Math.max(
      0.6,
      ...chartRows.map((r) => r.est.high.rate),
      ...chartRows.map((r) => r.baseline?.ratio ?? 0),
    ) * 1.05;
  const W = 640;
  const LEFT = 90;
  const RIGHT = 20;
  const ROW = 34;
  const H = chartRows.length * ROW + 40;
  const x = (v: number) => LEFT + (v / chartMax) * (W - LEFT - RIGHT);
  const ticks = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1].filter((t) => t <= chartMax);

  return (
    <div className="space-y-8">
      <section className={card}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className={eyebrow}>Attendance per unit</p>
          <div className="flex flex-wrap gap-2">
            {Object.keys(PRESETS).map((p) => (
              <button key={p} type="button" onClick={() => setA(PRESETS[p])} className={btn}>
                {p}
              </button>
            ))}
          </div>
        </div>
        <div className="mt-5 grid gap-8 md:grid-cols-2">
          {(["ward", "branch"] as const).map((kind) => (
            <fieldset key={kind} className="space-y-3">
              <legend className="serif mb-2 text-lg font-semibold">
                People attending per {kind}
              </legend>
              {SCENARIOS.map((s: Scenario) => (
                <Slider
                  key={s}
                  label={s}
                  value={a[kind][s]}
                  min={5}
                  max={kind === "ward" ? 400 : 150}
                  onChange={(v) => setA({ ...a, [kind]: setScenario(a[kind], s, v) })}
                />
              ))}
            </fieldset>
          ))}
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2">
        <div className={card}>
          <p className={eyebrow}>Implied active members</p>
          <p className="serif mt-2 text-4xl font-semibold tabular-nums">
            {nf.format(Math.round(total.est.mid.active))}
          </p>
          <p className="mt-1 text-sm tabular-nums text-[color:var(--muted)]">
            range {nf.format(Math.round(total.est.low.active))} –{" "}
            {nf.format(Math.round(total.est.high.active))}
          </p>
        </div>
        <div className={card}>
          <p className={eyebrow}>Implied attendance rate</p>
          <p className="serif mt-2 text-4xl font-semibold tabular-nums">
            {pct(total.est.mid.rate)}
          </p>
          <p className="mt-1 text-sm tabular-nums text-[color:var(--muted)]">
            range {pct(total.est.low.rate)} – {pct(total.est.high.rate)} of{" "}
            {nf.format(total.members)} members
          </p>
        </div>
      </section>
      <p className="-mt-4 flex flex-wrap items-center gap-2 text-sm text-[color:var(--muted)]">
        <Tag ink="honey">{pct(total.members / worldwideMembers)} of membership</Tag>
        {rows.length} countries, {nf.format(total.members)} of {nf.format(worldwideMembers)} members
        worldwide, as of {asOf}.
      </p>

      <section className={card}>
        <p className={eyebrow}>Implied rate, 15 largest countries</p>
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="mt-4 w-full"
          role="img"
          aria-label="Implied attendance rate by country: low to high range with a mid dot"
        >
          {ticks.map((t) => (
            <g key={t}>
              <line x1={x(t)} x2={x(t)} y1={10} y2={H - 26} stroke="var(--border)" />
              <text x={x(t)} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--muted)">
                {Math.round(t * 100)}%
              </text>
            </g>
          ))}
          {chartRows.map((r, i) => {
            const cy = 26 + i * ROW;
            return (
              <g key={r.name}>
                <text x={LEFT - 10} y={cy + 4} textAnchor="end" fontSize="12" fill="var(--foreground)">
                  {r.name}
                </text>
                <line
                  x1={x(r.est.low.rate)}
                  x2={x(r.est.high.rate)}
                  y1={cy}
                  y2={cy}
                  stroke="var(--accent)"
                  strokeWidth="3"
                />
                <circle cx={x(r.est.mid.rate)} cy={cy} r="5" fill="var(--accent)" />
                {r.baseline ? (
                  <line
                    x1={x(r.baseline.ratio)}
                    x2={x(r.baseline.ratio)}
                    y1={cy - 9}
                    y2={cy + 9}
                    stroke="var(--honey)"
                    strokeWidth="3"
                  >
                    <title>{`Survey baseline ${pct(r.baseline.ratio)} (${r.baseline.year})`}</title>
                  </line>
                ) : null}
              </g>
            );
          })}
        </svg>
        <p className="mt-2 text-xs text-[color:var(--muted)]">
          Blue: low–high range with mid dot. Gold tick: survey baseline where one exists.
        </p>
      </section>

      <section className={card}>
        <div className="flex items-center justify-between gap-3">
          <p className={eyebrow}>By country</p>
          <button type="button" onClick={downloadCsv} className={`inline-flex items-center gap-2 ${btn}`}>
            <Download aria-hidden="true" size={14} /> Export CSV
          </button>
        </div>
        <div className="mt-4 max-h-[36rem] overflow-auto">
          <table className="w-full min-w-[640px] text-sm tabular-nums">
            <thead className="sticky top-0 bg-[color:var(--background)]">
              <tr className="border-b border-[color:var(--border)] text-left text-[color:var(--muted)]">
                <th className="py-2 pr-3 font-medium">Country</th>
                <th className="py-2 pr-3 text-right font-medium">Members</th>
                <th className="py-2 pr-3 text-right font-medium">Wards</th>
                <th className="py-2 pr-3 text-right font-medium">Branches</th>
                <th className="py-2 pr-3 text-right font-medium">Active (mid)</th>
                <th className="py-2 pr-3 text-right font-medium">Rate (low–mid–high)</th>
                <th className="py-2 text-right font-medium">Survey</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.name} className="border-b border-[color:var(--border)] last:border-0">
                  <td className="py-2 pr-3">
                    <a href={r.units.source_url} className="text-[color:var(--accent)] hover:underline">
                      {r.name}
                    </a>
                  </td>
                  <td className="py-2 pr-3 text-right">{nf.format(r.units.members)}</td>
                  <td className="py-2 pr-3 text-right">{nf.format(r.units.wards)}</td>
                  <td className="py-2 pr-3 text-right">{nf.format(r.units.branches)}</td>
                  <td className="py-2 pr-3 text-right">{nf.format(Math.round(r.est.mid.active))}</td>
                  <td className="py-2 pr-3 text-right">
                    {pct(r.est.low.rate)} – {pct(r.est.mid.rate)} – {pct(r.est.high.rate)}
                  </td>
                  <td className="py-2 text-right">
                    {r.baseline ? `${pct(r.baseline.ratio)} (${r.baseline.year})` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
