"use client";

import { useState, useTransition } from "react";
import { Eye, EyeOff, Megaphone, MegaphoneOff } from "lucide-react";
import {
  setGraphicPostStatus,
  setGraphicPublished,
} from "@/app/actions/graphic-posts";

/**
 * Admin-only publish/posted controls for a graphic on a public page — meant
 * to sit in the same button row as Share/Download, below the image, e.g.:
 *
 *   <div className="flex flex-wrap gap-3">
 *     {isAdmin && <GraphicAdminControls ... />}
 *     <GraphicShareButton ... />
 *     <a download>...</a>
 *   </div>
 *
 * Renders a flex row of its own, so it wraps cleanly alongside those
 * buttons rather than overlapping the image.
 */
export function GraphicAdminControls({
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
    "inline-flex h-9 items-center gap-1.5 rounded-[var(--radius)] border px-2.5 text-xs font-medium disabled:opacity-60";

  return (
    <div className="flex flex-wrap items-center gap-2">
      <button
        type="button"
        onClick={togglePublished}
        disabled={publishPending}
        className={`${buttonBase} ${
          published
            ? "border-[color:var(--border)] hover:bg-[color:var(--muted-soft)]"
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

      <button
        type="button"
        onClick={togglePosted}
        disabled={postPending}
        className={`${buttonBase} border-[color:var(--border)] ${
          posted ? "text-[color:var(--accent)]" : "text-[color:var(--muted)] hover:bg-[color:var(--muted-soft)]"
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
          className="h-9 w-48 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-2.5 text-xs disabled:opacity-60"
        />
      )}

      {error && (
        <p className="w-full text-xs text-[color:var(--oxblood)]">{error}</p>
      )}
    </div>
  );
}
