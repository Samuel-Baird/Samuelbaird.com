alter table public.channels
  add column if not exists channel_type text,
  add column if not exists language text,
  add column if not exists state text,
  add column if not exists city text,
  add column if not exists owned_by text,
  add column if not exists handle text;

create index if not exists channels_channel_type_idx
  on public.channels (channel_type);

create index if not exists channels_handle_idx
  on public.channels (handle);
