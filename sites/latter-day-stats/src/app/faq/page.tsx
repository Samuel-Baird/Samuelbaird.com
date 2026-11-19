import type { Metadata } from "next";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";

export const metadata: Metadata = {
  title: "FAQ",
  description: "Frequently asked questions about Latter-day Stats.",
  alternates: { canonical: "/faq" },
};

type Faq = {
  question: string;
  // Plain-text answer for the FAQPage JSON-LD; the on-page answer below adds
  // real links over the same text.
  answerText: string;
  answer: React.ReactNode;
};

const FAQS: Faq[] = [
  {
    question: "Is Latter-day Stats affiliated with the Church?",
    answerText:
      "No. Latter-day Stats is an independent project with no institutional affiliation with The Church of Jesus Christ of Latter-day Saints, BYU, or any creator tracked on the site. The editor is a member of the Church, which is disclosed on the about page so visitors can weigh it appropriately.",
    answer: (
      <p>
        No. Latter-day Stats is an independent project with no institutional
        affiliation with The Church of Jesus Christ of Latter-day Saints, BYU,
        or any creator tracked on the site. The editor is a member of the
        Church, which is disclosed on the{" "}
        <Link
          href="/about"
          className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
        >
          about page
        </Link>{" "}
        so visitors can weigh it appropriately.
      </p>
    ),
  },
  {
    question: "Where does the data come from?",
    answerText:
      "Channel statistics come from the public YouTube Data API v3, pulled once per day. Studies are peer-reviewed research, institutional reports, or working papers, hosted with attribution and a link back to the original source. See the methodology page for the full breakdown.",
    answer: (
      <p>
        Channel statistics come from the public YouTube Data API v3, pulled
        once per day. Studies are peer-reviewed research, institutional
        reports, or working papers, hosted with attribution and a link back
        to the original source. See the{" "}
        <Link
          href="/methodology"
          className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
        >
          methodology page
        </Link>{" "}
        for the full breakdown.
      </p>
    ),
  },
  {
    question: "How often are channel statistics updated?",
    answerText:
      "Subscriber counts, total views, and video counts refresh automatically once a day. Growth charts are computed from that snapshot history — no estimates or projections.",
    answer: (
      <p>
        Subscriber counts, total views, and video counts refresh
        automatically once a day. Growth charts are computed from that snapshot
        history — no estimates or
        projections.
      </p>
    ),
  },
  {
    question: "How are channels and studies selected?",
    answerText:
      "Channels are manually curated for relevance to the Latter-day Saint community and must have at least 1,000 subscribers. Inclusion covers the full range of perspectives — faith-affirming, critical, and institutional — and does not constitute endorsement. Studies are selected for relevance to Latter-day Saint demographics, behavior, belief, or religious practice, with priority given to peer-reviewed work. Full criteria are on the methodology page.",
    answer: (
      <p>
        Channels are manually curated for relevance to the Latter-day Saint
        community and must have at least 1,000 subscribers. Inclusion covers
        the full range of perspectives — faith-affirming, critical, and
        institutional — and does not constitute endorsement. Studies are
        selected for relevance to Latter-day Saint demographics, behavior,
        belief, or religious practice, with priority given to peer-reviewed
        work. Full criteria are on the{" "}
        <Link
          href="/methodology"
          className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
        >
          methodology page
        </Link>
        .
      </p>
    ),
  },
  {
    question: "How can I suggest a channel or study, or report an error?",
    answerText: `Email ${CONTACT_EMAIL} (or see the contact page). We usually respond within 48 hours.`,
    answer: (
      <p>
        Use the{" "}
        <Link
          href="/contact"
          className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
        >
          contact page
        </Link>{" "}
        or email{" "}
        <a
          href={mailto("Latter-day Stats")}
          className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
        >
          {CONTACT_EMAIL}
        </a>
        . We usually respond within 48 hours.
      </p>
    ),
  },
];

const FAQ_JSON_LD = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: FAQS.map((f) => ({
    "@type": "Question",
    name: f.question,
    acceptedAnswer: { "@type": "Answer", text: f.answerText },
  })),
};

export default function FaqPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(FAQ_JSON_LD) }}
      />
      <header className="border-b border-[color:var(--border)] pb-10">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          FAQ
        </p>
        <h1 className="serif mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          <DeseretTitle text="Frequently asked questions." />
        </h1>
      </header>

      <div className="mt-10 max-w-2xl divide-y divide-[color:var(--border)] border-t border-[color:var(--border)]">
        {FAQS.map((f) => (
          <details key={f.question} className="group py-5">
            <summary className="serif flex cursor-pointer list-none items-center justify-between gap-4 text-lg font-semibold tracking-tight marker:content-none">
              {f.question}
              <span
                aria-hidden="true"
                className="shrink-0 text-[color:var(--muted)] transition-transform group-open:rotate-45"
              >
                +
              </span>
            </summary>
            <div className="mt-3 text-base leading-relaxed text-[color:var(--muted)]">
              {f.answer}
            </div>
          </details>
        ))}
      </div>

      <p className="mt-10 max-w-2xl text-sm text-[color:var(--muted)]">
        Question not answered here? Use the{" "}
        <Link
          href="/contact"
          className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
        >
          contact page
        </Link>
        .
      </p>
    </div>
  );
}
