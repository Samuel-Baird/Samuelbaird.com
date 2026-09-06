"use client";

import { useState, useTransition } from "react";
import { setGraphicPublished } from "@/app/actions/graphic-posts";
import {
  formatPublishAt,
  fromDateTimeLocal,
  publishState,
  toDateTimeLocal,
  type PublishState,
} from "@/lib/graphic-publish";

/**
 * Shared state machine for the two admin publish controls
 * (graphic-admin-controls.tsx on public pages, graphic-post-controls.tsx on
 * /admin/graphics). Three user intents map onto the one server action:
 *
 *   publishNow()     -> published = true,  publish_at = now
 *   schedule(iso)    -> published = true,  publish_at = iso (future => scheduled)
 *   hide()           -> published = false, publish_at untouched (kept as history)
 *
 * Optimistic: local state flips immediately and rolls back on error.
 */
export function useGraphicPublish({
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
  currentPath?: string;
}) {
  const [pending, startTransition] = useTransition();
  const [published, setPublished] = useState(initialPublished);
  const [publishAt, setPublishAt] = useState<string | null>(initialPublishAt);
  const [error, setError] = useState<string | null>(null);
  const [schedulerOpen, setSchedulerOpen] = useState(false);
  const [draft, setDraft] = useState("");

  const state: PublishState = publishState({ published, publish_at: publishAt });

  function commit(next: { published: boolean; publishAt?: string }) {
    const prev = { published, publishAt };
    setError(null);
    setPublished(next.published);
    if (next.published) setPublishAt(next.publishAt ?? new Date().toISOString());
    startTransition(async () => {
      try {
        const result = await setGraphicPublished({
          datasetSlug: slug,
          graphicId,
          published: next.published,
          publishAt: next.publishAt,
          currentPath,
        });
        if (result.publishAt) setPublishAt(result.publishAt);
      } catch (e) {
        setPublished(prev.published);
        setPublishAt(prev.publishAt);
        setError(e instanceof Error ? e.message : "Something went wrong.");
      }
    });
  }

  function publishNow() {
    commit({ published: true, publishAt: new Date().toISOString() });
  }

  function hide() {
    commit({ published: false });
  }

  /** Primary toggle: hidden -> live now; live/scheduled -> hidden. */
  function toggle() {
    if (state === "hidden") publishNow();
    else hide();
  }

  function openScheduler() {
    // Prefill with the existing schedule if it's still in the future,
    // otherwise with the current local time so the picker starts somewhere
    // sensible.
    setDraft(toDateTimeLocal(state === "scheduled" ? publishAt : null));
    setSchedulerOpen(true);
  }

  function closeScheduler() {
    setSchedulerOpen(false);
  }

  function saveSchedule() {
    const iso = fromDateTimeLocal(draft);
    if (!iso) {
      setError("Pick a date and time.");
      return;
    }
    setSchedulerOpen(false);
    commit({ published: true, publishAt: iso });
  }

  const label =
    state === "hidden"
      ? "Hidden"
      : state === "scheduled"
        ? `Scheduled · ${publishAt ? formatPublishAt(publishAt) : ""}`
        : publishAt
          ? `Published · ${formatPublishAt(publishAt)}`
          : "Published";

  return {
    pending,
    error,
    setError,
    state,
    published,
    publishAt,
    label,
    toggle,
    publishNow,
    hide,
    scheduler: {
      open: schedulerOpen,
      draft,
      setDraft,
      openScheduler,
      closeScheduler,
      saveSchedule,
    },
  };
}
