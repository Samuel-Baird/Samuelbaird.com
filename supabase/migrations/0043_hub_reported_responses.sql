-- Apologetics Hub: reported-response links. Distinct from
-- hub_video_statuses (your own "working on it"/"responded" status): this is
-- a shared, append-only log of "someone else already responded to this,
-- here's their video" — any apologist can add one, one link at a time, and
-- a video can accumulate as many as apologists want to log (several
-- different creators often respond to the same critical video).

create table if not exists public.hub_reported_responses (
  id uuid primary key default gen_random_uuid(),
  video_id uuid not null references public.hub_videos(id) on delete cascade,
  url text not null,
  added_by uuid references public.profiles(id) on delete set null,
  created_at timestamptz not null default now(),
  constraint hub_reported_responses_url_format check (url ~ '^https?://')
);

create index if not exists hub_reported_responses_video_idx
  on public.hub_reported_responses (video_id, created_at desc);

-- Service-role-only, same shape as every other hub table (see
-- 0039_apologetics_hub.sql) — gated in the app layer via requireApologist().
alter table public.hub_reported_responses enable row level security;

drop policy if exists "hub_reported_responses: no public access" on public.hub_reported_responses;
create policy "hub_reported_responses: no public access" on public.hub_reported_responses
  as restrictive
  for all
  using (false)
  with check (false);
