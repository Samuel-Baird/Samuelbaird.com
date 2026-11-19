import type { Metadata } from "next";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";

export const metadata: Metadata = {
  title: "Accessibility",
  description: "Latter-day Stats' commitment to an accessible site.",
  alternates: { canonical: "/accessibility" },
};

export default function AccessibilityPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <header className="border-b border-[color:var(--border)] pb-10">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Accessibility
        </p>
        <h1 className="serif mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          <DeseretTitle text="Accessibility statement." />
        </h1>
        <p className="mt-5 max-w-2xl text-sm text-[color:var(--muted)]">
          Last updated August 10, 2026.
        </p>
      </header>

      <div className="mt-10 max-w-2xl space-y-6 text-base leading-relaxed text-[color:var(--foreground)]">
        <p>
          Latter-day Stats aims to be usable by everyone, including people
          using screen readers, keyboard-only navigation, or browser
          zoom/reflow. We build against the Web Content Accessibility
          Guidelines (WCAG) 2.1, targeting level AA, as a working standard
          rather than a claim of full compliance.
        </p>

        <p>
          Concretely, that means: semantic headings and landmarks, visible
          focus states, sufficient color contrast in both light and dark
          themes, alt text on meaningful images, and motion that respects
          your system&apos;s reduced-motion preference.
        </p>

        <h2 className="serif pt-4 text-2xl font-semibold tracking-tight">
          Known limitations
        </h2>
        <p className="text-[color:var(--muted)]">
          This site hasn&apos;t had a formal accessibility audit. Some
          interactive widgets — chart tooltips, the command palette, data
          tables on wide screens — may not fully support every assistive
          technology yet. We&apos;re fixing issues as they&apos;re found
          rather than claiming a finished state.
        </p>

        <h2 className="serif pt-4 text-2xl font-semibold tracking-tight">
          Feedback
        </h2>
        <p className="text-[color:var(--muted)]">
          If you hit a barrier using the site, please tell us — include the
          page and what happened. Use the{" "}
          <Link
            href="/contact"
            className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
          >
            contact page
          </Link>{" "}
          or email{" "}
          <a
            href={mailto("Accessibility feedback")}
            className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
          >
            {CONTACT_EMAIL}
          </a>
          . We usually respond within 48 hours.
        </p>
      </div>
    </div>
  );
}
