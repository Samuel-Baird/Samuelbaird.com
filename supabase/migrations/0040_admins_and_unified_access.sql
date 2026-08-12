-- Admin role as an email allowlist, mirroring apologists/premium_users, so
-- admin access can be granted (including before someone has signed in) from
-- the same combined /admin/access screen that manages premium and apologist
-- status. profiles.is_admin remains the actual authority requireAdmin()
-- checks — this table is synced into it at sign-up time (below) and
-- immediately for existing profiles when toggled from the admin UI.

create table if not exists public.admins (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  name text,
  created_by uuid references public.profiles(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint admins_email_lowercase check (email = lower(trim(email)))
);

create unique index if not exists admins_email_idx
  on public.admins (email);

drop trigger if exists admins_set_updated_at on public.admins;
create trigger admins_set_updated_at
  before update on public.admins
  for each row execute function public.set_updated_at();

alter table public.admins enable row level security;

drop policy if exists "admins: no public access" on public.admins;
create policy "admins: no public access" on public.admins
  as restrictive
  for all
  using (false)
  with check (false);

-- ============================================================================
-- Extend the sign-up trigger: grant is_admin at first sign-in if the email
-- is on the admins allowlist, in addition to the hardcoded owner email
-- (kept unconditionally so the owner can never be locked out even if the
-- admins table is ever empty or misconfigured).
-- ============================================================================
create or replace function public.handle_new_auth_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  v_full_name text;
  v_avatar_url text;
  v_grant_admin boolean;
begin
  v_full_name := coalesce(
    new.raw_user_meta_data->>'full_name',
    new.raw_user_meta_data->>'name',
    null
  );
  v_avatar_url := coalesce(
    new.raw_user_meta_data->>'avatar_url',
    new.raw_user_meta_data->>'picture',
    null
  );
  v_grant_admin := (new.email = 'b13llama@gmail.com')
    or exists (
      select 1 from public.admins a where a.email = lower(trim(new.email))
    );

  insert into public.profiles (id, email, full_name, avatar_url, is_admin)
  values (new.id, new.email, v_full_name, v_avatar_url, v_grant_admin)
  on conflict (id) do update
    set email = excluded.email,
        full_name = coalesce(excluded.full_name, public.profiles.full_name),
        avatar_url = coalesce(excluded.avatar_url, public.profiles.avatar_url),
        is_admin = public.profiles.is_admin or excluded.is_admin;

  return new;
end;
$$;
