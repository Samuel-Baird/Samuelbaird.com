"use client";

import { useState, useTransition } from "react";
import {
  addReportedResponse,
  removeReportedResponse,
} from "@/app/actions/hub-reported-responses";
import { fmtRelative } from "@/lib/format";
import type { HubReportedResponseWithUser } from "@/lib/types";

function hostname(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

export function ReportedResponses({
  videoId,
  currentPath,
  responses,
  currentUserId,
  isAdmin,
}: {
  videoId: string;
  currentPath: string;
  responses: HubReportedResponseWithUser[];
  currentUserId: string;
  isAdmin: boolean;
}) {
  const [pending, startTransition] = useTransition();
  const [url, setUrl] = useState("");
  const [error, setError] = useState<string | null>(null);

  function add() {
    setError(null);
    if (!url.trim()) return;
    startTransition(async () => {
      try {
        await addReportedResponse({ videoId, url, currentPath });
        setUrl("");
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong.");
      }
    });
  }

  function remove(id: string) {
    setError(null);
    startTransition(async () => {
      try {
        await removeReportedResponse({ id, currentPath });
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong.");
      }
    });
  }

  return (
    <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5">
      <h2 className="serif text-lg font-semibold tracking-tight">
        Known responses
      </h2>
      <p className="mt-1 text-xs text-[color:var(--muted)]">
        Know of a response to this video — yours or someone else&rsquo;s? Log
        the link here so other apologists don&rsquo;t duplicate the work.
      </p>

      <div className="mt-3 flex flex-col gap-2 sm:flex-row">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              add();
            }
          }}
          placeholder="https://…"
          className="h-10 flex-1 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-sm"
        />
        <button
          type="button"
          disabled={pending || !url.trim()}
          onClick={add}
          className="h-10 shrink-0 rounded-[var(--radius)] border border-[color:var(--accent)] bg-[color:var(--accent-soft)] px-4 text-xs font-medium text-[color:var(--accent)] transition-colors disabled:opacity-60"
        >
          Add link
        </button>
      </div>

      {error && (
        <p className="mt-2 text-xs text-[color:var(--oxblood)]">{error}</p>
      )}

      {responses.length > 0 ? (
        <ul className="mt-4 space-y-2 border-t border-[color:var(--border)] pt-4">
          {responses.map((r) => {
            const canRemove = isAdmin || r.added_by === currentUserId;
            return (
              <li
                key={r.id}
                className="flex items-center justify-between gap-2 text-sm"
              >
                <a
                  href={r.url}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="min-w-0 truncate text-[color:var(--accent)] hover:underline"
                  title={r.url}
                >
                  {hostname(r.url)}
                </a>
                <span className="shrink-0 text-xs text-[color:var(--muted)]">
                  {r.full_name || r.email || "Apologist"} ·{" "}
                  {fmtRelative(r.created_at).text}
                  {canRemove && (
                    <button
                      type="button"
                      disabled={pending}
                      onClick={() => remove(r.id)}
                      className="ml-2 text-[color:var(--muted)] hover:text-[color:var(--oxblood)] disabled:opacity-60"
                    >
                      remove
                    </button>
                  )}
                </span>
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="mt-4 border-t border-[color:var(--border)] pt-4 text-xs text-[color:var(--muted)]">
          No responses logged yet.
        </p>
      )}
    </div>
  );
}
