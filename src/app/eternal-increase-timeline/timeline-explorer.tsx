"use client";

import {
  ChevronDown,
  Copy,
  Download,
  ExternalLink,
  Search,
  TriangleAlert,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  CATEGORY_META,
  ERAS,
  HEARSAY_META,
  STATUS_META,
  eraFor,
} from "./constants";
import { buildMarkdown, downloadMarkdown, type FilterState } from "./export-markdown";
import {
  CATEGORY_IDS,
  CORRELATION_STATUSES,
  HEARSAY_GRADES,
  type CategoryId,
  type CorrelationStatus,
  type HearsayGrade,
  type SourceEntry,
} from "./schema";

function norm(s: string): string {
  return s.toLowerCase().normalize("NFD").replace(/\p{M}/gu, "");
}

function toggleIn<T>(set: Set<T>, value: T): Set<T> {
  const next = new Set(set);
  if (next.has(value)) next.delete(value);
  else next.add(value);
  return next;
}

export function TimelineExplorer({ entries }: { entries: SourceEntry[] }) {
  const [cats, setCats] = useState<Set<CategoryId>>(new Set());
  const [grades, setGrades] = useState<Set<HearsayGrade>>(new Set());
  const [statuses, setStatuses] = useState<Set<CorrelationStatus>>(new Set());
  const [query, setQuery] = useState("");
  const [copied, setCopied] = useState(false);
  const barRef = useRef<HTMLDivElement>(null);

  // The site header is sticky and reflows with viewport width (73px wide,
  // 129px when the wordmark wraps beside the nav links), so park the filter
  // bar directly beneath whatever height it currently is.
  useEffect(() => {
    const header = document.querySelector("body > header");
    const bar = barRef.current;
    if (!header || !bar) return;
    const sync = () => {
      bar.style.top = `${header.getBoundingClientRect().height}px`;
    };
    sync();
    const observer = new ResizeObserver(sync);
    observer.observe(header);
    return () => observer.disconnect();
  }, []);

  const filtered = useMemo(() => {
    const tokens = norm(query).split(/\s+/).filter(Boolean);
    return entries.filter((entry) => {
      if (cats.size > 0 && !entry.categories.some((c) => cats.has(c))) {
        return false;
      }
      if (grades.size > 0 && !grades.has(entry.hearsay)) return false;
      if (statuses.size > 0 && !statuses.has(entry.correlationStatus)) {
        return false;
      }
      if (tokens.length > 0) {
        const haystack = norm(
          `${entry.title} ${entry.speaker} ${entry.transcription}`,
        );
        if (!tokens.every((t) => haystack.includes(t))) return false;
      }
      return true;
    });
  }, [entries, cats, grades, statuses, query]);

  const anyFilterActive =
    cats.size > 0 || grades.size > 0 || statuses.size > 0 || query.trim() !== "";

  const filters: FilterState = { categories: cats, grades, statuses, query };

  function handleExport() {
    downloadMarkdown(buildMarkdown(filtered, entries.length, filters));
  }

  function handleCopy() {
    navigator.clipboard
      .writeText(buildMarkdown(filtered, entries.length, filters))
      .then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
  }

  function clearAll() {
    setCats(new Set());
    setGrades(new Set());
    setStatuses(new Set());
    setQuery("");
  }

  return (
    <div className="mt-10">
      <div
        ref={barRef}
        style={{ top: 73 }}
        className="sticky z-30 -mx-5 border-b border-[color:var(--border)] bg-[color:var(--background)]/90 px-5 py-3 backdrop-blur sm:-mx-8 sm:px-8 print:hidden"
      >
        <div className="relative">
          <Search
            aria-hidden="true"
            className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--muted)]"
          />
          <input
            type="search"
            inputMode="search"
            placeholder="Search title, speaker, transcription…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="h-10 w-full rounded-full border border-[color:var(--border)] bg-white pl-11 pr-5 text-sm placeholder:text-[color:var(--muted)] focus:border-[color:var(--accent)] focus:outline-none"
          />
        </div>
        <div className="mt-2.5 flex flex-wrap items-center gap-2">
          <FilterDropdown label="Categories" count={cats.size}>
            {CATEGORY_IDS.map((id) => (
              <FilterOption
                key={id}
                checked={cats.has(id)}
                onChange={() => setCats(toggleIn(cats, id))}
              >
                <span
                  className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ring-1 ${CATEGORY_META[id].pill}`}
                >
                  {CATEGORY_META[id].label}
                </span>
              </FilterOption>
            ))}
          </FilterDropdown>
          <FilterDropdown label="Hearsay" count={grades.size}>
            {HEARSAY_GRADES.map((g) => (
              <FilterOption
                key={g}
                checked={grades.has(g)}
                onChange={() => setGrades(toggleIn(grades, g))}
              >
                <span className="flex items-center gap-2">
                  <HearsayBadge grade={g} />
                  <span className="text-xs text-[color:var(--muted)]">
                    {HEARSAY_META[g].description}
                  </span>
                </span>
              </FilterOption>
            ))}
          </FilterDropdown>
          <FilterDropdown label="Status" count={statuses.size}>
            {CORRELATION_STATUSES.map((s) => (
              <FilterOption
                key={s}
                checked={statuses.has(s)}
                onChange={() => setStatuses(toggleIn(statuses, s))}
              >
                <span className="flex items-center gap-2 text-sm">
                  <span
                    aria-hidden="true"
                    className={`inline-block h-1.5 w-1.5 rounded-full ${STATUS_META[s].dot}`}
                  />
                  {STATUS_META[s].label}
                </span>
              </FilterOption>
            ))}
          </FilterDropdown>
          {anyFilterActive && (
            <button
              type="button"
              onClick={clearAll}
              className="rounded-full px-2 text-sm text-[color:var(--accent)] hover:underline"
            >
              Clear
            </button>
          )}
          <span className="ml-auto text-xs tabular-nums text-[color:var(--muted)]">
            {filtered.length} of {entries.length} sources
          </span>
          <button
            type="button"
            onClick={handleExport}
            className="inline-flex h-8 items-center gap-1.5 rounded-full border border-[color:var(--border)] bg-white px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
          >
            <Download aria-hidden="true" size={13} />
            Export .md
          </button>
          <button
            type="button"
            onClick={handleCopy}
            className="inline-flex h-8 items-center gap-1.5 rounded-full border border-[color:var(--border)] bg-white px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
          >
            <Copy aria-hidden="true" size={13} />
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="mt-10 rounded-2xl border border-dashed border-[color:var(--border)] bg-white p-8 text-center text-sm text-[color:var(--muted)]">
          No sources match your filters.
        </div>
      ) : (
        <div className="mt-10 space-y-14">
          {ERAS.map((era) => {
            const inEra = filtered.filter((e) => eraFor(e).id === era.id);
            if (inEra.length === 0) return null;
            return (
              <section key={era.id}>
                <p className="text-xs font-medium uppercase tracking-[0.18em] tabular-nums text-[color:var(--muted)]">
                  {era.range}
                </p>
                <h2 className="serif mt-1 text-2xl font-semibold tracking-tight">
                  {era.label}
                </h2>
                <ol className="relative mt-6 space-y-6 border-l border-[color:var(--border)] pl-6 sm:pl-8">
                  {inEra.map((entry) => (
                    <TimelineEntry key={entry.id} entry={entry} />
                  ))}
                </ol>
              </section>
            );
          })}
        </div>
      )}
    </div>
  );
}

function FilterDropdown({
  label,
  count,
  children,
}: {
  label: string;
  count: number;
  children: React.ReactNode;
}) {
  return (
    <details className="relative">
      <summary className="inline-flex h-8 cursor-pointer list-none items-center gap-1.5 rounded-full border border-[color:var(--border)] bg-white px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)] [&::-webkit-details-marker]:hidden">
        {label}
        {count > 0 && (
          <span className="rounded-full bg-[color:var(--accent-soft)] px-1.5 py-0.5 text-[10px] tabular-nums text-[color:var(--accent)]">
            {count}
          </span>
        )}
        <ChevronDown aria-hidden="true" size={13} />
      </summary>
      <div className="absolute left-0 top-full z-40 mt-2 max-h-[50vh] w-72 overflow-y-auto rounded-2xl border border-[color:var(--border)] bg-white p-2 shadow-lg">
        {children}
      </div>
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
    <label className="flex min-h-9 cursor-pointer items-center gap-3 rounded-lg px-2 py-1.5 hover:bg-[color:var(--muted-soft)]/60">
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

function HearsayBadge({ grade }: { grade: HearsayGrade }) {
  const meta = HEARSAY_META[grade];
  return (
    <span
      title={`Hearsay ${grade}: ${meta.description} Example: ${meta.example}`}
      aria-label={`Hearsay rating ${grade}: ${meta.description}`}
      className={`inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold ring-1 ${meta.badge}`}
    >
      {grade}
    </span>
  );
}

function TimelineEntry({ entry }: { entry: SourceEntry }) {
  const [open, setOpen] = useState(false);
  const status = STATUS_META[entry.correlationStatus];

  return (
    <li className="relative">
      <span
        aria-hidden="true"
        className="absolute -left-[29px] top-7 h-2.5 w-2.5 rounded-full border-2 border-[color:var(--background)] bg-[color:var(--accent)] sm:-left-[37px]"
      />
      <article className="rounded-2xl border border-[color:var(--border)] bg-white p-5 sm:p-6 print:break-inside-avoid">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-[color:var(--muted-soft)] px-2.5 py-1 text-xs tabular-nums">
            {entry.dateDisplay}
          </span>
          <HearsayBadge grade={entry.hearsay} />
          {entry.needsVerification && (
            <span
              title="Citation not yet verified against the original source"
              className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-700 ring-1 ring-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:ring-amber-800/50"
            >
              <TriangleAlert aria-hidden="true" size={11} />
              verify
            </span>
          )}
          <a
            href={entry.url}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`Open source for ${entry.title}`}
            className="ml-auto inline-flex h-8 w-8 items-center justify-center rounded-full text-[color:var(--muted)] hover:bg-[color:var(--muted-soft)] hover:text-[color:var(--accent)] print:hidden"
          >
            <ExternalLink aria-hidden="true" size={15} />
          </a>
        </div>

        <h3 className="serif mt-3 text-lg font-semibold leading-snug tracking-tight">
          {entry.title}
        </h3>
        <p className="mt-1 text-sm text-[color:var(--muted)]">
          {entry.speaker} · {entry.office} · {entry.venue}
        </p>
        <p className="mt-2 flex items-center gap-1.5 text-[10px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
          <span
            aria-hidden="true"
            className={`inline-block h-1.5 w-1.5 rounded-full ${status.dot}`}
          />
          {status.label}
        </p>

        <div className="mt-3 flex flex-wrap gap-1.5">
          {entry.categories.map((c) => (
            <span
              key={c}
              title={CATEGORY_META[c].definition}
              className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-medium ring-1 ${CATEGORY_META[c].pill}`}
            >
              {CATEGORY_META[c].label}
            </span>
          ))}
        </div>

        <p className="mt-4 text-sm leading-relaxed">{entry.summary}</p>

        <button
          type="button"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline print:hidden"
        >
          Transcription
          <ChevronDown
            aria-hidden="true"
            size={13}
            className={open ? "rotate-180 transition-transform" : "transition-transform"}
          />
        </button>
        {/* Always in the DOM so `print:block` can force it open in printouts. */}
        <blockquote
          className={`serif mt-3 whitespace-pre-line border-l-2 border-[color:var(--border)] pl-4 text-[15px] leading-relaxed ${open ? "block" : "hidden print:block"}`}
        >
          {entry.transcription}
        </blockquote>

        <div className="mt-4 rounded-xl bg-[color:var(--muted-soft)]/60 p-3 text-xs leading-relaxed text-[color:var(--muted)]">
          <span className="font-medium uppercase tracking-wider">Notes · </span>
          {entry.notes}
        </div>
      </article>
    </li>
  );
}
