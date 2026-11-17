-- Refunds: let the Stripe webhook match a refunded charge back to its donation and undo the
-- premium access that donation granted.
--
-- donations.stripe_payment_intent_id: set for one-time donations, matched against the refunded
--   charge. Monthly donations have no single payment intent, so their refunds aren't matched
--   automatically.
-- donations.refunded_at: set when a full refund arrives.
-- premium_users.stripe_granted: true only for rows the webhook created itself. Refunds revoke
--   only these, so access granted by hand (receipts from PayPal/Venmo, the owner) is never
--   removed automatically.

alter table public.donations
  add column if not exists stripe_payment_intent_id text,
  add column if not exists refunded_at timestamptz;

create index if not exists donations_payment_intent_idx
  on public.donations (stripe_payment_intent_id)
  where stripe_payment_intent_id is not null;

alter table public.premium_users
  add column if not exists stripe_granted boolean not null default false;
