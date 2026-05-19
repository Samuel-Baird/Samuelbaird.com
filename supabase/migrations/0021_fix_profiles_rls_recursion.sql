-- Defensively fix the recursive "profiles: admins read all" policy.
--
-- Background: in production the migration history lost track of 0004 for a
-- while, and the original recursive policy from 0003 ended up live again.
-- This drops anything that could be recursing on profiles and recreates the
-- minimal policy set needed: read-own and update-own.

drop policy if exists "profiles: admins read all" on public.profiles;
drop policy if exists "profiles: update own non-admin fields" on public.profiles;
drop policy if exists "profiles: read own" on public.profiles;
drop policy if exists "profiles: update own" on public.profiles;

create policy "profiles: read own" on public.profiles
  for select using (auth.uid() = id);

create policy "profiles: update own" on public.profiles
  for update
  using (auth.uid() = id)
  with check (auth.uid() = id);
