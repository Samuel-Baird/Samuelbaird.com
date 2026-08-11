"use client";

import { useEffect } from "react";
import Link from "next/link";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="mx-auto max-w-2xl px-5 py-24 text-center sm:px-8 sm:py-32">
      <p className="small-caps text-xs font-medium text-[color:var(--oxblood)]">
        Error
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        Something went wrong.
      </h1>
      <p className="mt-5 text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        An unexpected error occurred loading this page. You can try again, or
        head back to the homepage.
      </p>
      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <button
          type="button"
          onClick={() => reset()}
          className="inline-flex h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90"
        >
          Try again
        </button>
        <Link
          href="/"
          className="inline-flex h-11 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-6 text-sm font-medium text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
        >
          Go home
        </Link>
      </div>
    </div>
  );
}
