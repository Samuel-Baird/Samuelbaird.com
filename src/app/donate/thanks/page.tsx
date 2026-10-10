import type { Metadata } from "next";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";
import { getStripe, isStripeConfigured, PREMIUM_MIN_CENTS } from "@/lib/stripe";

export const metadata: Metadata = {
  title: "Thank you",
  robots: { index: false },
};

export const dynamic = "force-dynamic";

type Summary = {
  amountCents: number;
  monthly: boolean;
  email: string | null;
  paid: boolean;
};

async function getSummary(sessionId: string | undefined): Promise<Summary | null> {
  if (!sessionId || !isStripeConfigured()) return null;
  try {
    const session = await getStripe().checkout.sessions.retrieve(sessionId);
    return {
      amountCents: session.amount_total ?? 0,
      monthly: session.mode === "subscription",
      email: session.metadata?.premium_email ?? session.customer_details?.email ?? null,
      paid: session.payment_status === "paid",
    };
  } catch {
    return null;
  }
}

export default async function DonateThanksPage({
  searchParams,
}: {
  searchParams: Promise<{ session_id?: string }>;
}) {
  const { session_id } = await searchParams;
  const summary = await getSummary(session_id);
  const premium = summary !== null && summary.amountCents >= PREMIUM_MIN_CENTS;

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
          {summary
            ? `Your ${summary.monthly ? "monthly " : ""}donation of $${(summary.amountCents / 100).toFixed(2)} helps make this website possible.`
            : "Your contribution helps make this website possible."}{" "}
          A receipt is on its way to your inbox.
        </p>

        {premium && summary ? (
          <div className="rounded-[var(--radius)] border border-[color:var(--honey)]/40 bg-[color:var(--honey-soft)] p-5 text-sm sm:text-base">
            <p className="font-medium">Premium is unlocked.</p>
            <p className="mt-2 leading-relaxed">
              {summary.paid
                ? "It's been added to"
                : "It will be added once your payment clears, to"}{" "}
              {summary.email ? <strong>{summary.email}</strong> : "your account"}. Sign
              in with that email to use it — it may take a minute to show up.
            </p>
            <Link
              href="/premium"
              className="mt-4 inline-flex h-11 items-center rounded-[var(--radius)] bg-[color:var(--honey)] px-5 text-sm font-medium text-white hover:opacity-90"
            >
              Go to premium →
            </Link>
          </div>
        ) : null}

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
