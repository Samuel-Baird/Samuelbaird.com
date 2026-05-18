import type { Metadata } from "next";
import { ChannelsTable } from "@/components/channels-table";
import { getChannelsWithLatest } from "@/lib/data";

export const metadata: Metadata = {
  title: "Channels",
  description: "Latter-day Saint YouTube creators tracked by Latter-day Stats.",
};

export const revalidate = 600; // 10 minutes

export default async function ChannelsPage() {
  const channels = await getChannelsWithLatest();

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Channels
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        LDS YouTube creators
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        {channels.length} channels covering Latter-day Saint apologetics,
        scholarship, and faith-promoting discussion — searchable and sortable
        by subscribers, views, upload cadence, and channel age.
      </p>

      <div className="mt-10">
        <ChannelsTable channels={channels} />
      </div>
    </div>
  );
}
