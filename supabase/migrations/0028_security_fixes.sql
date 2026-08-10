-- Security hardening per Supabase advisor (25 May 2026):
--
-- 1. schema_migrations is in the public schema but has no RLS, meaning
--    PostgREST would expose migration history to anonymous users. Enable RLS
--    with no policies so service_role still works (bypasses RLS) while anon
--    and authenticated are denied.
--
-- 2. Views created without an explicit security clause default to SECURITY
--    DEFINER in PostgreSQL, executing with the view-owner's privileges rather
--    than the querying user's. All three views only read tables that already
--    have permissive public-read RLS policies, so switching to SECURITY
--    INVOKER has no functional impact and closes the lint warning.

alter table public.schema_migrations enable row level security;

alter view public.upvote_counts set (security_invoker = true);
alter view public.site_stats    set (security_invoker = true);
alter view public.channel_full  set (security_invoker = true);
