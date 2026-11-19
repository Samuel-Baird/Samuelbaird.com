import type { Metadata } from "next";
import { sectionOgImage } from "@/lib/og-images";
import Image from "next/image";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";
import { getChannelByYouTubeId } from "@/lib/data";
import { fmtCompact, fmtNumber } from "@/lib/format";
import samuelPhoto from "./samuel-baird.jpg";

export const metadata: Metadata = {
  title: "About",
  description:
    "About Latter-day Stats — a public hub for statistics, research, and creator data on the Latter-day Saint community.",
  alternates: { canonical: "/about" },
  ...sectionOgImage("about", "Latter-day Stats — About"),
};

export const revalidate = 3600;

export default async function AboutPage() {
  // The rest of the page has nothing to do with this channel lookup — a data
  // hiccup here shouldn't take down the whole About page, just the optional
  // "author channel" card.
  let myChannel: Awaited<ReturnType<typeof getChannelByYouTubeId>> = null;
  try {
    myChannel = await getChannelByYouTubeId("UCT9gbDOQjYH8CQSG7-IMkTQ");
  } catch (error) {
    console.error("about page: author channel lookup failed:", error);
  }

  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <header className="border-b border-[color:var(--border)] pb-10">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          About
        </p>
        <h1 className="serif mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          <DeseretTitle text="A public hub for Latter-day Saint statistics & research." />
        </h1>
      </header>

      <div className="mt-10 lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-14">
        <div className="prose-like drop-cap-lead max-w-2xl space-y-6 text-base leading-relaxed text-[color:var(--foreground)] sm:text-lg">
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
          <Image
            src={samuelPhoto}
            alt="Samuel Baird"
            className="w-48 rounded-[var(--radius)] border border-[color:var(--border)] object-cover sm:w-56"
            placeholder="blur"
          />
          <p>
            I&apos;m <strong>Samuel Baird</strong> — a Latter-day Saint and the
            person behind this site. I run a small YouTube channel,{" "}
            <em>I think therefore I Sam</em>, where I explore faith, history, and
            the questions members and seekers actually ask. I&apos;m interested
            in learning more about my own faith tradition, as well as comparing
            and contrasting other perspectives. As someone interested in the
            data, I wanted to make this site for my own interest as well as to
            share with others.
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
        </div>

        <aside className="mt-14 space-y-8 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-10">
          {myChannel && (
            <section>
              <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
                The author
              </h2>
              <Link
                href={`/channels/${myChannel.slug}`}
                className="group mt-3 flex items-center gap-4 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-4 no-underline transition-colors hover:border-[color:var(--accent)]"
              >
                {myChannel.thumbnail_url ? (
                  <Image
                    src={myChannel.thumbnail_url}
                    alt=""
                    width={56}
                    height={56}
                    className="h-14 w-14 shrink-0 rounded-full object-cover"
                  />
                ) : (
                  <div className="h-14 w-14 shrink-0 rounded-full bg-[color:var(--muted-soft)]" />
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
                  <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-xs text-[color:var(--muted)]">
                    <span className="tabular-nums">
                      {fmtCompact(myChannel.latest?.subscribers)} subs
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
            </section>
          )}

          <section>
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Sources
            </h2>
            <ul className="mt-3 space-y-3 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              <li>
                Channel statistics come from the public YouTube Data API and are
                refreshed on a regular schedule.
              </li>
              <li>
                Studies are peer-reviewed or otherwise publicly available
                academic work, hosted with attribution.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Contact
            </h2>
            <p className="mt-3 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              Suggestions, corrections, or a creator/study you&apos;d like to
              see added? Email{" "}
              <a
                href={mailto("Latter-day Stats")}
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                {CONTACT_EMAIL}
              </a>
              .
            </p>
          </section>

          <section className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 text-sm">
            <p className="font-medium text-[color:var(--foreground)]">
              How stats are collected and channels are selected
            </p>
            <p className="mt-2 text-[color:var(--muted)]">
              Read the full explanation of our data sources, selection criteria,
              and editorial independence policy.
            </p>
            <Link
              href="/methodology"
              className="mt-3 inline-flex h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-xs small-caps font-medium hover:bg-[color:var(--muted-soft)]"
            >
              Read methodology →
            </Link>
          </section>
        </aside>
      </div>
    </div>
  );
}
