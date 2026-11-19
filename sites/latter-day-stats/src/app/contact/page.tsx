import type { Metadata } from "next";
import { sectionOgImage } from "@/lib/og-images";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";

export const metadata: Metadata = {
  title: "Contact",
  description:
    "Get in touch, report an error, or suggest a channel or study for Latter-day Stats.",
  alternates: { canonical: "/contact" },
  ...sectionOgImage("contact", "Latter-day Stats — Contact"),
};

// Contact is by email only. There used to be a form here that saved to the
// `messages` table and emailed the owner; both are gone (no outgoing email on
// the free hosting plan). Links elsewhere on the site open a pre-addressed
// email with a subject instead (mailto() in src/lib/contact.ts).
const TOPICS: { subject: string; label: string; hint: string }[] = [
  {
    subject: "Correction",
    label: "Report an error",
    hint: "Include a link to the page and what looks wrong.",
  },
  {
    subject: "Channel suggestion",
    label: "Suggest a channel",
    hint: "The channel's YouTube link is enough.",
  },
  {
    subject: "Study suggestion",
    label: "Suggest a study",
    hint: "A citation or link to the study.",
  },
  {
    subject: "Bug report",
    label: "Report a bug",
    hint: "What you did, what you expected, and your browser.",
  },
  { subject: "Latter-day Stats", label: "Anything else", hint: "Questions, ideas, or a note." },
];

export default function ContactPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <header className="border-b border-[color:var(--border)] pb-10">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Contact
        </p>
        <h1 className="serif mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          <DeseretTitle text="Get in touch." />
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
          Spot an error? Have a channel or study to suggest? Want to chat about
          the project? Email{" "}
          <a
            href={mailto("Latter-day Stats")}
            className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
          >
            {CONTACT_EMAIL}
          </a>
          .
        </p>
      </header>

      <div className="mt-10 lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-14">
        <div className="max-w-xl">
          <section className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6">
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Email
            </h2>
            <a
              href={mailto("Latter-day Stats")}
              className="serif mt-3 block break-all text-2xl font-semibold tracking-tight text-[color:var(--accent)] underline-offset-4 hover:underline"
            >
              {CONTACT_EMAIL}
            </a>
            <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              Opens your mail app. Pick a topic below to start the email with a
              subject line.
            </p>
          </section>

          <ul className="mt-8 divide-y divide-[color:var(--border)] border-y border-[color:var(--border)]">
            {TOPICS.map((t) => (
              <li key={t.subject} className="py-4">
                <a
                  href={mailto(t.subject)}
                  className="text-base font-medium text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                >
                  {t.label} →
                </a>
                <p className="mt-1 text-sm text-[color:var(--muted)]">{t.hint}</p>
              </li>
            ))}
          </ul>
        </div>

        <aside className="mt-14 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-10">
          <div className="space-y-8">
            <section>
              <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
                What to expect
              </h2>
              <ul className="mt-3 space-y-3 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed text-[color:var(--muted)]">
                <li>
                  Email is read by the site editor, not a support team.
                  We usually respond within 48 hours.
                </li>
                <li>
                  Corrections are the fastest to act on — include a link to the
                  page and what looks wrong.
                </li>
                <li>
                  Channel and study suggestions are reviewed against the
                  published selection criteria before anything is added.
                </li>
              </ul>
            </section>

            <section className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 text-sm">
              <p className="font-medium text-[color:var(--foreground)]">
                Before you write
              </p>
              <p className="mt-2 text-[color:var(--muted)]">
                How channels are chosen, how stats are collected, and who runs
                the site are all documented already.
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                <Link
                  href="/methodology"
                  className="small-caps inline-flex h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
                >
                  Methodology →
                </Link>
                <Link
                  href="/about"
                  className="small-caps inline-flex h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
                >
                  About →
                </Link>
              </div>
            </section>
          </div>
        </aside>
      </div>
    </div>
  );
}
