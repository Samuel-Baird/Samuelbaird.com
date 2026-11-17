-- Unified contact / correction inbox

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  category text not null check (category in (
    'general',
    'correction',
    'channel_suggestion',
    'study_suggestion',
    'bug'
  )),
  name text,
  email text,
  page_ref text,
  body text not null,
  user_id uuid references auth.users(id) on delete set null,
  resolved boolean not null default false,
  resolved_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists messages_created_idx
  on public.messages (created_at desc);
create index if not exists messages_resolved_idx
  on public.messages (resolved, created_at desc);

alter table public.messages enable row level security;

-- Anyone (anon or authenticated) may submit a message.
drop policy if exists "messages: public insert" on public.messages;
create policy "messages: public insert" on public.messages
  for insert with check (true);

-- Only admins can read messages.
drop policy if exists "messages: admins read" on public.messages;
create policy "messages: admins read" on public.messages
  for select using (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );

-- Only admins can mark resolved / update.
drop policy if exists "messages: admins update" on public.messages;
create policy "messages: admins update" on public.messages
  for update using (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );

drop policy if exists "messages: admins delete" on public.messages;
create policy "messages: admins delete" on public.messages
  for delete using (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_admin)
  );
