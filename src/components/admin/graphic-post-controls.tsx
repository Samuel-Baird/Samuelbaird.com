"use client";

import { useState, useTransition } from "react";
import { setGraphicPostStatus, setGraphicPublished } from "@/app/actions/graphic-posts";

export function GraphicPostControls({
  datasetSlug,
  graphicId,
  posted: initialPosted,
  postedDates: initialPostedDates,
  published: initialPublished,
}: {
  datasetSlug: string;
  graphicId: string;
  posted: boolean;
  postedDates: string;
  published: boolean;
}) {
  const [postPending, startPostTransition] = useTransition();
  const [publishPending, startPublishTransition] = useTransition();
  const [posted, setPosted] = useState(initialPosted);
  const [postedDates, setPostedDates] = useState(initialPostedDates);
  const [published, setPublished] = useState(initialPublished);
  const [error, setError] = useState<string | null>(null);

  function save(next: { posted: boolean; postedDates: string }) {
    setError(null);
    startPostTransition(async () => {
      try {
        await setGraphicPostStatus({ datasetSlug, graphicId, ...next });
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong.");
      }
    });
  }

  function togglePosted() {
    const next = !posted;
    setPosted(next);
    save({ posted: next, postedDates });
  }

  function saveDatesOnBlur() {
    if (postedDates === initialPostedDates) return;
    save({ posted, postedDates });
  }

  function togglePublished() {
    const next = !published;
    setError(null);
    setPublished(next);
    startPublishTransition(async () => {
      try {
        await setGraphicPublished({ datasetSlug, graphicId, published: next });
      } catch (e) {
        setPublished(!next);
        setError(e instanceof Error ? e.message : "Something went wrong.");
      }
    });
  }

  return (
    <div className="flex flex-wrap items-center gap-3">
      <label className="inline-flex items-center gap-1.5 text-xs font-medium">
        <input
          type="checkbox"
          checked={published}
          disabled={publishPending}
          onChange={togglePublished}
          className="h-4 w-4 accent-[color:var(--accent)] disabled:opacity-60"
        />
        Published
      </label>
      <label className="inline-flex items-center gap-1.5 text-xs font-medium">
        <input
          type="checkbox"
          checked={posted}
          disabled={postPending}
          onChange={togglePosted}
          className="h-4 w-4 accent-[color:var(--accent)] disabled:opacity-60"
        />
        Posted
      </label>
      <input
        type="text"
        value={postedDates}
        disabled={postPending}
        onChange={(e) => setPostedDates(e.target.value)}
        onBlur={saveDatesOnBlur}
        placeholder="Last posted… (free text)"
        className="h-9 min-w-0 flex-1 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-xs disabled:opacity-60"
      />
      {error && <p className="w-full text-xs text-[color:var(--oxblood)]">{error}</p>}
    </div>
  );
}
