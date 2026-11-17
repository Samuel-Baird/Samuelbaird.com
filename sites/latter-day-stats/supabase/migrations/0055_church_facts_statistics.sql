-- Church "Facts and Statistics" data, scraped from
-- churchofjesuschrist.org/learn/facts-statistics by
-- scripts/church-facts-statistics/scrape.mjs.
--
-- Three flat tables: country rows, continent rollups, and the worldwide total.
-- Figures are the church's own; `stats_year` is the year the figures describe
-- and `last_updated` is when the church last touched the record (a handful of
-- countries are older than the rest, e.g. Cape Verde and Czech Republic 2021).
--
-- RLS posture: public read (it is public data), no write policies, so only the
-- service role can write. Rows are loaded by 0056_seed_church_facts_statistics.sql.

create table if not exists public.church_continent_stats (
  continent text primary key,
  slug text not null unique,
  stats_year int,
  last_updated timestamptz,
  membership bigint,
  congregations int,
  stakes int,
  districts int,
  missions int,
  temples int,
  family_history_centers int
);

create table if not exists public.church_worldwide_stats (
  stats_year int primary key,
  last_updated timestamptz,
  membership bigint,
  congregations int,
  stakes int,
  missions int,
  temples int
);

create table if not exists public.church_country_stats (
  slug text primary key,
  country text not null unique,
  continent text not null references public.church_continent_stats(continent),
  capital text,
  official_languages text[] not null default '{}',
  stats_year int,
  last_updated timestamptz,
  membership bigint,
  congregations int,
  wards int,
  branches int,
  stakes int,
  districts int,
  missions int,
  temples int,
  family_history_centers int,
  -- Set when the church page could not supply this country's own figures
  -- (e.g. Andorra's page returns Greece's record); figures are null then.
  data_note text,
  source_url text not null,
  constraint church_country_stats_congregations_split
    check (wards is null or branches is null or congregations is null
           or wards + branches = congregations)
);

create index if not exists church_country_stats_continent_idx
  on public.church_country_stats (continent);

alter table public.church_continent_stats enable row level security;
alter table public.church_worldwide_stats enable row level security;
alter table public.church_country_stats enable row level security;

drop policy if exists "church_continent_stats: public read" on public.church_continent_stats;
create policy "church_continent_stats: public read" on public.church_continent_stats
  for select using (true);

drop policy if exists "church_worldwide_stats: public read" on public.church_worldwide_stats;
create policy "church_worldwide_stats: public read" on public.church_worldwide_stats
  for select using (true);

drop policy if exists "church_country_stats: public read" on public.church_country_stats;
create policy "church_country_stats: public read" on public.church_country_stats
  for select using (true);
