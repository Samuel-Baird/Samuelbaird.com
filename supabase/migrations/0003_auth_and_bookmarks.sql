-- Latter-day Stats — auth profiles + bookmarks
-- Idempotent: safe to re-run.

-- ============================================================================
-- profiles  (mirror of auth.users we can join + RLS-protect from app code)
-- ============================================================================
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  full_name text,
  avatar_url text,
  is_admin boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists profiles_email_idx on public.profiles (email);
create index if not exists profiles_is_admin_idx on public.profiles (is_admin) where is_admin = true;

drop trigger if exists profiles_set_updated_at on public.profiles;
create trigger profiles_set_updated_at
  before update on public.profiles
  for each row execute function public.set_updated_at();

-- ============================================================================
-- Auto-create a profile when a user signs in for the first time
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
  v_is_owner boolean;
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
  v_is_owner := (new.email = 'b13llama@gmail.com');

  insert into public.profiles (id, email, full_name, avatar_url, is_admin)
  values (new.id, new.email, v_full_name, v_avatar_url, v_is_owner)
  on conflict (id) do update
    set email = excluded.email,
        full_name = coalesce(excluded.full_name, public.profiles.full_name),
        avatar_url = coalesce(excluded.avatar_url, public.profiles.avatar_url),
        is_admin = public.profiles.is_admin or excluded.is_admin;

  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_auth_user();

-- Bootstrap: if the owner already signed up before this migration, promote them.
update public.profiles
  set is_admin = true
  where email = 'b13llama@gmail.com' and is_admin = false;

-- ============================================================================
-- bookmarks
-- ============================================================================
create table if not exists public.bookmarks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  target_type text not null check (target_type in ('channel', 'study')),
  target_id uuid not null,
  created_at timestamptz not null default now()
);

create unique index if not exists bookmarks_user_target_idx
  on public.bookmarks (user_id, target_type, target_id);
create index if not exists bookmarks_user_list_idx
  on public.bookmarks (user_id, target_type, created_at desc);

-- ============================================================================
-- RLS
-- ============================================================================
alter table public.profiles enable row level security;
alter table public.bookmarks enable row level security;

drop policy if exists "profiles: read own" on public.profiles;
create policy "profiles: read own" on public.profiles
  for select using (auth.uid() = id);

drop policy if exists "profiles: admins read all" on public.profiles;
create policy "profiles: admins read all" on public.profiles
  for select using (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );

drop policy if exists "profiles: update own non-admin fields" on public.profiles;
create policy "profiles: update own non-admin fields" on public.profiles
  for update using (auth.uid() = id)
  with check (
    auth.uid() = id
    and is_admin = (select is_admin from public.profiles where id = auth.uid())
  );

drop policy if exists "bookmarks: read own" on public.bookmarks;
create policy "bookmarks: read own" on public.bookmarks
  for select using (auth.uid() = user_id);

drop policy if exists "bookmarks: insert own" on public.bookmarks;
create policy "bookmarks: insert own" on public.bookmarks
  for insert with check (auth.uid() = user_id);

drop policy if exists "bookmarks: delete own" on public.bookmarks;
create policy "bookmarks: delete own" on public.bookmarks
  for delete using (auth.uid() = user_id);
