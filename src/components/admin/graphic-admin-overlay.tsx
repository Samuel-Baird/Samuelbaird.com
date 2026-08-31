"use client";

import { useState, useTransition } from "react";
import { Eye, EyeOff, Megaphone, MegaphoneOff } from "lucide-react";
import {
  setGraphicPostStatus,
  setGraphicPublished,
} from "@/app/actions/graphic-posts";

/**
 * Admin-only overlay rendered over a graphic image on a public page —
 * top-left publish/unpublish, top-right mark-as-posted. Meant to sit as a
 * sibling of the image (or the Link wrapping it) inside a `relative`
 * container, e.g.:
 *
 *   <div className="relative">
 *     <Link ...><Image .../></Link>
 *     {isAdmin && <GraphicAdminOverlay ... />}
 *   </div>
 *
 * Never nest it inside the Link/image itself — its buttons are interactive
 * elements and can't sit inside another interactive element.
 */
export function GraphicAdminOverlay({
  slug,
  graphicId,
  published: initialPublished,
  posted: initialPosted,
  postedDates: initialPostedDates,
  currentPath,
}: {
  slug: string;
  graphicId: string;
  published: boolean;
  posted: boolean;
  postedDates: string;
  currentPath: string;
}) {
  const [publishPending, startPublishTransition] = useTransition();
  const [postPending, startPostTransition] = useTransition();
  const [published, setPublished] = useState(initialPublished);
  const [posted, setPosted] = useState(initialPosted);
  const [postedDates, setPostedDates] = useState(initialPostedDates);
  const [datesOpen, setDatesOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function togglePublished() {
    const next = !published;
    setError(null);
    setPublished(next);
    startPublishTransition(async () => {
      try {
        await setGraphicPublished({ datasetSlug: slug, graphicId, published: next, currentPath });
      } catch (e) {
        setPublished(!next);
        setError(e instanceof Error ? e.message : "Something went wrong.");
      }
    });
  }

  function save(next: { posted: boolean; postedDates: string }) {
    setError(null);
    startPostTransition(async () => {
      try {
        await setGraphicPostStatus({ datasetSlug: slug, graphicId, ...next, currentPath });
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong.");
      }
    });
  }

  function togglePosted() {
    const next = !posted;
    setPosted(next);
    if (next) setDatesOpen(true);
    save({ posted: next, postedDates });
  }

  function saveDatesOnBlur() {
    if (postedDates === initialPostedDates) return;
    save({ posted, postedDates });
  }

  const buttonBase =
    "inline-flex h-9 items-center gap-1.5 rounded-[var(--radius)] border px-2.5 text-[11px] font-medium shadow-none disabled:opacity-60";

  return (
    <>
      <div className="absolute left-2 top-2 z-10">
        <button
          type="button"
          onClick={togglePublished}
          disabled={publishPending}
          className={`${buttonBase} bg-white/95 ${
            published
              ? "border-[color:var(--border)] text-[color:var(--foreground)]"
              : "border-[color:var(--oxblood)]/40 text-[color:var(--oxblood)]"
          }`}
        >
          {published ? (
            <Eye aria-hidden="true" size={13} />
          ) : (
            <EyeOff aria-hidden="true" size={13} />
          )}
          {published ? "Published" : "Hidden"}
        </button>
      </div>

      <div className="absolute right-2 top-2 z-10 flex flex-col items-end gap-2">
        <button
          type="button"
          onClick={togglePosted}
          disabled={postPending}
          className={`${buttonBase} border-[color:var(--border)] bg-white/95 ${
            posted ? "text-[color:var(--accent)]" : "text-[color:var(--muted)]"
          }`}
        >
          {posted ? (
            <Megaphone aria-hidden="true" size={13} />
          ) : (
            <MegaphoneOff aria-hidden="true" size={13} />
          )}
          {posted ? "Posted" : "Not posted"}
        </button>
        {(datesOpen || posted) && (
          <input
            type="text"
            value={postedDates}
            disabled={postPending}
            onChange={(e) => setPostedDates(e.target.value)}
            onBlur={saveDatesOnBlur}
            placeholder="Last posted… (free text)"
            className="h-9 w-48 rounded-[var(--radius)] border border-[color:var(--border)] bg-white/95 px-2.5 text-[11px] disabled:opacity-60"
          />
        )}
      </div>

      {error && (
        <p className="absolute bottom-2 left-2 right-2 z-10 rounded-[var(--radius)] border border-[color:var(--oxblood)]/40 bg-white/95 px-2.5 py-1 text-[11px] text-[color:var(--oxblood)]">
          {error}
        </p>
      )}
    </>
  );
}
