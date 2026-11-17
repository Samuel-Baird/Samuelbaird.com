-- Apologetics Hub — per-channel ingest tracking.
--
-- Records when a channel was last scanned for new videos (by
-- scripts/hub-list-new-videos.ts), independent of whether that scan found
-- anything new. This is what lets an agent picking up the ingest process
-- later answer "which tracked channel is most overdue for a check" without
-- re-deriving it from hub_videos, which only tells you what was found, not
-- when a channel was last looked at (a channel with no new uploads since
-- its last scan would otherwise look identical to one that has never been
-- scanned at all).
create table if not exists public.hub_channel_state (
  channel_id uuid primary key references public.channels(id) on delete cascade,
  last_ingested_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists hub_channel_state_set_updated_at on public.hub_channel_state;
create trigger hub_channel_state_set_updated_at
  before update on public.hub_channel_state
  for each row execute function public.set_updated_at();

alter table public.hub_channel_state enable row level security;

drop policy if exists "hub_channel_state: no public access" on public.hub_channel_state;
create policy "hub_channel_state: no public access" on public.hub_channel_state
  as restrictive
  for all
  using (false)
  with check (false);
