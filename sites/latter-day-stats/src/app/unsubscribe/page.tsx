import type { Metadata } from "next";
import Link from "next/link";

// The monthly newsletter has ended (November 2026) and its subscriber list is
// no longer read. Emails already sent link here (/unsubscribe?token=...), so
// this static page answers them instead of a 404.
export const metadata: Metadata = {
  title: "Newsletter ended",
  robots: { index: false },
};

export default function UnsubscribePage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <div className="mx-auto max-w-xl rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-8 text-center">
        <h1 className="serif text-2xl font-semibold tracking-tight">
          The newsletter has ended
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
          Latter-day Stats no longer sends the monthly email, so there is
          nothing to unsubscribe from. You won&apos;t receive it again. New
          channels and studies still appear on the site.
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link
            href="/channels"
            className="inline-flex h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90"
          >
            Browse channels
          </Link>
          <Link
            href="/studies"
            className="inline-flex h-11 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-6 text-sm font-medium hover:bg-[color:var(--muted-soft)]"
          >
            Browse studies
          </Link>
        </div>
      </div>
    </div>
  );
}
