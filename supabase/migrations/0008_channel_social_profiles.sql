-- Optional social profile links for a channel.
-- These are manually maintained links only; no statistics are tracked for them.

alter table public.channels
  add column if not exists facebook_url text,
  add column if not exists instagram_url text,
  add column if not exists tiktok_url text,
  add column if not exists x_url text;
