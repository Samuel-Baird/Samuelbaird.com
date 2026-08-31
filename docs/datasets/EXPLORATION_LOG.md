# Data Explorer exploration log

One line per dataset: what's been mined for charts, what's left. Datasets
not yet listed here haven't been through a dedicated pass — cross-reference
`data/` against `src/lib/data-explorer.ts`'s `DATASETS` array to find them.

- **pew-atp-w132-2023** (American Trends Panel, Wave 132, spirituality
  battery) — partial, 2026-08-31: had 1 chart (`beyond-this-world.json`,
  "feeling of connection beyond this world"); added 2 more this pass —
  `religious-community.json` (81.4% of Latter-day Saints involved in a
  religious community, highest of any tradition) and `has-cross.json`
  (11.7% of Latter-day Saints have a cross for spiritual purposes, lowest
  of any Christian tradition). Wave has a large SPIR*/DTHLKE battery
  (~50 items) still untouched — good remaining candidates: `DTHLKE_c`
  (dead can provide guidance/protection, LDS 93.5% vs. Catholic 77%/
  Protestant 50%, though thematically close to W143's already-shipped
  "ancestors' spirits" chart — check for overlap before charting),
  `SPIRIMP_W132` (importance of spirituality), `LIFESPIR_W132` (became
  more/less spiritual over time), `SPIRTHINGS` sub-items (jewelry, tattoo/
  piercing, crystals, home shrine).

- **pew-atp-w117-2022** (American Trends Panel, Wave 117, religion &
  technology) — partial, 2026-08-31: had 1 chart (`inperson-attendance.json`,
  "Who's back in the pews"); added 3 more this pass — `watch-online-monthly.json`
  (share watching religious services online/TV monthly; Latter-day Saints
  40%, middling despite leading in-person attendance at 80%), `nontech-prayer-groups.json`
  (share participating in in-person prayer groups/scripture study/religious
  education programs; Latter-day Saints 57%, highest of any tradition),
  and `follows-own-leaders.json` (among social media users, share who follow
  their own religious leaders online; Latter-day Saints 75%, highest of any
  tradition by a wide margin). Wave still has an untouched religion-and-tech
  battery — remaining candidates: `ATTENDPREF_W117` (prefer in-person vs.
  online, small screened subsample), `COVIDCONG2_W117` (own house of worship
  streams services), `NONTECH2_b_W117`/`APPUSE2_b_W117` (religion-focused
  reading/podcasts/videos), `SNSPOST3_W117` (posts about religion on social
  media) — check screener sample sizes per group before charting.
