-- 0013_channel_id_driven.sql
-- Refactor: make the YouTube channel ID the source of truth.
--
-- Splits `channels` into two concerns:
--   - `channels`         : user-curated metadata (state, owner, socials, manual overrides)
--                          — never touched by the YouTube refresh job.
--   - `channel_youtube`  : YouTube-derived display data (name, thumbnail, country,
--                          language, description, created_at_youtube) — fully overwritten
--                          on every refresh, plus sync status for diagnostics.
--
-- `channel_stats` (append-only history) keeps its existing FK to channels.id.
-- Slug is now equal to youtube_channel_id so URLs stay stable across renames.
--
-- This migration is DESTRUCTIVE: it wipes all existing channels and cascades to
-- channel_stats. Bookmarks/upvotes pointing at those channel UUIDs become
-- dangling (they render as "(unknown channel)"); rebuild them by re-bookmarking
-- after reseeding. Authorized by the user.

-- 1) Drop dependent views/materialized views first so column drops succeed.
drop view if exists public.channel_full cascade;
drop view if exists public.site_stats cascade;
drop materialized view if exists public.channel_stats_latest cascade;

-- 2) Wipe existing channel data (cascades to channel_stats via FK).
delete from public.channels;

-- 3) Strip YouTube-derived columns from channels (now metadata-only).
alter table public.channels
  drop column if exists name,
  drop column if exists description,
  drop column if exists country,
  drop column if exists language,
  drop column if exists thumbnail_url,
  drop column if exists created_at_youtube;

-- Notes field for admin free-form notes.
alter table public.channels
  add column if not exists notes text;

-- 4) New YouTube-derived table, keyed by channel_id (UUID FK).
create table if not exists public.channel_youtube (
  channel_id uuid primary key references public.channels(id) on delete cascade,
  name text,
  description text,
  country text,
  default_language text,
  thumbnail_url text,
  created_at_youtube timestamptz,
  last_synced_at timestamptz,
  last_sync_status text,           -- 'ok' | 'missing' | 'error'
  last_sync_error text
);

create index if not exists channel_youtube_last_sync_idx
  on public.channel_youtube (last_sync_status, last_synced_at desc);

alter table public.channel_youtube enable row level security;
drop policy if exists "channel_youtube: public read" on public.channel_youtube;
create policy "channel_youtube: public read" on public.channel_youtube
  for select using (true);

-- 5) Rebuild materialized view of latest stats.
create materialized view public.channel_stats_latest as
select distinct on (cs.channel_id)
  cs.channel_id,
  cs.captured_at,
  cs.subscribers,
  cs.total_views,
  cs.video_count
from public.channel_stats cs
order by cs.channel_id, cs.captured_at desc;

create unique index channel_stats_latest_channel_idx
  on public.channel_stats_latest (channel_id);

-- 6) Convenience view joining metadata + YouTube + latest stats.
create view public.channel_full as
select
  c.id,
  c.youtube_channel_id,
  c.slug,
  c.is_active,
  c.featured,
  c.channel_type,
  c.state,
  c.city,
  c.owned_by,
  c.country_manual,
  c.language_manual,
  c.lds_affiliation_source,
  c.handle,
  c.facebook_url,
  c.instagram_url,
  c.tiktok_url,
  c.x_url,
  c.notes,
  c.created_at,
  c.updated_at,
  coalesce(y.name, c.youtube_channel_id) as name,
  y.description,
  y.country,
  y.default_language as language,
  y.thumbnail_url,
  y.created_at_youtube,
  y.last_synced_at,
  y.last_sync_status,
  y.last_sync_error,
  l.captured_at as stats_captured_at,
  l.subscribers,
  l.total_views,
  l.video_count
from public.channels c
left join public.channel_youtube y on y.channel_id = c.id
left join public.channel_stats_latest l on l.channel_id = c.id;

-- 7) Rebuild site_stats view (old version referenced removed columns).
create view public.site_stats as
select
  (select count(*) from public.channels where is_active) as total_channels,
  coalesce(sum(l.subscribers), 0)::bigint as total_subscribers,
  coalesce(sum(l.total_views), 0)::bigint as total_views,
  coalesce(sum(l.video_count), 0)::bigint as total_videos,
  max(l.captured_at) as last_refresh
from public.channel_stats_latest l
join public.channels c on c.id = l.channel_id
where c.is_active;

-- 8) Default slug = youtube_channel_id for any future inserts that omit slug.
create or replace function public.channels_default_slug()
returns trigger
language plpgsql
as $$
begin
  if new.slug is null or new.slug = '' then
    new.slug := new.youtube_channel_id;
  end if;
  return new;
end;
$$;

drop trigger if exists channels_default_slug_trg on public.channels;
create trigger channels_default_slug_trg
  before insert or update on public.channels
  for each row execute function public.channels_default_slug();
