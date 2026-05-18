import type { Metadata } from "next";
import { ChannelsExplorer } from "@/components/channels-explorer";
import { getCurrentUser } from "@/lib/auth";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";
import { getBookmarkSetForUser, getChannelsWithLatest } from "@/lib/data";

export const metadata: Metadata = {
  title: "Channels",
  description: "Latter-day Saint YouTube creators tracked by Latter-day Stats.",
};

export const revalidate = 600; // 10 minutes

export default async function ChannelsPage() {
  const [channels, auth] = await Promise.all([
    getChannelsWithLatest(),
    getCurrentUser(),
  ]);
  const bookmarks = auth
    ? await getBookmarkSetForUser(auth.user.id)
    : { channels: new Set<string>(), studies: new Set<string>() };

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
        <ChannelsExplorer
          channels={channels}
          bookmarkedSet={bookmarks.channels}
          signedIn={Boolean(auth)}
        />
      </div>

      <aside className="mt-12 rounded-2xl border border-[color:var(--border)] bg-[color:var(--accent-soft)]/40 p-6 text-sm text-[color:var(--foreground)] sm:p-8">
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
      </aside>
    </div>
  );
}
