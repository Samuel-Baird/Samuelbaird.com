-- Monthly newsletter: opt-in subscribers and an idempotency/audit log for sends.
-- Both tables are service-role-only (same posture as premium_users, see 0035).
-- All application code touches them via createSupabaseServiceClient().

create table if not exists public.newsletter_subscribers (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  -- Snapshot at subscribe time; send-time code prefers the live profiles.email
  -- and only falls back to this if the profile lookup comes back empty.
  email text not null,
  -- Opaque unsubscribe token. Stable across unsubscribe/resubscribe cycles so
  -- an old email's link keeps working even after a resubscribe.
  token uuid not null default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unsubscribed_at timestamptz
);

create unique index if not exists newsletter_subscribers_token_idx
  on public.newsletter_subscribers (token);

drop trigger if exists newsletter_subscribers_set_updated_at on public.newsletter_subscribers;
create trigger newsletter_subscribers_set_updated_at
  before update on public.newsletter_subscribers
  for each row execute function public.set_updated_at();

alter table public.newsletter_subscribers enable row level security;

drop policy if exists "newsletter_subscribers: no public access" on public.newsletter_subscribers;
create policy "newsletter_subscribers: no public access" on public.newsletter_subscribers
  as restrictive
  for all
  using (false)
  with check (false);

-- One row per monthly send; the unique month_key is the double-send guard —
-- insert it first and treat a unique-violation as "already sent, skip".
create table if not exists public.newsletter_sends (
  id uuid primary key default gen_random_uuid(),
  month_key text not null unique, -- 'YYYY-MM' of the month being reported
  window_start timestamptz not null,
  window_end timestamptz not null,
  channel_count integer not null default 0,
  study_count integer not null default 0,
  recipient_count integer not null default 0,
  failed_count integer not null default 0,
  status text not null default 'pending', -- pending | sent | empty | failed
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

alter table public.newsletter_sends enable row level security;

drop policy if exists "newsletter_sends: no public access" on public.newsletter_sends;
create policy "newsletter_sends: no public access" on public.newsletter_sends
  as restrictive
  for all
  using (false)
  with check (false);
