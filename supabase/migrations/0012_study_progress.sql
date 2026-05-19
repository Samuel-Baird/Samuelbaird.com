-- Per-user study reading progress and private notes.
create table if not exists public.study_progress (
  user_id uuid not null references auth.users(id) on delete cascade,
  study_id uuid not null references public.studies(id) on delete cascade,
  status text not null default 'unread' check (status in ('unread', 'read')),
  notes text not null default '',
  updated_at timestamptz not null default now(),
  primary key (user_id, study_id)
);

create index if not exists study_progress_user_idx
  on public.study_progress (user_id, updated_at desc);

alter table public.study_progress enable row level security;

drop policy if exists "study_progress: read own" on public.study_progress;
create policy "study_progress: read own" on public.study_progress
  for select using (auth.uid() = user_id);

drop policy if exists "study_progress: insert own" on public.study_progress;
create policy "study_progress: insert own" on public.study_progress
  for insert with check (auth.uid() = user_id);

drop policy if exists "study_progress: update own" on public.study_progress;
create policy "study_progress: update own" on public.study_progress
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "study_progress: delete own" on public.study_progress;
create policy "study_progress: delete own" on public.study_progress
  for delete using (auth.uid() = user_id);
