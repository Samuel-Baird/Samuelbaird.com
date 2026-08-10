"use client";

import { ChevronDown, Copy, Download, Search } from "lucide-react";
import { useEffect, useRef } from "react";
import { Tag } from "@/components/tag";
import { HearsayBadge } from "./badges";
import {
  CATEGORY_META,
  HEARSAY_META,
  REFERENT_META,
  SOURCE_TYPE_META,
  STATUS_META,
} from "./constants";
import { ScalesLegend } from "./legend";
import {
  CATEGORY_IDS,
  CORRELATION_STATUSES,
  HEARSAY_GRADES,
  REFERENTS,
  SOURCE_TYPES,
  type CategoryId,
  type CorrelationStatus,
  type HearsayGrade,
  type Referent,
  type SourceType,
} from "./schema";

/**
 * Search + the five filter facets + the scales legend. Rendered twice: as the
 * sticky desktop sidebar and inside the mobile drawer. Filter state lives in
 * TimelineExplorer so both instances stay in sync and the graph can read it.
 */

export type FilterPanelProps = {
  variant: "desktop" | "drawer";
  query: string;
  onQueryChange: (value: string) => void;
  cats: Set<CategoryId>;
  onToggleCat: (id: CategoryId) => void;
  referents: Set<Referent>;
  onToggleReferent: (r: Referent) => void;
  sourceTypes: Set<SourceType>;
  onToggleSourceType: (t: SourceType) => void;
  grades: Set<HearsayGrade>;
  onToggleGrade: (g: HearsayGrade) => void;
  statuses: Set<CorrelationStatus>;
  onToggleStatus: (s: CorrelationStatus) => void;
  collapseCitations: boolean;
  onToggleCollapseCitations: () => void;
  visibleCount: number;
  totalCount: number;
  anyFilterActive: boolean;
  onClearAll: () => void;
  onExport: () => void;
  onCopy: () => void;
  copied: boolean;
};

export function FilterPanel({
  variant,
  query,
  onQueryChange,
  cats,
  onToggleCat,
  referents,
  onToggleReferent,
  sourceTypes,
  onToggleSourceType,
  grades,
  onToggleGrade,
  statuses,
  onToggleStatus,
  collapseCitations,
  onToggleCollapseCitations,
  visibleCount,
  totalCount,
  anyFilterActive,
  onClearAll,
  onExport,
  onCopy,
  copied,
}: FilterPanelProps) {
  const catsPanelRef = useRef<HTMLDetailsElement>(null);

  // The desktop sidebar server-renders closed (compact on phones) and pops
  // open after mount, where the layout has room. `open` is uncontrolled, so
  // there is no hydration mismatch. The drawer opens on demand and is tall
  // enough already, so it keeps every panel collapsed.
  useEffect(() => {
    if (variant !== "desktop") return;
    if (window.matchMedia("(min-width: 1024px)").matches && catsPanelRef.current) {
      catsPanelRef.current.open = true;
    }
  }, [variant]);

  return (
    <div className={variant === "drawer" ? "p-4" : undefined}>
      <div className="relative">
        <Search
          aria-hidden="true"
          className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--muted)]"
        />
        <input
          type="search"
          inputMode="search"
          placeholder="Search sources…"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          className="h-10 w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white pl-11 pr-5 text-sm placeholder:text-[color:var(--muted)] focus:border-[color:var(--accent)] focus:outline-none"
        />
      </div>

      <div className="mt-2 flex items-center gap-2 py-1">
        <span className="text-xs tabular-nums text-[color:var(--muted)]">
          {visibleCount} of {totalCount} sources
        </span>
        {anyFilterActive && (
          <button
            type="button"
            onClick={onClearAll}
            className="text-xs font-medium text-[color:var(--accent)] hover:underline"
          >
            Clear
          </button>
        )}
        <span className="ml-auto flex gap-1.5">
          <button
            type="button"
            onClick={onExport}
            title="Export filtered sources as Markdown"
            className="small-caps inline-flex h-8 items-center gap-1.5 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
          >
            <Download aria-hidden="true" size={13} />
            .md
          </button>
          <button
            type="button"
            onClick={onCopy}
            title="Copy filtered sources as Markdown"
            className="small-caps inline-flex h-8 items-center gap-1.5 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
          >
            <Copy aria-hidden="true" size={13} />
            {copied ? "Copied!" : "Copy"}
          </button>
        </span>
      </div>

      <label className="flex cursor-pointer items-center gap-2 py-1.5 text-xs font-medium">
        <input
          type="checkbox"
          checked={collapseCitations}
          onChange={onToggleCollapseCitations}
          className="h-3.5 w-3.5 rounded border-[color:var(--border)] accent-[color:var(--accent)]"
        />
        Collapse citations
      </label>
      {collapseCitations && (
        <p className="pb-1.5 text-xs leading-relaxed text-[color:var(--muted)]">
          Showing originals only. Later sources that quote them are listed
          beneath each original as citations.
        </p>
      )}

      <PanelSection label="Categories" count={cats.size} panelRef={catsPanelRef}>
        {CATEGORY_IDS.map((id) => (
          <FilterOption
            key={id}
            checked={cats.has(id)}
            onChange={() => onToggleCat(id)}
          >
            <Tag ink={CATEGORY_META[id].ink}>{CATEGORY_META[id].label}</Tag>
          </FilterOption>
        ))}
      </PanelSection>
      <PanelSection label="Referent" count={referents.size}>
        {REFERENTS.map((r) => (
          <FilterOption
            key={r}
            checked={referents.has(r)}
            onChange={() => onToggleReferent(r)}
          >
            <Tag ink={REFERENT_META[r].ink}>{REFERENT_META[r].short}</Tag>
          </FilterOption>
        ))}
      </PanelSection>
      <PanelSection label="Type" count={sourceTypes.size}>
        {SOURCE_TYPES.map((t) => (
          <FilterOption
            key={t}
            checked={sourceTypes.has(t)}
            onChange={() => onToggleSourceType(t)}
          >
            <span className="text-sm">{SOURCE_TYPE_META[t].label}</span>
          </FilterOption>
        ))}
      </PanelSection>
      <PanelSection label="Hearsay" count={grades.size}>
        {HEARSAY_GRADES.map((g) => (
          <FilterOption
            key={g}
            checked={grades.has(g)}
            onChange={() => onToggleGrade(g)}
          >
            <span className="flex items-center gap-2">
              <HearsayBadge grade={g} />
              <span className="text-xs text-[color:var(--muted)]">
                {HEARSAY_META[g].description}
              </span>
            </span>
          </FilterOption>
        ))}
      </PanelSection>
      <PanelSection label="Status" count={statuses.size}>
        {CORRELATION_STATUSES.map((s) => (
          <FilterOption
            key={s}
            checked={statuses.has(s)}
            onChange={() => onToggleStatus(s)}
          >
            <span className="flex items-center gap-2 text-sm">
              <span
                aria-hidden="true"
                className={`inline-block h-1.5 w-1.5 rounded-full ${STATUS_META[s].dot}`}
              />
              <span className="small-caps">{STATUS_META[s].label}</span>
            </span>
          </FilterOption>
        ))}
      </PanelSection>

      <PanelSection label="About the scales">
        <ScalesLegend />
      </PanelSection>
    </div>
  );
}

function PanelSection({
  label,
  count,
  panelRef,
  children,
}: {
  label: string;
  count?: number;
  panelRef?: React.Ref<HTMLDetailsElement>;
  children: React.ReactNode;
}) {
  return (
    <details
      ref={panelRef}
      className="group border-t border-[color:var(--border)] first-of-type:border-t-0"
    >
      <summary className="flex cursor-pointer list-none items-center gap-1.5 py-2.5 text-sm font-medium hover:text-[color:var(--accent)] [&::-webkit-details-marker]:hidden">
        {label}
        {count != null && count > 0 && (
          <span className="rounded-[var(--radius)] bg-[color:var(--accent-soft)] px-1.5 py-0.5 text-[10px] tabular-nums text-[color:var(--accent)]">
            {count}
          </span>
        )}
        <ChevronDown
          aria-hidden="true"
          size={13}
          className="ml-auto transition-transform group-open:rotate-180"
        />
      </summary>
      <div className="pb-2">{children}</div>
    </details>
  );
}

function FilterOption({
  checked,
  onChange,
  children,
}: {
  checked: boolean;
  onChange: () => void;
  children: React.ReactNode;
}) {
  return (
    <label className="flex min-h-9 cursor-pointer items-center gap-3 rounded-[var(--radius)] px-2 py-1.5 hover:bg-[color:var(--muted-soft)]/60">
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="h-4 w-4 shrink-0 rounded border-[color:var(--border)] accent-[color:var(--accent)]"
      />
      {children}
    </label>
  );
}
