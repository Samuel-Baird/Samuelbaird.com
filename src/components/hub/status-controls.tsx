"use client";

import { useState, useTransition } from "react";
import { clearHubVideoStatus, setHubVideoStatus } from "@/app/actions/hub-status";
import { Tag } from "@/components/tag";
import type { HubVideoStatusValue, HubVideoStatusWithUser } from "@/lib/types";

export function StatusControls({
  videoId,
  currentPath,
  ownStatus,
  allStatuses,
  currentUserId,
}: {
  videoId: string;
  currentPath: string;
  ownStatus: HubVideoStatusWithUser | null;
  allStatuses: HubVideoStatusWithUser[];
  currentUserId: string;
}) {
  const [pending, startTransition] = useTransition();
  const [responseUrl, setResponseUrl] = useState(
    ownStatus?.response_url ?? "",
  );
  const [error, setError] = useState<string | null>(null);

  function setStatus(status: HubVideoStatusValue) {
    setError(null);
    startTransition(async () => {
      try {
        await setHubVideoStatus({
          videoId,
          status,
          responseUrl: status === "responded" ? responseUrl : undefined,
          currentPath,
        });
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong.");
      }
    });
  }

  function clear() {
    setError(null);
    startTransition(async () => {
      try {
        await clearHubVideoStatus({ videoId, currentPath });
        setResponseUrl("");
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong.");
      }
    });
  }

  const others = allStatuses.filter((s) => s.user_id !== currentUserId);

  return (
    <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5">
      <h2 className="serif text-lg font-semibold tracking-tight">
        Your status
      </h2>

      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          disabled={pending}
          onClick={() => setStatus("working_on_it")}
          className={
            "rounded-[var(--radius)] border px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-60 " +
            (ownStatus?.status === "working_on_it"
              ? "border-[color:var(--accent)] bg-[color:var(--accent-soft)] text-[color:var(--accent)]"
              : "border-[color:var(--border)] text-[color:var(--muted)] hover:text-[color:var(--foreground)]")
          }
        >
          Working on it
        </button>
        <button
          type="button"
          disabled={pending}
          onClick={() => setStatus("responded")}
          className={
            "rounded-[var(--radius)] border px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-60 " +
            (ownStatus?.status === "responded"
              ? "border-[color:var(--accent)] bg-[color:var(--accent-soft)] text-[color:var(--accent)]"
              : "border-[color:var(--border)] text-[color:var(--muted)] hover:text-[color:var(--foreground)]")
          }
        >
          Responded
        </button>
        {ownStatus && (
          <button
            type="button"
            disabled={pending}
            onClick={clear}
            className="rounded-[var(--radius)] px-3 py-1.5 text-xs font-medium text-[color:var(--muted)] hover:text-[color:var(--oxblood)] disabled:opacity-60"
          >
            Clear
          </button>
        )}
      </div>

      {ownStatus?.status === "responded" && (
        <div className="mt-3">
          <label className="block">
            <span className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
              Link to your response (optional)
            </span>
            <input
              type="text"
              value={responseUrl}
              onChange={(e) => setResponseUrl(e.target.value)}
              onBlur={() => setStatus("responded")}
              placeholder="https://…"
              className="mt-1.5 h-10 w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-sm"
            />
          </label>
        </div>
      )}

      {error && (
        <p className="mt-2 text-xs text-[color:var(--oxblood)]">{error}</p>
      )}

      {others.length > 0 && (
        <div className="mt-5 border-t border-[color:var(--border)] pt-4">
          <p className="small-caps text-xs text-[color:var(--muted)]">
            Others working this video
          </p>
          <ul className="mt-2 space-y-2">
            {others.map((s) => (
              <li key={s.user_id} className="flex items-center gap-2 text-sm">
                <Tag ink={s.status === "responded" ? "ink" : "accent"}>
                  {s.status === "responded" ? "Responded" : "Working on it"}
                </Tag>
                <span className="text-[color:var(--foreground)]">
                  {s.full_name || s.email || "Apologist"}
                </span>
                {s.response_url && (
                  <a
                    href={s.response_url}
                    target="_blank"
                    rel="noreferrer noopener"
                    className="text-xs text-[color:var(--accent)] hover:underline"
                  >
                    view
                  </a>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
