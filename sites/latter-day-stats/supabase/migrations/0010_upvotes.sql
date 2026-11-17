-- Public upvotes for channels & studies (mirrors bookmarks pattern from 0003)
create table if not exists public.upvotes (
  user_id uuid not null references auth.users(id) on delete cascade,
  target_type text not null check (target_type in ('channel', 'study')),
  target_id uuid not null,
  created_at timestamptz not null default now(),
  primary key (user_id, target_type, target_id)
);

create index if not exists upvotes_target_idx
  on public.upvotes (target_type, target_id);

alter table public.upvotes enable row level security;

drop policy if exists "upvotes: read all" on public.upvotes;
create policy "upvotes: read all" on public.upvotes
  for select using (true);

drop policy if exists "upvotes: insert own" on public.upvotes;
create policy "upvotes: insert own" on public.upvotes
  for insert with check (auth.uid() = user_id);

drop policy if exists "upvotes: delete own" on public.upvotes;
create policy "upvotes: delete own" on public.upvotes
  for delete using (auth.uid() = user_id);

-- Aggregate view (readable via anon — RLS on upvotes already allows select)
create or replace view public.upvote_counts as
  select target_type, target_id, count(*)::int as upvotes
  from public.upvotes
  group by target_type, target_id;

grant select on public.upvote_counts to anon, authenticated;
