-- Seed / upsert 26 channels from updated-1.csv (batch 5 — new rows only;
-- the first 80 rows in that file are already covered by migration 0018).

insert into public.channels (youtube_channel_id, slug, channel_type, city, state, owned_by, is_active)
values
  ('UCyEs326admEf6ymfk5knRkw', 'UCyEs326admEf6ymfk5knRkw', 'Critical',    null,          null,     null,          true),
  ('UCL0WbeBUAAOT04VZxaJapSw', 'UCL0WbeBUAAOT04VZxaJapSw', 'Religious',   null,          null,     null,          false),
  ('UCLX_I1gnLyaejAulCaP_7vQ', 'UCLX_I1gnLyaejAulCaP_7vQ', 'Church',      null,          null,     'Church',      true),
  ('UC39wTXHUl7X_evZvT0bGiqA', 'UC39wTXHUl7X_evZvT0bGiqA', 'Church',      null,          null,     'Church',      true),
  ('UCenBG7hxMzeq7jyWv9fSncA', 'UCenBG7hxMzeq7jyWv9fSncA', 'Religious',   null,          null,     null,          true),
  ('UCjIAv6oCjoGfwbQIwf8Oj_A', 'UCjIAv6oCjoGfwbQIwf8Oj_A', 'Religious',   null,          'NM',     null,          true),
  ('UCvTSmw2wl5xCBQm-_6G-D6Q', 'UCvTSmw2wl5xCBQm-_6G-D6Q', 'Religious',   null,          'Canada', null,          true),
  ('UCknoI9jFTVpfoe39OwSuLZQ', 'UCknoI9jFTVpfoe39OwSuLZQ', 'Religious',   null,          null,     null,          true),
  ('UCtkLPAJ2amGTmEkUTZEaVBQ', 'UCtkLPAJ2amGTmEkUTZEaVBQ', 'Religious',   null,          null,     null,          false),
  ('UCdEn_305X2zVrFm7Mf14dPQ', 'UCdEn_305X2zVrFm7Mf14dPQ', 'Religious',   null,          null,     null,          true),
  ('UCI9fpaX6IANUTajB2_4-tbQ', 'UCI9fpaX6IANUTajB2_4-tbQ', 'Religious',   null,          'Spain',  null,          true),
  ('UCIE1rkt6qovlO-frbHg71Rw', 'UCIE1rkt6qovlO-frbHg71Rw', 'Religious',   null,          null,     null,          true),
  ('UCx7CJu9uq8PTpq5pG3fOfIQ', 'UCx7CJu9uq8PTpq5pG3fOfIQ', 'Religious',   null,          null,     null,          true),
  ('UC0pLChxPxkYitL5-yg6HgAA', 'UC0pLChxPxkYitL5-yg6HgAA', 'Religious',   null,          null,     null,          true),
  ('UCSlmU_LBLolo-9n85PTfCwA', 'UCSlmU_LBLolo-9n85PTfCwA', 'Critical',    null,          null,     null,          true),
  ('UCdrqnSKFIOzNDOmJSjATE6g', 'UCdrqnSKFIOzNDOmJSjATE6g', 'Church',      null,          null,     'Church',      true),
  ('UCnQaEhkHWl4ytK0ALDey85w', 'UCnQaEhkHWl4ytK0ALDey85w', 'Religious',   null,          null,     null,          true),
  ('UCpQxtFsUI9fKAgKNBlbsylA', 'UCpQxtFsUI9fKAgKNBlbsylA', 'Apologetics', null,          null,     null,          true),
  ('UCwayy4vjn_8Vx9i7JIpC2ow', 'UCwayy4vjn_8Vx9i7JIpC2ow', 'Religious',   null,          null,     null,          true),
  ('UCEPz7ejobmEkXiMFmsnNcRw', 'UCEPz7ejobmEkXiMFmsnNcRw', 'Church',      null,          null,     'Church',      true),
  ('UCMg-xWl-z29AIN8do0faNaQ', 'UCMg-xWl-z29AIN8do0faNaQ', 'Religious',   'Utah County', 'UT',     'Lynzi Clyde', true),
  ('UCVVt1NOMv-nZRdwdN0YawXw', 'UCVVt1NOMv-nZRdwdN0YawXw', 'Critical',    null,          null,     null,          true),
  ('UCPBqd6vXug3NQOPTGauAyMw', 'UCPBqd6vXug3NQOPTGauAyMw', 'Church',      null,          null,     'Church',      true),
  ('UCM7cbpbRGF_wAvjSTNKHsRA', 'UCM7cbpbRGF_wAvjSTNKHsRA', 'Religious',   null,          null,     null,          true),
  ('UChjEQUh6qC7-AlH4Zh_MwFA', 'UChjEQUh6qC7-AlH4Zh_MwFA', 'Religious',   null,          null,     null,          true),
  ('UCiPDUvVNqeIQhex0_4hMERw', 'UCiPDUvVNqeIQhex0_4hMERw', 'Religious',   null,          null,     null,          true)
on conflict (youtube_channel_id) do update set
  channel_type = excluded.channel_type,
  city         = excluded.city,
  state        = excluded.state,
  owned_by     = excluded.owned_by,
  is_active    = excluded.is_active,
  updated_at   = now();
