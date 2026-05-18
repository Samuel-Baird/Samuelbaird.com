-- Studies: standardized sections (findings, limitations, flagged methodology)

alter table public.studies
  add column if not exists findings text[] not null default '{}',
  add column if not exists limitations text,
  add column if not exists flagged_problematic boolean not null default false,
  add column if not exists flag_reason text,
  add column if not exists context_note text;

create index if not exists studies_flagged_idx
  on public.studies (flagged_problematic)
  where flagged_problematic = true;
