-- Security hardening (from Supabase advisors): SECURITY DEFINER functions
-- were executable by anon/authenticated via /rest/v1/rpc, letting anyone
-- trigger the materialized-view refresh. Only the service role (cron + admin
-- actions) should call it. handle_new_auth_user is a trigger function and
-- needs no caller EXECUTE at all.

revoke execute on function public.refresh_channel_stats_latest()
  from public, anon, authenticated;
grant execute on function public.refresh_channel_stats_latest() to service_role;

revoke execute on function public.handle_new_auth_user()
  from public, anon, authenticated;
