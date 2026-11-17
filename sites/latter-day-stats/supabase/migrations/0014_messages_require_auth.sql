-- Require an authenticated account for contact form submissions.
-- This keeps casual spam out before it reaches the application code.

drop policy if exists "messages: public insert" on public.messages;
drop policy if exists "messages: authenticated insert" on public.messages;

create policy "messages: authenticated insert" on public.messages
  for insert
  to authenticated
  with check (auth.uid() = user_id and user_id is not null);
