import { revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";
import type Stripe from "stripe";
import { getStripe, PREMIUM_MIN_CENTS } from "@/lib/stripe";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

// Stripe webhook. Configure the endpoint (dashboard, or `stripe listen
// --forward-to localhost:3000/api/stripe/webhook` locally) to send
// checkout.session.completed and checkout.session.async_payment_succeeded.
// Records each paid donation and, at $5+, adds the donor to premium_users.
export async function POST(req: NextRequest) {
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  const signature = req.headers.get("stripe-signature");
  if (!secret || !signature) {
    return NextResponse.json({ error: "Not configured" }, { status: 400 });
  }

  let event: Stripe.Event;
  try {
    // Signature is computed over the raw body, so read it as text.
    event = getStripe().webhooks.constructEvent(
      await req.text(),
      signature,
      secret,
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
    if (session.payment_status === "paid") {
      await recordDonation(session);
    }
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
    },
    { onConflict: "stripe_session_id", ignoreDuplicates: true },
  );
  // Throwing returns a 500, so Stripe retries the delivery later.
  if (donationError) throw donationError;

  if (email && amount >= PREMIUM_MIN_CENTS) {
    const { error } = await supabase
      .from("premium_users")
      .upsert(
        { email, name: session.customer_details?.name ?? null },
        { onConflict: "email", ignoreDuplicates: true },
      );
    if (error) throw error;
    revalidateTag("premium-users", { expire: 0 });
  }
}
