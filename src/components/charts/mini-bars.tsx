import { CONTEXT_GRAY, SERIES_PAINT } from "./palette";

export type MiniBarRow = {
  label: string;
  value: number;
  highlight?: boolean;
};

/**
 * A small horizontal bar row set for use inside a FacetGrid panel —
 * highlight-vs-gray coloring, an optional dashed reference line, values
 * printed at each bar's end. Deliberately minimal: no gridlines, no axis,
 * so a grid of these reads as one repeated small chart rather than twenty
 * competing full charts.
 */
export function MiniBars({
  rows,
  reference,
  formatValue = (n) => `${n.toFixed(0)}%`,
  domain = [0, 100],
}: {
  rows: MiniBarRow[];
  reference?: { value: number; label: string };
  formatValue?: (n: number) => string;
  domain?: [number, number];
}) {
  const [lo, hi] = domain;
  const pct = (v: number) => (100 * (v - lo)) / (hi - lo || 1);

  return (
    <div
      className="relative space-y-1.5"
      role="img"
      aria-label={
        rows.map((r) => `${r.label} ${formatValue(r.value)}`).join(", ") +
        (reference ? `; ${reference.label} ${formatValue(reference.value)}` : "")
      }
    >
      {reference && (
        <div
          className="absolute top-0 bottom-0 w-px bg-[color:var(--muted)]"
          style={{ left: `${pct(reference.value)}%`, opacity: 0.5 }}
          title={`${reference.label}: ${formatValue(reference.value)}`}
        />
      )}
      {rows.map((r) => (
        <div key={r.label} className="flex items-center gap-2 text-[11px]">
          <span className="w-20 shrink-0 truncate text-[color:var(--muted)]">{r.label}</span>
          <div className="relative h-3 flex-1 rounded-[var(--radius)] bg-[color:var(--muted-soft)]">
            <div
              className="h-full rounded-[var(--radius)]"
              style={{
                width: `${Math.max(2, pct(r.value))}%`,
                backgroundColor: r.highlight ? SERIES_PAINT[1] : CONTEXT_GRAY,
              }}
            />
          </div>
          <span className="tabular-nums w-9 shrink-0 text-right text-[color:var(--foreground)]">
            {formatValue(r.value)}
          </span>
        </div>
      ))}
    </div>
  );
}
