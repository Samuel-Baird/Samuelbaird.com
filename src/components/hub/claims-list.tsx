"use client";

import type { HubClaim } from "@/lib/types";

function formatTimestamp(totalSeconds: number): string {
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = Math.floor(totalSeconds % 60);
  const mm = h > 0 ? String(m).padStart(2, "0") : String(m);
  const ss = String(s).padStart(2, "0");
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
}

export function ClaimsList({
  claims,
  onSeek,
}: {
  claims: HubClaim[];
  onSeek: (seconds: number) => void;
}) {
  if (claims.length === 0) {
    return (
      <p className="text-sm text-[color:var(--muted)]">
        No claims recorded for this video yet.
      </p>
    );
  }

  return (
    <ol className="space-y-6">
      {claims.map((claim) => (
        <li
          key={claim.id}
          className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5"
        >
          <button
            type="button"
            onClick={() => onSeek(claim.timestamp_seconds)}
            className="small-caps inline-flex items-center gap-1.5 rounded-[var(--radius)] bg-[color:var(--accent-soft)] px-2 py-1 text-xs font-medium text-[color:var(--accent)] transition-opacity hover:opacity-80 motion-reduce:transition-none"
          >
            ▶ {formatTimestamp(claim.timestamp_seconds)}
          </button>

          <p className="serif mt-3 italic leading-relaxed text-[color:var(--foreground)]">
            &ldquo;{claim.excerpt}&rdquo;
          </p>

          <p className="mt-3 text-sm font-medium text-[color:var(--foreground)]">
            {claim.claim_summary}
          </p>

          <p className="mt-2 text-sm leading-relaxed text-[color:var(--muted)]">
            {claim.response}
          </p>

          {claim.sources.length > 0 && (
            <div className="mt-4 border-t border-[color:var(--border)] pt-3">
              <p className="small-caps text-xs text-[color:var(--muted)]">
                Sources to respond
              </p>
              <ul className="mt-2 space-y-1.5">
                {claim.sources.map((source, i) => (
                  <li key={i} className="text-sm">
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noreferrer noopener"
                      className="text-[color:var(--accent)] hover:underline"
                    >
                      {source.title}
                    </a>
                    {source.note && (
                      <span className="text-[color:var(--muted)]">
                        {" "}
                        — {source.note}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </li>
      ))}
    </ol>
  );
}
