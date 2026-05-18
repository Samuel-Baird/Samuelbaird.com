import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Channels",
  description: "LDS YouTube channels tracked by Latter-day Stats.",
};

export default function ChannelsPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Channels
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        LDS YouTube creators
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        Sortable view of channels we track — subscribers, total views, upload
        cadence, and channel age. Data table appears here once the database is
        connected.
      </p>
      <div className="mt-12 rounded-2xl border border-dashed border-[color:var(--border)] bg-white p-8 text-sm text-[color:var(--muted)]">
        Channel table loading after Supabase setup.
      </div>
    </div>
  );
}
