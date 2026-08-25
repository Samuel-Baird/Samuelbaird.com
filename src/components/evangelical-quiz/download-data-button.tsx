import Link from "next/link";
import { Download, Lock } from "lucide-react";

/**
 * Premium-gated download of the underlying survey dataset (every statement,
 * every group, the real percentages — same numbers build_data.py reads).
 * `premium` is resolved server-side in the page and passed down; the actual
 * gate lives in the route handler (requireCapability), this is just the UX
 * for it. A signed-out or non-premium reader gets a plain upsell, never a
 * link that would just redirect them away.
 */
export function DownloadDataButton({ premium }: { premium: boolean }) {
  if (!premium) {
    return (
      <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-4">
        <p className="small-caps flex items-center gap-1.5 text-[11px] font-medium text-[color:var(--honey)]">
          <Lock aria-hidden="true" size={12} />
          Premium
        </p>
        <p className="mt-2 text-xs leading-relaxed text-[color:var(--muted)]">
          Download the full dataset behind this quiz — every statement, every
          group, as CSV.
        </p>
        <div className="mt-3 flex flex-wrap gap-3 text-xs font-medium">
          <Link href="/donate" className="text-[color:var(--accent)] hover:underline">
            Donate to unlock
          </Link>
          <Link href="/premium" className="text-[color:var(--muted)] hover:underline">
            Learn more
          </Link>
        </div>
      </div>
    );
  }

  return (
    <a
      href="/api/exports/evangelical-quiz.csv"
      className="inline-flex min-h-9 items-center gap-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
    >
      <Download aria-hidden="true" size={13} />
      Download the data (CSV)
    </a>
  );
}
