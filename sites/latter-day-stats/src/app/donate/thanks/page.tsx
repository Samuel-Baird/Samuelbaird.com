import type { Metadata } from "next";
import { sectionOgImage } from "@/lib/og-images";
import { DeseretTitle } from "@/components/deseret-title";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";

export const metadata: Metadata = {
  title: "Thank you",
  robots: { index: false },
  ...sectionOgImage("donate", "Latter-day Stats — Donate"),
};

// Plain thank-you page. It used to read the Stripe Checkout session for the
// amount; Stripe was removed (PayPal/Venmo donations happen off-site).
export default function DonateThanksPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <header className="border-b border-[color:var(--border)] pb-10">
        <p className="small-caps text-xs font-medium text-[color:var(--honey)]">
          Donate
        </p>
        <h1 className="serif mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight text-[color:var(--honey)] sm:text-5xl">
          <DeseretTitle text="Thank you!" />
        </h1>
      </header>

      <div className="mt-10 max-w-2xl space-y-6 text-base leading-relaxed sm:text-lg">
        <p>
          Your contribution helps make this website possible.
        </p>

        <p className="text-sm text-[color:var(--muted)]">
          Something not right? Email{" "}
          <a
            href={mailto("Donation")}
            className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
          >
            {CONTACT_EMAIL}
          </a>
          .
        </p>
      </div>
    </div>
  );
}
