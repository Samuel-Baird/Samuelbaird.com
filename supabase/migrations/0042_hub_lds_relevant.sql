-- Apologetics Hub: some tracked Critical channels (e.g. general Christian
-- apologetics channels) don't address Latter-day Saints/Mormonism in every
-- upload. hub-insert-analysis.ts now requires the analyst to record whether
-- a video is actually on-topic; off-topic videos are hidden from the public
-- feed (src/app/apologetics-hub/page.tsx) while their row, transcript, and
-- any claims are retained for the record.
--
-- Null means "not yet analyzed" (existing rows, and anything still at the
-- metadata/transcript stage) and stays visible in the feed by default —
-- only an explicit false hides a video.
alter table public.hub_videos
  add column if not exists lds_relevant boolean;

comment on column public.hub_videos.lds_relevant is
  'Set by scripts/hub-insert-analysis.ts during analysis. Null = not yet determined (visible in feed). false = video does not address Latter-day Saints/Mormonism, hidden from the public feed but retained.';
