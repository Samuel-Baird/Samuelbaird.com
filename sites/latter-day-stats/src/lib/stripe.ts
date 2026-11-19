import "server-only";

import Stripe from "stripe";

// One-time or monthly donations of at least this much grant premium
// automatically (via the webhook at /api/stripe/webhook). Mirrors the "$5+
// once" rule the site has always advertised.
export const PREMIUM_MIN_CENTS = 500;
// Several sites share this Stripe account, so every Checkout session carries `metadata.site`
// and the webhook acts only on its own. Never reuse this value on another site.
export const SITE_TAG = "latter-day-stats";

export function isOurSession(metadata: Record<string, string> | null | undefined): boolean {
  const site = metadata?.site;
  // Sessions created before tagging have no site, and no application_id (the other site's marker).
  return site ? site === SITE_TAG : !metadata?.application_id;
}
export const MIN_DONATION_CENTS = 100;
export const MAX_DONATION_CENTS = 1_000_000;

let client: Stripe | null = null;

// Lazily constructed so builds and pages that never touch Stripe don't need
// STRIPE_SECRET_KEY set. Uses the SDK's pinned API version. The fetch HTTP
// client works on both Node and Cloudflare Workers (workerd has no node:https
// agent the default client wants).
export function getStripe(): Stripe {
  if (client) return client;
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error("STRIPE_SECRET_KEY is not set");
  client = new Stripe(key, { httpClient: Stripe.createFetchHttpClient() });
  return client;
}

// Web Crypto provider for webhook signature checks. Must be used with the
// async constructEventAsync (Web Crypto has no synchronous HMAC).
export const stripeCryptoProvider = Stripe.createSubtleCryptoProvider();

export function isStripeConfigured(): boolean {
  return Boolean(process.env.STRIPE_SECRET_KEY);
}
