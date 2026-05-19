"use client";

import { Search, SlidersHorizontal, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState, useTransition } from "react";
import { BookmarkButton } from "@/components/bookmark-button";
import { UpvoteButton } from "@/components/upvote-button";
import type { Study } from "@/lib/types";

type Props = {
  studies: Study[];
  tags: { value: string; count: number }[];
  bookmarkedSet: Set<string>;
  upvotedSet: Set<string>;
  upvoteCounts: Record<string, number>;
  signedIn: boolean;
  initial: { q: string; tags: string[]; sort: "featured" | "year" | "upvotes" };
};

const SORT_LABELS: Record<Props["initial"]["sort"], string> = {
  featured: "Featured",
  year: "Newest",
  upvotes: "Most upvoted",
};

const CATEGORY_ORDER = [
  "Wellbeing & Flourishing",
  "Mental Health",
  "Major Demographic Surveys",
  "Physical Health & Longevity",
  "Retention & Generational Change",
];

const SOURCE_TYPE_LABELS: Record<string, { label: string; className: string }> = {
  primary_dataset: {
    label: "Primary Dataset",
    className: "bg-emerald-100 text-emerald-800",
  },
  study: {
    label: "Study",
    className: "bg-blue-100 text-blue-800",
  },
  secondary_analysis: {
    label: "Secondary Analysis",
    className: "bg-[color:var(--muted-soft)] text-[color:var(--muted)]",
  },
};

export function StudiesExplorer({
  studies,
  tags,
  bookmarkedSet,
  upvotedSet,
  upvoteCounts,
  signedIn,
  initial,
}: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [, startTransition] = useTransition();
  const [queryInput, setQueryInput] = useState(initial.q);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const drawerRef = useRef<HTMLDivElement>(null);
  const firstRender = useRef(true);

  const selectedTags = useMemo(() => new Set(initial.tags), [initial.tags]);

  function pushParams(next: URLSearchParams) {
    const qs = next.toString();
    startTransition(() => {
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
    });
  }

  // Debounced search input
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

  function setSort(value: Props["initial"]["sort"]) {
    const next = new URLSearchParams(searchParams?.toString() ?? "");
    if (value === "featured") next.delete("sort");
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
    <div className="rounded-2xl border border-[color:var(--border)] bg-white p-5">
      <div className="flex items-center justify-between gap-4">
        <h2 className="serif text-xl font-semibold tracking-tight">Topics</h2>
        {selectedTags.size > 0 && (
          <button
            type="button"
            onClick={clearTags}
            className="rounded-full px-2 text-sm text-[color:var(--accent)] hover:underline"
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
            className="flex min-h-10 cursor-pointer items-center gap-3 rounded-lg px-1 py-2 text-sm hover:bg-[color:var(--muted-soft)]/60"
          >
            <input
              type="checkbox"
              checked={selectedTags.has(tag.value)}
              onChange={() => toggleTag(tag.value)}
              className="h-4 w-4 rounded border-[color:var(--border)] accent-[color:var(--accent)]"
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

  const isGrouped =
    !initial.q && initial.tags.length === 0 && initial.sort === "featured";

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
            placeholder="Search title, author, abstract, tags…"
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            className="h-11 w-full rounded-full border border-[color:var(--border)] bg-white pl-11 pr-5 text-sm placeholder:text-[color:var(--muted)] focus:border-[color:var(--accent)] focus:outline-none"
          />
        </div>
        <label className="flex items-center gap-2 text-sm text-[color:var(--muted)]">
          <span className="hidden sm:inline">Sort</span>
          <select
            value={initial.sort}
            onChange={(e) =>
              setSort(e.target.value as Props["initial"]["sort"])
            }
            className="h-11 rounded-full border border-[color:var(--border)] bg-white px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none"
          >
            {(Object.keys(SORT_LABELS) as Array<keyof typeof SORT_LABELS>).map(
              (k) => (
                <option key={k} value={k}>
                  {SORT_LABELS[k]}
                </option>
              ),
            )}
          </select>
        </label>
        <button
          type="button"
          onClick={() => setDrawerOpen(true)}
          className="inline-flex h-11 items-center gap-2 rounded-full border border-[color:var(--border)] bg-white px-4 text-sm font-medium md:hidden"
        >
          <SlidersHorizontal aria-hidden="true" size={16} />
          Topics
          {selectedTags.size > 0 && (
            <span className="rounded-full bg-[color:var(--accent-soft)] px-2 py-0.5 text-xs text-[color:var(--accent)]">
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
            {studies.length} {studies.length === 1 ? "study" : "studies"}
            {initial.q ? ` matching "${initial.q}"` : ""}
            {selectedTags.size > 0
              ? ` · topics: ${[...selectedTags].join(", ")}`
              : ""}
          </p>

          {studies.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-[color:var(--border)] bg-white p-8 text-center text-sm text-[color:var(--muted)]">
              No studies match your filters.
            </div>
          ) : isGrouped ? (
            <GroupedStudies
              studies={studies}
              bookmarkedSet={bookmarkedSet}
              upvotedSet={upvotedSet}
              upvoteCounts={upvoteCounts}
              signedIn={signedIn}
            />
          ) : (
            <StudyGrid
              studies={studies}
              bookmarkedSet={bookmarkedSet}
              upvotedSet={upvotedSet}
              upvoteCounts={upvoteCounts}
              signedIn={signedIn}
            />
          )}
        </div>
      </div>

      {drawerOpen && (
        <div
          className="fixed inset-0 z-50 md:hidden"
          role="dialog"
          aria-modal="true"
        >
          <button
            type="button"
            aria-label="Close topics"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/35"
          />
          <div
            ref={drawerRef}
            className="absolute right-0 top-0 flex h-full w-[88vw] max-w-sm flex-col bg-[color:var(--background)] shadow-xl"
          >
            <div className="flex items-center justify-between border-b border-[color:var(--border)] p-4">
              <h3 className="serif text-lg font-semibold">Topics</h3>
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                aria-label="Close"
                className="inline-flex h-10 w-10 items-center justify-center rounded-full hover:bg-[color:var(--muted-soft)]"
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

type GridProps = {
  studies: Study[];
  bookmarkedSet: Set<string>;
  upvotedSet: Set<string>;
  upvoteCounts: Record<string, number>;
  signedIn: boolean;
};

function GroupedStudies({ studies, ...rest }: GridProps) {
  const byCategory = new Map<string, Study[]>();
  for (const s of studies) {
    const key = s.category ?? "Other";
    if (!byCategory.has(key)) byCategory.set(key, []);
    byCategory.get(key)!.push(s);
  }

  const orderedKeys = [
    ...CATEGORY_ORDER.filter((k) => byCategory.has(k)),
    ...[...byCategory.keys()].filter((k) => !CATEGORY_ORDER.includes(k)),
  ];

  return (
    <div className="space-y-12">
      {orderedKeys.map((cat) => (
        <section key={cat}>
          <h2 className="serif mb-5 text-xl font-semibold tracking-tight text-[color:var(--foreground)]">
            {cat}
          </h2>
          <StudyGrid studies={byCategory.get(cat)!} {...rest} />
        </section>
      ))}
    </div>
  );
}

function StudyGrid({ studies, bookmarkedSet, upvotedSet, upvoteCounts, signedIn }: GridProps) {
  return (
    <ul className="grid gap-5 sm:grid-cols-2">
      {studies.map((s) => (
        <StudyCard
          key={s.id}
          study={s}
          bookmarked={bookmarkedSet.has(s.id)}
          upvoted={upvotedSet.has(s.id)}
          upvoteCount={upvoteCounts[s.id] ?? 0}
          signedIn={signedIn}
        />
      ))}
    </ul>
  );
}

function StudyCard({
  study: s,
  bookmarked,
  upvoted,
  upvoteCount,
  signedIn,
}: {
  study: Study;
  bookmarked: boolean;
  upvoted: boolean;
  upvoteCount: number;
  signedIn: boolean;
}) {
  const sourceType = s.source_type ? SOURCE_TYPE_LABELS[s.source_type] : null;
  return (
    <li className="relative">
      <div className="absolute right-3 top-3 z-10 flex items-center gap-2">
        <UpvoteButton
          targetType="study"
          targetId={s.id}
          initialCount={upvoteCount}
          initialUpvoted={upvoted}
          signedIn={signedIn}
          size="sm"
        />
        <BookmarkButton
          targetType="study"
          targetId={s.id}
          initial={bookmarked}
          signedIn={signedIn}
          size="sm"
        />
      </div>
      <Link
        href={`/studies/${s.slug}`}
        className={
          "group block h-full rounded-2xl border bg-white p-6 pr-28 transition-colors " +
          (s.flagged_problematic
            ? "border-red-200 hover:border-red-500"
            : "border-[color:var(--border)] hover:border-[color:var(--accent)]")
        }
      >
        {s.flagged_problematic && (
          <span
            aria-label="Flagged for methodological concerns"
            className="absolute left-3 top-3 z-10 inline-flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-xs font-bold text-white"
          >
            !
          </span>
        )}
        <div className="flex flex-wrap items-center gap-2 text-xs text-[color:var(--muted)]">
          {sourceType && (
            <span className={`rounded-full px-2.5 py-1 font-medium uppercase tracking-wide text-[10px] ${sourceType.className}`}>
              {sourceType.label}
            </span>
          )}
          {s.year && (
            <span className="rounded-full bg-[color:var(--muted-soft)] px-2.5 py-1 tabular-nums">
              {s.year}
            </span>
          )}
          {s.tags.slice(0, 2).map((t) => (
            <span
              key={t}
              className="rounded-full bg-[color:var(--accent-soft)] px-2.5 py-1 text-[color:var(--accent)]"
            >
              {t}
            </span>
          ))}
        </div>
        <h2 className="serif mt-4 text-xl font-semibold leading-snug tracking-tight text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
          {s.title}
        </h2>
        {s.authors.length > 0 && (
          <p className="mt-2 text-sm text-[color:var(--muted)]">
            {s.authors.join(", ")}
          </p>
        )}
        {s.abstract && (
          <p className="mt-4 line-clamp-4 text-sm leading-relaxed text-[color:var(--foreground)]">
            {s.abstract}
          </p>
        )}
        <p className="mt-5 text-xs text-[color:var(--accent)]">Read study →</p>
      </Link>
    </li>
  );
}
