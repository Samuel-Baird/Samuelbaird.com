"use client";

import { labelInkFor } from "./palette";

export type StackedBarsRow = {
  label: string;
  /** Percentages aligned to `segmentLabels`, ideally summing to ~100. */
  segments: number[];
};

type Props = {
  rows: StackedBarsRow[];
  segmentLabels: string[];
  paints: string[];
  /** Segments narrower than this (in percent of the bar) don't print a
   * label — Burge's "suppress what won't fit" rule. */
  minLabelPct?: number;
  legend?: "bottom" | "none";
};

/**
 * A 100%-stacked composition chart: one full-width bar per row, each
 * segment printing its own percent, value axis fully blanked because the
 * printed labels make it redundant. Built as flex/div markup rather than
 * SVG — the segment fills are simple rectangles and this sidesteps the
 * SVG-text-distortion problem entirely, matching the precedent set by
 * evangelical-quiz/group-breakdown-chart.tsx.
 */
export function StackedBars({
  rows,
  segmentLabels,
  paints,
  minLabelPct = 4,
  legend = "bottom",
}: Props) {
  return (
    <div>
      <div className="space-y-3">
        {rows.map((row) => (
          <div key={row.label}>
            <div className="mb-1 text-xs font-medium text-[color:var(--foreground)]">
              {row.label}
            </div>
            <div
              className="flex h-7 w-full overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]"
              role="img"
              aria-label={`${row.label}: ${segmentLabels
                .map((l, i) => `${l} ${row.segments[i]?.toFixed(0) ?? 0}%`)
                .join(", ")}`}
            >
              {row.segments.map((pct, i) => {
                const paint = paints[i % paints.length];
                const showLabel = pct >= minLabelPct;
                return (
                  <div
                    key={i}
                    className="flex items-center justify-center border-r border-[color:var(--border)] last:border-r-0"
                    style={{ width: `${Math.max(0, pct)}%`, backgroundColor: paint }}
                    title={`${segmentLabels[i]}: ${pct.toFixed(0)}%`}
                  >
                    {showLabel && (
                      <span
                        className="tabular-nums text-[11px] font-medium"
                        style={{ color: labelInkFor(paint) }}
                      >
                        {pct.toFixed(0)}%
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {legend === "bottom" && (
        <ul className="mt-4 flex flex-wrap gap-x-4 gap-y-1.5 text-xs">
          {segmentLabels.map((label, i) => (
            <li key={label} className="flex items-center gap-1.5">
              <span
                className="inline-block h-2.5 w-2.5 rounded-[var(--radius)] border border-[color:var(--border)]"
                style={{ backgroundColor: paints[i % paints.length] }}
                aria-hidden="true"
              />
              <span className="text-[color:var(--muted)]">{label}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
