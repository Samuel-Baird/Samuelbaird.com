-- Per-channel source link for "this channel is LDS-affiliated."
-- When null, the UI shows "Source: channel content" (i.e. the affiliation is
-- self-evident from what the channel posts).

alter table public.channels
  add column if not exists lds_affiliation_source text;
