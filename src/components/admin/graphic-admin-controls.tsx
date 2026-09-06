"use client";

import { useState, useTransition } from "react";
import { CalendarClock, Clock, Eye, EyeOff, Megaphone, MegaphoneOff } from "lucide-react";
import { setGraphicPostStatus } from "@/app/actions/graphic-posts";
import { useGraphicPublish } from "@/components/admin/use-graphic-publish";

/**
 * Admin-only publish/schedule/posted controls for a graphic on a public page
 * — meant to sit in the same button row as Share/Download, below the image,
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
 * hidden/scheduled/published state is derived in useGraphicPublish.
 */
export function GraphicAdminControls({
  slug,
  graphicId,
  published: initialPublished,
  publishAt: initialPublishAt,
  posted: initialPosted,
  postedDates: initialPostedDates,
  currentPath,
}: {
  slug: string;
  graphicId: string;
  published: boolean;
  publishAt: string | null;
  posted: boolean;
  postedDates: string;
  currentPath: string;
}) {
  const publish = useGraphicPublish({
    slug,
    graphicId,
    published: initialPublished,
    publishAt: initialPublishAt,
    currentPath,
  });
  const [postPending, startPostTransition] = useTransition();
  const [posted, setPosted] = useState(initialPosted);
  const [postedDates, setPostedDates] = useState(initialPostedDates);
  const [datesOpen, setDatesOpen] = useState(false);
  const [postError, setPostError] = useState<string | null>(null);

  function save(next: { posted: boolean; postedDates: string }) {
    setPostError(null);
    startPostTransition(async () => {
      try {
        await setGraphicPostStatus({ datasetSlug: slug, graphicId, ...next, currentPath });
      } catch (e) {
        setPostError(e instanceof Error ? e.message : "Something went wrong.");
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
  const error = publish.error ?? postError;

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
        title="Schedule a publish time"
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
          placeholder="Where posted… (free text)"
          className={`${inputBase} w-48`}
        />
      )}

      {error && (
        <p className="w-full text-xs text-[color:var(--oxblood)]">{error}</p>
      )}
    </div>
  );
}
