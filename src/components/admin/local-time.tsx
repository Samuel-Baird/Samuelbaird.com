"use client";

import { formatPublishAt } from "@/lib/graphic-publish";

/** Renders an ISO instant in the viewer's local zone. The server renders it
 * in its own zone first, so the text is expected to differ on hydration. */
export function LocalTime({ iso, className }: { iso: string; className?: string }) {
  return (
    <time dateTime={iso} className={className} suppressHydrationWarning>
      {formatPublishAt(iso)}
    </time>
  );
}
