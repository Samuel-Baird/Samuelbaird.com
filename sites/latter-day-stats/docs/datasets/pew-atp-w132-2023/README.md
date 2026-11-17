# Pew Research Center — American Trends Panel, Wave 132 (August 2023)

A general-topic wave of Pew's American Trends Panel: 11,201 U.S. adults
surveyed online (Web mode, full panel) July 31–Aug. 6, 2023, in English and
Spanish. Most of the wave is a large battery of belief/practice items about
spirituality (belief in God, souls, spirits, unseen forces, near-death-style
experiences, etc.), plus separate short batteries on women in political
leadership and on public attitudes toward artificial intelligence.

Unlike Wave 70 (2020) and most other ATP waves in this pipeline, **Wave 132
does not carry an `F_RELTRAD` frame variable** — confirmed by reading the
raw `.sav`'s own column list (`ATP W132 Readme.txt` has no `F_RELTRAD`
section, and it isn't among the 140 columns pyreadstat reads from the file).
The finest-grained religion breakout this wave offers instead is `F_RELIG`
(Pew's standard religion question, un-collapsed — Latter-day
Saints/Mormons are code `3.0`, labeled `"Mormon (Church of Jesus Christ of
Latter-day Saints or LDS)"` in the .sav's own value labels). There's also a
coarser `F_RELIGCAT1` (Protestant/Catholic/Unaffiliated/Other, no Mormon
category of its own) and `CHRELIG_W132` (childhood religion, same code
scheme as `F_RELIG`). Charts from this wave use `F_RELIG` to keep "Mormon"
as its own row, matching every other flagship chart's convention — just
note the different frame-variable name if you're used to `F_RELTRAD` from
the other ATP waves in this pipeline.

## What's in here

Raw microdata lives in `data/pew-atp-w132-2023/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `ATP W132.sav` | SPSS microdata, N=11,201 |
| `ATP W132 Readme.txt` | Pew's own readme, incl. weight variable name and a list of report releases from this wave |
| `ATP W132 Codebook.xlsx` | Full variable/value-label codebook |
| `ATP W132 Methodology.pdf` | Sample design, weighting |
| `ATP W132 Questionnaire.pdf` | Full survey instrument |

Weight variable: `WEIGHT_W132`.

This wave arrived with several known report releases (listed in the
readme), most relevantly Pew's Dec. 7, 2023 "Spirituality Among Americans"
(https://www.pewresearch.org/religion/2023/12/07/spirituality-among-americans/)
and its Jan. 17, 2024 short-read "Around 4 in 10 Americans have become more
spiritual over time" — this wave's large SPIR*/BEYONDEXP/DTHLKE battery is
almost certainly the source data for both. Neither report was checked
question-by-question against this wave before shipping the chart below;
confirm the specific figure against the published report text before citing
it as replicating Pew's own published number, rather than assuming Pew
computed it the same way (same population, same rounding) as the script
here.

## Status

Seven charts shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-atp-w132-2023`), using the shared
chart shape in `scripts/flagship-charts/common.py`:

- `beyond-this-world.json` (share who have ever had "a sudden or
  unexpected feeling of connection with something from beyond this world,"
  `BEYONDEXP_W132`, asked of all respondents) — computed by
  `beyond_this_world.py`, rendered by `render_beyond_this_world_chart.py`.
  Latter-day Saints report this at 75.5%, clearly higher than every other
  named tradition in the wave (next highest among named groups: Protestants
  at 49.8%) — picked over the wave's many belief-in-God-style items, where
  Mormons cluster with other highly religious groups rather than standing
  out on their own.
- `religious-community.json` (share involved in "a religious community,
  such as a church or religious congregation," `SPIRCOM1_a_W132`, asked of
  all respondents) — computed by `religious_community.py`, rendered by
  `render_religious_community_chart.py`. Latter-day Saints report this at
  81.4%, the highest of any named tradition (next: Orthodox Christian
  77.2%, Protestant 59.0%, Catholic 49.6%) — matches the Church's
  congregational-participation emphasis (ward/stake callings, weekly
  meetings, ministering).
- `has-cross.json` (share who have a cross "for spiritual purposes,"
  `SPIRTHINGS_e_W132`, asked of all respondents) — computed by
  `has_cross.py`, rendered by `render_has_cross_chart.py`. Latter-day
  Saints report this at just 11.7%, far below every other named Christian
  tradition (Protestant 41.7%, Catholic 72.8%, Orthodox Christian 82.0%) —
  tracks the Church's well-known choice not to use the cross as a symbol of
  the faith.
- `spirituality-important.json` (share calling spirituality "very
  important" in their life, `SPIRIMP_W132`, asked of all respondents) —
  computed by `spirituality_important.py`, rendered by
  `render_spirituality_important_chart.py`. Latter-day Saints report this
  at 66.5%, the highest of any Christian tradition (Protestant 60.1%,
  Catholic 36.3%) and essentially tied with Muslims (66.7%).
- `tattoo-piercing-spiritual.json` (share who have a tattoo or piercing
  "for spiritual purposes," `SPIRTHINGS_b_W132`, one item in the same
  battery as `has-cross.json`) — computed by
  `tattoo_piercing_spiritual.py`, rendered by
  `render_tattoo_piercing_spiritual_chart.py`.
- `dead-aware-living.json` (share who believe people who have died "can be
  aware of things going on among those who are still living,"
  `DTHLKE_a_W132`, one item in a six-part "Do you believe people who have
  died can..." battery asked of all respondents) — computed by
  `dead_aware_living.py`, rendered by `render_dead_aware_living_chart.py`.
  Latter-day Saints report this at 89.9%, the highest of any named
  tradition by a wide margin (next: Catholic 73.6%, Orthodox Christian
  64.2%, Protestant 57.6%) — ties to LDS doctrine of an active spirit world
  (D&C 138) and to temple/family-history work performed on behalf of
  deceased ancestors.
- `reunited-with-loved-ones.json` (share who believe people who have died
  "can be united with other loved ones who have already died,"
  `DTHLKE_f_W132`, the last item in the same battery as
  `dead-aware-living.json`) — computed by `reunited_with_loved_ones.py`,
  rendered by `render_reunited_with_loved_ones_chart.py`. Latter-day Saints
  report this at 98.4%, the highest of any named tradition (next: Orthodox
  Christian 95.2%, Catholic 84.5%, Protestant 79.8%) — maps directly onto
  the LDS doctrine of eternal marriage and family sealing (D&C 132), which
  makes permanent reunion with family a defining, distinctive feature of
  LDS theology rather than a generic afterlife hope. Shipped alongside
  `dead-aware-living.json` as a tight two-chart cluster from the same
  DTHLKE battery — distinct from `has-cross.json`/`tattoo-piercing-
  spiritual.json` (physical objects, not beliefs) and from
  `pew-atp-w143-2024`'s `believe-ancestor-spirits.json` (a different
  wave's merged help/harm framing).

Further charts from this dataset should follow the same two-stage pattern.
Groups under 30 valid respondents are dropped (`MIN_VALID_N` convention,
same as every other chart in this pipeline). Remaining untouched
candidates in the DTHLKE/SPIRTHINGS battery: `DTHLKE_b`/`DTHLKE_c` (both
close to already-shipped material - `c`'s "assistance/protection/guidance"
framing overlaps `pew-atp-w143-2024`'s ancestor-spirits chart, `b`'s
"communicate with the living" is close to this pass's `dead-aware-living`),
`DTHLKE_d` (dead can harm the living, negative framing), `DTHLKE_e`
(reincarnation, likely close to `pew-atp-w143-2024`'s already-shipped
reincarnation chart), `SPIRTHINGS_a`/`SPIRTHINGS_c` (jewelry/crystals for
spiritual purposes, weak/no distinctive LDS story once computed), and
`LIFESPIR_W132` (became more/less spiritual over time - Mormon 50.1% is
mid-pack, no distinctiveness story).
