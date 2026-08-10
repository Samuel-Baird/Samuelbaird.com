"use client";

import {
  ChevronDown,
  Copy,
  Download,
  ExternalLink,
  Quote as QuoteIcon,
  Search,
  TriangleAlert,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { BeehiveMark } from "@/components/beehive-mark";
import { Tag } from "@/components/tag";
import {
  CATEGORY_META,
  ERAS,
  HEARSAY_META,
  INK_VARS,
  REFERENT_META,
  SOURCE_TYPE_META,
  STATUS_META,
  categoriesOf,
  eraFor,
  hearsayForQuote,
} from "./constants";
import {
  buildMarkdown,
  downloadMarkdown,
  type FilterState,
} from "./export-markdown";
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
  type Quote,
  type Referent,
  type SourceEntry,
  type SourceType,
} from "./schema";
import { TimelineGraph } from "./timeline-graph";

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
  const [referents, setReferents] = useState<Set<Referent>>(new Set());
  const [sourceTypes, setSourceTypes] = useState<Set<SourceType>>(new Set());
  const [query, setQuery] = useState("");
  const [collapseCitations, setCollapseCitations] = useState(false);
  const [copied, setCopied] = useState(false);
  const catsPanelRef = useRef<HTMLDetailsElement>(null);

  // Server-renders closed (compact on phones); pops open after mount where
  // the sidebar layout has room. `open` is uncontrolled, so no hydration
  // mismatch.
  useEffect(() => {
    if (window.matchMedia("(min-width: 1024px)").matches && catsPanelRef.current) {
      catsPanelRef.current.open = true;
    }
  }, []);

  const byId = useMemo(
    () => new Map(entries.map((e) => [e.id, e])),
    [entries],
  );

  /** Citations that survived filtering, grouped under the original they cite. */
  const filtered = useMemo(() => {
    const tokens = norm(query).split(/\s+/).filter(Boolean);
    return entries.filter((entry) => {
      const entryCats = categoriesOf(entry);
      if (cats.size > 0 && !entryCats.some((c) => cats.has(c))) return false;
      if (grades.size > 0) {
        const allGrades = [
          entry.hearsay,
          ...entry.quotes.map((q) => hearsayForQuote(entry, q.quoteId)),
        ];
        if (!allGrades.some((g) => grades.has(g))) return false;
      }
      if (statuses.size > 0 && !statuses.has(entry.correlationStatus)) return false;
      if (referents.size > 0) {
        const allReferents = [
          entry.referent,
          ...entry.quotes.flatMap((q) => (q.referent ? [q.referent] : [])),
        ];
        if (!allReferents.some((r) => referents.has(r))) return false;
      }
      if (sourceTypes.size > 0 && !sourceTypes.has(entry.sourceType)) return false;
      if (tokens.length > 0) {
        const haystack = norm(
          [
            entry.title,
            entry.speaker,
            entry.notes,
            ...entry.quotes.map((q) => `${q.excerpt} ${q.note ?? ""}`),
          ].join(" "),
        );
        if (!tokens.every((t) => haystack.includes(t))) return false;
      }
      return true;
    });
  }, [entries, cats, grades, statuses, referents, sourceTypes, query]);

  // Collapse mode hides citations from the timeline and lists them under the
  // original each one cites, so "what is actually attested" reads directly.
  const visible = useMemo(
    () => (collapseCitations ? filtered.filter((e) => e.sourceType === "original") : filtered),
    [filtered, collapseCitations],
  );

  const citationsByOriginal = useMemo(() => {
    const map = new Map<string, SourceEntry[]>();
    if (!collapseCitations) return map;
    for (const entry of filtered) {
      if (entry.sourceType !== "citation") continue;
      for (const target of entry.citesId ?? []) {
        map.set(target, [...(map.get(target) ?? []), entry]);
      }
    }
    return map;
  }, [filtered, collapseCitations]);

  const anyFilterActive =
    cats.size > 0 ||
    grades.size > 0 ||
    statuses.size > 0 ||
    referents.size > 0 ||
    sourceTypes.size > 0 ||
    query.trim() !== "";

  const filters: FilterState = {
    categories: cats,
    grades,
    statuses,
    referents,
    sourceTypes,
    query,
    collapseCitations,
  };

  function handleExport() {
    downloadMarkdown(buildMarkdown(visible, entries.length, filters, byId));
  }

  function handleCopy() {
    navigator.clipboard
      .writeText(buildMarkdown(visible, entries.length, filters, byId))
      .then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
  }

  function clearAll() {
    setCats(new Set());
    setGrades(new Set());
    setStatuses(new Set());
    setReferents(new Set());
    setSourceTypes(new Set());
    setQuery("");
  }

  return (
    <div className="mt-10 lg:grid lg:grid-cols-[17rem_minmax(0,1fr)] lg:items-start lg:gap-10">
      {/* top-24 clears the single-line site header at lg widths; below lg the
          panel sits in normal flow so no header-height sync is needed. */}
      <aside className="print:hidden lg:sticky lg:top-24 lg:max-h-[calc(100vh-7rem)] lg:overflow-y-auto lg:pb-4">
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
            onChange={(e) => setQuery(e.target.value)}
            className="h-10 w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white pl-11 pr-5 text-sm placeholder:text-[color:var(--muted)] focus:border-[color:var(--accent)] focus:outline-none"
          />
        </div>

        <div className="mt-2 flex items-center gap-2 py-1">
          <span className="text-xs tabular-nums text-[color:var(--muted)]">
            {visible.length} of {entries.length} sources
          </span>
          {anyFilterActive && (
            <button
              type="button"
              onClick={clearAll}
              className="text-xs font-medium text-[color:var(--accent)] hover:underline"
            >
              Clear
            </button>
          )}
          <span className="ml-auto flex gap-1.5">
            <button
              type="button"
              onClick={handleExport}
              title="Export filtered sources as Markdown"
              className="small-caps inline-flex h-8 items-center gap-1.5 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
            >
              <Download aria-hidden="true" size={13} />
              .md
            </button>
            <button
              type="button"
              onClick={handleCopy}
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
            onChange={() => setCollapseCitations(!collapseCitations)}
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
                onChange={() => setCats(toggleIn(cats, id))}
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
                onChange={() => setReferents(toggleIn(referents, r))}
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
                onChange={() => setSourceTypes(toggleIn(sourceTypes, t))}
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
          </PanelSection>
          <PanelSection label="Status" count={statuses.size}>
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
                  <span className="small-caps">{STATUS_META[s].label}</span>
                </span>
              </FilterOption>
            ))}
          </PanelSection>

        <PanelSection label="About the scales">
          <ScalesLegend />
        </PanelSection>
      </aside>

      <div className="min-w-0">
        <div className="mb-8 print:hidden">
          <TimelineGraph
            entries={visible}
            onSelect={(id) => {
              const el = document.getElementById(id);
              el?.scrollIntoView({ behavior: "smooth", block: "start" });
            }}
          />
        </div>
      {visible.length === 0 ? (
        <div className="mt-8 rounded-[var(--radius)] border border-dashed border-[color:var(--border)] bg-white p-8 text-center text-sm text-[color:var(--muted)] lg:mt-0">
          No sources match your filters.
        </div>
      ) : (
        <div className="mt-8 lg:mt-0">
          {(() => {
            let rendered = 0;
            return ERAS.map((era) => {
              const inEra = visible.filter((e) => eraFor(e).id === era.id);
              if (inEra.length === 0) return null;
              const isFirst = rendered === 0;
              rendered += 1;
              return (
                <section key={era.id} className={isFirst ? "" : "mt-14"}>
                  {!isFirst && (
                    <div className="dinkus" aria-hidden="true">
                      <BeehiveMark className="h-4 w-4" />
                    </div>
                  )}
                  <p className="serif-onum text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--muted)]">
                    {era.range}
                  </p>
                  <h2 className="serif mt-1 text-2xl font-semibold tracking-tight">
                    {era.label}
                  </h2>
                  <ol className="relative mt-6 space-y-6 border-l border-[color:var(--border)] pl-6 sm:pl-8">
                    {inEra.map((entry) => (
                      <TimelineEntry
                        key={entry.id}
                        entry={entry}
                        byId={byId}
                        citations={citationsByOriginal.get(entry.id) ?? []}
                      />
                    ))}
                  </ol>
                </section>
              );
            });
          })()}
        </div>
      )}
      </div>
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

function HearsayBadge({ grade }: { grade: HearsayGrade }) {
  const meta = HEARSAY_META[grade];
  const c = INK_VARS[meta.ink];
  return (
    <span
      title={`Hearsay ${grade}: ${meta.description} Example: ${meta.example}`}
      aria-label={`Hearsay rating ${grade}: ${meta.description}`}
      className={`inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-[var(--radius)] text-xs font-semibold ring-1 ${c.bg} ${c.text} ${c.ring}`}
    >
      {grade}
    </span>
  );
}

function ReferentChip({ referent }: { referent: Referent }) {
  const meta = REFERENT_META[referent];
  return (
    <Tag ink={meta.ink} title={`${meta.label} — ${meta.definition}`}>
      {meta.short}
    </Tag>
  );
}

function TimelineEntry({
  entry,
  byId,
  citations,
}: {
  entry: SourceEntry;
  byId: Map<string, SourceEntry>;
  citations: SourceEntry[];
}) {
  const [open, setOpen] = useState(false);
  const status = STATUS_META[entry.correlationStatus];
  const typeMeta = SOURCE_TYPE_META[entry.sourceType];

  return (
    <li id={entry.id} className="relative scroll-mt-40">
      <span
        aria-hidden="true"
        className={`absolute -left-[29px] top-7 h-2.5 w-2.5 rounded-full border-2 border-[color:var(--background)] sm:-left-[37px] ${
          entry.sourceType === "original"
            ? "bg-[color:var(--accent)]"
            : "bg-[color:var(--muted)]"
        }`}
      />
      <article className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 sm:p-6 print:break-inside-avoid">
        <div className="flex flex-wrap items-center gap-2">
          <span className="serif-onum rounded-[var(--radius)] bg-[color:var(--muted-soft)] px-2.5 py-1 text-xs tabular-nums">
            {entry.dateDisplay}
          </span>
          <HearsayBadge grade={entry.hearsay} />
          <Tag ink={typeMeta.ink} title={typeMeta.definition}>
            {typeMeta.label}
          </Tag>
          {entry.referent !== "n/a" && <ReferentChip referent={entry.referent} />}
          {entry.needsVerification && (
            <Tag
              ink="oxblood"
              title="Citation not yet verified against the original source"
              className="inline-flex items-center gap-1"
            >
              <TriangleAlert aria-hidden="true" size={11} />
              verify
            </Tag>
          )}
          <a
            href={entry.url}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`Open source for ${entry.title}`}
            className="ml-auto inline-flex h-8 w-8 items-center justify-center rounded-[var(--radius)] text-[color:var(--muted)] hover:bg-[color:var(--muted-soft)] hover:text-[color:var(--accent)] print:hidden"
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
        <p className="small-caps mt-2 flex items-center gap-1.5 text-[10px] font-medium text-[color:var(--muted)]">
          <span
            aria-hidden="true"
            className={`inline-block h-1.5 w-1.5 rounded-full ${status.dot}`}
          />
          {status.label}
        </p>

        {entry.citesId && entry.citesId.length > 0 && (
          <p className="mt-3 text-xs leading-relaxed text-[color:var(--muted)]">
            <span className="small-caps font-medium">Cites · </span>
            {entry.citesId.map((id, i) => (
              <span key={id}>
                {i > 0 && "; "}
                <a
                  href={`#${id}`}
                  className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                >
                  {byId.get(id)?.title ?? id}
                </a>
              </span>
            ))}
          </p>
        )}

        {entry.witnesses && entry.witnesses.length > 0 && (
          <div className="mt-3 rounded-[var(--radius)] border border-[color:var(--border)] p-3">
            <p className="small-caps text-[10px] font-medium text-[color:var(--muted)]">
              Witnesses
            </p>
            <ul className="mt-2 space-y-1.5">
              {entry.witnesses.map((w) => (
                <li key={w.scribe} className="text-xs leading-relaxed">
                  {w.url ? (
                    <a
                      href={w.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                    >
                      {w.scribe}
                    </a>
                  ) : (
                    <span className="font-medium">{w.scribe}</span>
                  )}
                  {w.note && (
                    <span className="text-[color:var(--muted)]"> — {w.note}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-4 space-y-4">
          {entry.quotes.map((quote) => (
            <QuoteBlock
              key={quote.quoteId}
              entry={entry}
              quote={quote}
              open={open}
            />
          ))}
        </div>

        <button
          type="button"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline print:hidden"
        >
          {open ? "Hide excerpts" : `Show excerpts (${entry.quotes.length})`}
          <ChevronDown
            aria-hidden="true"
            size={13}
            className={open ? "rotate-180 transition-transform" : "transition-transform"}
          />
        </button>

        <div className="mt-4 rounded-[var(--radius)] bg-[color:var(--muted-soft)]/60 p-3 text-xs leading-relaxed text-[color:var(--muted)]">
          <span className="small-caps font-medium">Notes · </span>
          {entry.notes}
        </div>

        {citations.length > 0 && (
          <div className="mt-4 rounded-[var(--radius)] border border-dashed border-[color:var(--border)] p-3">
            <p className="small-caps text-[10px] font-medium text-[color:var(--muted)]">
              Cited by {citations.length}{" "}
              {citations.length === 1 ? "later source" : "later sources"}
            </p>
            <ul className="mt-2 space-y-1">
              {citations.map((c) => (
                <li key={c.id} className="text-xs leading-relaxed">
                  <span className="tabular-nums text-[color:var(--muted)]">
                    {c.dateDisplay}
                  </span>{" "}
                  —{" "}
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                  >
                    {c.title}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
      </article>
    </li>
  );
}

function QuoteBlock({
  entry,
  quote,
  open,
}: {
  entry: SourceEntry;
  quote: Quote;
  open: boolean;
}) {
  const grade = hearsayForQuote(entry, quote.quoteId);
  const overridden = grade !== entry.hearsay;

  return (
    <div id={quote.quoteId}>
      <div className="flex flex-wrap items-center gap-1.5">
        {quote.categories.length === 0 ? (
          <Tag ink="muted">context</Tag>
        ) : (
          quote.categories.map((c) => (
            <Tag key={c} ink={CATEGORY_META[c].ink} title={CATEGORY_META[c].definition}>
              {CATEGORY_META[c].label}
              {quote.implied && (
                <span className="opacity-70" title="Read into the quote rather than stated by it">
                  {" "}· implied
                </span>
              )}
            </Tag>
          ))
        )}
        {quote.referent && <ReferentChip referent={quote.referent} />}
        {overridden && (
          <span
            title={`Hearsay for this quote differs from the source: ${HEARSAY_META[grade].description}`}
            className={`inline-flex h-5 w-5 items-center justify-center rounded-[var(--radius)] text-[10px] font-semibold ring-1 ${INK_VARS[HEARSAY_META[grade].ink].bg} ${INK_VARS[HEARSAY_META[grade].ink].text} ${INK_VARS[HEARSAY_META[grade].ink].ring}`}
          >
            {grade}
          </span>
        )}
      </div>

      {/* Always in the DOM so `print:block` can force it open in printouts. */}
      <blockquote
        className={`serif mt-2 whitespace-pre-line border-l-2 border-[color:var(--border)] pl-4 text-[15px] leading-relaxed ${
          open ? "block" : "hidden print:block"
        }`}
      >
        {quote.excerpt}
      </blockquote>

      {quote.note && (
        <p
          className={`mt-2 flex gap-2 text-xs leading-relaxed text-[color:var(--muted)] ${
            open ? "flex" : "hidden print:flex"
          }`}
        >
          <QuoteIcon
            aria-hidden="true"
            size={12}
            className="mt-0.5 shrink-0 opacity-50"
          />
          {quote.note}
        </p>
      )}
    </div>
  );
}
