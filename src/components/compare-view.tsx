"use client";

import { useState } from "react";
import { SectionBodyWithDiff } from "@/components/section-diff";
import type { ChangelogSection, ChangelogVersion } from "@/lib/types";

type Pair = { left: ChangelogSection | null; right: ChangelogSection | null };

function normalizeHeading(h: string | null | undefined): string {
  if (!h) return "";
  return h
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function isMatched(pair: Pair): boolean {
  if (!pair.left || !pair.right) return false;
  const lh = normalizeHeading(pair.left.heading);
  const rh = normalizeHeading(pair.right.heading);
  if (!lh && !rh) return true;
  return lh === rh;
}

function AlignmentBadge() {
  return (
    <span className="mb-2 inline-block rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-amber-700">
      No match
    </span>
  );
}

function SectionCell({
  section,
  matched,
  counterpart,
  diffMode,
  side,
}: {
  section: ChangelogSection | null;
  matched: boolean;
  counterpart: ChangelogSection | null;
  diffMode: boolean;
  side: "left" | "right";
}) {
  if (!section) {
    return (
      <div className="min-h-[5rem] rounded-xl border border-dashed border-[color:var(--border)] bg-[color:var(--muted-soft)]/40 p-4 text-xs italic text-[color:var(--muted)]">
        No corresponding section
      </div>
    );
  }
  return (
    <div className="rounded-xl border border-[color:var(--border)] bg-white p-4">
      {!matched && <AlignmentBadge />}
      {section.heading && (
        <p className="serif mb-3 text-base font-semibold leading-snug tracking-tight">
          {section.heading}
        </p>
      )}
      {section.body_markdown ? (
        <SectionBodyWithDiff
          markdown={section.body_markdown}
          counterpart={counterpart?.body_markdown}
          diffMode={diffMode}
          side={side}
        />
      ) : (
        !section.heading && (
          <p className="text-xs italic text-[color:var(--muted)]">
            Empty section
          </p>
        )
      )}
    </div>
  );
}

export function CompareView({
  va,
  vb,
  pairs,
}: {
  va: ChangelogVersion;
  vb: ChangelogVersion;
  pairs: Pair[];
}) {
  const [diffMode, setDiffMode] = useState(false);

  return (
    <>
      {/* Sticky column headers + toggle */}
      <div className="sticky top-0 z-10 mt-6 border-b border-[color:var(--border)] bg-[color:var(--background)] pb-3 pt-2">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="serif text-lg font-semibold leading-tight tracking-tight">
              {va.label}
            </p>
            {va.published_on && (
              <p className="mt-0.5 text-xs tabular-nums text-[color:var(--muted)]">
                {va.published_on}
              </p>
            )}
          </div>
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="serif text-lg font-semibold leading-tight tracking-tight">
                {vb.label}
              </p>
              {vb.published_on && (
                <p className="mt-0.5 text-xs tabular-nums text-[color:var(--muted)]">
                  {vb.published_on}
                </p>
              )}
            </div>
            <button
              onClick={() => setDiffMode((d) => !d)}
              className={`shrink-0 rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
                diffMode
                  ? "border-[color:var(--accent)] bg-[color:var(--accent)] text-white"
                  : "border-[color:var(--border)] bg-white text-[color:var(--foreground)] hover:border-[color:var(--accent)]"
              }`}
            >
              {diffMode ? "Diff on" : "Diff off"}
            </button>
          </div>
        </div>
      </div>

      {/* Legend */}
      {diffMode && (
        <div className="mt-4 flex flex-wrap gap-4 text-xs text-[color:var(--muted)]">
          <span className="flex items-center gap-1.5">
            <mark className="rounded bg-red-100 px-1 text-red-900 line-through not-italic">
              removed
            </mark>
            words removed in the newer edition
          </span>
          <span className="flex items-center gap-1.5">
            <mark className="rounded bg-emerald-100 px-1 text-emerald-900 not-italic">
              added
            </mark>
            words added in the newer edition
          </span>
        </div>
      )}

      {/* Section pairs */}
      {pairs.length === 0 ? (
        <p className="mt-12 text-sm text-[color:var(--muted)]">
          Neither edition has sections loaded yet.
        </p>
      ) : (
        <div className="mt-6 space-y-4">
          {pairs.map((pair, i) => {
            const matched = isMatched(pair);
            return (
              <div
                key={i}
                className={`grid grid-cols-2 gap-4 ${
                  !matched && pair.left && pair.right
                    ? "rounded-2xl ring-1 ring-amber-200 ring-offset-2"
                    : ""
                }`}
              >
                <SectionCell
                  section={pair.left}
                  matched={matched}
                  counterpart={pair.right}
                  diffMode={diffMode}
                  side="left"
                />
                <SectionCell
                  section={pair.right}
                  matched={matched}
                  counterpart={pair.left}
                  diffMode={diffMode}
                  side="right"
                />
              </div>
            );
          })}
        </div>
      )}

      <div className="mt-12 border-t border-[color:var(--border)] pt-6 text-xs text-[color:var(--muted)]">
        Sections with matching headings are aligned automatically. Pairs marked
        &ldquo;No match&rdquo; are positionally paired within unmatched gaps.
        AI-assisted change summaries are planned for a future phase.
      </div>
    </>
  );
}
