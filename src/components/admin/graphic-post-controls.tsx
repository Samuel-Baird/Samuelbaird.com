"use client";

import { useState, useTransition } from "react";
import { setGraphicPostStatus } from "@/app/actions/graphic-posts";

export function GraphicPostControls({
  datasetSlug,
  graphicId,
  posted: initialPosted,
  postedDates: initialPostedDates,
}: {
  datasetSlug: string;
  graphicId: string;
  posted: boolean;
  postedDates: string;
}) {
  const [pending, startTransition] = useTransition();
  const [posted, setPosted] = useState(initialPosted);
  const [postedDates, setPostedDates] = useState(initialPostedDates);
  const [error, setError] = useState<string | null>(null);

  function save(next: { posted: boolean; postedDates: string }) {
    setError(null);
    startTransition(async () => {
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

  return (
    <div className="flex flex-wrap items-center gap-3">
      <label className="inline-flex items-center gap-1.5 text-xs font-medium">
        <input
          type="checkbox"
          checked={posted}
          disabled={pending}
          onChange={togglePosted}
          className="h-4 w-4 accent-[color:var(--accent)] disabled:opacity-60"
        />
        Posted
      </label>
      <input
        type="text"
        value={postedDates}
        disabled={pending}
        onChange={(e) => setPostedDates(e.target.value)}
        onBlur={saveDatesOnBlur}
        placeholder="Last posted… (free text)"
        className="h-9 min-w-0 flex-1 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-xs disabled:opacity-60"
      />
      {error && <p className="w-full text-xs text-[color:var(--oxblood)]">{error}</p>}
    </div>
  );
}
