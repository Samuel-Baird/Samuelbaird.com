-- Latter-day Stats — initial schema
-- Run this in Supabase Dashboard → SQL Editor → New query, then click Run.

-- ============================================================================
-- Extensions
-- ============================================================================
create extension if not exists "pgcrypto";

-- ============================================================================
-- channels
-- ============================================================================
create table if not exists public.channels (
  id uuid primary key default gen_random_uuid(),
  youtube_channel_id text not null unique,
  name text not null,
  slug text not null unique,
  description text,
  country text,
  thumbnail_url text,
  created_at_youtube timestamptz,
  featured boolean not null default false,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists channels_featured_idx on public.channels (featured) where featured = true;
create index if not exists channels_is_active_idx on public.channels (is_active);

-- ============================================================================
-- channel_stats  (append-only history)
-- ============================================================================
create table if not exists public.channel_stats (
  id bigserial primary key,
  channel_id uuid not null references public.channels(id) on delete cascade,
  captured_at timestamptz not null default now(),
  subscribers bigint not null,
  total_views bigint not null,
  video_count integer not null
);

create index if not exists channel_stats_channel_captured_idx
  on public.channel_stats (channel_id, captured_at desc);

-- ============================================================================
-- channel_stats_latest  (materialized view of most recent row per channel)
-- ============================================================================
create materialized view if not exists public.channel_stats_latest as
select distinct on (cs.channel_id)
  cs.channel_id,
  cs.captured_at,
  cs.subscribers,
  cs.total_views,
  cs.video_count
from public.channel_stats cs
order by cs.channel_id, cs.captured_at desc;

create unique index if not exists channel_stats_latest_channel_idx
  on public.channel_stats_latest (channel_id);

-- ============================================================================
-- studies
-- ============================================================================
create table if not exists public.studies (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text not null,
  authors text[] not null default '{}',
  year integer,
  source text,
  abstract text,
  tags text[] not null default '{}',
  pdf_path text,
  external_url text,
  featured boolean not null default false,
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists studies_featured_idx on public.studies (featured) where featured = true;
create index if not exists studies_year_idx on public.studies (year desc nulls last);

-- ============================================================================
-- updated_at trigger
-- ============================================================================
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

drop trigger if exists channels_set_updated_at on public.channels;
create trigger channels_set_updated_at
  before update on public.channels
  for each row execute function public.set_updated_at();

drop trigger if exists studies_set_updated_at on public.studies;
create trigger studies_set_updated_at
  before update on public.studies
  for each row execute function public.set_updated_at();

-- ============================================================================
-- refresh function
-- ============================================================================
create or replace function public.refresh_channel_stats_latest()
returns void
language sql
security definer
set search_path = public
as $$
  refresh materialized view concurrently public.channel_stats_latest;
$$;

-- ============================================================================
-- site_stats view (totals — drives homepage tiles)
-- ============================================================================
create or replace view public.site_stats as
select
  (select count(*) from public.channels where is_active) as total_channels,
  coalesce(sum(l.subscribers), 0)::bigint as total_subscribers,
  coalesce(sum(l.total_views), 0)::bigint as total_views,
  coalesce(sum(l.video_count), 0)::bigint as total_videos,
  max(l.captured_at) as last_refresh
from public.channel_stats_latest l
join public.channels c on c.id = l.channel_id
where c.is_active;

-- ============================================================================
-- Row Level Security: public read, no public write
-- ============================================================================
alter table public.channels enable row level security;
alter table public.channel_stats enable row level security;
alter table public.studies enable row level security;

drop policy if exists "channels: public read" on public.channels;
create policy "channels: public read" on public.channels
  for select using (true);

drop policy if exists "channel_stats: public read" on public.channel_stats;
create policy "channel_stats: public read" on public.channel_stats
  for select using (true);

drop policy if exists "studies: public read" on public.studies;
create policy "studies: public read" on public.studies
  for select using (true);

-- Writes go through service_role only (server actions / cron), which bypasses RLS.

-- ============================================================================
-- Storage bucket for study PDFs
-- ============================================================================
insert into storage.buckets (id, name, public)
values ('studies', 'studies', true)
on conflict (id) do nothing;

drop policy if exists "studies bucket: public read" on storage.objects;
create policy "studies bucket: public read" on storage.objects
  for select using (bucket_id = 'studies');
