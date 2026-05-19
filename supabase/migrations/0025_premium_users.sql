-- Premium user allowlist for future paid/limited capabilities.

create table if not exists public.premium_users (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  name text,
  created_by uuid references public.profiles(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint premium_users_email_lowercase check (email = lower(trim(email)))
);

create unique index if not exists premium_users_email_idx
  on public.premium_users (email);

drop trigger if exists premium_users_set_updated_at on public.premium_users;
create trigger premium_users_set_updated_at
  before update on public.premium_users
  for each row execute function public.set_updated_at();

alter table public.premium_users enable row level security;
