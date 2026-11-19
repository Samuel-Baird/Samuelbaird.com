import type { Metadata } from "next";
import { sectionOgImage } from "@/lib/og-images";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { CONTACT_EMAIL } from "@/lib/contact";

export const metadata: Metadata = {
  title: "Methodology",
  description:
    "How Latter-day Stats selects channels, collects statistics, and curates academic studies.",
  alternates: { canonical: "/methodology" },
  ...sectionOgImage("methodology", "Latter-day Stats — Methodology"),
};

const SECTIONS: { id: string; title: string }[] = [
  { id: "channel-selection", title: "Channel selection" },
  { id: "statistics-collection", title: "Statistics collection" },
  { id: "academic-studies", title: "Academic studies" },
  { id: "independence", title: "Independence & conflicts of interest" },
  { id: "corrections", title: "Corrections" },
];

export default function MethodologyPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <header className="border-b border-[color:var(--border)] pb-10">
        <Link
          href="/about"
          className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
        >
          ← About
        </Link>

        <p className="small-caps mt-6 text-xs font-medium text-[color:var(--accent)]">
          Methodology
        </p>
        <h1 className="serif mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          <DeseretTitle text="How this site works." />
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
          Latter-day Stats is an independent project. It has no institutional
          affiliation with The Church of Jesus Christ of Latter-day Saints, BYU,
          or any content creator tracked on the site.
        </p>
      </header>

      <div className="mt-10 lg:grid lg:grid-cols-[minmax(0,1fr)_18rem] lg:gap-14">
        <div className="max-w-2xl">
          <Section id="channel-selection" title="Channel selection">
            <p>
              Channels are manually curated by the site editor based on
              relevance to the Latter-day Saint community. To be included, a
              channel must discuss or revolve around Latter-day Saint doctrine,
              culture, music, history, or criticism. Channels that talk
              significantly about the Church even if it isn&apos;t their main
              focus — for example, broader Christian apologetics channels that
              regularly engage with Latter-day Saint topics — may also be
              included.
            </p>
            <p className="mt-3">
              Channels run by members whose content has nothing to do with the
              Church are <strong>not</strong> included — membership alone is not
              the criterion. The content itself has to engage with Latter-day
              Saint topics in a meaningful way.
            </p>
            <p className="mt-3">
              Inclusion does not constitute endorsement. Channels representing a
              range of perspectives — faith-affirming, critical, and
              institutional — are tracked. Each channel is tagged with a type
              (Religious, Apologetics, Critical, Institutional, etc.) to help
              visitors understand the source&apos;s perspective.
            </p>
            <p className="mt-3">
              Channels with fewer than 1,000 YouTube subscribers are not
              tracked. Each channel adds to the daily YouTube Data API quota
              cost, so the catalog is limited to channels with enough audience
              for the statistics to be meaningful.
            </p>
            <p className="mt-3">
              To suggest a channel,{" "}
              <Link href="/contact?category=channel_suggestion" className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline">
                use the contact form
              </Link>
              .
            </p>
          </Section>

          <Section id="statistics-collection" title="Statistics collection">
            <p>
              Subscriber counts, total views, and video counts are pulled from
              the YouTube Data API v3 using each channel&apos;s public channel
              ID. Each snapshot records the values at a single point in time.
            </p>
            <p className="mt-3">
              Stats are refreshed automatically once per day. Growth charts are
              computed from the snapshot history — no estimates or projections are used.
            </p>
            <p className="mt-3">
              YouTube API data is public. No non-public data is accessed.
            </p>
          </Section>

          <Section id="academic-studies" title="Academic studies">
            <p>
              Studies are selected for relevance to Latter-day Saint
              demographics, behavior, belief, or religious practice. Priority is
              given to peer-reviewed work published in academic journals, though
              significant institutional reports and working papers may also be
              included.
            </p>
            <p className="mt-3">
              Studies flagged with a methodological concern badge have been
              reviewed and found to have significant limitations — small sample
              sizes, non-representative sampling, or conclusions that exceed
              what the data support. These are kept in the library with the flag
              visible rather than removed, so visitors can make their own
              informed judgement.
            </p>
            <p className="mt-3">
              To suggest a study,{" "}
              <Link href="/contact?category=study_suggestion" className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline">
                use the contact form
              </Link>
              .
            </p>
          </Section>

          <Section id="independence" title="Independence & conflicts of interest">
            <p>
              This site is self-funded and does not accept payment from creators
              or institutions for inclusion, placement, or favorable coverage.
              Featured slots on the homepage are editorial choices, not paid
              placements.
            </p>
            <p className="mt-3">
              The editor is a member of The Church of Jesus Christ of Latter-day
              Saints. This is disclosed so visitors can weigh it appropriately.
              The goal is accurate, fair representation of the full range of
              voices in the community.
            </p>
          </Section>

          <Section id="corrections" title="Corrections">
            <p>
              Errors in channel metadata, stats attribution, or study summaries
              can be reported via the{" "}
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

        <aside className="mt-14 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-8">
          <div className="lg:sticky lg:top-24">
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              On this page
            </h2>
            <ul className="mt-3 space-y-3 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed">
              {SECTIONS.map((section) => (
                <li key={section.id}>
                  <a
                    href={`#${section.id}`}
                    className="text-[color:var(--muted)] hover:text-[color:var(--accent)]"
                  >
                    {section.title}
                  </a>
                </li>
              ))}
            </ul>

            <h2 className="small-caps mt-8 text-xs font-medium text-[color:var(--muted)]">
              Questions or corrections
            </h2>
            <p className="mt-3 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              Something here look wrong? Write to{" "}
              <a
                href={`mailto:${CONTACT_EMAIL}`}
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                {CONTACT_EMAIL}
              </a>{" "}
              or{" "}
              <Link
                href="/contact?category=correction"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                use the contact form
              </Link>
              .
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}

function Section({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="mt-12 scroll-mt-24 first:mt-0">
      <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
        {title}
      </h2>
      <div className="mt-4 text-base leading-relaxed text-[color:var(--foreground)]">
        {children}
      </div>
    </section>
  );
}
