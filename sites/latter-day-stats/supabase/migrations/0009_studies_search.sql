-- Full-text search over studies (title, authors, abstract, tags)
-- Uses a trigger because to_tsvector with implicit regconfig isn't immutable enough
-- for a generated column.

alter table public.studies
  add column if not exists search_tsv tsvector;

create or replace function public.studies_search_tsv_refresh()
returns trigger
language plpgsql
as $$
begin
  new.search_tsv :=
    to_tsvector(
      'english'::regconfig,
      coalesce(new.title, '') || ' ' ||
      coalesce(array_to_string(new.authors, ' '), '') || ' ' ||
      coalesce(new.abstract, '') || ' ' ||
      coalesce(array_to_string(new.tags, ' '), '')
    );
  return new;
end;
$$;

drop trigger if exists studies_search_tsv_trg on public.studies;
create trigger studies_search_tsv_trg
  before insert or update of title, authors, abstract, tags on public.studies
  for each row execute function public.studies_search_tsv_refresh();

-- Backfill
update public.studies set search_tsv =
  to_tsvector(
    'english'::regconfig,
    coalesce(title, '') || ' ' ||
    coalesce(array_to_string(authors, ' '), '') || ' ' ||
    coalesce(abstract, '') || ' ' ||
    coalesce(array_to_string(tags, ' '), '')
  );

create index if not exists studies_search_tsv_idx
  on public.studies using gin (search_tsv);

create index if not exists studies_tags_gin_idx
  on public.studies using gin (tags);
