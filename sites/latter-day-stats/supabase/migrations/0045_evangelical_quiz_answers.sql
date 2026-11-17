-- Evangelical quiz answers: one row per user per statement.
--
-- Mirrors quiz_answers (0038): per-question rather than one blob, so the
-- summary (score, percentile, tradition match, breakdown) is always derived
-- from these rows at read time rather than stored - changing the scoring
-- constants or adding a statement never leaves a stale saved verdict behind.
--
-- Unlike quiz_answers, this quiz is playable with no account (see
-- scripts/evangelical-quiz/README.md and the original build spec) - saving
-- is opt-in for signed-in readers only, never a login requirement. The save
-- action must not redirect an anonymous reader; it just does nothing.
--
-- item_id is a content id from src/lib/evangelical-quiz/data.json, not a
-- foreign key - the item bank ships with the code, validated in the server
-- action before anything is written. response_index is the chosen option's
-- index into that item's `scale` array at save time; data_version records
-- which build of data.json produced that scale, for interpretability if the
-- workbook is later rebuilt with a different item order.
create table if not exists public.evangelical_quiz_answers (
  user_id uuid not null references auth.users(id) on delete cascade,
  item_id text not null,
  response_index smallint not null,
  data_version text not null,
  updated_at timestamptz not null default now(),
  primary key (user_id, item_id)
);

drop trigger if exists evangelical_quiz_answers_set_updated_at on public.evangelical_quiz_answers;
create trigger evangelical_quiz_answers_set_updated_at
  before update on public.evangelical_quiz_answers
  for each row execute function public.set_updated_at();

alter table public.evangelical_quiz_answers enable row level security;

drop policy if exists "evangelical_quiz_answers: read own" on public.evangelical_quiz_answers;
create policy "evangelical_quiz_answers: read own" on public.evangelical_quiz_answers
  for select using (auth.uid() = user_id);

drop policy if exists "evangelical_quiz_answers: insert own" on public.evangelical_quiz_answers;
create policy "evangelical_quiz_answers: insert own" on public.evangelical_quiz_answers
  for insert with check (auth.uid() = user_id);

drop policy if exists "evangelical_quiz_answers: update own" on public.evangelical_quiz_answers;
create policy "evangelical_quiz_answers: update own" on public.evangelical_quiz_answers
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "evangelical_quiz_answers: delete own" on public.evangelical_quiz_answers;
create policy "evangelical_quiz_answers: delete own" on public.evangelical_quiz_answers
  for delete using (auth.uid() = user_id);
