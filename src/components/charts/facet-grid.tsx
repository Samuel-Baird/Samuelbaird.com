/**
 * Layout wrapper for faceted small multiples — a grid of mini-panels, one
 * per group, each with a small-caps strip label. The caller owns the shared
 * scale across facets (each facet's `children` is whatever mini-chart it
 * wants); this component only lays them out consistently.
 */
export function FacetGrid({
  facets,
}: {
  facets: { label: string; children: React.ReactNode }[];
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {facets.map((f) => (
        <div
          key={f.label}
          className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-4"
        >
          <div className="small-caps text-[11px] font-medium text-[color:var(--muted)]">
            {f.label}
          </div>
          <div className="mt-2">{f.children}</div>
        </div>
      ))}
    </div>
  );
}
