# Data Explorer exploration log

One line per dataset: what's been mined for charts, what's left. Datasets
not yet listed here haven't been through a dedicated pass — cross-reference
`data/` against `src/lib/data-explorer.ts`'s `DATASETS` array to find them.

- **pew-hispanics-religion-2007** (Pew Hispanic Center/Pew Forum Survey of
  Latinos, 2006) — partial, 2026-08-31: had 1 chart
  (`latino-religious-converts.json`). Added 3 more this pass, all broken
  out by the survey's own recoded `relig` variable (34 unweighted Latino
  Mormon respondents, just over the 30-valid floor; every item below still
  cleared it at n=34) — `importance-of-religion.json` (84.8% of Latino
  Mormons call religion "very important" in their own life, 2nd only to
  Jehovah's Witnesses at 92.1%), `weekly-attendance.json` (67.4% of Latino
  Mormons attend religious services weekly or more, again 2nd only to JWs
  at 74.5%), and `volunteered-for-church.json` (66.5% of Latino Mormons
  volunteered time to their congregation in the past year — highest of any
  group by a wide margin, well above Protestants' 52.7% and more than
  double Catholics' 26.2%, plausibly reflecting the Church's lay-ministry/
  callings model). One item was checked and dropped: `qn52_d` (belief
  Jesus will return in the respondent's lifetime) has only 25 valid Mormon
  respondents once refusals are excluded, under the 30 floor. Dataset
  still has a large untouched battery, but it's mostly Catholic-specific
  (F1406_qn1-F1406_qn36, gated to a Catholic recontact subsample with its
  own weight) or thematically thin for LDS (political/immigration items,
  Hispanic-clergy-representation items). Remaining general candidates
  worth checking: `qn14_d` (favorability toward Mormons, rated by other
  groups — thematically close to the already-shipped w114-2022
  `relfav-mormons` chart, check for overlap first), `qn53` (crucifix/
  religious objects displayed at home), `qn25` (born-again/evangelical
  self-identification).

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

- **pew-atp-w114-2022** (American Trends Panel, Wave 114, September 2022) —
  partial, 2026-08-31: had 1 chart (`christian-nation.json`). Added 3 more
  this pass, all broken out by F_RELIG (this wave has no F_RELTRAD frame
  variable) — `essent-jesus.json` (83.5% of Mormons call a personal
  relationship with Jesus Christ essential to their faith, highest of any
  Christian tradition, vs. 79.6% Protestant/64.2% Catholic/49.8% Orthodox),
  `essent-attend.json` (49.1% of Mormons call regular service attendance
  essential, 2nd only to Muslims at 57.5% and well above every other
  Christian tradition), and `relfav-mormons.json` (how outsiders see
  Latter-day Saints: Mormons rate their own group 81.1% favorable while
  every other group clusters near the 18.9% national average — Hindu
  highest among outsiders at 25.9%). Wave still has an untouched battery
  worth checking for remaining candidates: other ESSENT_* sub-items
  (a/g/h/i/j — believing in God, patriotism, family traditions, moral
  living, community), other RELFAV_* sub-items (views of Evangelicals,
  Catholics, Jews, Muslims, Atheists, Mainline Protestants by F_RELIG),
  REL4_* ("do you personally know a Mormon" by F_RELIG), and CHRNAT1a/b
  (awareness/favorability toward "Christian nationalism").

- **pew-atp-w162-2025** (American Trends Panel, Wave 162, February 2025 —
  Catholicism/religion's place in American life) — partial, 2026-08-31: had
  4 charts, all Catholic-specific (`religious-conflict.json`,
  `cathessent.json`, `confession-frequency.json`, and a devotion-to-saints
  chart from `holiday-batch.json`). Added 2 more this pass, both drawn from
  general (non-Catholic-coded) items broken out by RELIG_W162 (this wave has
  no F_RELTRAD frame variable) — `attendance.json` (52.3% of Latter-day
  Saints attend religious services in person at least weekly, highest of
  any group in the wave, ahead of Muslims at 43.4% and every other Christian
  tradition) and `wear-religious-items.json` (50.5% of Latter-day Saints
  wear religious items/symbols or carry them with them at least weekly,
  2nd only to Orthodox Christians at 51.2%). Wave's remaining items are
  almost entirely Catholic-specific (CATHESSENT_*, CATHATTEND*, CCHRCH_*,
  parish/Mass items) — not usable for further LDS breakouts; the only other
  general items are RELART_W162 (religious objects/artwork at home, but
  worded around cross/crucifix/pictures of Jesus or saints — too close to
  the shipped devotion-to-saints chart) and PRACTICEA_BIB_W162/
  PRACTICEA_OTHSCRPT_W162 (scripture reading, but skip-logic-gated to a
  small subsample — only 35 and 100 valid Mormon respondents respectively).
  Consider this wave essentially fully mined.

- **pew-atp-w70-2020** (American Trends Panel, Wave 70, July 2020 —
  religion during COVID) — partial, 2026-08-31: had 5 charts (online
  worship, prayer, in-person attendance, financial threat, BLM sermons).
  Added 3 more this pass, all broken out by F_RELTRAD — `scripture-covid-coping.json`
  (48.4% of Latter-day Saints read scripture daily to cope with the
  pandemic, highest of any tradition, vs. 38.0% Historically Black
  Protestant/36.3% Evangelical and far above Catholic/Mainline at ~13%),
  `religious-org-giving-covid.json` (56.9% of Latter-day Saints volunteered
  or donated through a religious organization because of COVID, well
  ahead of 2nd-place Evangelical Protestant at 32.0%), and
  `congregation-donating.json` (93.3% of Latter-day Saints who attend at
  least monthly kept donating to their congregation during COVID, highest
  of any tradition, vs. 86-87% for Evangelical/Mainline/Historically Black
  Protestant and 77% for Catholic/Jewish). Wave still has an untouched
  slate of items worth checking for remaining candidates: COVIDVOL2_b_W70
  (turned to a religious org for help with bills/housing/food during
  COVID — receiving rather than giving), COVIDLESSON1/COVIDLESSON2_W70
  (belief there's a lesson from COVID, and whether God sent it), and
  ATTENDFUT1/ATTENDFUT2_W70 (post-pandemic attendance intentions, but
  these are speculative/hypothetical and thematically thinner).

- **pew-black-faith-2021** (Pew's "Faith Among Black Americans," fielded
  2019-2020) — partial, 2026-08-31: had 1 chart (`women-leaders.json`).
  Added 3 more this pass, all broken out by RELIGMOD using "black faith
  black respondents.sav" (34 valid Mormon respondents, above the 30-N
  floor) — `convert-duty.json` (61.4% of Black Mormons believe people of
  faith have a religious duty to convert nonbelievers, near the top
  alongside Jehovah's Witnesses at 65.2% and Protestants at 63.7% — ties to
  LDS full-time missionary practice), `god-responds.json` (58.2% of Black
  Mormons say God ever talks directly with them, 2nd only to Protestants
  at 59.3% — ties to LDS personal-revelation doctrine), and
  `turned-to-church-for-help.json` (58.2% of Black Mormons have ever
  turned to their congregation for help with bills, housing, or food — the
  highest of any group by a wide margin, nearly double Protestants' 32.1%
  — reflects the Church's organized welfare system: fast offerings,
  bishop's storehouses, Latter-day Saint Charities). Dataset has a large
  untouched battery worth checking for remaining candidates: ESSENT_a-f
  (what's essential to being a moral/religious person), PERSDO1_a-e
  (meditate, read scripture, burn candles/incense, pray at a shrine,
  consult a diviner), TYPEGODSUM/GODBELIEFSMOD_b/d (nature and character
  of God), CLERGYSSM (should clergy perform same-sex marriages — plausible
  but check for overlap with already-shipped SSM-favorability charts in
  pew-rls-2014 and pew-latin-america-2014 first), COMMINFL1/2 and
  BLKEQL1_c (predominantly Black churches' influence — Black-church-
  specific framing, likely not a good LDS fit), and CHURCHLOOK_a-e
  (what matters when choosing a new congregation). Also has an "all
  respondents.sav" file (adds a ~4,574-person non-Black comparison sample,
  109 total Mormon respondents) not yet used for anything — could support
  a Black-vs-non-Black-Mormon comparison in a future pass.

- **pew-rls-2014** (2014 Religious Landscape Study) — partial, 2026-08-31:
  had 5 charts (samesex-marriage, weekly-attendance, certainty-of-god,
  millennial-share, nones-growth). Added 3 more this pass, all broken out
  by RELTRAD — `view-of-god.json` (91.8% of Mormons say God is a person one
  can have a relationship with rather than an impersonal force, highest of
  any tradition, ties to LDS teaching of an embodied, personal Godhead),
  `eternal-life-non-christian.json` (84.2% of Mormons say some non-Christian
  religions can also lead to eternal life, well above Evangelical
  Protestants' 64.1%, plausibly reflects LDS doctrine of vicarious
  salvation for those who never heard the gospel; item is skip-logic-gated
  to Christian-identified respondents only, so non-Christian/Unaffiliated
  groups have no valid cases), and `born-again-identity.json` (only 24.0%
  of Mormons call themselves "born-again" or evangelical, near the bottom
  of Christian traditions despite the Church's own strong doctrine of
  spiritual rebirth, "born-again" reads as a distinctly Evangelical
  self-label most Latter-day Saints don't reach for; same Christian-only
  skip-gate as above). Note: `view-of-god.png` inherits the same row-label
  wrap collision ("Historically Black Protestant Tradition" / "Evangelical
  Protestant Tradition" rows crowd each other) already present in the
  existing `certainty-of-god.png` for this same 12-group RELTRAD list,
  pre-existing to this pass, not introduced by it. Dataset has a large
  untouched battery worth checking for remaining candidates: qm5a/b/d
  (views that churches focus too much on rules / are too concerned with
  money and power / are too involved in politics, note qm5e/f/g are
  already charted, under different labels, in the 2023-24 wave's
  public-life battery, so check for near-duplicate framing before using
  these), qh4 (should one's church try to preserve traditional beliefs vs.
  adjust to modern beliefs), qg7/qg7b (nature of scripture, word of God
  vs. book written by man), qk10a-d (religious practices with children:
  pray/scripture together, Sunday school, religious homeschooling,
  volunteering together), qi2t/qi2u (dietary restrictions, eating beef/
  pork), and qi3b (volunteering specifically through a religious
  organization, distinct from the general qi3 volunteering item).

- **pew-rls-2014** (2014 Religious Landscape Study) — partial, 2026-08-31
  (second pass same day): had 8 charts after the pass above. Added 3 more
  from that pass's remaining-battery list, all full 12-group RELTRAD —
  `family-scripture-prayer.json` (92.7% of Mormon parents pray or read
  Scripture with their child(ren), 2nd only to Jehovah's Witnesses at
  93.4% and well above Evangelical/Historically Black Protestant at ~85%,
  ties to the Church's family scripture study and family home evening
  practice; qk10a is asked only of parents, so every group's N is smaller
  than the full sample but all 12 groups still clear the 30-valid floor),
  `scripture-word-of-god.json` (93.8% of Mormons call their own scripture
  the literal word of God rather than a book written by men, 2nd only to
  Jehovah's Witnesses at 97.6%, from qg7 which is worded to each
  respondent's own tradition's scripture and asked of the full sample),
  and `volunteer-through-church.json` (among people who volunteered in the
  past week, 59.2% of Mormon volunteers channeled that service mainly
  through their congregation, 2nd only to Jehovah's Witnesses at 81.4% and
  well ahead of every other Christian tradition's ~32-43%, ties to the
  Church's organized ward-level welfare/service culture; qi3b is
  skip-gated to qi3=1 volunteers only, distinct from the general qi3 item
  this site doesn't chart on its own). All three RELTRAD_CODES dicts in
  this pass use the short canonical group labels ("Evangelical
  Protestant," "Mainline Protestant," "Historically Black Protestant,"
  "Unaffiliated") instead of the long "...Tradition"-suffixed Pew labels —
  at 12-13 total rows the long two-line-wrapping forms of "Evangelical
  Protestant Tradition" and "Historically Black Protestant Tradition"
  visually collided with their neighboring rows in every one of this
  pass's first draft renders (confirmed by reading the PNGs), the same
  known row-label-wrap issue already flagged against
  certainty-of-god.png/view-of-god.png. Switching to the short forms
  (already the convention in the ATP-wave and RLS-2014-recontact scripts,
  aliased to the same identity colors in chart_style.py's GROUP_ALIASES)
  fixed the collision cleanly without touching the shared renderer — worth
  using for any future 12-group RELTRAD chart in this folder, and
  potentially for regenerating certainty-of-god.png/view-of-god.png too
  when that follow-up task is picked up. Remaining untouched candidates
  from the prior pass's list: qm5a/b/d, qh4, qg7b (literal vs.
  not-everything-literal, a natural follow-up to this pass's qg7 chart),
  qk10b-d (Sunday school, religious homeschooling, volunteering with
  kids), qi2t/qi2u (dietary restrictions).

- **pew-atp-w44-2018** (American Trends Panel, Wave 44, February 2019 —
  religious knowledge and belief) — previously had 8 charts (5 knowledge-
  quiz items, Communion belief, feeling-thermometer warmth toward Mormons).
  Added 3 more this pass, all broken out by F_RELTRAD with the same
  13-group Protestant-collapsed set as knowledge_batch.py —
  `learns-about-own-religion-weekly.png` (66.1% of Latter-day Saints do
  things to learn about their own religion — reading scripture, podcasts,
  books — at least weekly, 2nd only to Jehovah's Witnesses at 81.3% and
  well above every other tradition's ~20-53%, ties to LDS personal/family
  scripture study), `personally-knows-a-mormon.png` (which traditions are
  most/least likely to personally know a Mormon: "Other faiths" highest at
  62.1%, Protestants at 49.5%, down to Jehovah's Witnesses at 10.7% and
  Muslims at 13.1% — a social-visibility/proximity story, not an LDS
  self-report), and `religious-ed-4plus-years.png` (74.8% of Latter-day
  Saints attended Sunday school/CCD/religious education for 4+ years,
  highest of any named tradition — Protestants 2nd at 68.3% — ties to the
  Church's youth Primary/Sunday School programs). Checked
  pew-atp-w44-2018's remaining battery for other candidates: TRINITY_W44
  (knowledge item testing the textbook definition of the Trinity, not a
  belief item — skipped as a weak fit for the "own belief" story given
  LDS non-creedal theology), RELTEACHc_W44 (self-rated knowledge of
  Mormonism by other traditions — conceptually redundant with this pass's
  "knows a Mormon" chart), CHIMPRELa/b (importance of religion growing
  up — skipped as a near-duplicate of pew-rls-2023-24's already-shipped
  `chimprel_very_important` chart), and READREL2_W44 (learning about
  *other* religions — thinner LDS angle than READREL1's own-religion
  version already used). Also confirmed (by reading each entry's own
  description in data-explorer.ts) that every other 1-chart dataset in
  data/ — pew-10-country-religion-2007, pew-subsaharan-africa-2010,
  pew-eastern-europe-2015, pew-global-restrictions-religion,
  pew-india-2021, pew-church-tax-western-europe,
  pew-religious-composition-2010-2020, pew-religion-migration — is
  capped by design: each is a cross-national or country-level dataset
  with no Latter-day-Saint/U.S.-specific frame variable, documented as
  such in its own description. Not worth revisiting for more charts.
