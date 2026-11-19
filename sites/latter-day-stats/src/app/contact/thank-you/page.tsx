import type { Metadata } from "next";
import { sectionOgImage } from "@/lib/og-images";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";

export const metadata: Metadata = {
  title: "Message sent",
  description: "Your message to Latter-day Stats was received.",
  robots: { index: false, follow: true },
  ...sectionOgImage("contact", "Latter-day Stats — Contact"),
};

export default function ContactThankYouPage() {
  return (
    <div className="mx-auto max-w-2xl px-5 py-16 text-center sm:px-8 sm:py-24">
      <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
        Message sent
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="Thanks — got it." />
      </h1>
      <p className="mt-5 text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        Your message was received. Messages are read by the site editor, not
        a support team — we usually respond within 48 hours if a reply is
        needed.
      </p>
      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <Link
          href="/"
          className="inline-flex h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90"
        >
          Back to home
        </Link>
        <Link
          href="/contact"
          className="inline-flex h-11 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-6 text-sm font-medium text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
        >
          Send another message
        </Link>
      </div>
      <p className="mt-8 text-sm text-[color:var(--muted)]">
        Prefer email? Write to{" "}
        <a
          href={mailto("Latter-day Stats")}
          className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
        >
          {CONTACT_EMAIL}
        </a>
        .
      </p>
    </div>
  );
}
