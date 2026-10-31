import { Download } from "lucide-react";

/**
 * Free download of the underlying survey dataset (every statement, every
 * group, the real percentages — same numbers build_data.py reads).
 */
export function DownloadDataButton() {
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
