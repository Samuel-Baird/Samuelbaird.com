-- Opt-in flag for the weekly digest email. Stored on premium_users so only
-- premium users can opt in. Admins read this list via /admin/notifications
-- and send the digest manually.

alter table public.premium_users
  add column if not exists notify_weekly boolean not null default false;
