"use client";

/** One checkbox-list facet, shared by the graphics gallery
 * (/data-explorer/gallery) and the Data Explorer's own folder filters
 * (/data-explorer) - both are "search + multi-select facets over a flat
 * list of cards" UIs, so they share this one building block. */
export type FacetOption = { value: string; label: string; count: number };

export function FacetGroup({
  title,
  options,
  selected,
  onToggle,
}: {
  title: string;
  options: FacetOption[];
  selected: Set<string>;
  onToggle: (value: string) => void;
}) {
  if (options.length === 0) return null;
  return (
    <div>
      <h3 className="small-caps text-xs font-medium text-[color:var(--muted)]">{title}</h3>
      <div className="mt-2 max-h-56 space-y-0.5 overflow-y-auto pr-1">
        {options.map((opt) => (
          <label
            key={opt.value}
            className="flex min-h-9 cursor-pointer items-center gap-2.5 rounded-[var(--radius)] px-1 text-sm hover:bg-[color:var(--muted-soft)]/60"
          >
            <input
              type="checkbox"
              checked={selected.has(opt.value)}
              onChange={() => onToggle(opt.value)}
              className="h-4 w-4 shrink-0 rounded border-[color:var(--border)] accent-[color:var(--accent)]"
            />
            <span className="min-w-0 flex-1 truncate">{opt.label}</span>
            <span className="shrink-0 text-xs text-[color:var(--muted)]">({opt.count})</span>
          </label>
        ))}
      </div>
    </div>
  );
}
