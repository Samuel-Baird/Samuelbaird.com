"use client";

import { Search, SlidersHorizontal, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { CategoryCard, DatasetCard, StudyCard } from "@/components/dataset-card";
import { FacetGroup } from "@/components/facet-group";
import type { Folder } from "@/lib/explorer-folders";

const TYPE_LABELS: Record<Folder["kind"], string> = {
  dataset: "Dataset",
  category: "Collection",
  study: "Study",
};

function folderSearchText(folder: Folder): string {
  if (folder.kind === "dataset") {
    const d = folder.dataset;
    return `${d.name} ${d.shortDescription} ${d.sponsor} ${d.fielder}`;
  }
  if (folder.kind === "category") {
    return `${folder.category} ${folder.items.map((d) => d.name).join(" ")}`;
  }
  const s = folder.study;
  return `${s.title} ${s.authors.join(" ")} ${s.abstract ?? ""}`;
}

function folderCard(folder: Folder) {
  if (folder.kind === "dataset") return <DatasetCard key={folder.key} dataset={folder.dataset} />;
  if (folder.kind === "category") {
    return (
      <CategoryCard
        key={folder.key}
        category={folder.category}
        slug={folder.slug}
        items={folder.items}
      />
    );
  }
  return <StudyCard key={folder.key} study={folder.study} graphicsCount={folder.graphics.length} />;
}

/** Search + facet filters over the Data Explorer's folders (datasets,
 * dataset collections, and studies with their own graphics) - the same
 * "search box + checkbox facets" pattern as GraphicsGallery
 * (/data-explorer/gallery), scoped to which folders show rather than which
 * individual graphics show. */
export function FolderExplorer({ folders }: { folders: Folder[] }) {
  const [query, setQuery] = useState("");
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(new Set());
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set());
  const [selectedTraditions, setSelectedTraditions] = useState<Set<string>>(new Set());
  const [drawerOpen, setDrawerOpen] = useState(false);

  const typeOptions = useMemo(() => {
    const counts = new Map<string, number>();
    for (const f of folders) counts.set(f.kind, (counts.get(f.kind) ?? 0) + 1);
    return [...counts.entries()]
      .map(([value, count]) => ({ value, label: TYPE_LABELS[value as Folder["kind"]], count }))
      .sort((a, b) => b.count - a.count);
  }, [folders]);

  const categoryOptions = useMemo(() => {
    const counts = new Map<string, number>();
    for (const f of folders) {
      if (f.category) counts.set(f.category, (counts.get(f.category) ?? 0) + 1);
    }
    return [...counts.entries()]
      .map(([value, count]) => ({ value, label: value, count }))
      .sort((a, b) => a.label.localeCompare(b.label));
  }, [folders]);

  const traditionOptions = useMemo(() => {
    const counts = new Map<string, number>();
    for (const f of folders) {
      for (const t of f.traditions) counts.set(t, (counts.get(t) ?? 0) + 1);
    }
    return [...counts.entries()]
      .map(([value, count]) => ({ value, label: value, count }))
      .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
  }, [folders]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return folders.filter((f) => {
      if (selectedTypes.size > 0 && !selectedTypes.has(f.kind)) return false;
      if (selectedCategories.size > 0 && (!f.category || !selectedCategories.has(f.category))) {
        return false;
      }
      if (
        selectedTraditions.size > 0 &&
        !f.traditions.some((t) => selectedTraditions.has(t))
      ) {
        return false;
      }
      if (!q) return true;
      return folderSearchText(f).toLowerCase().includes(q);
    });
  }, [folders, query, selectedTypes, selectedCategories, selectedTraditions]);

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

  const activeFilterCount = selectedTypes.size + selectedCategories.size + selectedTraditions.size;

  function clearAll() {
    setSelectedTypes(new Set());
    setSelectedCategories(new Set());
    setSelectedTraditions(new Set());
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
        <FacetGroup
          title="Type"
          options={typeOptions}
          selected={selectedTypes}
          onToggle={(v) => toggle(selectedTypes, setSelectedTypes, v)}
        />
        <FacetGroup
          title="Category"
          options={categoryOptions}
          selected={selectedCategories}
          onToggle={(v) => toggle(selectedCategories, setSelectedCategories, v)}
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
            placeholder="Search dataset or study name…"
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
            {filtered.length} {filtered.length === 1 ? "folder" : "folders"}
            {query ? ` matching "${query}"` : ""}
          </p>

          {filtered.length === 0 ? (
            <div className="rounded-[var(--radius)] border border-dashed border-[color:var(--border)] bg-white p-8 text-center text-sm text-[color:var(--muted)]">
              No datasets or studies match your filters.
            </div>
          ) : (
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {filtered.map((f) => folderCard(f))}
            </div>
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
