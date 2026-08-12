-- Apologetics Hub: private feed of critical-channel videos with claim-level
-- rebuttals, sourced during a manual Claude Code ingest session, for accounts
-- granted apologist status.
--
-- All five tables below are service-role-only (RLS enabled, restrictive
-- deny-all policy — same shape as premium_users in 0025 + 0035). The hub is
-- gated entirely in the app layer via requireApologist() rather than via
-- apologist-aware RLS: the allowlist is email-keyed like premium_users, and
-- an RLS check that joins auth.uid() -> profiles.email -> apologists.email
-- would risk the same recursion class of bug that 0021 had to fix on
-- profiles itself. Deny-all avoids that surface entirely; every hub read and
-- write goes through createSupabaseServiceClient() behind requireApologist().

-- ============================================================================
-- apologists  (email allowlist granting hub access; exact mirror of
-- premium_users)
-- ============================================================================
create table if not exists public.apologists (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  name text,
  created_by uuid references public.profiles(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint apologists_email_lowercase check (email = lower(trim(email)))
);

create unique index if not exists apologists_email_idx
  on public.apologists (email);

drop trigger if exists apologists_set_updated_at on public.apologists;
create trigger apologists_set_updated_at
  before update on public.apologists
  for each row execute function public.set_updated_at();

-- ============================================================================
-- hub_videos  (one row per tracked critical video)
-- ============================================================================
create table if not exists public.hub_videos (
  id uuid primary key default gen_random_uuid(),
  channel_id uuid not null references public.channels(id) on delete cascade,
  youtube_video_id text not null,
  title text not null,
  published_at timestamptz not null,
  duration_seconds integer,
  thumbnail_url text,
  summary text not null default '',
  view_count bigint not null default 0,
  view_count_updated_at timestamptz,
  -- Channel-baseline view estimate computed at ingest time (median of recent
  -- qualifying uploads) — see scripts/hub-list-new-videos.ts. Nullable until
  -- a baseline could be computed (e.g. too little upload history).
  expected_views numeric,
  debunkability smallint check (debunkability between 1 and 10),
  -- Computed by scripts/hub-insert-analysis.ts, not a generated column, so
  -- the ranking formula can evolve without a migration.
  priority_score numeric,
  video_status text not null default 'active'
    check (video_status in ('active', 'removed', 'private')),
  analyzed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint hub_videos_ytid_format check (youtube_video_id ~ '^[A-Za-z0-9_-]{8,20}$')
);

create unique index if not exists hub_videos_ytid_idx
  on public.hub_videos (youtube_video_id);
create index if not exists hub_videos_published_idx
  on public.hub_videos (published_at desc);
create index if not exists hub_videos_priority_idx
  on public.hub_videos (priority_score desc nulls last);
create index if not exists hub_videos_channel_idx
  on public.hub_videos (channel_id);

drop trigger if exists hub_videos_set_updated_at on public.hub_videos;
create trigger hub_videos_set_updated_at
  before update on public.hub_videos
  for each row execute function public.set_updated_at();

-- ============================================================================
-- hub_transcripts  (1:1 with hub_videos; stored for analysis, never rendered
-- in the UI — only summary/claims/excerpts are shown)
-- ============================================================================
create table if not exists public.hub_transcripts (
  video_id uuid primary key references public.hub_videos(id) on delete cascade,
  transcript text not null,
  segments jsonb,
  source text not null default 'timedtext'
    check (source in ('timedtext', 'yt-dlp', 'manual')),
  fetched_at timestamptz not null default now()
);

-- ============================================================================
-- hub_claims  (ordered claim-level rebuttals per video)
-- ============================================================================
create table if not exists public.hub_claims (
  id uuid primary key default gen_random_uuid(),
  video_id uuid not null references public.hub_videos(id) on delete cascade,
  position integer not null,
  timestamp_seconds integer not null check (timestamp_seconds >= 0),
  excerpt text not null,
  claim_summary text not null,
  response text not null,
  -- [{ title, url, note }] — sources are only ever read alongside their
  -- claim, and ingest arrives as one JSON document per video, so this is
  -- jsonb rather than a join table.
  sources jsonb not null default '[]'::jsonb
    check (jsonb_typeof(sources) = 'array'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (video_id, position)
);

create index if not exists hub_claims_video_idx
  on public.hub_claims (video_id, position);

drop trigger if exists hub_claims_set_updated_at on public.hub_claims;
create trigger hub_claims_set_updated_at
  before update on public.hub_claims
  for each row execute function public.set_updated_at();

-- ============================================================================
-- hub_video_statuses  (per-apologist, per-video: "working on it" /
-- "responded" + link. Per-creator, not exclusive — several apologists can
-- work the same video.)
-- ============================================================================
create table if not exists public.hub_video_statuses (
  user_id uuid not null references auth.users(id) on delete cascade,
  video_id uuid not null references public.hub_videos(id) on delete cascade,
  status text not null check (status in ('working_on_it', 'responded')),
  response_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (user_id, video_id)
);

create index if not exists hub_video_statuses_video_idx
  on public.hub_video_statuses (video_id);

drop trigger if exists hub_video_statuses_set_updated_at on public.hub_video_statuses;
create trigger hub_video_statuses_set_updated_at
  before update on public.hub_video_statuses
  for each row execute function public.set_updated_at();

-- ============================================================================
-- RLS: all five tables are service-role-only. Every read/write in app code
-- goes through createSupabaseServiceClient() behind requireApologist().
-- ============================================================================
alter table public.apologists enable row level security;
alter table public.hub_videos enable row level security;
alter table public.hub_transcripts enable row level security;
alter table public.hub_claims enable row level security;
alter table public.hub_video_statuses enable row level security;

drop policy if exists "apologists: no public access" on public.apologists;
create policy "apologists: no public access" on public.apologists
  as restrictive
  for all
  using (false)
  with check (false);

drop policy if exists "hub_videos: no public access" on public.hub_videos;
create policy "hub_videos: no public access" on public.hub_videos
  as restrictive
  for all
  using (false)
  with check (false);

drop policy if exists "hub_transcripts: no public access" on public.hub_transcripts;
create policy "hub_transcripts: no public access" on public.hub_transcripts
  as restrictive
  for all
  using (false)
  with check (false);

drop policy if exists "hub_claims: no public access" on public.hub_claims;
create policy "hub_claims: no public access" on public.hub_claims
  as restrictive
  for all
  using (false)
  with check (false);

drop policy if exists "hub_video_statuses: no public access" on public.hub_video_statuses;
create policy "hub_video_statuses: no public access" on public.hub_video_statuses
  as restrictive
  for all
  using (false)
  with check (false);
