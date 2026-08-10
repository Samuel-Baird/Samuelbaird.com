"use client";

import { useMemo, useState } from "react";
import { CATEGORY_META, categoriesOf } from "./constants";
import type { CategoryId, SourceEntry } from "./schema";

/**
 * Dot-plot overview of the filtered sources: one dot per source, placed on a
 * decade-gridded year axis that autoscales to the earliest and latest
 * datapoints currently in view. Dots are coloured by category and stack
 * vertically when several sources share a year, so density reads at a glance.
 *
 * Reusable across timelines: it takes entries plus a category-colour lookup
 * and knows nothing about this dataset's specific tags.
 */

// Dot fills, keyed to the same hue families as the category pills. Literal
// class strings only — Tailwind v4 cannot see constructed names.
const DOT_FILL: Record<CategoryId, string> = {
  "FATHER-MORTAL-EXPERIENCE": "bg-sky-500",
  "FATHER-BECAME-GOD": "bg-blue-600",
  "FATHER-ALWAYS-GOD": "bg-stone-500",
  "BACKWARD-EXPLICIT": "bg-blue-800",
  "BACKWARD-AGNOSTIC": "bg-indigo-500",
  "FORWARD-EXPLICIT": "bg-emerald-600",
  "FORWARD-EUPHEMISM": "bg-teal-500",
  "SPIRIT-BIRTH-VIVIPAROUS": "bg-purple-600",
  "SPIRIT-BIRTH-ADOPTION": "bg-fuchsia-600",
  "TRIPARTITE-FRAMEWORK": "bg-violet-500",
  "MANY-WORLDS": "bg-cyan-500",
  "HEAVENLY-MOTHER": "bg-amber-500",
  "INFINITE-CHAIN": "bg-slate-500",
  "DIVINE-PROGRESSION": "bg-rose-500",
  "RETREAT-REFRAME": "bg-orange-500",
};

const UNTAGGED_FILL = "bg-[color:var(--muted)]";

/**
 * Decade-rounded bounds for layout, kept separate from the true data range.
 * Padding the plot to round decades keeps edge dots off the border and puts
 * tick labels on readable numbers, but the caption reports the real first and
 * last years — rounding up would otherwise advertise a year with no source in
 * it (a 2025 source must not make the axis claim 2030).
 */
function axisBounds(years: number[]): {
  min: number;
  max: number;
  dataMin: number;
  dataMax: number;
} {
  const dataMin = Math.min(...years);
  const dataMax = Math.max(...years);
  const min = Math.floor(dataMin / 10) * 10;
  const max = Math.ceil(dataMax / 10) * 10;
  return { min, max: max === min ? min + 10 : max, dataMin, dataMax };
}

function tickYears(min: number, max: number): number[] {
  const span = max - min;
  const step = span <= 60 ? 10 : span <= 140 ? 20 : span <= 260 ? 50 : 100;
  const ticks: number[] = [];
  for (let y = Math.ceil(min / step) * step; y <= max; y += step) ticks.push(y);
  return ticks;
}

export function TimelineGraph({
  entries,
  onSelect,
}: {
  entries: SourceEntry[];
  onSelect?: (id: string) => void;
}) {
  const [hovered, setHovered] = useState<string | null>(null);

  const model = useMemo(() => {
    if (entries.length === 0) return null;
    const years = entries.map((e) => Number(e.date.slice(0, 4)));
    const { min, max, dataMin, dataMax } = axisBounds(years);
    const span = max - min;

    // Stack sources that land on the same rounded x position.
    const columns = new Map<number, SourceEntry[]>();
    for (const entry of entries) {
      const year = Number(entry.date.slice(0, 4));
      const pct = Math.round(((year - min) / span) * 1000) / 10;
      columns.set(pct, [...(columns.get(pct) ?? []), entry]);
    }

    const dots = [...columns.entries()].flatMap(([pct, group]) =>
      group.map((entry, i) => {
        const cats = categoriesOf(entry);
        return {
          entry,
          pct,
          row: i,
          fill: cats.length > 0 ? DOT_FILL[cats[0]] : UNTAGGED_FILL,
          cats,
        };
      }),
    );
    const maxRow = Math.max(...dots.map((d) => d.row));
    return { min, max, dataMin, dataMax, dots, maxRow, ticks: tickYears(min, max) };
  }, [entries]);

  if (!model) {
    return (
      <div className="rounded-2xl border border-dashed border-[color:var(--border)] bg-white p-6 text-center text-xs text-[color:var(--muted)]">
        No sources to plot.
      </div>
    );
  }

  // 18px per stacked dot, with headroom so the tallest column never clips.
  const plotHeight = Math.max(64, (model.maxRow + 1) * 18 + 16);

  return (
    <figure className="rounded-2xl border border-[color:var(--border)] bg-white p-4 sm:p-5">
      <figcaption className="flex flex-wrap items-baseline justify-between gap-2">
        <span className="text-[10px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
          Distribution over time
        </span>
        <span className="text-[10px] tabular-nums text-[color:var(--muted)]">
          {entries.length} {entries.length === 1 ? "source" : "sources"} ·{" "}
          {model.dataMin}
          {model.dataMax !== model.dataMin ? `–${model.dataMax}` : ""}
        </span>
      </figcaption>

      <div className="relative mt-3" style={{ height: plotHeight }}>
        {/* decade gridlines */}
        {model.ticks.map((y) => (
          <span
            key={y}
            aria-hidden="true"
            className="absolute top-0 w-px bg-[color:var(--border)]"
            style={{
              left: `${((y - model.min) / (model.max - model.min)) * 100}%`,
              height: plotHeight,
            }}
          />
        ))}

        {model.dots.map((d) => {
          const active = hovered === d.entry.id;
          return (
            <button
              key={d.entry.id}
              type="button"
              onMouseEnter={() => setHovered(d.entry.id)}
              onMouseLeave={() => setHovered(null)}
              onFocus={() => setHovered(d.entry.id)}
              onBlur={() => setHovered(null)}
              onClick={() => onSelect?.(d.entry.id)}
              title={`${d.entry.dateDisplay} — ${d.entry.title}${
                d.cats.length ? ` (${d.cats.map((c) => CATEGORY_META[c].label).join(", ")})` : ""
              }`}
              aria-label={`${d.entry.dateDisplay}, ${d.entry.title}`}
              className={`absolute h-2.5 w-2.5 -translate-x-1/2 rounded-full ring-2 ring-white transition-transform hover:scale-150 focus:scale-150 focus:outline-none focus-visible:ring-[color:var(--accent)] dark:ring-[#161a20] ${d.fill} ${
                active ? "scale-150" : ""
              } ${d.entry.sourceType === "citation" ? "opacity-55" : ""}`}
              style={{ left: `${d.pct}%`, top: d.row * 18 + 4 }}
            />
          );
        })}
      </div>

      {/* year axis */}
      <div className="relative mt-1 h-4 border-t border-[color:var(--border)]">
        {model.ticks.map((y) => (
          <span
            key={y}
            className="absolute -translate-x-1/2 pt-1 text-[10px] tabular-nums text-[color:var(--muted)]"
            style={{
              left: `${((y - model.min) / (model.max - model.min)) * 100}%`,
            }}
          >
            {y}
          </span>
        ))}
      </div>

      <p className="mt-3 text-[10px] leading-relaxed text-[color:var(--muted)]">
        Each dot is one source, coloured by its first category and dimmed when
        it is a citation rather than an original. The axis rescales to whatever
        the filters leave in view; click a dot to jump to its entry.
      </p>
    </figure>
  );
}
