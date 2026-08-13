"use client";

import { Search, SlidersHorizontal, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState, useTransition } from "react";
import { Tag } from "@/components/tag";
import type { Claim, ClaimReach } from "@/lib/types";

export type ClaimSortValue = "recent" | "reach" | "title";

type Props = {
  claims: Claim[];
  tags: { value: string; count: number }[];
  reach: Record<string, ClaimReach>;
  initial: { q: string; tags: string[]; sort: ClaimSortValue };
};

const SORT_LABELS: Record<ClaimSortValue, string> = {
  recent: "Most recent",
  reach: "Most repeated",
  title: "A–Z",
};

export function ClaimsExplorer({ claims, tags, reach, initial }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [, startTransition] = useTransition();
  const [queryInput, setQueryInput] = useState(initial.q);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const firstRender = useRef(true);

  const selectedTags = useMemo(() => new Set(initial.tags), [initial.tags]);

  function pushParams(next: URLSearchParams) {
    const qs = next.toString();
    startTransition(() => {
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
    });
  }

  // Debounced search input — same 250ms as the studies explorer.
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    const t = setTimeout(() => {
      const next = new URLSearchParams(searchParams?.toString() ?? "");
      const trimmed = queryInput.trim();
      if (trimmed) next.set("q", trimmed);
      else next.delete("q");
      pushParams(next);
    }, 250);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [queryInput]);

  function toggleTag(tag: string) {
    const next = new URLSearchParams(searchParams?.toString() ?? "");
    const current = next.getAll("tag");
    next.delete("tag");
    const setNext = new Set(current);
    if (setNext.has(tag)) setNext.delete(tag);
    else setNext.add(tag);
    for (const t of setNext) next.append("tag", t);
    pushParams(next);
  }

  function clearTags() {
    const next = new URLSearchParams(searchParams?.toString() ?? "");
    next.delete("tag");
    pushParams(next);
  }

  function setSort(value: ClaimSortValue) {
    const next = new URLSearchParams(searchParams?.toString() ?? "");
    if (value === "recent") next.delete("sort");
    else next.set("sort", value);
    pushParams(next);
  }

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

  const sidebar = (
    <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5">
      <div className="flex items-center justify-between gap-4">
        <h2 className="serif text-xl font-semibold tracking-tight">Topics</h2>
        {selectedTags.size > 0 && (
          <button
            type="button"
            onClick={clearTags}
            className="rounded-[var(--radius)] px-2 text-sm text-[color:var(--accent)] hover:underline"
          >
            Clear
          </button>
        )}
      </div>
      <div className="mt-4 max-h-[60vh] space-y-1 overflow-y-auto pr-1">
        {tags.length === 0 && (
          <p className="text-sm text-[color:var(--muted)]">No topics yet.</p>
        )}
        {tags.map((tag) => (
          <label
            key={tag.value}
            className="flex min-h-10 cursor-pointer items-center gap-3 rounded-[var(--radius)] px-1 py-2 text-sm hover:bg-[color:var(--muted-soft)]/60"
          >
            <input
              type="checkbox"
              checked={selectedTags.has(tag.value)}
              onChange={() => toggleTag(tag.value)}
              className="h-4 w-4 rounded-[var(--radius)] border-[color:var(--border)] accent-[color:var(--accent)]"
            />
            <span className="min-w-0 flex-1 truncate">{tag.value}</span>
            <span className="text-xs text-[color:var(--muted)]">
              ({tag.count})
            </span>
          </label>
        ))}
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
            placeholder="Search claims and responses…"
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            className="h-11 w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white pl-11 pr-5 text-sm placeholder:text-[color:var(--muted)] focus:border-[color:var(--accent)] focus:outline-none"
          />
        </div>
        <label className="flex items-center gap-2 text-sm text-[color:var(--muted)]">
          <span className="hidden sm:inline">Sort</span>
          <select
            value={initial.sort}
            onChange={(e) => setSort(e.target.value as ClaimSortValue)}
            className="h-11 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none"
          >
            {(Object.keys(SORT_LABELS) as ClaimSortValue[]).map((k) => (
              <option key={k} value={k}>
                {SORT_LABELS[k]}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={() => setDrawerOpen(true)}
          className="inline-flex h-11 items-center gap-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm font-medium md:hidden"
        >
          <SlidersHorizontal aria-hidden="true" size={16} />
          Topics
          {selectedTags.size > 0 && (
            <span className="rounded-[var(--radius)] bg-[color:var(--accent-soft)] px-2 py-0.5 text-xs text-[color:var(--accent)]">
              {selectedTags.size}
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
            {claims.length} {claims.length === 1 ? "claim" : "claims"}
            {initial.q ? ` matching "${initial.q}"` : ""}
            {selectedTags.size > 0
              ? ` · topics: ${[...selectedTags].join(", ")}`
              : ""}
          </p>

          {claims.length === 0 ? (
            <div className="rounded-[var(--radius)] border border-dashed border-[color:var(--border)] bg-white p-8 text-center text-sm text-[color:var(--muted)]">
              No claims match your filters.
            </div>
          ) : (
            <ul className="space-y-4">
              {claims.map((claim) => (
                <li key={claim.id}>
                  <ClaimCard claim={claim} reach={reach[claim.id]} />
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {drawerOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <button
            type="button"
            aria-label="Close topics"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/40"
          />
          <div className="absolute inset-y-0 right-0 w-[85%] max-w-sm overflow-y-auto border-l border-[color:var(--border)] bg-[color:var(--background)] p-5 shadow-lg">
            <div className="mb-4 flex items-center justify-between">
              <p className="small-caps text-xs font-medium text-[color:var(--muted)]">
                Filter by topic
              </p>
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                aria-label="Close"
                className="inline-flex h-10 w-10 items-center justify-center rounded-[var(--radius)] border border-[color:var(--border)]"
              >
                <X aria-hidden="true" size={16} />
              </button>
            </div>
            {sidebar}
          </div>
        </div>
      )}
    </div>
  );
}

function ClaimCard({ claim, reach }: { claim: Claim; reach?: ClaimReach }) {
  return (
    <Link
      href={`/claims/${claim.slug}`}
      className="group block rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 transition-colors hover:border-[color:var(--accent)]"
    >
      <div className="flex flex-wrap items-center gap-2">
        {claim.topic_tags.slice(0, 3).map((t) => (
          <Tag key={t} ink="accent">
            {t}
          </Tag>
        ))}
        {reach && reach.videoCount > 0 && (
          <Tag ink="muted">
            {reach.videoCount === 1
              ? "1 tracked video"
              : `${reach.videoCount} tracked videos`}
          </Tag>
        )}
      </div>

      <p className="serif mt-3 text-lg font-semibold leading-snug tracking-tight group-hover:text-[color:var(--accent)]">
        {claim.title}
      </p>

      <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-[color:var(--muted)]">
        {claim.claim_text}
      </p>

      <p className="small-caps mt-3 text-xs font-medium text-[color:var(--accent)]">
        {claim.sources.length === 1
          ? "1 source"
          : `${claim.sources.length} sources`}
      </p>
    </Link>
  );
}
