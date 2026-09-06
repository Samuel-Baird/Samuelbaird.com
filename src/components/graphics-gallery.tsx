"use client";

import { Search, SlidersHorizontal, X } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { GraphicAdminControls } from "@/components/admin/graphic-admin-controls";
import { FacetGroup } from "@/components/facet-group";
import { Tag } from "@/components/tag";
import { graphicId, type GalleryGraphic } from "@/lib/data-explorer";
import type { GraphicPostMap } from "@/lib/graphic-posts";
import { publishState, type PublishState } from "@/lib/graphic-publish";

const PAGE_SIZE = 24;

function stripLeadingPunctuation(title: string): string {
  return title.replace(/^[^\p{L}\p{N}]+/u, "");
}

/** Extracts the first 4-digit year in a fielded-period string, for sorting
 * the date filter chronologically instead of alphabetically (which would
 * put "2000-2025" before "1990s" but after "1997-1998"). */
function firstYear(period: string): number {
  const match = period.match(/\d{4}/);
  return match ? Number(match[0]) : 0;
}

type PublishFilter = "all" | PublishState;

const PUBLISH_FILTER_OPTIONS: { value: PublishFilter; label: string }[] = [
  { value: "all", label: "All" },
  { value: "published", label: "Published" },
  { value: "scheduled", label: "Scheduled" },
  { value: "hidden", label: "Hidden" },
];

/** Admin-only tri-state toggle over publish status - exclusive, so a plain
 * segmented control rather than FacetGroup's checkbox multi-select. */
function PublishFilterToggle({
  value,
  onChange,
  counts,
}: {
  value: PublishFilter;
  onChange: (v: PublishFilter) => void;
  counts: Record<PublishFilter, number>;
}) {
  return (
    <div>
      <h3 className="small-caps text-xs font-medium text-[color:var(--muted)]">Status</h3>
      <div className="mt-2 flex overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]">
        {PUBLISH_FILTER_OPTIONS.map((opt, i) => (
          <button
            key={opt.value}
            type="button"
            onClick={() => onChange(opt.value)}
            className={`flex-1 px-2 py-2 text-xs font-medium transition-colors ${
              i > 0 ? "border-l border-[color:var(--border)]" : ""
            } ${
              value === opt.value
                ? "bg-[color:var(--accent-soft)] text-[color:var(--accent)]"
                : "hover:bg-[color:var(--muted-soft)]"
            }`}
          >
            {opt.label} ({counts[opt.value]})
          </button>
        ))}
      </div>
    </div>
  );
}

export function GraphicsGallery({
  graphics,
  isAdmin = false,
  postMap,
}: {
  graphics: GalleryGraphic[];
  /** Admins see every graphic (unpublished included) plus the publish/posted
   * overlay on each card; non-admins get only what the server already
   * filtered to published. */
  isAdmin?: boolean;
  postMap?: GraphicPostMap;
}) {
  const [query, setQuery] = useState("");
  const [selectedDatasets, setSelectedDatasets] = useState<Set<string>>(new Set());
  const [selectedPeriods, setSelectedPeriods] = useState<Set<string>>(new Set());
  const [selectedTraditions, setSelectedTraditions] = useState<Set<string>>(new Set());
  const [publishFilter, setPublishFilter] = useState<PublishFilter>("all");
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const [drawerOpen, setDrawerOpen] = useState(false);

  function stateOf(g: GalleryGraphic): PublishState {
    return publishState(postMap?.[`${g.datasetSlug}/${graphicId(g)}`]);
  }

  const sorted = useMemo(
    () =>
      [...graphics].sort((a, b) =>
        stripLeadingPunctuation(a.title).localeCompare(stripLeadingPunctuation(b.title), "en", {
          sensitivity: "base",
        }),
      ),
    [graphics],
  );

  const datasetOptions = useMemo(() => {
    const counts = new Map<string, { label: string; count: number }>();
    for (const g of graphics) {
      const entry = counts.get(g.datasetSlug);
      if (entry) entry.count += 1;
      else counts.set(g.datasetSlug, { label: g.datasetName, count: 1 });
    }
    return [...counts.entries()]
      .map(([value, { label, count }]) => ({ value, label, count }))
      .sort((a, b) => a.label.localeCompare(b.label));
  }, [graphics]);

  const periodOptions = useMemo(() => {
    const counts = new Map<string, number>();
    for (const g of graphics) counts.set(g.fieldedPeriod, (counts.get(g.fieldedPeriod) ?? 0) + 1);
    return [...counts.entries()]
      .map(([value, count]) => ({ value, label: value, count }))
      .sort((a, b) => firstYear(a.value) - firstYear(b.value));
  }, [graphics]);

  const traditionOptions = useMemo(() => {
    const counts = new Map<string, number>();
    for (const g of graphics) {
      for (const t of g.traditions) counts.set(t, (counts.get(t) ?? 0) + 1);
    }
    return [...counts.entries()]
      .map(([value, count]) => ({ value, label: value, count }))
      .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
  }, [graphics]);

  const publishCounts = useMemo(() => {
    const counts: Record<PublishFilter, number> = {
      all: graphics.length,
      published: 0,
      scheduled: 0,
      hidden: 0,
    };
    for (const g of graphics) counts[stateOf(g)] += 1;
    return counts;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [graphics, postMap]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return sorted.filter((g) => {
      if (isAdmin && publishFilter !== "all" && stateOf(g) !== publishFilter) return false;
      if (selectedDatasets.size > 0 && !selectedDatasets.has(g.datasetSlug)) return false;
      if (selectedPeriods.size > 0 && !selectedPeriods.has(g.fieldedPeriod)) return false;
      if (selectedTraditions.size > 0 && !g.traditions.some((t) => selectedTraditions.has(t)))
        return false;
      if (!q) return true;
      const haystack = `${g.title} ${g.description} ${g.alt} ${g.datasetName}`.toLowerCase();
      return haystack.includes(q);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sorted, query, selectedDatasets, selectedPeriods, selectedTraditions, isAdmin, publishFilter, postMap]);

  const firstRender = useRef(true);
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    setVisibleCount(PAGE_SIZE);
  }, [query, selectedDatasets, selectedPeriods, selectedTraditions, publishFilter]);

  useEffect(() => {
    if (!drawerOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setDrawerOpen(false);
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [drawerOpen]);

  function toggle(set: Set<string>, setter: (s: Set<string>) => void, value: string) {
    const next = new Set(set);
    if (next.has(value)) next.delete(value);
    else next.add(value);
    setter(next);
  }

  const activeFilterCount =
    selectedDatasets.size +
    selectedPeriods.size +
    selectedTraditions.size +
    (publishFilter !== "all" ? 1 : 0);

  function clearAll() {
    setSelectedDatasets(new Set());
    setSelectedPeriods(new Set());
    setSelectedTraditions(new Set());
    setPublishFilter("all");
  }

  const sidebar = (
    <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5">
      <div className="flex items-center justify-between gap-4">
        <h2 className="serif text-xl font-semibold tracking-tight">Filters</h2>
        {activeFilterCount > 0 && (
          <button
            type="button"
            onClick={clearAll}
            className="rounded-[var(--radius)] px-2 text-sm text-[color:var(--accent)] hover:underline"
          >
            Clear
          </button>
        )}
      </div>
      <div className="mt-4 space-y-6">
        {isAdmin && (
          <PublishFilterToggle value={publishFilter} onChange={setPublishFilter} counts={publishCounts} />
        )}
        <FacetGroup
          title="Source"
          options={datasetOptions}
          selected={selectedDatasets}
          onToggle={(v) => toggle(selectedDatasets, setSelectedDatasets, v)}
        />
        <FacetGroup
          title="Fielded"
          options={periodOptions}
          selected={selectedPeriods}
          onToggle={(v) => toggle(selectedPeriods, setSelectedPeriods, v)}
        />
        <FacetGroup
          title="Tradition"
          options={traditionOptions}
          selected={selectedTraditions}
          onToggle={(v) => toggle(selectedTraditions, setSelectedTraditions, v)}
        />
      </div>
    </div>
  );

  const visible = filtered.slice(0, visibleCount);

  return (
    <div>
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search
            aria-hidden="true"
            className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--muted)]"
          />
          <input
            type="search"
            inputMode="search"
            placeholder="Search title, description, group…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="h-11 w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white pl-11 pr-5 text-sm placeholder:text-[color:var(--muted)] focus:border-[color:var(--accent)] focus:outline-none"
          />
        </div>
        <button
          type="button"
          onClick={() => setDrawerOpen(true)}
          className="inline-flex h-11 items-center gap-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm font-medium md:hidden"
        >
          <SlidersHorizontal aria-hidden="true" size={16} />
          Filters
          {activeFilterCount > 0 && (
            <span className="rounded-[var(--radius)] bg-[color:var(--accent-soft)] px-2 py-0.5 text-xs text-[color:var(--accent)]">
              {activeFilterCount}
            </span>
          )}
        </button>
      </div>

      <div className="grid gap-8 md:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="hidden md:block">
          <div className="sticky top-20">{sidebar}</div>
        </aside>
        <div className="min-w-0">
          <p className="mb-4 text-xs text-[color:var(--muted)]">
            {filtered.length} {filtered.length === 1 ? "graphic" : "graphics"}
            {query ? ` matching "${query}"` : ""}
          </p>

          {filtered.length === 0 ? (
            <div className="rounded-[var(--radius)] border border-dashed border-[color:var(--border)] bg-white p-8 text-center text-sm text-[color:var(--muted)]">
              No graphics match your filters.
            </div>
          ) : (
            <>
              <ul className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
                {visible.map((g) => {
                  const id = graphicId(g);
                  const href = g.href ?? `/data-explorer/${g.datasetSlug}/graphics/${id}`;
                  const status = postMap?.[`${g.datasetSlug}/${id}`];
                  const state = publishState(status);
                  return (
                    <li key={`${g.datasetSlug}/${id}`}>
                      <div
                        className={`group flex h-full flex-col overflow-hidden rounded-[var(--radius)] border bg-white transition-colors hover:border-[color:var(--accent)] ${
                          isAdmin && state === "hidden"
                            ? "border-dashed border-[color:var(--oxblood)]/40"
                            : isAdmin && state === "scheduled"
                              ? "border-dashed border-[color:var(--accent)]/50"
                              : "border-[color:var(--border)]"
                        }`}
                      >
                        <Link href={href} className="flex flex-1 flex-col">
                          <div className="overflow-hidden border-b border-[color:var(--border)]">
                            <Image
                              src={g.imageSrc}
                              alt={g.alt}
                              width={g.width}
                              height={g.height}
                              className="h-auto w-full"
                            />
                          </div>
                          <div className="flex flex-1 flex-col p-4">
                            <div className="flex flex-wrap items-center gap-1.5">
                              <Tag ink="ink">{g.datasetName}</Tag>
                              <Tag ink="muted">{g.fieldedPeriod}</Tag>
                              {isAdmin && state === "hidden" && <Tag ink="oxblood">Hidden</Tag>}
                              {isAdmin && state === "scheduled" && <Tag ink="accent">Scheduled</Tag>}
                            </div>
                            <h3 className="serif mt-3 text-base font-semibold leading-snug tracking-tight text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
                              {g.title}
                            </h3>
                            {g.traditions.length > 0 && (
                              <div className="mt-2 flex flex-wrap gap-1.5">
                                {g.traditions.slice(0, 3).map((t) => (
                                  <Tag key={t} ink="accent">
                                    {t}
                                  </Tag>
                                ))}
                                {g.traditions.length > 3 && (
                                  <Tag ink="muted" title={g.traditions.slice(3).join(", ")}>
                                    +{g.traditions.length - 3} more
                                  </Tag>
                                )}
                              </div>
                            )}
                          </div>
                        </Link>
                        {isAdmin && (
                          <div className="border-t border-[color:var(--border)] p-3">
                            <GraphicAdminControls
                              slug={g.datasetSlug}
                              graphicId={id}
                              published={status?.published === true}
                              publishAt={status?.publish_at ?? null}
                              posted={status?.posted === true}
                              postedDates={status?.posted_dates ?? ""}
                              currentPath="/data-explorer/gallery"
                            />
                          </div>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>

              {visibleCount < filtered.length && (
                <div className="mt-8 flex justify-center">
                  <button
                    type="button"
                    onClick={() => setVisibleCount((n) => n + PAGE_SIZE)}
                    className="inline-flex h-11 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-6 text-sm font-medium hover:bg-[color:var(--muted-soft)]"
                  >
                    Load more ({filtered.length - visibleCount} remaining)
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {drawerOpen && (
        <div className="fixed inset-0 z-50 md:hidden" role="dialog" aria-modal="true">
          <button
            type="button"
            aria-label="Close filters"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/35"
          />
          <div className="absolute right-0 top-0 flex h-full w-[88vw] max-w-sm flex-col bg-[color:var(--background)] shadow-xl">
            <div className="flex items-center justify-between border-b border-[color:var(--border)] p-4">
              <h3 className="serif text-lg font-semibold">Filters</h3>
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                aria-label="Close"
                className="inline-flex h-10 w-10 items-center justify-center rounded-[var(--radius)] hover:bg-[color:var(--muted-soft)]"
              >
                <X size={18} aria-hidden="true" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4">{sidebar}</div>
          </div>
        </div>
      )}
    </div>
  );
}
