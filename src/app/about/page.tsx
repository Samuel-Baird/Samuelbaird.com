import type { Metadata } from "next";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";

export const metadata: Metadata = {
  title: "About",
  description:
    "About Latter-day Stats — a public hub for statistics, research, and creator data on the Latter-day Saint community.",
};

export default function AboutPage() {
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
      </div>
    </div>
  );
}
