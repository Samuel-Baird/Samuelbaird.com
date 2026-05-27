-- Explicitly define RLS policies for tables that had RLS enabled but no policies.
-- (lint: rls_enabled_no_policy)
--
-- Having RLS on with zero policies already denies all direct API access, but
-- the linter flags the absence of policies as potentially accidental.  These
-- migrations make the intent explicit: both tables are service-role-only.
-- All application code that touches them uses createSupabaseServiceClient(),
-- which bypasses RLS entirely.

-- ============================================================================
-- premium_users: deny all direct API access
-- Email addresses and beta-tester status are admin-only data.  Every read and
-- write in the codebase goes through the service_role key.
-- ============================================================================

drop policy if exists "premium_users: no public access" on public.premium_users;
create policy "premium_users: no public access" on public.premium_users
  as restrictive
  for all
  using (false)
  with check (false);

-- ============================================================================
-- schema_migrations: deny all direct API access
-- Internal migration-tracking table; never needs to be exposed via the API.
-- ============================================================================

drop policy if exists "schema_migrations: no public access" on public.schema_migrations;
create policy "schema_migrations: no public access" on public.schema_migrations
  as restrictive
  for all
  using (false)
  with check (false);
