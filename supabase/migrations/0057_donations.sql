-- Stripe donations, written by /api/stripe/webhook. One row per paid Checkout
-- session (idempotent on stripe_session_id). Service-role-only, same posture
-- as premium_users (see 0035). Paid donations of $5+ also insert the donor's
-- email into premium_users.

create table if not exists public.donations (
  id uuid primary key default gen_random_uuid(),
  stripe_session_id text not null,
  stripe_customer_id text,
  email text,
  -- Null for donors who weren't signed in; their premium is keyed by email.
  user_id uuid references public.profiles(id) on delete set null,
  amount_cents integer not null check (amount_cents >= 0),
  currency text not null default 'usd',
  recurring boolean not null default false,
  created_at timestamptz not null default now()
);

create unique index if not exists donations_stripe_session_id_idx
  on public.donations (stripe_session_id);

create index if not exists donations_email_idx on public.donations (email);

alter table public.donations enable row level security;

drop policy if exists "donations: no public access" on public.donations;
create policy "donations: no public access" on public.donations
  as restrictive
  for all
  using (false)
  with check (false);
