"use server";

import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import { SITE_URL } from "@/lib/site";
import {
  getStripe,
  MAX_DONATION_CENTS,
  MIN_DONATION_CENTS,
} from "@/lib/stripe";

export type DonateState = { error: string | null };

// Builds a Stripe Checkout session for the amount the donor picked and sends
// them to Stripe's hosted page. Premium is granted later by the webhook, not
// here, so nothing is trusted until Stripe confirms the payment.
export async function startDonationCheckout(
  _prev: DonateState,
  formData: FormData,
): Promise<DonateState> {
  const dollars = Number(formData.get("amount"));
  const cents = Math.round(dollars * 100);
  if (
    !Number.isFinite(cents) ||
    cents < MIN_DONATION_CENTS ||
    cents > MAX_DONATION_CENTS
  ) {
    return { error: "Enter an amount between $1 and $10,000." };
  }
  const monthly = formData.get("frequency") === "monthly";

  const auth = await getCurrentUser();
  const email = (auth?.profile?.email ?? auth?.user.email ?? "")
    .trim()
    .toLowerCase();

  // Return to whichever deployment the donor came from (localhost, a Vercel
  // preview, or production) rather than always bouncing to SITE_URL.
  const origin = (await headers()).get("origin") ?? SITE_URL;

  const productData = {
    name: monthly
      ? "Monthly donation to Latter-day Stats"
      : "Donation to Latter-day Stats",
  };

  let url: string | null;
  try {
    const session = await getStripe().checkout.sessions.create({
      mode: monthly ? "subscription" : "payment",
      line_items: [
        {
          quantity: 1,
          price_data: {
            currency: "usd",
            unit_amount: cents,
            product_data: productData,
            ...(monthly ? { recurring: { interval: "month" as const } } : {}),
          },
        },
      ],
      ...(monthly ? {} : { submit_type: "donate" as const }),
      ...(email ? { customer_email: email } : {}),
      client_reference_id: auth?.user.id,
      // The account premium should land on. Falls back to the email typed
      // into Checkout when the donor isn't signed in.
      metadata: email ? { premium_email: email } : {},
      success_url: `${origin}/donate/thanks?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/donate`,
    });
    url = session.url;
  } catch (error) {
    console.error("stripe checkout create failed:", error);
    url = null;
  }

  if (!url) {
    return { error: "Couldn't start checkout. Please try again." };
  }
  redirect(url);
}
