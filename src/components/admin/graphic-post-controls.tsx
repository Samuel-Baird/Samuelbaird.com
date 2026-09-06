"use client";

import { useState, useTransition } from "react";
import { CalendarClock } from "lucide-react";
import { setGraphicPostStatus } from "@/app/actions/graphic-posts";
import { useGraphicPublish } from "@/components/admin/use-graphic-publish";

/** Compact publish/schedule/posted row for /admin/graphics. Same state
 * machine as GraphicAdminControls (useGraphicPublish), denser layout. */
export function GraphicPostControls({
  datasetSlug,
  graphicId,
  posted: initialPosted,
  postedDates: initialPostedDates,
  published: initialPublished,
  publishAt: initialPublishAt,
}: {
  datasetSlug: string;
  graphicId: string;
  posted: boolean;
  postedDates: string;
  published: boolean;
  publishAt: string | null;
}) {
  const publish = useGraphicPublish({
    slug: datasetSlug,
    graphicId,
    published: initialPublished,
    publishAt: initialPublishAt,
  });
  const [postPending, startPostTransition] = useTransition();
  const [posted, setPosted] = useState(initialPosted);
  const [postedDates, setPostedDates] = useState(initialPostedDates);
  const [postError, setPostError] = useState<string | null>(null);

  function save(next: { posted: boolean; postedDates: string }) {
    setPostError(null);
    startPostTransition(async () => {
      try {
        await setGraphicPostStatus({ datasetSlug, graphicId, ...next });
      } catch (e) {
        setPostError(e instanceof Error ? e.message : "Something went wrong.");
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

  const stateText =
    publish.state === "hidden"
      ? "text-[color:var(--oxblood)]"
      : publish.state === "scheduled"
        ? "text-[color:var(--accent)]"
        : "text-[color:var(--muted)]";
  const smallButton =
    "inline-flex h-8 items-center gap-1 rounded-[var(--radius)] border px-2 text-xs font-medium disabled:opacity-60";
  const inputBase =
    "h-8 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-2 text-xs disabled:opacity-60";
  const error = publish.error ?? postError;

  return (
    <div className="flex flex-wrap items-center gap-3">
      <label className="inline-flex items-center gap-1.5 text-xs font-medium">
        <input
          type="checkbox"
          checked={publish.state !== "hidden"}
          disabled={publish.pending}
          onChange={publish.toggle}
          className="h-4 w-4 accent-[color:var(--accent)] disabled:opacity-60"
        />
        <span suppressHydrationWarning className={stateText}>
          {publish.label}
        </span>
      </label>

      <button
        type="button"
        onClick={publish.scheduler.open ? publish.scheduler.closeScheduler : publish.scheduler.openScheduler}
        disabled={publish.pending}
        aria-expanded={publish.scheduler.open}
        title="Schedule a publish time"
        className={`${smallButton} border-[color:var(--border)] text-[color:var(--muted)] hover:bg-[color:var(--muted-soft)]`}
      >
        <CalendarClock aria-hidden="true" size={12} />
        Schedule
      </button>

      {publish.scheduler.open && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            publish.scheduler.saveSchedule();
          }}
          className="flex items-center gap-1.5"
        >
          <label className="sr-only" htmlFor={`publish-at-${datasetSlug}-${graphicId}`}>
            Publish date and time
          </label>
          <input
            id={`publish-at-${datasetSlug}-${graphicId}`}
            type="datetime-local"
            value={publish.scheduler.draft}
            onChange={(e) => publish.scheduler.setDraft(e.target.value)}
            disabled={publish.pending}
            required
            className={inputBase}
          />
          <button
            type="submit"
            disabled={publish.pending}
            className={`${smallButton} border-[color:var(--accent)] bg-[color:var(--accent-soft)] text-[color:var(--accent)]`}
          >
            Set
          </button>
          <button
            type="button"
            onClick={publish.scheduler.closeScheduler}
            className={`${smallButton} border-transparent text-[color:var(--muted)]`}
          >
            Cancel
          </button>
        </form>
      )}

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
        placeholder="Where posted… (free text)"
        className={`${inputBase} h-9 min-w-0 flex-1 px-3`}
      />
      {error && <p className="w-full text-xs text-[color:var(--oxblood)]">{error}</p>}
    </div>
  );
}
