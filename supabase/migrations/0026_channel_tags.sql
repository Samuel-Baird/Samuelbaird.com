-- Multi-tag support for channels.
--
-- Adds `channel_types text[]` alongside the legacy single `channel_type`.
-- A trigger keeps `channel_type` in sync as the first element of the array so
-- any code still reading the singular column keeps working until it's removed.

alter table public.channels
  add column if not exists channel_types text[] not null default '{}';

update public.channels
  set channel_types = array[channel_type]
  where channel_type is not null
    and (channel_types is null or array_length(channel_types, 1) is null);

create index if not exists channels_channel_types_idx
  on public.channels using gin (channel_types);

create or replace function public.channels_sync_channel_type()
returns trigger
language plpgsql
as $$
begin
  if new.channel_types is null then
    new.channel_types := '{}';
  end if;

  if array_length(new.channel_types, 1) is null then
    -- array empty: derive from legacy scalar if present
    if new.channel_type is not null then
      new.channel_types := array[new.channel_type];
    end if;
  else
    -- array authoritative: mirror first element into legacy scalar
    new.channel_type := new.channel_types[1];
  end if;
  return new;
end;
$$;

drop trigger if exists channels_sync_channel_type_trg on public.channels;
create trigger channels_sync_channel_type_trg
  before insert or update on public.channels
  for each row execute function public.channels_sync_channel_type();

-- Recreate channel_full view to expose the new array column.
drop view if exists public.channel_full cascade;
create view public.channel_full as
select
  c.id,
  c.youtube_channel_id,
  c.slug,
  c.is_active,
  c.featured,
  c.channel_type,
  c.channel_types,
  c.state,
  c.city,
  c.owned_by,
  c.country_manual,
  c.language_manual,
  c.lds_affiliation_source,
  c.handle,
  c.facebook_url,
  c.instagram_url,
  c.tiktok_url,
  c.x_url,
  c.notes,
  c.created_at,
  c.updated_at,
  coalesce(y.name, c.youtube_channel_id) as name,
  y.description,
  y.country,
  y.default_language as language,
  y.thumbnail_url,
  y.created_at_youtube,
  y.last_synced_at,
  y.last_sync_status,
  y.last_sync_error,
  l.captured_at as stats_captured_at,
  l.subscribers,
  l.total_views,
  l.video_count
from public.channels c
left join public.channel_youtube y on y.channel_id = c.id
left join public.channel_stats_latest l on l.channel_id = c.id;
