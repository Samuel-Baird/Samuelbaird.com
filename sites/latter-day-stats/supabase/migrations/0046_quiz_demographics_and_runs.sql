-- Traditions lookup: Pew-style religious tradition slugs for the quiz's
-- optional demographic intake. TS constant in
-- src/lib/evangelical-quiz/demographics.ts is the runtime source (the quiz
-- stays zero-network for anonymous takers); these rows exist for FK
-- integrity on tradition_slug columns and admin joins. pew_category maps a
-- slug to the quiz's matchable traditions, powering the self-reported vs
-- matched crosstab's agreement diagonal. Swapping in the full Pew taxonomy
-- later is a data change here + in the TS constant, not a schema change.
create table if not exists public.traditions (
  slug text primary key
    check (slug ~ '^[a-z0-9]+(_[a-z0-9]+)*$'),
  display_label text not null,
  sort_order int not null,
  pew_category text
);

insert into public.traditions (slug, display_label, sort_order, pew_category) values
  ('evangelical_protestant','Evangelical Protestant',1,'Evangelical'),
  ('mainline_protestant','Mainline Protestant',2,'Mainline'),
  ('historically_black_protestant','Historically Black Protestant',3,'Black Protestant'),
  ('roman_catholic','Roman Catholic',4,'Roman Catholic'),
  ('latter_day_saint','Latter-day Saint',5,null),
  ('orthodox_christian','Orthodox Christian',6,null),
  ('other_christian','Other Christian',7,null),
  ('jewish','Jewish',8,null),
  ('muslim','Muslim',9,null),
  ('other_religion','Another religion',10,null),
  ('atheist_agnostic','Atheist / agnostic',11,null),
  ('nothing_in_particular','Nothing in particular',12,null),
  ('prefer_not_to_say','Prefer not to say',13,null)
on conflict (slug) do nothing;

-- Deny-all RLS (0039 house pattern): nothing client-side reads this;
-- server actions and admin pages use the service-role client.
alter table public.traditions enable row level security;

-- Optional demographics on profiles (0037 pattern: nullable adds, no
-- backfill). Rides the existing "profiles: update own" RLS policy.
-- demographics_updated_at doubles as the "already asked" marker - set on
-- both submit and skip, so declining doesn't re-nag on every visit.
alter table public.profiles
  add column if not exists age smallint check (age between 1 and 110),
  add column if not exists gender text
    check (gender in ('male','female','other','prefer_not_to_say')),
  add column if not exists tradition_slug text references public.traditions(slug),
  add column if not exists demographics_updated_at timestamptz;

-- Completed evangelical-quiz runs: append-only snapshots, one row per
-- completion (retakes append). id is client-generated so retries are
-- idempotent; score/percentile/match are recomputed server-side from
-- `answers` before insert - never trusted from the client. Demographic
-- columns are a snapshot at completion time (profile for signed-in,
-- localStorage payload for anonymous). No IP or user-agent columns by
-- design, per the quiz's disclosure copy.
create table if not exists public.evangelical_quiz_runs (
  id uuid primary key,
  user_id uuid references auth.users(id) on delete cascade,
  anon_id uuid,
  age smallint check (age between 1 and 110),
  gender text check (gender in ('male','female','other','prefer_not_to_say')),
  tradition_slug text references public.traditions(slug),
  answers jsonb not null,
  score numeric not null,
  percentile numeric not null,
  matched_tradition text,
  runner_up_tradition text,
  tie boolean not null default false,
  data_version text not null,
  created_at timestamptz not null default now(),
  check (user_id is not null or anon_id is not null)
);

create index if not exists evangelical_quiz_runs_user_idx
  on public.evangelical_quiz_runs (user_id);
create index if not exists evangelical_quiz_runs_anon_idx
  on public.evangelical_quiz_runs (anon_id) where user_id is null;

-- Deny-all RLS: all writes go through validated server actions using the
-- service-role client; all reads are admin-only pages on the same client.
alter table public.evangelical_quiz_runs enable row level security;
