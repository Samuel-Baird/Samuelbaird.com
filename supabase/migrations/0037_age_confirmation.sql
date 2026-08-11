-- COPPA: record that a user affirmatively confirmed they're 13+ before their
-- account was created. Nullable/no backfill — existing accounts predate this
-- gate and there's no reliable way to retroactively confirm their age.
alter table public.profiles
  add column if not exists age_confirmed_at timestamptz;
