-- Seed / upsert new channels from "more creators.csv" — batch 6.
-- Only channels with >=1000 subscribers are included; channels with fewer
-- subscribers are intentionally skipped per the new minimum-subscriber policy
-- (see methodology page). Skipped (sub count at time of import):
--   UCwpWEDymijB7ookaGsqMsIg (316), UCk3mE8l0_MUR23q5SEi6cSA (595),
--   UCQsnIBEUk3ibez9AvqhsjbA (171), UCuDPPEamDRNyzkJWiSO2Cvg (603),
--   UCj_3LxWyGAlX6fmOqn3J99A (851), UC_qt7tTG1fLEHS2bHNBC3IA (270),
--   UCjQGXMCQKMYWoq5XL_3qmKA (218), UCcPIQD43dVC8ZmkbBlvzzYQ (699),
--   UCdrdpdhejHQ0KA8eCsgKybg (244).
-- "Come Follow Christ" was in the CSV without a YouTube channel ID and is
-- also skipped.

insert into public.channels (youtube_channel_id, slug, channel_type, city, state, owned_by, is_active)
values
  ('UC10ImcjMuf3EtBjUxCh2Qdg', 'UC10ImcjMuf3EtBjUxCh2Qdg', 'Religious',    null,            null, null, true),
  ('UCSp7McDueBPBFm6MCxznBqw', 'UCSp7McDueBPBFm6MCxznBqw', 'Ancestry',     'Lee''s Summit', 'MO', null, true),
  ('UCn4eQa8iEhaPPU3kph3GQsA', 'UCn4eQa8iEhaPPU3kph3GQsA', 'Critical',     null,            null, null, false),
  ('UCSeoHSALl1j0YCPuAxvkrOQ', 'UCSeoHSALl1j0YCPuAxvkrOQ', 'Critical',     null,            null, null, true),
  ('UCRry4HF5A-OLL861_FAUfyg', 'UCRry4HF5A-OLL861_FAUfyg', 'Religious',    'Kansas City',   'MO', null, true),
  ('UCQLkj5TX9vqhibqdj8yi0Rg', 'UCQLkj5TX9vqhibqdj8yi0Rg', 'Religious',    null,            null, null, true),
  ('UCg0z0-s7yOFDc9PF4YUdOKQ', 'UCg0z0-s7yOFDc9PF4YUdOKQ', 'Investigator', null,            null, null, true),
  ('UChGtUIlEr_pS4ZnEk4uBEaQ', 'UChGtUIlEr_pS4ZnEk4uBEaQ', 'Critical',     null,            null, null, true)
on conflict (youtube_channel_id) do update set
  channel_type = excluded.channel_type,
  city         = excluded.city,
  state        = excluded.state,
  owned_by     = excluded.owned_by,
  is_active    = excluded.is_active,
  updated_at   = now();
