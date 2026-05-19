"use client";

import { Bell } from "lucide-react";
import Link from "next/link";

export type AdminMessagePreview = {
  id: string;
  category: string;
  body: string;
  created_at: string;
  page_ref: string | null;
  name: string | null;
  email: string | null;
};

type AdminMessageNotificationsProps = {
  openCount: number;
  previews: AdminMessagePreview[];
};

const CATEGORY_LABELS: Record<string, string> = {
  general: "General",
  correction: "Correction",
  channel_suggestion: "Channel",
  study_suggestion: "Study",
  bug: "Bug",
};

function previewText(message: AdminMessagePreview) {
  const text = message.body.replace(/\s+/g, " ").trim();
  return text.length > 120 ? `${text.slice(0, 117)}...` : text;
}

function sender(message: AdminMessagePreview) {
  return message.name || message.email || "Signed-in visitor";
}

export function AdminMessageNotifications({
  openCount,
  previews,
}: AdminMessageNotificationsProps) {
  return (
    <div className="group relative">
      <Link
        href="/admin/messages"
        aria-label={
          openCount === 1 ? "1 open message" : `${openCount} open messages`
        }
        className="relative inline-flex h-10 w-10 items-center justify-center rounded-full border border-[color:var(--border)] bg-white text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
      >
        <Bell className="h-4 w-4" aria-hidden="true" />
        {openCount > 0 ? (
          <span className="absolute -right-1 -top-1 inline-flex min-w-5 items-center justify-center rounded-full bg-[color:var(--accent)] px-1.5 py-0.5 text-[10px] font-semibold tabular-nums text-white">
            {openCount > 99 ? "99+" : openCount}
          </span>
        ) : null}
      </Link>

      <div className="pointer-events-none absolute right-0 top-12 z-50 hidden w-[min(22rem,calc(100vw-2.5rem))] rounded-lg border border-[color:var(--border)] bg-[color:var(--background)] p-2 opacity-0 shadow-lg transition-opacity group-hover:pointer-events-auto group-hover:block group-hover:opacity-100 group-focus-within:pointer-events-auto group-focus-within:block group-focus-within:opacity-100">
        <div className="flex items-center justify-between gap-3 border-b border-[color:var(--border)] px-3 py-2">
          <p className="text-sm font-semibold text-[color:var(--foreground)]">
            Open messages
          </p>
          <span className="rounded-full bg-[color:var(--accent-soft)] px-2 py-0.5 text-xs font-medium text-[color:var(--accent)]">
            {openCount}
          </span>
        </div>

        {previews.length === 0 ? (
          <p className="px-3 py-4 text-sm text-[color:var(--muted)]">
            No open messages right now.
          </p>
        ) : (
          <div className="max-h-96 overflow-y-auto py-1">
            {previews.map((message) => (
              <Link
                key={message.id}
                href={`/admin/messages#message-${message.id}`}
                className="block rounded-md px-3 py-2 hover:bg-[color:var(--muted-soft)]"
              >
                <div className="flex items-center justify-between gap-3 text-xs text-[color:var(--muted)]">
                  <span className="truncate font-medium text-[color:var(--accent)]">
                    {CATEGORY_LABELS[message.category] ?? message.category}
                  </span>
                  <span className="shrink-0">
                    {new Date(message.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="mt-1 truncate text-sm font-medium text-[color:var(--foreground)]">
                  {sender(message)}
                </p>
                <p className="mt-1 line-clamp-2 text-sm leading-snug text-[color:var(--muted)]">
                  {previewText(message)}
                </p>
                {message.page_ref ? (
                  <p className="mt-1 truncate text-xs text-[color:var(--muted)]">
                    ref: {message.page_ref}
                  </p>
                ) : null}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
