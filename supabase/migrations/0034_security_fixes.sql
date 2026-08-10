-- Security hardening: address Supabase database linter warnings.

-- ============================================================================
-- 1. Fix mutable search_path on trigger functions
--    (lint: function_search_path_mutable)
--
--    Adding `set search_path = ''` makes the search_path immutable so that a
--    superuser cannot hijack the function by injecting a malicious schema name
--    into the session search_path at call time.  These functions only reference
--    pg_catalog built-ins and NEW row fields, so the empty search_path is safe.
-- ============================================================================

create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

create or replace function public.channels_sync_channel_type()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if new.channel_types is null then
    new.channel_types := '{}';
  end if;

  if array_length(new.channel_types, 1) is null then
    -- array empty: derive from legacy scalar if present
    if new.channel_type is not null then
      new.channel_types := array[new.channel_type];
    end if;
  else
    -- array authoritative: mirror first element into legacy scalar
    new.channel_type := new.channel_types[1];
  end if;
  return new;
end;
$$;

create or replace function public.studies_search_tsv_refresh()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.search_tsv :=
    to_tsvector(
      'english'::regconfig,
      coalesce(new.title, '') || ' ' ||
      coalesce(array_to_string(new.authors, ' '), '') || ' ' ||
      coalesce(new.abstract, '') || ' ' ||
      coalesce(array_to_string(new.tags, ' '), '')
    );
  return new;
end;
$$;

create or replace function public.channels_default_slug()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if new.slug is null or new.slug = '' then
    new.slug := new.youtube_channel_id;
  end if;
  return new;
end;
$$;

-- ============================================================================
-- 2. Revoke direct RPC access to SECURITY DEFINER functions
--    (lint: anon_security_definer_function_executable,
--           authenticated_security_definer_function_executable)
--
--    Superseded: migration 0032_lock_down_definer_functions.sql already
--    revokes EXECUTE on handle_new_auth_user() and refresh_channel_stats_latest()
--    from public/anon/authenticated and grants the latter to service_role.
--    The statements originally in this section are therefore omitted rather
--    than repeated here.
-- ============================================================================


-- ============================================================================
-- 3. Remove broad storage SELECT policy that allows file listing
--    (lint: public_bucket_allows_listing)
--
--    The "studies" bucket is created with public = true, so objects are already
--    accessible via their public URL (/storage/v1/object/public/studies/...).
--    A broad SELECT policy on storage.objects is not needed for URL-based
--    access and additionally allows any client to enumerate all files in the
--    bucket.  All admin operations that need to list or delete objects use the
--    service_role key, which bypasses RLS entirely.
-- ============================================================================

drop policy if exists "studies bucket: public read" on storage.objects;

-- ============================================================================
-- Notes on remaining lint items (not addressed here):
--
--  * materialized_view_in_api (channel_stats_latest): channel stats are
--    intentionally public data.  The public.site_stats view, which is queried
--    by anonymous users for the homepage totals, JOINs this materialized view.
--    Revoking SELECT from anon would break site_stats for public visitors.
--    The data exposed (subscriber/view/video counts) carries no privacy risk.
--
--  * auth_leaked_password_protection: this is an Auth service setting that
--    cannot be changed via SQL.  Enable it in the Supabase Dashboard under
--    Authentication → Sign In / Up → Password protection → check
--    "Prevent use of leaked passwords".
-- ============================================================================
