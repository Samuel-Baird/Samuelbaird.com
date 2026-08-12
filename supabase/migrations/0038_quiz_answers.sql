-- Quiz answers: one row per user per question.
--
-- Deliberately per-question rather than one blob per quiz. Questions belong to
-- a timeline, but a reader can answer them from that timeline's page or from
-- the whole-bank quiz at /quiz, and either way the answer is the same fact
-- about them — storing it once means answering in one place shows up in the
-- other. Results are derived from these rows rather than stored, so changing a
-- question's scoring never leaves a stale saved verdict behind.
--
-- question_id and option_id are content ids from src/lib/quiz/, not foreign
-- keys: the question bank ships with the code. Validity is checked in the
-- server action against that bank before anything is written.
create table if not exists public.quiz_answers (
  user_id uuid not null references auth.users(id) on delete cascade,
  question_id text not null,
  option_id text not null,
  -- Denormalised so a reader's answers can be grouped by timeline without the
  -- database needing to know the question bank.
  timeline text not null,
  updated_at timestamptz not null default now(),
  primary key (user_id, question_id)
);

create index if not exists quiz_answers_user_timeline_idx
  on public.quiz_answers (user_id, timeline);

drop trigger if exists quiz_answers_set_updated_at on public.quiz_answers;
create trigger quiz_answers_set_updated_at
  before update on public.quiz_answers
  for each row execute function public.set_updated_at();

alter table public.quiz_answers enable row level security;

drop policy if exists "quiz_answers: read own" on public.quiz_answers;
create policy "quiz_answers: read own" on public.quiz_answers
  for select using (auth.uid() = user_id);

drop policy if exists "quiz_answers: insert own" on public.quiz_answers;
create policy "quiz_answers: insert own" on public.quiz_answers
  for insert with check (auth.uid() = user_id);

drop policy if exists "quiz_answers: update own" on public.quiz_answers;
create policy "quiz_answers: update own" on public.quiz_answers
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "quiz_answers: delete own" on public.quiz_answers;
create policy "quiz_answers: delete own" on public.quiz_answers
  for delete using (auth.uid() = user_id);
