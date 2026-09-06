"use client";

import { CalendarClock, Clock, Eye, EyeOff } from "lucide-react";
import { useGraphicPublish } from "@/components/admin/use-graphic-publish";

/**
 * Admin-only publish/schedule controls for a graphic on a public page —
 * meant to sit in the same button row as Share/Download, below the image,
 * e.g.:
 *
 *   <div className="flex flex-wrap gap-3">
 *     {isAdmin && <GraphicAdminControls ... />}
 *     <GraphicShareButton ... />
 *     <a download>...</a>
 *   </div>
 *
 * Renders a flex row of its own, so it wraps cleanly alongside those
 * buttons rather than overlapping the image.
 *
 * `published` is the raw DB flag and `publishAt` the raw timestamp; the
 * hidden/scheduled/published state is derived in useGraphicPublish. The
 * Schedule picker doubles as the record of when a graphic was posted: a
 * past time just means "published as of then".
 */
export function GraphicAdminControls({
  slug,
  graphicId,
  published: initialPublished,
  publishAt: initialPublishAt,
  currentPath,
}: {
  slug: string;
  graphicId: string;
  published: boolean;
  publishAt: string | null;
  currentPath: string;
}) {
  const publish = useGraphicPublish({
    slug,
    graphicId,
    published: initialPublished,
    publishAt: initialPublishAt,
    currentPath,
  });

  const buttonBase =
    "inline-flex h-9 items-center gap-1.5 rounded-[var(--radius)] border px-2.5 text-xs font-medium disabled:opacity-60";
  const inputBase =
    "h-9 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-2.5 text-xs disabled:opacity-60";

  const StateIcon =
    publish.state === "published" ? Eye : publish.state === "scheduled" ? Clock : EyeOff;
  const stateClass =
    publish.state === "published"
      ? "border-[color:var(--border)] hover:bg-[color:var(--muted-soft)]"
      : publish.state === "scheduled"
        ? "border-[color:var(--accent)]/50 text-[color:var(--accent)] hover:bg-[color:var(--accent-soft)]"
        : "border-[color:var(--oxblood)]/40 text-[color:var(--oxblood)]";

  return (
    <div className="flex flex-wrap items-center gap-2">
      <button
        type="button"
        onClick={publish.toggle}
        disabled={publish.pending}
        title={publish.state === "hidden" ? "Publish now" : "Hide from the public site"}
        className={`${buttonBase} ${stateClass}`}
      >
        <StateIcon aria-hidden="true" size={13} />
        {/* Date text is formatted in the viewer's zone, so server and
            browser can disagree; that's expected. */}
        <span suppressHydrationWarning>{publish.label}</span>
      </button>

      <button
        type="button"
        onClick={publish.scheduler.open ? publish.scheduler.closeScheduler : publish.scheduler.openScheduler}
        disabled={publish.pending}
        aria-expanded={publish.scheduler.open}
        title="Set the publish date and time (past or future)"
        className={`${buttonBase} border-[color:var(--border)] text-[color:var(--muted)] hover:bg-[color:var(--muted-soft)]`}
      >
        <CalendarClock aria-hidden="true" size={13} />
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
          <label className="sr-only" htmlFor={`publish-at-${slug}-${graphicId}`}>
            Publish date and time
          </label>
          <input
            id={`publish-at-${slug}-${graphicId}`}
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
            className={`${buttonBase} border-[color:var(--accent)] bg-[color:var(--accent-soft)] text-[color:var(--accent)]`}
          >
            Set
          </button>
          <button
            type="button"
            onClick={publish.scheduler.closeScheduler}
            className={`${buttonBase} border-transparent text-[color:var(--muted)]`}
          >
            Cancel
          </button>
        </form>
      )}

      {publish.error && (
        <p className="w-full text-xs text-[color:var(--oxblood)]">{publish.error}</p>
      )}
    </div>
  );
}
