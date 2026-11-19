import type { Metadata } from "next";
import { sectionOgImage } from "@/lib/og-images";
import Link from "next/link";
import { ChannelsExplorer } from "@/components/channels-explorer";
import { DeseretTitle } from "@/components/deseret-title";
import { FreshnessBadge } from "@/components/freshness-badge";
import { getCurrentUser } from "@/lib/auth";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";
import { getBookmarkSetForUser, getChannelsWithLatest } from "@/lib/data";

export const metadata: Metadata = {
  title: "Channels",
  description: "Latter-day Saint YouTube creators tracked by Latter-day Stats.",
  alternates: { canonical: "/channels" },
  ...sectionOgImage("channels", "Latter-day Stats — Channels"),
};

export default async function ChannelsPage() {
  const auth = await getCurrentUser();
  const [channels, bookmarks] = await Promise.all([
    getChannelsWithLatest({
      includeInactive: true,
    }),
    auth
      ? getBookmarkSetForUser(auth.user.id)
      : Promise.resolve({
          channels: new Set<string>(),
          studies: new Set<string>(),
        }),
  ]);

  const latestCapture = channels
    .map((c) => c.latest?.captured_at)
    .filter((s): s is string => Boolean(s))
    .sort()
    .at(-1);

  return (
    <div className="w-full px-5 py-14 sm:px-8 sm:py-20">
      <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
        Channels
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        <DeseretTitle text="LDS YouTube creators" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        {channels.length} channels covering Latter-day Saint related content —
        apologetics, scholarship, faith-promoting discussion, and critical
        content — searchable and sortable by subscribers, views, upload
        cadence, and channel age.
      </p>

      <div className="mt-5">
        <FreshnessBadge iso={latestCapture} size="md" prefix="Stats refreshed" />
      </div>

      <div className="mt-10">
        <ChannelsExplorer
          channels={channels}
          bookmarkedSet={bookmarks.channels}
          signedIn={Boolean(auth)}
        />
      </div>

      <aside className="mt-12 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--accent-soft)]/40 p-6 text-sm text-[color:var(--foreground)] sm:p-8">
        <p className="serif text-lg font-semibold tracking-tight">
          Know a creator we should track?
        </p>
        <p className="mt-2 leading-relaxed text-[color:var(--muted)]">
          Email{" "}
          <a
            href={mailto("Add a creator")}
            className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
          >
            {CONTACT_EMAIL}
          </a>{" "}
          with the channel name and a link, and I&apos;ll review it for the list.
        </p>
        <p className="mt-3 text-xs leading-relaxed text-[color:var(--muted)]">
          Channels with fewer than 1,000 subscribers aren&apos;t tracked — each
          channel adds to the daily YouTube API quota cost.
        </p>
      </aside>
    </div>
  );
}
