import "server-only";

import Stripe from "stripe";

// One-time or monthly donations of at least this much grant premium
// automatically (via the webhook at /api/stripe/webhook). Mirrors the "$5+
// once" rule the site has always advertised.
export const PREMIUM_MIN_CENTS = 500;
export const MIN_DONATION_CENTS = 100;
export const MAX_DONATION_CENTS = 1_000_000;

let client: Stripe | null = null;

// Lazily constructed so builds and pages that never touch Stripe don't need
// STRIPE_SECRET_KEY set. Uses the SDK's pinned API version.
export function getStripe(): Stripe {
  if (client) return client;
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error("STRIPE_SECRET_KEY is not set");
  client = new Stripe(key);
  return client;
}

export function isStripeConfigured(): boolean {
  return Boolean(process.env.STRIPE_SECRET_KEY);
}
