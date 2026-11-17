"use client";

import { CalendarClock } from "lucide-react";
import { useGraphicPublish } from "@/components/admin/use-graphic-publish";

/** Compact publish/schedule row for /admin/graphics. Same state machine as
 * GraphicAdminControls (useGraphicPublish), denser layout. */
export function GraphicPostControls({
  datasetSlug,
  graphicId,
  published: initialPublished,
  publishAt: initialPublishAt,
}: {
  datasetSlug: string;
  graphicId: string;
  published: boolean;
  publishAt: string | null;
}) {
  const publish = useGraphicPublish({
    slug: datasetSlug,
    graphicId,
    published: initialPublished,
    publishAt: initialPublishAt,
  });

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
        title="Set the publish date and time (past or future)"
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

      {publish.error && <p className="w-full text-xs text-[color:var(--oxblood)]">{publish.error}</p>}
    </div>
  );
}
