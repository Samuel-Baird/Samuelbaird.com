"use client";

import {
  ChevronDown,
  ExternalLink,
  Quote as QuoteIcon,
  SlidersHorizontal,
  TriangleAlert,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { BeehiveMark } from "@/components/beehive-mark";
import { Tag } from "@/components/tag";
import { HearsayBadge, ReferentChip } from "./badges";
import {
  CATEGORY_META,
  ERAS,
  HEARSAY_META,
  INK_VARS,
  SOURCE_TYPE_META,
  STATUS_META,
  QUESTIONS,
  categoriesOf,
  eraFor,
  hearsayForQuote,
} from "./constants";
import { BackToTop, EraNav } from "./era-nav";
import {
  buildMarkdown,
  downloadMarkdown,
  type FilterState,
} from "./export-markdown";
import { FilterPanel } from "./filter-panel";
import { scrollToId } from "./scroll";
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
  type QuestionId,
} from "./schema";
import { StanceGraph } from "./stance-graph";
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
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [expandAll, setExpandAll] = useState(false);
  // Fixed default rather than "whichever subject has most in view": the server
  // render and the first client render have to agree, and a data-dependent
  // default would differ the moment a filter arrived from the URL.
  const [subject, setSubject] = useState<QuestionId>("divinity");
  // Shared between the graph and the cards so hovering either one marks the
  // other; the plot is otherwise hard to tie back to a specific entry.
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const drawerRef = useRef<HTMLDivElement>(null);

  // Filters live in the query string so a filtered reading is a shareable
  // link and survives a reload. Deliberately not useSearchParams: nothing on
  // the server reads these, and subscribing to them would put every keystroke
  // through the router and force a Suspense boundary around the explorer for
  // nothing. Next routes native history calls through its router anyway — see
  // node_modules/next/dist/docs/01-app/01-getting-started/04-linking-and-navigating.md.
  //
  // This has to be an effect that writes state: the server renders with the
  // filters empty, so reading the URL during render instead would make the
  // client's first paint disagree with the server's HTML. One pass on mount,
  // never again — the eslint rule flags the shape, not a real cascade.
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    const pick = <T extends string>(key: string, allowed: readonly T[]) => {
      const found = p.getAll(key).filter((v): v is T => allowed.includes(v as T));
      return found.length > 0 ? new Set(found) : null;
    };
    const c = pick("c", CATEGORY_IDS);
    if (c) setCats(c);
    const g = pick("g", HEARSAY_GRADES);
    if (g) setGrades(g);
    const s = pick("s", CORRELATION_STATUSES);
    if (s) setStatuses(s);
    const r = pick("r", REFERENTS);
    if (r) setReferents(r);
    const t = pick("t", SOURCE_TYPES);
    if (t) setSourceTypes(t);
    const q = p.get("q");
    if (q) setQuery(q);
    if (p.get("cc") === "1") setCollapseCitations(true);
    const subj = p.get("subj");
    if (subj && QUESTIONS.some((s) => s.id === subj)) setSubject(subj as QuestionId);
  }, []);
  /* eslint-enable react-hooks/set-state-in-effect */

  // Skips the mount pass so reading the URL above cannot be undone by an
  // immediate write of the still-empty initial state.
  const urlWriteReady = useRef(false);
  useEffect(() => {
    if (!urlWriteReady.current) {
      urlWriteReady.current = true;
      return;
    }
    const timer = window.setTimeout(() => {
      const p = new URLSearchParams();
      for (const c of cats) p.append("c", c);
      for (const g of grades) p.append("g", g);
      for (const s of statuses) p.append("s", s);
      for (const r of referents) p.append("r", r);
      for (const t of sourceTypes) p.append("t", t);
      if (query.trim()) p.set("q", query.trim());
      if (collapseCitations) p.set("cc", "1");
      if (subject !== "divinity") p.set("subj", subject);
      const qs = p.toString();
      window.history.replaceState(
        null,
        "",
        qs ? `?${qs}` : window.location.pathname,
      );
    }, 300);
    return () => window.clearTimeout(timer);
  }, [cats, grades, statuses, referents, sourceTypes, query, collapseCitations, subject]);

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

  // One grouping, read by both the jump bar's counts and the card sections,
  // so a disabled jump button always means an absent section.
  const byEra = useMemo(
    () =>
      ERAS.map((era) => ({
        era,
        inEra: visible.filter((e) => eraFor(e).id === era.id),
      })),
    [visible],
  );

  const facetCount =
    cats.size + grades.size + statuses.size + referents.size + sourceTypes.size;
  const anyFilterActive = facetCount > 0 || query.trim() !== "";

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

  // Drawer plumbing mirrors the channels explorer (src/components/
  // channels-explorer.tsx): lock the page behind it, close on Escape, and
  // keep Tab inside it while it is open.
  useEffect(() => {
    if (!drawerOpen) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const focusableSelector =
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), details, [tabindex]:not([tabindex="-1"])';

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setDrawerOpen(false);
        return;
      }
      if (event.key !== "Tab" || !drawerRef.current) return;

      const focusable = Array.from(
        drawerRef.current.querySelectorAll<HTMLElement>(focusableSelector),
      ).filter((element) => element.offsetParent !== null);
      if (focusable.length === 0) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    window.setTimeout(() => {
      drawerRef.current?.querySelector<HTMLElement>(focusableSelector)?.focus();
    }, 0);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [drawerOpen]);

  const panelProps = {
    query,
    onQueryChange: setQuery,
    cats,
    onToggleCat: (id: CategoryId) => setCats(toggleIn(cats, id)),
    referents,
    onToggleReferent: (r: Referent) => setReferents(toggleIn(referents, r)),
    sourceTypes,
    onToggleSourceType: (t: SourceType) => setSourceTypes(toggleIn(sourceTypes, t)),
    grades,
    onToggleGrade: (g: HearsayGrade) => setGrades(toggleIn(grades, g)),
    statuses,
    onToggleStatus: (s: CorrelationStatus) => setStatuses(toggleIn(statuses, s)),
    collapseCitations,
    onToggleCollapseCitations: () => setCollapseCitations(!collapseCitations),
    visibleCount: visible.length,
    totalCount: entries.length,
    anyFilterActive,
    onClearAll: clearAll,
    onExport: handleExport,
    onCopy: handleCopy,
    copied,
  };

  return (
    <div className="mt-10 lg:grid lg:grid-cols-[17rem_minmax(0,1fr)] lg:items-start lg:gap-10">
      {/* top-24 clears the single-line site header at lg widths. Below lg the
          panel moves into the drawer, so the graph is the first thing under
          the heading instead of thirty checkboxes. */}
      <aside className="hidden print:hidden lg:sticky lg:top-24 lg:block lg:max-h-[calc(100vh-7rem)] lg:overflow-y-auto lg:pb-4">
        <FilterPanel variant="desktop" {...panelProps} />
      </aside>

      <div className="min-w-0">
        <div className="mb-5 flex items-center justify-between gap-3 lg:hidden print:hidden">
          <button
            type="button"
            aria-label="Open filters"
            onClick={() => setDrawerOpen(true)}
            className="inline-flex min-h-10 items-center gap-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm font-medium"
          >
            <SlidersHorizontal aria-hidden="true" size={16} />
            Filters
            {facetCount > 0 && (
              <span className="rounded-[var(--radius)] bg-[color:var(--accent-soft)] px-2 py-0.5 text-xs tabular-nums text-[color:var(--accent)]">
                {facetCount}
              </span>
            )}
          </button>
          <span className="text-xs tabular-nums text-[color:var(--muted)]">
            {visible.length} of {entries.length}
          </span>
        </div>

        <div className="mb-4 print:hidden">
          <TimelineGraph
            entries={visible}
            hoveredId={hoveredId}
            onHover={setHoveredId}
            onSelect={scrollToId}
          />
        </div>

        <div className="mb-8 print:hidden">
          <StanceGraph
            entries={visible}
            corpus={entries}
            subject={subject}
            onSubjectChange={setSubject}
            hoveredId={hoveredId}
            onHover={setHoveredId}
            onSelect={scrollToId}
          />
        </div>

        {visible.length > 0 && (
          <EraNav
            eras={byEra.map(({ era, inEra }) => ({ era, count: inEra.length }))}
            expandAll={expandAll}
            onToggleExpandAll={() => setExpandAll(!expandAll)}
          />
        )}

        {visible.length === 0 ? (
          <div className="mt-8 rounded-[var(--radius)] border border-dashed border-[color:var(--border)] bg-white p-8 text-center text-sm text-[color:var(--muted)] lg:mt-0">
            No sources match your filters.
          </div>
        ) : (
          <div>
            {(() => {
              let rendered = 0;
              return byEra.map(({ era, inEra }) => {
                if (inEra.length === 0) return null;
                const isFirst = rendered === 0;
                rendered += 1;
                return (
                  <section
                    key={era.id}
                    id={`era-${era.id}`}
                    className={isFirst ? "scroll-mt-32" : "mt-14 scroll-mt-32"}
                  >
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
                          expandAll={expandAll}
                          hovered={hoveredId === entry.id}
                          onHoverChange={setHoveredId}
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

      {drawerOpen && (
        <div className="fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true">
          <button
            type="button"
            aria-label="Close filters"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/35"
          />
          <div
            ref={drawerRef}
            className="absolute right-0 top-0 flex h-full w-[88vw] max-w-sm flex-col border-l border-[color:var(--border)] bg-[color:var(--background)]"
          >
            <div className="flex-1 overflow-y-auto">
              <FilterPanel variant="drawer" {...panelProps} />
            </div>
            <div className="sticky bottom-0 border-t border-[color:var(--border)] bg-[color:var(--background)] p-4">
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                className="min-h-11 w-full rounded-[var(--radius)] bg-[color:var(--accent)] px-5 text-sm font-medium text-white"
              >
                Show {visible.length}{" "}
                {visible.length === 1 ? "source" : "sources"}
              </button>
            </div>
          </div>
        </div>
      )}

      <BackToTop />
    </div>
  );
}

function TimelineEntry({
  entry,
  byId,
  citations,
  expandAll,
  hovered,
  onHoverChange,
}: {
  entry: SourceEntry;
  byId: Map<string, SourceEntry>;
  citations: SourceEntry[];
  expandAll: boolean;
  hovered: boolean;
  onHoverChange: (id: string | null) => void;
}) {
  // null means "follow the page-wide toggle". Flipping that toggle clears any
  // per-card override, so the global control always wins the next time it is
  // used without stranding a card the reader opened by hand.
  const [override, setOverride] = useState<boolean | null>(null);
  const [lastExpandAll, setLastExpandAll] = useState(expandAll);
  if (lastExpandAll !== expandAll) {
    setLastExpandAll(expandAll);
    setOverride(null);
  }
  const open = override ?? expandAll;

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
      <article
        onMouseEnter={() => onHoverChange(entry.id)}
        onMouseLeave={() => onHoverChange(null)}
        className={`rounded-[var(--radius)] border bg-white p-5 sm:p-6 print:break-inside-avoid ${
          hovered
            ? "border-[color:var(--honey)]"
            : "border-[color:var(--border)]"
        }`}
      >
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
          onClick={() => setOverride(!open)}
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
