import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Studies",
  description:
    "Academic studies and research relating to the Latter-day Saint community.",
};

export default function StudiesPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Studies
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        Research library
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        A curated, growing collection of academic studies relating to the
        Latter-day Saint community.
      </p>
      <div className="mt-12 rounded-2xl border border-dashed border-[color:var(--border)] bg-white p-8 text-sm text-[color:var(--muted)]">
        Study cards loading after Supabase setup.
      </div>
    </div>
  );
}
