import type { Metadata } from "next";
import Link from "next/link";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";
import { getChannelByYouTubeId } from "@/lib/data";
import { fmtCompact, fmtNumber } from "@/lib/format";

export const metadata: Metadata = {
  title: "About",
  description:
    "About Latter-day Stats — a public hub for statistics, research, and creator data on the Latter-day Saint community.",
};

export const revalidate = 600;

export default async function AboutPage() {
  const myChannel = await getChannelByYouTubeId("UCT9gbDOQjYH8CQSG7-IMkTQ");

  return (
    <div className="mx-auto max-w-3xl px-5 py-16 sm:px-8 sm:py-24">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        About
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        A public hub for Latter-day Saint statistics &amp; research.
      </h1>

      <div className="prose-like mt-10 space-y-6 text-base leading-relaxed text-[color:var(--foreground)] sm:text-lg">
        <p>
          <span className="serif text-[color:var(--foreground)]">Latter-day Stats</span>{" "}
          gathers public statistics about the Latter-day Saint community —
          starting with YouTube creators who explore and defend the restored
          gospel of Jesus Christ, and academic research about the Church and
          its members.
        </p>
        <p>
          The goal is simple: make it easier for members, seekers, and
          researchers to see at a glance who is talking, how their reach is
          growing, and what scholarship is being published.
        </p>

        <h2 className="serif pt-4 text-2xl font-semibold tracking-tight text-[color:var(--foreground)]">
          About me
        </h2>
        <p>
          I&apos;m <strong>Samuel Baird</strong> — a Latter-day Saint and the
          person behind this site. I run a small YouTube channel,{" "}
          <em>I think therefore I Sam</em>, where I explore faith, history, and
          the questions members and seekers actually ask. Latter-day Stats grew
          out of wanting a clearer picture of the LDS conversation happening
          online and in the literature, and a place to point people who want
          something more concrete than vibes.
        </p>

        {myChannel && (
          <Link
            href={`/channels/${myChannel.slug}`}
            className="not-prose group flex items-center gap-4 rounded-2xl border border-[color:var(--border)] bg-white p-4 no-underline transition-colors hover:border-[color:var(--accent)]"
          >
            {myChannel.thumbnail_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={myChannel.thumbnail_url}
                alt=""
                className="h-16 w-16 shrink-0 rounded-full object-cover"
              />
            ) : (
              <div className="h-16 w-16 shrink-0 rounded-full bg-[color:var(--muted-soft)]" />
            )}
            <div className="min-w-0 flex-1">
              <div className="text-sm font-semibold text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
                {myChannel.name}
              </div>
              {myChannel.handle && (
                <div className="text-xs text-[color:var(--muted)]">
                  {myChannel.handle}
                </div>
              )}
              <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-[color:var(--muted)]">
                <span className="tabular-nums">
                  {fmtCompact(myChannel.latest?.subscribers)} subscribers
                </span>
                <span className="tabular-nums">
                  {fmtCompact(myChannel.latest?.total_views)} views
                </span>
                <span className="tabular-nums">
                  {fmtNumber(myChannel.latest?.video_count)} videos
                </span>
              </div>
            </div>
          </Link>
        )}

        <h2 className="serif pt-4 text-2xl font-semibold tracking-tight text-[color:var(--foreground)]">
          Sources
        </h2>
        <ul className="list-disc space-y-2 pl-5 text-[color:var(--muted)]">
          <li>
            Channel statistics come from the public YouTube Data API and are
            refreshed on a regular schedule.
          </li>
          <li>
            Studies are peer-reviewed or otherwise publicly available academic
            work, hosted with attribution.
          </li>
        </ul>

        <h2 className="serif pt-4 text-2xl font-semibold tracking-tight text-[color:var(--foreground)]">
          Contact
        </h2>
        <p className="text-[color:var(--muted)]">
          Suggestions, corrections, or a creator/study you&apos;d like to see
          added? Email{" "}
          <a
            href={mailto("Latter-day Stats")}
            className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
          >
            {CONTACT_EMAIL}
          </a>
          .
        </p>

        <h2 className="serif pt-4 text-2xl font-semibold tracking-tight text-[color:var(--foreground)]">
          Disclaimer
        </h2>
        <p className="text-[color:var(--muted)]">
          This project is independent and{" "}
          <strong className="text-[color:var(--foreground)]">
            not affiliated with The Church of Jesus Christ of Latter-day Saints
          </strong>
          . It aims to honor the Church&apos;s teachings and mission while
          presenting public data honestly.
        </p>

        <div className="mt-8 rounded-2xl border border-[color:var(--border)] bg-white p-5 text-sm">
          <p className="font-medium text-[color:var(--foreground)]">
            How stats are collected and channels are selected
          </p>
          <p className="mt-2 text-[color:var(--muted)]">
            Read the full explanation of our data sources, selection criteria, and editorial independence policy.
          </p>
          <Link
            href="/methodology"
            className="mt-3 inline-flex h-9 items-center rounded-full border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
          >
            Read methodology →
          </Link>
        </div>
      </div>
    </div>
  );
}
