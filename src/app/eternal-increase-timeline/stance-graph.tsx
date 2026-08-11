"use client";

import { useMemo, useRef, useState } from "react";
import {
  CATEGORY_META,
  QUESTIONS,
  QUESTION_META,
  STATUS_META,
  hearsayForQuote,
} from "./constants";
import {
  ERA_STRIP,
  INK_PAINT,
  buildAxis,
  nearestDot,
  rowHeight,
  stackOffset,
} from "./graph-shared";
import {
  NOT_ADDRESSED,
  questionsFor,
  type CategoryId,
  type QuestionId,
  type SourceEntry,
} from "./schema";

/**
 * How settled one teaching was, decade by decade.
 *
 * The distribution graph above answers "who said something about this, and
 * when". It cannot answer the question underneath it — whether the Church was
 * getting more or less committed to a claim — because a dot there looks the
 * same whether the speaker taught the doctrine or repudiated it. Here the
 * vertical axis is the commitment itself: affirmations on top, denials at the
 * bottom, and hedging in the band between, which is where a teaching tends to
 * go on its way from one to the other.
 *
 * One subject at a time, deliberately. Four propositions share this corpus and
 * they drifted at different rates; overlaying them would produce a smear that
 * says less than any single question does on its own.
 *
 * Placement is editorial. Each dot sits where a reader judged the excerpt to
 * fall against a written-out proposition, recorded per quote in sources.json
 * rather than inferred here, so the chart can be argued with from the data.
 */



type Dot = {
  key: string;
  entry: SourceEntry;
  quoteId: string;
  excerpt: string;
  pct: number;
  cy: number;
  paint: string;
  isCitation: boolean;
  strong: boolean; // first-hand or scribal provenance (hearsay A/B)
  unreviewed: boolean;
  cats: CategoryId[];
  // The question's own name for this band, so the tooltip and the screen-reader
  // label say what the gutter says rather than a bare band id.
  bandLabel: string;
  bandCriteria: string;
};

type Row = {
  id: string;
  label: string;
  offScale: boolean;
  y: number;
  height: number;
  dots: Dot[];
};

export function StanceGraph({
  entries,
  corpus,
  subject,
  onSubjectChange,
  onSelect,
  hoveredId,
  onHover,
}: {
  entries: SourceEntry[];
  /**
   * Every source in the timeline, filtered or not. The axis is pinned to this
   * rather than to what is on screen, so the six questions share one ruler and
   * a long silence stays visibly long.
   */
  corpus: SourceEntry[];
  subject: QuestionId;
  onSubjectChange: (id: QuestionId) => void;
  onSelect?: (id: string) => void;
  hoveredId?: string | null;
  onHover?: (id: string | null) => void;
}) {
  const [tip, setTip] = useState<{
    key: string;
    x: number;
    y: number;
    width: number;
  } | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const figureRef = useRef<HTMLElement>(null);

  // Dot counts for every tab, so the picker can show what each question holds
  // under the current filters and disable the ones the filters emptied.
  const counts = useMemo(() => {
    const out = {} as Record<QuestionId, number>;
    for (const q of QUESTIONS) out[q.id] = 0;
    for (const entry of entries) {
      for (const quote of entry.quotes) {
        for (const q of questionsFor(quote.categories)) {
          const band = quote.bands?.[q];
          // A quote that was asked and answered "does not address it" is not
          // on this chart, and must not be counted as though it were.
          if (band && band !== NOT_ADDRESSED) out[q] += 1;
        }
      }
    }
    return out;
  }, [entries]);

  const model = useMemo(() => {
    const meta = QUESTION_META[subject];

    // One dot per quote per question: a quote gives this question exactly one
    // answer, however many categories raised it.
    const raw: {
      entry: SourceEntry;
      quoteId: string;
      excerpt: string;
      year: number;
      band: string;
      cats: CategoryId[];
    }[] = [];

    const asked = new Set<string>(
      QUESTIONS.find((q) => q.id === subject)?.bands.map((b) => b.id) ?? [],
    );

    for (const entry of entries) {
      for (const quote of entry.quotes) {
        if (!questionsFor(quote.categories).includes(subject)) continue;
        const band = quote.bands?.[subject];
        // Unanswered is blocked by the build; answered "not-addressed" means
        // the passage was read and found not to speak to this question, so it
        // belongs on no band here.
        if (!band || band === NOT_ADDRESSED || !asked.has(band)) continue;
        raw.push({
          entry,
          quoteId: quote.quoteId,
          excerpt: quote.excerpt,
          year: Number(entry.date.slice(0, 4)),
          band,
          cats: quote.categories,
        });
      }
    }

    if (raw.length === 0) return null;

    const years = raw.map((r) => r.year);
    const axis = buildAxis(
      years,
      corpus.map((e) => Number(e.date.slice(0, 4))),
    );

    let y = ERA_STRIP;
    const rows: Row[] = [];
    for (const band of meta.bands) {
      const members = raw.filter((r) => r.band === band.id);

      const columns = new Map<number, typeof members>();
      for (const r of members) {
        const pct = axis.pctFor(r.year);
        columns.set(pct, [...(columns.get(pct) ?? []), r]);
      }
      const maxStack = columns.size
        ? Math.max(...[...columns.values()].map((c) => c.length))
        : 0;
      const height = rowHeight(maxStack);
      const centre = y + height / 2;

      const dots: Dot[] = [];
      for (const [pct, group] of columns) {
        group.forEach((r, i) => {
          const quote = r.entry.quotes.find((q) => q.quoteId === r.quoteId);
          const grade = hearsayForQuote(r.entry, r.quoteId);
          dots.push({
            key: `${r.quoteId}:${r.band}`,
            entry: r.entry,
            quoteId: r.quoteId,
            excerpt: r.excerpt,
            pct,
            cy: centre + stackOffset(i, group.length),
            paint: INK_PAINT[STATUS_META[r.entry.correlationStatus].ink],
            isCitation: r.entry.sourceType === "citation",
            strong: grade === "A" || grade === "B",
            unreviewed: quote?.stanceNeedsReview === true,
            cats: r.cats,
            bandLabel: band.label,
            bandCriteria: band.criteria,
          });
        });
      }
      // Every band is drawn even when empty. A question with nothing in its
      // denial band is making a claim about the record, and collapsing the row
      // would hide it — the reader would see five rows on one tab and three on
      // another without being told why.
      rows.push({
        id: band.id,
        label: band.label,
        offScale: band.offScale === true,
        y,
        height,
        dots,
      });
      y += height;
    }

    return {
      ...axis,
      eraMarks: axis.bands,
      bands: rows,
      height: y,
      quoteCount: new Set(raw.map((r) => r.quoteId)).size,
      dataMin: Math.min(...years),
      dataMax: Math.max(...years),
    };
  }, [entries, corpus, subject]);

  const allDots = model ? model.bands.flatMap((b) => b.dots) : [];
  const tipDot = tip ? allDots.find((d) => d.key === tip.key) : null;
  const meta = QUESTION_META[subject];

  const nearestTo = (event: { clientX: number; clientY: number }): Dot | null => {
    const box = svgRef.current?.getBoundingClientRect();
    return box ? nearestDot(allDots, box, event.clientX, event.clientY) : null;
  };

  /**
   * Anchored to the figure rather than the plot: `overflow-x-auto` makes the
   * plot a scroll container on both axes, so a card taller than the bands
   * would be clipped by it.
   */
  const show = (dot: Dot | null) => {
    onHover?.(dot?.entry.id ?? null);
    const svg = svgRef.current?.getBoundingClientRect();
    const fig = figureRef.current?.getBoundingClientRect();
    if (!dot || !svg || !fig) {
      setTip(null);
      return;
    }
    setTip({
      key: dot.key,
      x: svg.left - fig.left + (dot.pct / 100) * svg.width,
      y: svg.top - fig.top + dot.cy,
      width: fig.width,
    });
  };

  const track = (event: { clientX: number; clientY: number }) =>
    show(nearestTo(event));

  return (
    <figure
      ref={figureRef}
      className="relative rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-4 sm:p-5"
    >
      <figcaption className="flex flex-wrap items-baseline justify-between gap-2">
        <span className="text-[10px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
          Stance over time
        </span>
        {model && (
          <span className="text-[10px] tabular-nums text-[color:var(--muted)]">
            {model.quoteCount} {model.quoteCount === 1 ? "quote" : "quotes"} ·{" "}
            {model.dataMin}
            {model.dataMax !== model.dataMin ? `–${model.dataMax}` : ""}
          </span>
        )}
      </figcaption>

      <SubjectTabs subject={subject} counts={counts} onChange={onSubjectChange} />

      <p className="mt-2 text-[11px] leading-relaxed text-[color:var(--muted)]">
        <span className="text-[color:var(--foreground)]">{meta.question}</span>{" "}
        {meta.blurb}
      </p>

      {!model ? (
        <div className="mt-3 rounded-[var(--radius)] border border-dashed border-[color:var(--border)] p-6 text-center text-xs text-[color:var(--muted)]">
          No quotes answer this question in view.
        </div>
      ) : (
        <>
          <div className="mt-3 overflow-x-auto">
            <div className="flex min-w-[560px]">
              <div
                className="relative w-16 shrink-0"
                style={{ height: model.height }}
                aria-hidden="true"
              >
                {model.bands.map((band) => (
                  <span
                    key={band.id}
                    className="small-caps absolute right-2 text-[9px] leading-none text-[color:var(--muted)]"
                    style={{ top: band.y + band.height / 2 - 4 }}
                  >
                    {band.label}
                  </span>
                ))}
              </div>

              <div className="relative min-w-0 flex-1">
                <svg
                  ref={svgRef}
                  width="100%"
                  height={model.height}
                  role="img"
                  aria-label={`${model.quoteCount} quotes on "${meta.question}" from ${model.dataMin} to ${model.dataMax}, grouped by whether they affirm, hedge on, or deny the claim`}
                  className="block"
                >
                  {/* The backdrop marks eras, not bands. Shading the rows too
                      would cross the two into a plaid, and eras earn the ink:
                      a denial arriving in the correlated era means something a
                      bare year does not. The rows are already told apart by
                      their gutter labels and separators — and this way the two
                      figures on the page share one backdrop and read as a
                      pair. */}
                  {model.bands.map((band, i) =>
                    i % 2 === 1 ? (
                      <rect
                        key={band.id}
                        x={0}
                        y={band.y}
                        width="100%"
                        height={band.height}
                        fill="var(--muted-soft)"
                        opacity={0.4}
                      />
                    ) : null,
                  )}

                  {/* Era labels only, no era fill: the rows already carry the
                      one wash this plot can afford, and a second one crossing
                      it would read as a plaid. The labels are what matter —
                      a denial arriving in the correlated era means something
                      that a bare year does not. */}
                  {model.eraMarks
                    .filter((band) => band.left > 2)
                    .map((band) => (
                      <line
                        key={`era-${band.id}`}
                        x1={`${band.left}%`}
                        x2={`${band.left}%`}
                        y1={0}
                        y2={model.height}
                        stroke="var(--border)"
                        strokeDasharray="2 3"
                      />
                    ))}

                  {model.eraMarks.map((band) =>
                    band.width >= 12 ? (
                      <text
                        key={`eralabel-${band.id}`}
                        x={`${band.left + band.width / 2}%`}
                        y={10}
                        textAnchor="middle"
                        fontSize={9}
                        fill="var(--muted)"
                        className="small-caps"
                      >
                        {band.label}
                      </text>
                    ) : null,
                  )}

                  {model.ticks.grid.map((year) => (
                    <line
                      key={year}
                      x1={`${model.pctFor(year)}%`}
                      x2={`${model.pctFor(year)}%`}
                      y1={ERA_STRIP}
                      y2={model.height}
                      stroke="var(--border)"
                    />
                  ))}

                  {/* A plain rule between rungs of the scale; a dashed one
                      where the scale stops. Below that line the rows are not
                      further steps in the same direction — declining to say is
                      not a weaker version of denying — and drawing the two
                      boundaries alike would imply an order that is not there. */}
                  {model.bands.map((band, i) =>
                    i === 0 ? null : (
                      <line
                        key={band.id}
                        x1="0"
                        x2="100%"
                        y1={band.y}
                        y2={band.y}
                        stroke="var(--border)"
                        strokeDasharray={
                          band.offScale && !model.bands[i - 1].offScale
                            ? "3 3"
                            : undefined
                        }
                        opacity={
                          band.offScale && !model.bands[i - 1].offScale ? 1 : 0.7
                        }
                      />
                    ),
                  )}

                  {model.bands.map((band) =>
                    band.dots.length === 0 ? (
                      <text
                        key={`empty-${band.id}`}
                        x="50%"
                        y={band.y + band.height / 2 + 3}
                        textAnchor="middle"
                        fontSize={9}
                        fill="var(--muted)"
                        opacity={0.7}
                      >
                        nothing in view
                      </text>
                    ) : null,
                  )}

                  {model.bands.map((band) =>
                    band.dots.map((d) => (
                      <circle
                        key={d.key}
                        cx={`${d.pct}%`}
                        cy={d.cy}
                        r={6}
                        fill="var(--surface)"
                      />
                    )),
                  )}

                  {allDots
                    .filter((d) => d.entry.id === hoveredId)
                    .map((d) => (
                      <circle
                        key={`ring-${d.key}`}
                        cx={`${d.pct}%`}
                        cy={d.cy}
                        r={8.5}
                        fill="var(--surface)"
                        stroke="var(--honey)"
                        strokeWidth={1.5}
                      />
                    ))}

                  {allDots.map((d) => {
                    const active = hoveredId === d.entry.id;
                    const r = (d.strong ? 4.5 : 3.2) + (active ? 1 : 0);
                    return (
                      <g
                        key={d.key}
                        role="button"
                        tabIndex={0}
                        aria-label={`${d.entry.dateDisplay}, ${d.entry.title} — ${d.bandLabel.toLowerCase()}`}
                        style={{ pointerEvents: "none" }}
                        className="focus:outline-none"
                        onFocus={() => show(d)}
                        onBlur={() => show(null)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            onSelect?.(d.entry.id);
                          }
                        }}
                      >
                        {d.isCitation ? (
                          <circle
                            cx={`${d.pct}%`}
                            cy={d.cy}
                            r={r}
                            fill="var(--surface)"
                            stroke={d.paint}
                            strokeWidth={1.6}
                          />
                        ) : (
                          <circle cx={`${d.pct}%`} cy={d.cy} r={r} fill={d.paint} />
                        )}
                        {/* A reading the backfill was unsure of. Shown rather
                            than withheld: dropping it would quietly thin
                            whichever band it belongs to. */}
                        {d.unreviewed && (
                          <circle
                            cx={`${d.pct}%`}
                            cy={d.cy}
                            r={r + 2.5}
                            fill="none"
                            stroke={d.paint}
                            strokeWidth={1}
                            strokeDasharray="2 2"
                            // Muted on purpose. A third of the placements carry
                            // this ring, and at that density a bold marker
                            // stops reading as a caveat and starts competing
                            // with the status colour. The proportion is stated
                            // as a number in the key instead, which is the
                            // honest way to carry a fact that large.
                            opacity={0.5}
                          />
                        )}
                      </g>
                    );
                  })}

                  <rect
                    x={0}
                    y={0}
                    width="100%"
                    height={model.height}
                    fill="transparent"
                    style={{ cursor: tip ? "pointer" : "default" }}
                    onPointerMove={track}
                    onPointerLeave={() => show(null)}
                    onClick={(e) => {
                      const dot = nearestTo(e);
                      track(e);
                      if (dot) onSelect?.(dot.entry.id);
                    }}
                  />
                </svg>

                <div className="relative mt-1 h-4 border-t border-[color:var(--border)]">
                  {model.ticks.minor.map((year) => (
                    <span
                      key={year}
                      aria-hidden="true"
                      className="absolute top-0 h-1 w-px bg-[color:var(--border)]"
                      style={{ left: `${model.pctFor(year)}%` }}
                    />
                  ))}
                  {model.ticks.grid.map((year) => (
                    <span
                      key={year}
                      className="absolute -translate-x-1/2 pt-1 text-[10px] tabular-nums text-[color:var(--muted)]"
                      style={{ left: `${model.pctFor(year)}%` }}
                    >
                      {year}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {tip && tipDot && <StanceTooltip dot={tipDot} anchor={tip} />}

          <StanceKey dots={allDots} />

          <p className="mt-2 text-[10px] leading-relaxed text-[color:var(--muted)]">
            The axis is the whole corpus, {model.min}–{model.max}, on every
            question and under every filter — so empty stretches are years
            nobody addressed it. The count above is the range with material in
            it. Click a dot to jump to its entry.
          </p>
        </>
      )}
    </figure>
  );
}

function SubjectTabs({
  subject,
  counts,
  onChange,
}: {
  subject: QuestionId;
  counts: Record<QuestionId, number>;
  onChange: (id: QuestionId) => void;
}) {
  return (
    <div
      role="tablist"
      aria-label="Choose a question"
      className="-mx-1 mt-3 flex gap-1 overflow-x-auto whitespace-nowrap border-b border-[color:var(--border)]"
    >
      {QUESTIONS.map((s) => {
        const active = s.id === subject;
        const empty = counts[s.id] === 0;
        return (
          <button
            key={s.id}
            type="button"
            role="tab"
            aria-selected={active}
            disabled={empty && !active}
            onClick={() => onChange(s.id)}
            className={
              active
                ? "small-caps border-b-2 border-[color:var(--accent)] px-2 py-1.5 text-[11px] text-[color:var(--accent)]"
                : empty
                  ? "small-caps border-b-2 border-transparent px-2 py-1.5 text-[11px] text-[color:var(--border)]"
                  : "small-caps border-b-2 border-transparent px-2 py-1.5 text-[11px] text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
            }
          >
            {s.label}{" "}
            <span className="tabular-nums">{counts[s.id]}</span>
          </button>
        );
      })}
    </div>
  );
}

const TOOLTIP_HEIGHT = 150;

function StanceTooltip({
  dot,
  anchor,
}: {
  dot: Dot;
  anchor: { x: number; y: number; width: number };
}) {
  const ratio = anchor.x / anchor.width;
  const shiftX =
    ratio < 0.2 ? "translateX(0)" : ratio > 0.8 ? "translateX(-100%)" : "translateX(-50%)";
  const above = anchor.y >= TOOLTIP_HEIGHT + 15;

  return (
    <div
      role="tooltip"
      className="pointer-events-none absolute z-10 w-64 max-w-[80vw] rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-3"
      style={{
        left: anchor.x,
        top: above ? anchor.y - 10 : anchor.y + 12,
        transform: above ? `${shiftX} translateY(-100%)` : shiftX,
      }}
    >
      <p className="serif-onum text-[11px] tabular-nums text-[color:var(--muted)]">
        {dot.entry.dateDisplay}
        {dot.isCitation && <span className="small-caps"> · citation</span>}
      </p>
      <p className="serif mt-0.5 text-sm font-semibold leading-snug">
        {dot.entry.title}
      </p>
      <p className="mt-0.5 text-[11px] leading-snug text-[color:var(--muted)]">
        {dot.entry.speaker} · {dot.entry.office}
      </p>
      <p className="mt-2 text-[11px] leading-snug">
        <span
          className="small-caps"
          style={{ color: INK_PAINT[STATUS_META[dot.entry.correlationStatus].ink] }}
        >
          {dot.bandLabel}
        </span>{" "}
        <span className="text-[color:var(--muted)]">
          · {STATUS_META[dot.entry.correlationStatus].label}
        </span>
      </p>
      <ul className="mt-1.5 space-y-0.5">
        {dot.cats.map((c) => (
          <li
            key={c}
            className="flex items-center gap-1.5 text-[11px] leading-snug text-[color:var(--muted)]"
          >
            <span
              aria-hidden="true"
              className="inline-block h-1.5 w-1.5 shrink-0 rounded-full"
              style={{ background: INK_PAINT[CATEGORY_META[c].ink] }}
            />
            {CATEGORY_META[c].label}
          </li>
        ))}
      </ul>
      {dot.unreviewed && (
        <p className="mt-1.5 text-[10px] leading-snug text-[color:var(--muted)]">
          Placement not yet confirmed by the author.
        </p>
      )}
    </div>
  );
}

/**
 * Only the encodings actually on screen. A key that lists four statuses when
 * the filters left one is noise pretending to be information.
 */
function StanceKey({ dots }: { dots: Dot[] }) {
  const statuses = [...new Set(dots.map((d) => d.entry.correlationStatus))];
  const hasCitation = dots.some((d) => d.isCitation);
  const hasOriginal = dots.some((d) => !d.isCitation);
  const hasWeak = dots.some((d) => !d.strong);
  const unreviewed = dots.filter((d) => d.unreviewed).length;

  return (
    <ul className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 border-t border-[color:var(--border)] pt-2.5 text-[10px] text-[color:var(--muted)]">
      {statuses.map((s) => (
        <li key={s} className="flex items-center gap-1.5">
          <span
            aria-hidden="true"
            className="inline-block h-2 w-2 shrink-0 rounded-full"
            style={{ background: INK_PAINT[STATUS_META[s].ink] }}
          />
          {STATUS_META[s].label}
        </li>
      ))}
      {hasOriginal && hasCitation && (
        <li className="flex items-center gap-1.5">
          <span
            aria-hidden="true"
            className="inline-block h-2 w-2 shrink-0 rounded-full border border-[color:var(--muted)]"
          />
          Citation
        </li>
      )}
      {hasWeak && (
        <li className="flex items-center gap-1.5">
          <span
            aria-hidden="true"
            className="inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-[color:var(--muted)]"
          />
          Secondhand or later account
        </li>
      )}
      {unreviewed > 0 && (
        <li className="flex items-center gap-1.5">
          <span
            aria-hidden="true"
            className="inline-block h-2.5 w-2.5 shrink-0 rounded-full border border-dashed border-[color:var(--muted)]"
          />
          <span className="tabular-nums">
            {unreviewed} of {dots.length}
          </span>{" "}
          unconfirmed
        </li>
      )}
    </ul>
  );
}
