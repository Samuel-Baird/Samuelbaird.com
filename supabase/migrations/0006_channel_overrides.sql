-- Channels: admin overrides for fields that may come from the YouTube API.
-- The `country` and `language` columns are populated automatically by the
-- stats refresh job. These `_manual` columns let an admin set a value when
-- the API returns null, or override a wrong API value. Effective value is
-- coalesce(manual, api).

alter table public.channels
  add column if not exists country_manual text,
  add column if not exists language_manual text;
