-- Enforce the new minimum-subscriber policy: channels with fewer than 1,000
-- subscribers (or no recorded stats) are removed from the catalog to keep
-- YouTube Data API quota costs sustainable. Cascading FKs on channel_stats,
-- channel_youtube, channel_socials, etc. handle dependent rows.
--
-- Subscriber counts captured at time of writing (2026-05-19) from
-- channel_stats_latest.

delete from public.channels
where youtube_channel_id in (
  'UChjEQUh6qC7-AlH4Zh_MwFA','UCta9ZWDY95GMnMFZdqkfq1w','UCmugDAfPv3uysim0HmQe85A',
  'UCpQxtFsUI9fKAgKNBlbsylA','UCVFL50rVv4O0REBZYr93q_Q','UCl0mSlNPGoXAlNT27veV1dA',
  'UC0KCTqlMiZ6QsOpcAh1jx1Q','UC-kMAhFUfr55FQEMYsET0QA','UCc1_qgYXADqNH5nJsbtUaZA',
  'UC2nLd_yrneAOeTQvnx-OaNw','UCh280X-ZB7Vf12udX_7kZ0Q','UCj_3LxWyGAlX6fmOqn3J99A',
  'UCV3bQaVdzbianf3XprIqyVA','UC0pLChxPxkYitL5-yg6HgAA','UC8nnyKFyjqFsXB_fDTWuVIA',
  'UC_-q-lIBnzzyB0BKISrmcCQ','UCEceTBOm8ZNz5yudrV2Z0tQ','UChVuASWRKMk-n4resMaFfEQ',
  'UCVVt1NOMv-nZRdwdN0YawXw','UCDIA7na0zrI-NtdnXPE1yhg','UCS8SFlYwiqDoTPQHJpTasRw',
  'UCRU72ZtAGL2CTTb_K3I4CKA','UCRpLQ76COpXkaOEc3Oo6NoQ','UCTNK6LIS0Ke0ofBWIUmWPNg',
  'UCyEs326admEf6ymfk5knRkw','UC8W69RxeGiWhKcfsxVyeIUA','UCpezVg6lkEfkeEoTdOdbjig',
  'UCuDPPEamDRNyzkJWiSO2Cvg','UCvU1xudd-yNHECibH8AaHUA','UCYV6w3DfdL90Kx25eny2jew',
  'UCbD1Pm0TOcRK2zaCrwgcTTg','UCSlmU_LBLolo-9n85PTfCwA','UCKjiCfQV_Uw4JxczNXM_oRw',
  'UCLf2y5Kt0CYeFPXMTHBgXhg','UC8PPvHzJ9TPad5qWHAYmJHA','UCocFtIzP_6VWXgGWVRPzPeQ',
  'UCtGm9BMgK6tDRwj6ReQcPZw','UCZ_kURL6ICI7Q3XFdKT1w6g','UC8xDEFFmc20O945JN8e-uoQ',
  'UCM7cbpbRGF_wAvjSTNKHsRA','UCwayy4vjn_8Vx9i7JIpC2ow','UCf8T7ZdEUibXa1BmMru-O_w',
  'UCYi_-dQ8eP_al0rg73bj7SA','UCiVblqPv8HIAJxe-qDdXvDQ','UCSFheLzrWf6LHrUNyqiNrCA',
  'UCIE1rkt6qovlO-frbHg71Rw','UCu_FGWjEUvFeS3tMNwbSc4A','UCu5C5cITg74Pan5NnT9a9PA',
  'UCenBG7hxMzeq7jyWv9fSncA','UCmUkJ1wrz5ld86GeLbo-L9g','UC6nQ1HxVl0Ky7LtlT0G2iyA',
  'UCksFY6uP8K5UEMghFue7AWA','UCWkVSgQolt8Af-nw2w1MekQ','UCNYun19DjvHSJjrn2HiS8nw',
  'UCcsZhpmYdAPzTC2x__JREiA','UCnQaEhkHWl4ytK0ALDey85w','UCR0ONc9S_6Ni6Fl4lHd6MLA',
  'UCicTb-Z1c7xeutxkHM-xy6w','UC5Njt-96Uor0p-jhnoZHwMQ','UC86Rjr7VBtXPoqMyjHVQz1Q',
  'UCgfDFzn_Vd3F0BfWwhpNGqw','UCY62oGTp1JfbxB5Jjb-ZlA','UCeQYJQ0PKlT3rp1xE15K1Fg',
  'UCAnRNCf5m5I0pEdqYMfGOgA','UCL0WbeBUAAOT04VZxaJapSw','UCVvVB4PM3bhMZk_EY5t8ntw',
  'UCrsTCEZc7x2Co0VDU2nAYew','UCu92CJ0MCI6c7OhXfKF66Tw','UCtkLPAJ2amGTmEkUTZEaVBQ',
  'UCz4gtc_KIUDjFiovK2jLBnw'
);
