-- Remove the Apologetics Hub entirely: the private, apologist-gated feed of
-- critical-channel videos with claim-level rebuttals (0039, 0041, 0042, 0043).
-- The app's /apologetics-hub routes, hub components, and apologist gating
-- (requireApologist/isApologistUser) have all been removed from the code.
--
-- Drop order respects foreign keys: children of hub_videos first, then
-- hub_videos and hub_channel_state (both reference channels), then the
-- apologists allowlist (no incoming references left).

drop table if exists public.hub_video_statuses;
drop table if exists public.hub_reported_responses;
drop table if exists public.hub_claims;
drop table if exists public.hub_transcripts;
drop table if exists public.hub_videos;
drop table if exists public.hub_channel_state;
drop table if exists public.apologists;
