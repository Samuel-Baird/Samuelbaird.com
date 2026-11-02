-- Add the "Mormon Transhumanist Association" YouTube channel (handle @Transfigurism).
-- Channel ID resolved from https://www.youtube.com/@Transfigurism (canonical
-- /channel/UCITb34rqLBLeiozyYGXo1OA). Type "Religious" is the closest fit for a
-- Latter-day Saint community channel; change it in /admin/channels if needed.
-- Name, stats and thumbnail are filled in by the next stats refresh.

insert into public.channels (youtube_channel_id, slug, handle, channel_type, is_active)
values
  ('UCITb34rqLBLeiozyYGXo1OA', 'UCITb34rqLBLeiozyYGXo1OA', '@Transfigurism', 'Religious', true)
on conflict (youtube_channel_id) do update set
  handle       = excluded.handle,
  channel_type = excluded.channel_type,
  is_active    = excluded.is_active,
  updated_at   = now();
