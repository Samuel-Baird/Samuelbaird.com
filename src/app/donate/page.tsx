import type { Metadata } from "next";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { DonateButtons } from "@/components/donate-buttons";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";
import { AMAZON_WISHLIST_URL, PAYPAL_URL, VENMO_URL } from "@/lib/donate-links";

export const metadata: Metadata = {
  title: "Donate",
  description:
    "Support Latter-day Stats — donations go toward hosting and keeping the site free and ad-free.",
  alternates: { canonical: "/donate" },
};


export default function DonatePage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <header className="border-b border-[color:var(--border)] pb-10">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Donate
        </p>
        <h1 className="serif mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          <DeseretTitle text="Help keep the site running." />
        </h1>
      </header>

      <div className="mt-10 lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-14">
        <div className="max-w-2xl space-y-6 text-base leading-relaxed text-[color:var(--foreground)] sm:text-lg">
          <p>
            Latter-day Stats is free, independent, and ad-free. Donations go
            directly toward hosting and keeping it that way. Anything helps
            and is appreciated.
          </p>
          <section>
            <DonateButtons paypalUrl={PAYPAL_URL} venmoUrl={VENMO_URL} />
            <p className="mt-3 text-sm text-[color:var(--muted)]">
              You&apos;ll be taken to {PAYPAL_URL.replace("https://", "")} or{" "}
              {VENMO_URL.replace("https://", "")} to complete the donation.
            </p>
          </section>
          <section>
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Or send a book
            </h2>
            <p className="mt-3">
              Prefer to give something tangible? My Amazon wishlist is mostly
              books and research materials.
            </p>
            <a
              href={AMAZON_WISHLIST_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-flex h-11 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-6 text-sm font-medium text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
            >
              View Amazon wishlist →
            </a>
            <p className="mt-3 text-sm text-[color:var(--muted)]">
              Opens my wishlist on amazon.com. Amazon handles the purchase and
              shipping.
            </p>
          </section>
        </div>

        <aside className="mt-14 space-y-8 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-10">
          <section>
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Where it goes
            </h2>
            <ul className="mt-3 space-y-3 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              <li>Hosting and infrastructure costs.</li>
              <li>Books and research materials from the wishlist.</li>
              <li>Keeping the site free, public, and without ads.</li>
            </ul>
          </section>

          <section>
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Questions
            </h2>
            <p className="mt-3 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              Email{" "}
              <a
                href={mailto("Latter-day Stats")}
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                {CONTACT_EMAIL}
              </a>{" "}
              or visit the{" "}
              <Link
                href="/contact"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                contact page
              </Link>
              .
            </p>
          </section>
        </aside>
      </div>
    </div>
  );
}
