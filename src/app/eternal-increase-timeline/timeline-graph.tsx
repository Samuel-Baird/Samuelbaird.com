"use client";

import { useMemo, useRef, useState } from "react";
import type { TagInk } from "@/components/tag";
import { CATEGORY_META, categoriesOf } from "./constants";
import {
  ERA_STRIP,
  INK_PAINT,
  buildAxis,
  nearestDot,
  rowHeight,
  stackOffset,
} from "./graph-shared";
import type { SourceEntry } from "./schema";

/**
 * Swimlane plot of the filtered sources: one dot per source on a year axis
 * that autoscales to whatever the filters leave in view.
 *
 * Vertical position carries meaning. Each lane is one ink family from
 * CATEGORY_META — the dataset's own claim axes (backward-direction, forward /
 * eternal increase, structural frameworks, the orthodox baseline, and the
 * meta categories) — so a lane's dots read as one argument's life over time
 * rather than as a single band of mixed colour. Lane and colour encode the
 * same thing deliberately: the redundancy is what makes the plot legible at a
 * glance and still legible to someone who cannot separate the hues.
 *
 * Geometry is mixed on purpose: x is a percentage, so the plot reflows with
 * its container and needs no width measurement; y is pixels, so the lane
 * labels in the HTML gutter can be placed from the same numbers the SVG uses.
 * Era bands come from ERAS, so the plot and the card sections below it always
 * agree about where a period starts.
 */

// Lane order runs down the claim axes as constants.ts documents them:
// contested backward claims first, the site's namesake forward axis second,
// explanatory frameworks third, the orthodox counter-position fourth, and the
// meta categories last.
const LANES: { ink: TagInk; label: string }[] = [
  { ink: "oxblood", label: "Backward" },
  { ink: "honey", label: "Forward" },
  { ink: "accent", label: "Structural" },
  { ink: "ink", label: "Always God" },
  { ink: "muted", label: "Other" },
];

type Dot = {
  entry: SourceEntry;
  pct: number;
  cy: number;
  paint: string;
  isCitation: boolean;
  cats: ReturnType<typeof categoriesOf>;
};

type Lane = {
  ink: TagInk;
  label: string;
  y: number;
  height: number;
  dots: Dot[];
};

export function TimelineGraph({
  entries,
  onSelect,
  hoveredId,
  onHover,
}: {
  entries: SourceEntry[];
  onSelect?: (id: string) => void;
  hoveredId?: string | null;
  onHover?: (id: string | null) => void;
}) {
  // Kept separate from `hoveredId`, which the parent also sets when a card is
  // hovered: that direction should mark the dot without popping a tooltip over
  // a plot the reader is not looking at. Carries the anchor it was measured
  // with, because measuring happens in the handler that opened it — by render
  // time the ref may be null, and reading layout mid-render is not safe under
  // concurrent rendering.
  const [tip, setTip] = useState<{
    id: string;
    x: number;
    y: number;
    width: number;
  } | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const figureRef = useRef<HTMLElement>(null);

  const model = useMemo(() => {
    if (entries.length === 0) return null;
    const axis = buildAxis(entries.map((e) => Number(e.date.slice(0, 4))));
    const { pctFor } = axis;

    // Lane = the ink family of the entry's first category, the same rule the
    // dot's colour follows. Untagged entries fall to the meta lane.
    const byLane = new Map<TagInk, SourceEntry[]>();
    for (const entry of entries) {
      const cats = categoriesOf(entry);
      const ink: TagInk = cats.length > 0 ? CATEGORY_META[cats[0]].ink : "muted";
      byLane.set(ink, [...(byLane.get(ink) ?? []), entry]);
    }

    let y = ERA_STRIP;
    const lanes: Lane[] = [];
    for (const { ink, label } of LANES) {
      const members = byLane.get(ink);
      if (!members || members.length === 0) continue; // never draw an empty lane

      const columns = new Map<number, SourceEntry[]>();
      for (const entry of members) {
        const pct = pctFor(Number(entry.date.slice(0, 4)));
        columns.set(pct, [...(columns.get(pct) ?? []), entry]);
      }
      const maxStack = Math.max(...[...columns.values()].map((c) => c.length));
      const height = rowHeight(maxStack);
      const centre = y + height / 2;

      const dots: Dot[] = [];
      for (const [pct, group] of columns) {
        group.forEach((entry, i) => {
          dots.push({
            entry,
            pct,
            cy: centre + stackOffset(i, group.length),
            paint: INK_PAINT[ink],
            isCitation: entry.sourceType === "citation",
            cats: categoriesOf(entry),
          });
        });
      }
      lanes.push({ ink, label, y, height, dots });
      y += height;
    }

    return { ...axis, lanes, height: y };
  }, [entries]);

  if (!model) {
    return (
      <div className="rounded-[var(--radius)] border border-dashed border-[color:var(--border)] bg-white p-6 text-center text-xs text-[color:var(--muted)]">
        No sources to plot.
      </div>
    );
  }

  const allDots = model.lanes.flatMap((l) => l.dots);
  const tipDot = tip ? allDots.find((d) => d.entry.id === tip.id) : null;
  // Keyed to the shared hover state, not the tooltip's: hovering a card marks
  // its dot too, and that direction never opens a tooltip.
  const activeDot = hoveredId
    ? allDots.find((d) => d.entry.id === hoveredId)
    : null;

  const nearestTo = (event: { clientX: number; clientY: number }): Dot | null => {
    const box = svgRef.current?.getBoundingClientRect();
    return box ? nearestDot(allDots, box, event.clientX, event.clientY) : null;
  };

  /**
   * Open the tooltip on a dot, or close it when there is none.
   *
   * The anchor is measured against the figure, not the plot: `overflow-x-auto`
   * makes the plot a scroll container on both axes, so a tooltip taller than
   * the lanes would be clipped by it. Measuring through the figure also folds
   * in the lane gutter and the plot's current horizontal scroll offset.
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
      id: dot.entry.id,
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
          Distribution over time
        </span>
        <span className="text-[10px] tabular-nums text-[color:var(--muted)]">
          {entries.length} {entries.length === 1 ? "source" : "sources"} ·{" "}
          {model.dataMin}
          {model.dataMax !== model.dataMin ? `–${model.dataMax}` : ""}
        </span>
      </figcaption>

      {/* Under ~560px the year columns would sit closer together than the dots
          are wide, so the plot scrolls sideways instead of overlapping itself. */}
      <div className="mt-3 overflow-x-auto">
        <div className="flex min-w-[560px]">
          {/* Lane labels live in an HTML gutter rather than inside the SVG so
              they can never collide with a dot sitting at the axis minimum. */}
          <div
            className="relative w-16 shrink-0"
            style={{ height: model.height }}
            aria-hidden="true"
          >
            {model.lanes.map((lane) => (
              <span
                key={lane.ink}
                className="small-caps absolute right-2 text-[9px] leading-none text-[color:var(--muted)]"
                style={{ top: lane.y + lane.height / 2 - 4 }}
              >
                {lane.label}
              </span>
            ))}
          </div>

          <div className="relative min-w-0 flex-1">
            <svg
              ref={svgRef}
              width="100%"
              height={model.height}
              role="img"
              aria-label={`${entries.length} sources from ${model.dataMin} to ${model.dataMax}, grouped into ${model.lanes.length} claim lanes`}
              className="block"
            >
              {/* Era backdrop, alternating so period boundaries read without
                  spending another colour on them. */}
              {model.bands.map((band, i) =>
                i % 2 === 1 ? (
                  <rect
                    key={band.id}
                    x={`${band.left}%`}
                    y={0}
                    width={`${band.width}%`}
                    height={model.height}
                    fill="var(--muted-soft)"
                    opacity={0.55}
                  />
                ) : null,
              )}
              {model.bands.map((band) =>
                band.width >= 10 ? (
                  <text
                    key={band.id}
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

              {model.lanes.slice(1).map((lane) => (
                <line
                  key={lane.ink}
                  x1="0"
                  x2="100%"
                  y1={lane.y}
                  y2={lane.y}
                  stroke="var(--border)"
                  opacity={0.7}
                />
              ))}

              {/* Every halo before any mark. Adjacent years can sit closer
                  together than a halo is wide, so drawing each dot's halo
                  immediately before its own mark let a later dot's halo bite
                  a crescent out of its neighbour. */}
              {allDots.map((d) => (
                <circle
                  key={d.entry.id}
                  cx={`${d.pct}%`}
                  cy={d.cy}
                  r={6}
                  fill="var(--surface)"
                />
              ))}

              {activeDot && (
                <circle
                  cx={`${activeDot.pct}%`}
                  cy={activeDot.cy}
                  r={8.5}
                  fill="var(--surface)"
                  stroke="var(--honey)"
                  strokeWidth={1.5}
                />
              )}

              {allDots.map((d) => {
                const active = hoveredId === d.entry.id;
                return (
                  <g
                    key={d.entry.id}
                    role="button"
                    tabIndex={0}
                    aria-label={`${d.entry.dateDisplay}, ${d.entry.title}`}
                    // Pointer input belongs to the overlay below; these groups
                    // exist for keyboard reach and the accessibility tree.
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
                      // Hollow for citations, filled for originals: shape
                      // carries the distinction, so it survives alongside the
                      // colour encoding. Dimming used to fight it.
                      <circle
                        cx={`${d.pct}%`}
                        cy={d.cy}
                        r={active ? 5 : 4}
                        fill="var(--surface)"
                        stroke={d.paint}
                        strokeWidth={1.6}
                      />
                    ) : (
                      <circle
                        cx={`${d.pct}%`}
                        cy={d.cy}
                        r={active ? 5.5 : 4.5}
                        fill={d.paint}
                      />
                    )}
                  </g>
                );
              })}

              {/* Pointer layer, painted last so it owns every hover and tap. */}
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
                  // A tap has no hover to precede it, so show the entry the
                  // touch actually landed on before jumping to it.
                  track(e);
                  if (dot) onSelect?.(dot.entry.id);
                }}
              />
            </svg>

            {/* year axis */}
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

      {tip && tipDot && <Tooltip dot={tipDot} anchor={tip} />}

      <GraphKey lanes={model.lanes} />

      <p className="mt-2 text-[10px] leading-relaxed text-[color:var(--muted)]">
        The axis rescales to whatever the filters leave in view; click a dot to
        jump to its entry.
      </p>
    </figure>
  );
}

/**
 * Rough card height, used only to choose a side. Real ones run 104–230px
 * depending on how many categories an entry carries and how far its title
 * wraps, and the plot is barely taller than that, so an entry with five
 * categories will overhang the figure whichever side it takes. That is
 * deliberate: it floats over the section below, which is what a tooltip does.
 * What must not happen is clipping, which is why it is anchored to the figure
 * rather than to the plot's scroll container.
 */
const TOOLTIP_HEIGHT = 130;

function Tooltip({
  dot,
  anchor,
}: {
  dot: Dot;
  anchor: { x: number; y: number; width: number };
}) {
  // Flip against the near edge rather than letting the card hang off the side.
  const ratio = anchor.x / anchor.width;
  const shiftX =
    ratio < 0.2 ? "translateX(0)" : ratio > 0.8 ? "translateX(-100%)" : "translateX(-50%)";
  // Above when there is room above, so the card stays inside the figure.
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
      {dot.cats.length > 0 && (
        <ul className="mt-2 space-y-0.5">
          {dot.cats.map((c) => (
            <li key={c} className="flex items-center gap-1.5 text-[11px] leading-snug">
              <span
                aria-hidden="true"
                className="inline-block h-1.5 w-1.5 shrink-0 rounded-full"
                style={{ background: INK_PAINT[CATEGORY_META[c].ink] }}
              />
              {CATEGORY_META[c].label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/**
 * The key that used to live only in the sidebar's collapsed "About the
 * scales" panel, moved next to the marks it explains. It lists the lanes
 * currently in view, so it doubles as the lane legend once the gutter labels
 * scroll off the side on a phone.
 */
function GraphKey({ lanes }: { lanes: Lane[] }) {
  return (
    <ul className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 border-t border-[color:var(--border)] pt-2.5 text-[10px] text-[color:var(--muted)]">
      {lanes.map((lane) => (
        <li key={lane.ink} className="flex items-center gap-1.5">
          <span
            aria-hidden="true"
            className="inline-block h-2 w-2 shrink-0 rounded-full"
            style={{ background: INK_PAINT[lane.ink] }}
          />
          {lane.label}
        </li>
      ))}
      <li className="flex items-center gap-1.5">
        <span
          aria-hidden="true"
          className="inline-block h-2 w-2 shrink-0 rounded-full bg-[color:var(--muted)]"
        />
        Original
      </li>
      <li className="flex items-center gap-1.5">
        <span
          aria-hidden="true"
          className="inline-block h-2 w-2 shrink-0 rounded-full border border-[color:var(--muted)]"
        />
        Citation
      </li>
    </ul>
  );
}
