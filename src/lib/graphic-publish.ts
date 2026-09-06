// Pure, client-safe publish-state helpers shared by the server gate
// (src/lib/graphic-posts.ts), the admin controls, and the gallery client
// component. Kept free of "server-only" imports on purpose.
//
// A graphic_posts row (supabase/migrations/0049, 0051, 0054) encodes three
// states:
//   hidden     - published = false (publish_at, if any, is just history)
//   scheduled  - published = true and publish_at is in the future
//   published  - published = true and publish_at is null or in the past
// Only "published" is visible to non-admins.

export type PublishState = "hidden" | "scheduled" | "published";

export type PublishFields = {
  published: boolean;
  publish_at: string | null;
};

export function publishState(
  row: PublishFields | null | undefined,
  now: number = Date.now(),
): PublishState {
  if (!row || row.published !== true) return "hidden";
  if (row.publish_at) {
    const at = Date.parse(row.publish_at);
    if (Number.isFinite(at) && at > now) return "scheduled";
  }
  return "published";
}

export function isLive(row: PublishFields | null | undefined, now: number = Date.now()): boolean {
  return publishState(row, now) === "published";
}

/** Short human label for a publish instant, in the viewer's local zone, e.g.
 * "Sep 8, 9:00 AM". Client-side only for hydration safety (server and
 * browser zones differ) - callers render it inside suppressHydrationWarning
 * or after mount. */
export function formatPublishAt(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const sameYear = d.getFullYear() === new Date().getFullYear();
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    ...(sameYear ? {} : { year: "numeric" }),
    hour: "numeric",
    minute: "2-digit",
  });
}

/** ISO instant -> value for <input type="datetime-local"> in local time. */
export function toDateTimeLocal(iso: string | null): string {
  const d = iso ? new Date(iso) : new Date();
  if (Number.isNaN(d.getTime())) return "";
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** <input type="datetime-local"> value (local time) -> ISO instant, or null
 * when empty/invalid. */
export function fromDateTimeLocal(value: string): string | null {
  if (!value) return null;
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d.toISOString();
}
