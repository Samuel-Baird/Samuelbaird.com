"use client";

import { ChevronDown, ExternalLink } from "lucide-react";
import { useRef, useState } from "react";
import { Tag } from "@/components/tag";
import { Cameo, FramedPortrait } from "./cameo";
import { SPEAKERS, STANCE_QUESTIONS, type Speaker } from "./data";

/**
 * The portrait hall: the ten speakers most often cited in this timeline's
 * sources (plus Joseph Smith), hung as framed cameos. Selecting a portrait
 * opens that speaker's catalogue card — a summary of beliefs first, then the
 * detailed profile — in a panel directly below the gallery.
 */
export function PortraitHall({ citedCounts }: { citedCounts: Record<string, number> }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const selected = SPEAKERS.find((s) => s.id === selectedId) ?? null;

  function select(id: string) {
    const next = selectedId === id ? null : id;
    setSelectedId(next);
    if (next) {
      // After the panel mounts, bring it into view without yanking the page.
      requestAnimationFrame(() => {
        panelRef.current?.scrollIntoView({
          behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
            ? "auto"
            : "smooth",
          block: "nearest",
        });
      });
    }
  }

  return (
    <section className="mt-12" aria-label="Portrait hall of most-cited speakers">
      <h2 className="serif text-2xl font-semibold tracking-tight">The portrait hall</h2>
      <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
        The ten voices heard most often in this timeline&rsquo;s sources — ranked by citation
        count, with Joseph Smith seated by commission. Portraits are cartoons, not likenesses;
        the nameplates are set in the Deseret Alphabet, the phonetic script the territory once
        printed its schoolbooks in. Select a portrait for a summary of what its sitter believed,
        followed by the detailed profile.
      </p>

      <ul className="mt-6 grid grid-cols-2 gap-x-4 gap-y-6 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {SPEAKERS.map((speaker) => {
          const isSelected = speaker.id === selectedId;
          return (
            <li key={speaker.id} className="flex">
              <button
                type="button"
                onClick={() => select(speaker.id)}
                aria-expanded={isSelected}
                aria-label={`${isSelected ? "Close" : "Open"} the catalogue card for ${speaker.name}`}
                className={`group w-full rounded-[var(--radius)] border p-2 text-left motion-safe:transition-colors ${
                  isSelected
                    ? "border-[color:var(--honey)] bg-[color:var(--honey-soft)]/50"
                    : "border-transparent hover:border-[color:var(--border)] hover:bg-[color:var(--muted-soft)]/50"
                }`}
              >
                <FramedPortrait
                  face={speaker.face}
                  frame={speaker.frame}
                  deseret={speaker.deseret}
                  name={speaker.name}
                  id={speaker.id}
                />
                <p className="small-caps mt-2 flex items-center justify-between gap-2 text-[11px] font-medium text-[color:var(--muted)]">
                  <span>{speaker.dates}</span>
                  <span className="tabular-nums">
                    cited {citedCounts[speaker.name] ?? 0}×
                  </span>
                </p>
              </button>
            </li>
          );
        })}
      </ul>

      {selected && (
        <div ref={panelRef} className="mt-6 scroll-mt-28">
          <CatalogueCard
            speaker={selected}
            cited={citedCounts[selected.name] ?? 0}
            rank={SPEAKERS.indexOf(selected) + 1}
            onClose={() => setSelectedId(null)}
          />
        </div>
      )}
    </section>
  );
}

function CatalogueCard({
  speaker,
  cited,
  rank,
  onClose,
}: {
  speaker: Speaker;
  cited: number;
  rank: number;
  onClose: () => void;
}) {
  const [showDetail, setShowDetail] = useState(false);

  return (
    <article className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 sm:p-7">
      <div className="flex flex-wrap items-start gap-4 border-b border-[color:var(--border)] pb-5">
        <div className="h-20 w-20 shrink-0 overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]">
          <Cameo face={speaker.face} id={`card-${speaker.id}`} />
        </div>
        <div className="min-w-0 flex-1">
          <p className="small-caps text-[11px] font-medium text-[color:var(--muted)]">
            Catalogue no. {String(rank).padStart(2, "0")} · {speaker.era} · cited {cited}{" "}
            {cited === 1 ? "time" : "times"} in this timeline
          </p>
          <h3 className="serif mt-1 text-2xl font-semibold tracking-tight">{speaker.name}</h3>
          <p
            className="mt-0.5 text-sm text-[color:var(--honey)]"
            style={{ fontFamily: "var(--font-deseret), sans-serif" }}
            aria-hidden="true"
          >
            {speaker.deseret}
          </p>
          <p className="serif-onum mt-1 text-sm text-[color:var(--muted)]">
            {speaker.dates} — {speaker.role}
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="small-caps inline-flex min-h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
        >
          Close
        </button>
      </div>

      <dl className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {STANCE_QUESTIONS.map(({ key, label }) => {
          const stance = speaker.stances[key];
          return (
            <div
              key={key}
              className="rounded-[var(--radius)] border border-[color:var(--border)] p-3"
            >
              <dt className="small-caps text-[10px] font-medium text-[color:var(--muted)]">
                {label}
              </dt>
              <dd className="mt-1.5">
                <Tag ink={stance.ink}>{stance.answer}</Tag>
              </dd>
            </div>
          );
        })}
      </dl>

      <p className="mt-3 text-xs leading-relaxed text-[color:var(--muted)]">
        <span className="small-caps font-medium">Evidence · </span>
        {speaker.evidence}
      </p>

      <SectionLabel>Summary of beliefs</SectionLabel>
      <p className="serif mt-2 max-w-2xl border-l-2 border-[color:var(--honey)] pl-4 text-[15px] italic leading-relaxed">
        {speaker.summary}
      </p>

      <button
        type="button"
        onClick={() => setShowDetail(!showDetail)}
        aria-expanded={showDetail}
        className="mt-5 inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline"
      >
        {showDetail ? "Hide the detailed profile" : "Read the detailed profile"}
        <ChevronDown
          aria-hidden="true"
          size={13}
          className={showDetail ? "rotate-180 transition-transform" : "transition-transform"}
        />
      </button>

      {showDetail && (
        <div className="mt-2">
          <SectionLabel>The detailed profile</SectionLabel>
          <div className="mt-2 max-w-2xl space-y-3 text-sm leading-relaxed">
            {speaker.beliefs.map((paragraph, i) => (
              <p key={i}>{paragraph}</p>
            ))}
          </div>

          <SectionLabel>In their own words</SectionLabel>
          <div className="mt-2 max-w-2xl space-y-4">
            {speaker.quotes.map((quote) => (
              <blockquote
                key={quote.url + quote.text.slice(0, 24)}
                className="serif border-l-2 border-[color:var(--border)] pl-4 text-[15px] leading-relaxed"
              >
                “{quote.text}”
                <footer className="mt-1 text-xs not-italic text-[color:var(--muted)]">
                  — {quote.source} ·{" "}
                  <a
                    href={quote.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                  >
                    view source
                    <ExternalLink aria-hidden="true" size={11} />
                  </a>
                </footer>
              </blockquote>
            ))}
          </div>

          <SectionLabel>From the bookshelf</SectionLabel>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed">{speaker.books}</p>

          <SectionLabel>Museum gossip</SectionLabel>
          <p className="mt-2 max-w-2xl rounded-[var(--radius)] border border-dashed border-[color:var(--honey)]/50 bg-[color:var(--honey-soft)]/40 p-3 text-sm leading-relaxed">
            {speaker.fun}
          </p>
        </div>
      )}
    </article>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="small-caps mt-6 border-b border-[color:var(--border)] pb-1 text-[11px] font-medium text-[color:var(--honey)]">
      {children}
    </p>
  );
}
