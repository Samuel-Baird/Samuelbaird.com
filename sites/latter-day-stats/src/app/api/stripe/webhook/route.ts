import { revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";
import type Stripe from "stripe";
import { getStripe, isOurSession, PREMIUM_MIN_CENTS, stripeCryptoProvider } from "@/lib/stripe";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

// Stripe webhook. Configure the endpoint (dashboard, or `stripe listen
// --forward-to localhost:3000/api/stripe/webhook` locally) to send
// checkout.session.completed, checkout.session.async_payment_succeeded and charge.refunded.
// Records each paid donation and, at $5+, adds the donor to premium_users; a full refund of a
// one-time donation undoes that (see refundDonation).
export async function POST(req: NextRequest) {
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  const signature = req.headers.get("stripe-signature");
  if (!secret || !signature) {
    return NextResponse.json({ error: "Not configured" }, { status: 400 });
  }

  let event: Stripe.Event;
  try {
    // Signature is computed over the raw body, so read it as text. Async +
    // Web Crypto so it runs on Cloudflare Workers as well as Node.
    event = await getStripe().webhooks.constructEventAsync(
      await req.text(),
      signature,
      secret,
      undefined,
      stripeCryptoProvider,
    );
  } catch (error) {
    console.error("stripe webhook signature check failed:", error);
    return NextResponse.json({ error: "Bad signature" }, { status: 400 });
  }

  if (
    event.type === "checkout.session.completed" ||
    event.type === "checkout.session.async_payment_succeeded"
  ) {
    const session = event.data.object;
    // Bank-debit style methods complete as "unpaid" and settle later via
    // async_payment_succeeded; only act once money has actually moved.
    // This Stripe account is shared with other sites; skip their checkouts.
    if (session.payment_status === "paid" && isOurSession(session.metadata)) {
      await recordDonation(session);
    }
  }

  if (event.type === "charge.refunded") {
    await refundDonation(event.data.object);
  }

  return NextResponse.json({ received: true });
}

async function recordDonation(session: Stripe.Checkout.Session) {
  const email = (
    session.metadata?.premium_email ??
    session.customer_details?.email ??
    ""
  )
    .trim()
    .toLowerCase();
  const amount = session.amount_total ?? 0;
  const supabase = createSupabaseServiceClient();

  // Idempotent on the session id: Stripe retries deliveries, and both
  // completed + async_payment_succeeded can arrive for one session.
  const { error: donationError } = await supabase.from("donations").upsert(
    {
      stripe_session_id: session.id,
      email: email || null,
      user_id: session.client_reference_id,
      amount_cents: amount,
      currency: session.currency ?? "usd",
      recurring: session.mode === "subscription",
      stripe_customer_id:
        typeof session.customer === "string" ? session.customer : null,
      // One-time donations only; lets a refund be matched back to this row.
      stripe_payment_intent_id:
        typeof session.payment_intent === "string" ? session.payment_intent : null,
    },
    { onConflict: "stripe_session_id", ignoreDuplicates: true },
  );
  // Throwing returns a 500, so Stripe retries the delivery later.
  if (donationError) throw donationError;

  if (email && amount >= PREMIUM_MIN_CENTS) {
    // Create the row only if absent, and mark it as site-granted so a later refund may
    // revoke it. A row that already exists (granted by hand) is left exactly as it is.
    const { data: existing, error: lookupError } = await supabase
      .from("premium_users")
      .select("id")
      .eq("email", email)
      .maybeSingle();
    if (lookupError) throw lookupError;
    if (!existing) {
      const { error } = await supabase.from("premium_users").insert({
        email,
        name: session.customer_details?.name ?? null,
        stripe_granted: true,
      });
      if (error) throw error;
    }
    revalidateTag("premium-users", { expire: 0 });
  }
}

/**
 * A full refund of a one-time donation removes the premium access it granted, unless the
 * donor has another unrefunded $5+ donation or the access was granted by hand. Partial
 * refunds are ignored. Monthly donations aren't matched (no single payment intent per row),
 * so refunding one never touches premium; remove it by hand if you want it gone.
 */
async function refundDonation(charge: Stripe.Charge) {
  if (!charge.refunded) return;
  const paymentIntent =
    typeof charge.payment_intent === "string" ? charge.payment_intent : null;
  if (!paymentIntent) return;

  const supabase = createSupabaseServiceClient();
  const { data, error } = await supabase
    .from("donations")
    .update({ refunded_at: new Date().toISOString() })
    .eq("stripe_payment_intent_id", paymentIntent)
    .is("refunded_at", null)
    .select("email, amount_cents");
  if (error) throw error;

  const donation = data?.[0];
  if (!donation?.email || donation.amount_cents < PREMIUM_MIN_CENTS) return;

  const { count, error: countError } = await supabase
    .from("donations")
    .select("id", { count: "exact", head: true })
    .eq("email", donation.email)
    .gte("amount_cents", PREMIUM_MIN_CENTS)
    .is("refunded_at", null);
  if (countError) throw countError;
  if (count && count > 0) return; // Still qualifies through another donation.

  const { data: revoked, error: revokeError } = await supabase
    .from("premium_users")
    .delete()
    .eq("email", donation.email)
    .eq("stripe_granted", true)
    .select("id");
  if (revokeError) throw revokeError;
  if (revoked?.length) revalidateTag("premium-users", { expire: 0 });
}
