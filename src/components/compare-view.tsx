"use client";

import { useState } from "react";
import { alignSections, type ManualLink, type Pair } from "@/lib/align-sections";
import { SectionBodyWithDiff } from "@/components/section-diff";
import type { ChangelogSection, ChangelogVersion } from "@/lib/types";

function normalizeHeading(h: string | null | undefined): string {
  if (!h) return "";
  return h
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function isHeadingMatched(pair: Pair): boolean {
  if (!pair.left || !pair.right) return false;
  const lh = normalizeHeading(pair.left.heading);
  const rh = normalizeHeading(pair.right.heading);
  if (!lh && !rh) return true;
  return lh === rh;
}

// ---------------------------------------------------------------------------
// Section cell
// ---------------------------------------------------------------------------

function SectionCell({
  section,
  aligned,
  manual,
  diffMode,
  counterpart,
  side,
  pendingId,
  onLinkClick,
  onUnlink,
}: {
  section: ChangelogSection | null;
  aligned: boolean;
  manual: boolean;
  diffMode: boolean;
  counterpart: ChangelogSection | null;
  side: "left" | "right";
  pendingId: string | null;
  onLinkClick: (id: string, side: "left" | "right") => void;
  onUnlink: (id: string, side: "left" | "right") => void;
}) {
  if (!section) {
    return (
      <div className="min-h-[5rem] rounded-xl border border-dashed border-[color:var(--border)] bg-[color:var(--muted-soft)]/40 p-4 text-xs italic text-[color:var(--muted)]">
        No corresponding section
      </div>
    );
  }

  const isPending = pendingId === section.id;

  let borderClass = "border-[color:var(--border)]";
  if (isPending) borderClass = "border-[color:var(--accent)] ring-2 ring-[color:var(--accent)]/30";
  else if (manual) borderClass = "border-violet-300";

  return (
    <div className={`rounded-xl border bg-white p-4 ${borderClass} transition-colors`}>
      {/* Badges row */}
      <div className="mb-2 flex flex-wrap items-center gap-2">
        {!aligned && !manual && (
          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-amber-700">
            No match
          </span>
        )}
        {manual && (
          <span className="rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-violet-700">
            Pinned
          </span>
        )}
        {isPending && (
          <span className="rounded-full bg-[color:var(--accent)] px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-white">
            Select counterpart →
          </span>
        )}
      </div>

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

      {/* Link / unlink button */}
      <div className="mt-3 border-t border-[color:var(--border)] pt-2">
        {manual ? (
          <button
            onClick={() => onUnlink(section.id, side)}
            className="text-xs text-violet-600 hover:underline"
          >
            Unpin
          </button>
        ) : (
          <button
            onClick={() => onLinkClick(section.id, side)}
            className={`text-xs hover:underline ${
              isPending
                ? "font-medium text-[color:var(--accent)]"
                : "text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
            }`}
          >
            {isPending ? "Cancel" : "Pin to…"}
          </button>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main view
// ---------------------------------------------------------------------------

export function CompareView({
  va,
  vb,
  initialLeft,
  initialRight,
}: {
  va: ChangelogVersion;
  vb: ChangelogVersion;
  initialLeft: ChangelogSection[];
  initialRight: ChangelogSection[];
}) {
  const [diffMode, setDiffMode] = useState(false);
  const [manualLinks, setManualLinks] = useState<ManualLink[]>([]);
  // { id, side } of the section currently waiting for its counterpart
  const [pending, setPending] = useState<{ id: string; side: "left" | "right" } | null>(null);

  const pairs = alignSections(initialLeft, initialRight, manualLinks);

  function handleLinkClick(id: string, side: "left" | "right") {
    if (pending === null) {
      // Start a new link
      setPending({ id, side });
      return;
    }

    // Cancel if clicking the same section again
    if (pending.id === id && pending.side === side) {
      setPending(null);
      return;
    }

    // Ignore clicks on the same side
    if (pending.side === side) {
      // Switch pending to the newly clicked section on the same side
      setPending({ id, side });
      return;
    }

    // Complete the link
    const leftId = side === "right" ? pending.id : id;
    const rightId = side === "right" ? id : pending.id;

    setManualLinks((prev) => {
      // Remove any existing links that involve either section
      const filtered = prev.filter(
        (l) => l.leftId !== leftId && l.rightId !== rightId,
      );
      return [...filtered, { leftId, rightId }];
    });
    setPending(null);
  }

  function handleUnlink(id: string, side: "left" | "right") {
    setManualLinks((prev) =>
      prev.filter((l) =>
        side === "left" ? l.leftId !== id : l.rightId !== id,
      ),
    );
  }

  const manualLinkedIds = new Set([
    ...manualLinks.map((l) => l.leftId),
    ...manualLinks.map((l) => l.rightId),
  ]);

  return (
    <>
      {/* Sticky column headers + controls */}
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
            <div className="flex shrink-0 items-center gap-2">
              {manualLinks.length > 0 && (
                <button
                  onClick={() => setManualLinks([])}
                  className="rounded-full border border-[color:var(--border)] bg-white px-3 py-1 text-xs font-medium text-[color:var(--muted)] hover:border-red-300 hover:text-red-600"
                >
                  Clear pins ({manualLinks.length})
                </button>
              )}
              <button
                onClick={() => setDiffMode((d) => !d)}
                className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
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
      </div>

      {/* Legends */}
      {(diffMode || pending) && (
        <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-xs text-[color:var(--muted)]">
          {diffMode && (
            <>
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
            </>
          )}
          {pending && (
            <span className="font-medium text-[color:var(--accent)]">
              Now click any section on the other side to pin it.
            </span>
          )}
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
            const headingMatched = isHeadingMatched(pair);
            const aligned = headingMatched || !!pair.manual;
            const ringClass =
              !aligned && pair.left && pair.right
                ? "rounded-2xl ring-1 ring-amber-200 ring-offset-2"
                : "";
            return (
              <div key={i} className={`grid grid-cols-2 gap-4 ${ringClass}`}>
                <SectionCell
                  section={pair.left}
                  aligned={aligned}
                  manual={!!pair.manual && manualLinkedIds.has(pair.left?.id ?? "")}
                  diffMode={diffMode}
                  counterpart={pair.right}
                  side="left"
                  pendingId={pending?.id ?? null}
                  onLinkClick={handleLinkClick}
                  onUnlink={handleUnlink}
                />
                <SectionCell
                  section={pair.right}
                  aligned={aligned}
                  manual={!!pair.manual && manualLinkedIds.has(pair.right?.id ?? "")}
                  diffMode={diffMode}
                  counterpart={pair.left}
                  side="right"
                  pendingId={pending?.id ?? null}
                  onLinkClick={handleLinkClick}
                  onUnlink={handleUnlink}
                />
              </div>
            );
          })}
        </div>
      )}

      <div className="mt-12 border-t border-[color:var(--border)] pt-6 text-xs text-[color:var(--muted)]">
        Sections with matching headings are aligned automatically. Use{" "}
        <span className="font-medium">Pin to…</span> on any section to manually
        pair it with a section on the other side.
      </div>
    </>
  );
}
