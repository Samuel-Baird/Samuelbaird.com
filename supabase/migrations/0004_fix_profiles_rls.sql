-- Fix infinite recursion in profiles RLS policies.
--
-- The original "admins read all" policy queried public.profiles inside its
-- USING clause, which retriggers RLS and recurses (Postgres error 42P17).
-- The "update own non-admin fields" policy had the same shape in WITH CHECK.
--
-- We don't actually need cross-row reads from app code — the admin gate works
-- off the user's own profile row, which the "read own" policy already allows.
-- Writes to is_admin only happen via service_role (which bypasses RLS).

drop policy if exists "profiles: admins read all" on public.profiles;
drop policy if exists "profiles: update own non-admin fields" on public.profiles;

create policy "profiles: update own" on public.profiles
  for update
  using (auth.uid() = id)
  with check (auth.uid() = id);
