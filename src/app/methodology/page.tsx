import type { Metadata } from "next";
import Link from "next/link";
import { CONTACT_EMAIL } from "@/lib/contact";

export const metadata: Metadata = {
  title: "Methodology",
  description:
    "How Latter-day Stats selects channels, collects statistics, and curates academic studies.",
};

export default function MethodologyPage() {
  return (
    <div className="mx-auto max-w-2xl px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href="/about"
        className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
      >
        ← About
      </Link>

      <p className="mt-6 text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Methodology
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        How this site works.
      </h1>
      <p className="mt-5 text-base leading-relaxed text-[color:var(--muted)]">
        Latter-day Stats is an independent project. It has no institutional
        affiliation with The Church of Jesus Christ of Latter-day Saints, BYU,
        or any content creator tracked on the site.
      </p>

      <Section title="Channel selection">
        <p>
          Channels are manually curated by the site editor based on relevance to
          the Latter-day Saint community. A channel must primarily discuss
          Latter-day Saint doctrine, culture, history, or criticism to be
          included.
        </p>
        <p className="mt-3">
          Inclusion does not constitute endorsement. Channels representing a
          range of perspectives — faith-affirming, critical, and institutional —
          are tracked. Each channel is tagged with a type (Religious,
          Apologetics, Critical, Institutional, etc.) to help visitors understand
          the source&apos;s perspective.
        </p>
        <p className="mt-3">
          To suggest a channel,{" "}
          <Link href="/contact?category=channel_suggestion" className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline">
            use the contact form
          </Link>
          .
        </p>
      </Section>

      <Section title="Statistics collection">
        <p>
          Subscriber counts, total views, and video counts are pulled from the
          YouTube Data API v3 using each channel&apos;s public channel ID. Each
          snapshot records the values at a single point in time.
        </p>
        <p className="mt-3">
          Stats are refreshed automatically once per day. Growth charts and the
          Risers &amp; Fallers widget are computed from the snapshot history — no
          estimates or projections are used.
        </p>
        <p className="mt-3">
          YouTube API data is public. No non-public data is accessed.
        </p>
      </Section>

      <Section title="Academic studies">
        <p>
          Studies are selected for relevance to Latter-day Saint demographics,
          behavior, belief, or religious practice. Priority is given to
          peer-reviewed work published in academic journals, though significant
          institutional reports and working papers may also be included.
        </p>
        <p className="mt-3">
          Studies flagged with a methodological concern badge have been reviewed
          and found to have significant limitations — small sample sizes,
          non-representative sampling, or conclusions that exceed what the data
          support. These are kept in the library with the flag visible rather
          than removed, so visitors can make their own informed judgement.
        </p>
        <p className="mt-3">
          To suggest a study,{" "}
          <Link href="/contact?category=study_suggestion" className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline">
            use the contact form
          </Link>
          .
        </p>
      </Section>

      <Section title="Independence & conflicts of interest">
        <p>
          This site is self-funded and does not accept payment from creators or
          institutions for inclusion, placement, or favorable coverage. Featured
          slots on the homepage are editorial choices, not paid placements.
        </p>
        <p className="mt-3">
          The editor is a member of The Church of Jesus Christ of Latter-day
          Saints. This is disclosed so visitors can weigh it appropriately.
          The goal is accurate, fair representation of the full range of voices
          in the community.
        </p>
      </Section>

      <Section title="Corrections">
        <p>
          Errors in channel metadata, stats attribution, or study summaries can
          be reported via the{" "}
          <Link href="/contact?category=correction" className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline">
            contact form
          </Link>{" "}
          or by emailing{" "}
          <a
            href={`mailto:${CONTACT_EMAIL}`}
            className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
          >
            {CONTACT_EMAIL}
          </a>
          . Corrections are made promptly.
        </p>
      </Section>
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="mt-12">
      <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        {title}
      </h2>
      <div className="mt-4 text-base leading-relaxed text-[color:var(--foreground)]">
        {children}
      </div>
    </section>
  );
}
