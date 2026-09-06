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

- **pew-rls-2014-recontact** (2014 RLS recontact survey) — partial,
  2026-08-31: had 5 charts (all qd-series marriage/family items). Added 2
  more this pass, both broken out by current tradition (reltrad) from the
  qb/qc batteries not yet touched — `parents-talked-religion.json` (77.8%
  of Mormons say their parents or guardians talked about religion "a lot"
  growing up, from qb15, highest of any tradition by 16 points over 2nd-
  place Historically Black Protestant at 62.0% and well above Evangelical
  Protestant's 42.4% — ties to the Church's family gospel-teaching culture,
  e.g. family home evening/family scripture study) and
  `attendance-stability.json` (only 39.2% of Mormons have ever gone
  through a period since turning 18 of attending religious services less
  often than they do now, from qc9, the lowest "lapsed" share of any
  tradition — Evangelical/Mainline Protestant both ~58-59% — reads as the
  most stable, unbroken lifelong attendance pattern of any group).
  Confirmed pew-latin-america-2014's existing 6 charts already max out
  that dataset's LDS content before starting this pass: Mormons in Latin
  America aren't broken out as their own respondent group in QCURRELrec
  (folded into "Other religion," too small a sample), so the only
  Mormon-specific item is Q63e ("do you consider Mormons Christian"),
  already shipped as `mormons-as-christian.json` — not worth revisiting.
  Back in pew-rls-2014-recontact: checked and dropped qc3 ("only
  considered congregations in your own denomination when looking for a
  new one" — Mormon valid n=29, just under the 30 floor), qc11/qd7/qd9a
  (all Mormon n<30 once skip-gated to their relevant subsamples), and
  qb17/qb18 (importance of religion to self/family growing up — both read
  as near-duplicates of the already-shipped pew-religious-landscape-study
  `childhood-importance.png` CHIMPREL chart, same construct different
  survey). Remaining untouched candidates if this dataset gets a third
  pass: qb16 (parental disagreement about religion growing up), qb21
  (currently belonging to more than one religion — check against the
  already-shipped `raised-interfaith.json` for overlap first), and the
  qc1a/b/d "reasons for looking for a new congregation" battery (likely
  too small a Mormon n given the qc3 sibling item's 29).

- **pew-rls-2007** (2007 U.S. Religious Landscape Survey) — partial,
  2026-08-31: had 5 charts (evolution-belief, certainty-of-god,
  daily-prayer, retention-rate, lds-share-by-region). Added 3 more this
  pass, all broken out by RELTRAD using the continental-US main survey
  file — `official-membership.json` (92.4% of Mormons are official
  members of the church or house of worship they attend, highest of any
  tradition by 9 points over 2nd-place Historically Black Protestant at
  83.3%, ties to LDS formal membership records created at baptism/
  confirmation), `prayer-scripture-groups.json` (64.8% of Mormons
  participate in a prayer group, Scripture study group, or religious
  education program at least weekly, 2nd only to Jehovah's Witnesses at
  83.0% and well above every other tradition's <45%, ties to LDS Sunday
  School/seminary/institute culture), and `volunteer-with-children.json`
  (45.5% of Mormons work with children or youth at their place of worship
  at least weekly, 2nd only to Jehovah's Witnesses at 47.3%, q28c is
  skip-gated to respondents with a usual place of worship so its "All
  respondents" baseline is smaller than the full RELTRAD sample, ties to
  the Church's lay-volunteer calling system including Primary and youth
  leadership). Dataset has a large untouched battery worth checking for
  remaining candidates: q32 (view of God, person vs. impersonal force —
  check against the already-shipped 2014 `view-of-god` chart before using,
  same framing different year could work as a trend point), q37/q38
  (nature of scripture, word of God vs. book written by man — likewise
  near-duplicate of 2014's `scripture-word-of-god`), q39b (angels/demons
  active in the world), q42d (share faith with non-believers — ties to
  full-time missionary work), q43a/q43c (spiritual peace/answered prayer
  experiences — q43c checked this pass, mid-pack at 36.6%, weaker
  distinctiveness story so skipped), q46/q47 (perceived conflict between
  religious devotion and modern society), and q55a-c (family religious
  practices with children — q55a/b likely near-duplicates of 2014's
  qk10a/qk10b family-scripture-prayer chart, check before using).

- **pew-catholic-family-2015** (2015 Survey of U.S. Catholics and Family
  Life) — 2026-08-31: had 6 charts (5 from the qb12 "raised by [household
  type]" battery, 1 Catholic-only annulment/Communion item). Added 3
  more this pass, all broken out by present religion (relig, the same
  general-public + Catholic-oversample sample as qb12) from the
  qb15a-c battery — the adult-focused counterpart to qb12's child-
  focused version, same "as good a way of life as any other" top-box
  framing. `unmarried-cohabiting-couple.png` (17% of Mormons say an
  unmarried couple living together is as good a way of life as any
  other, lowest of any tradition — next-lowest is Jehovah's Witness at
  34%, U.S. adults overall 56%), `samesex-couple-living-together.png`
  (20% of Mormons, also lowest — Muslims next at 30%, U.S. adults 50%;
  a distinct construct from the site's existing "favor same-sex
  marriage" charts, which ask about legal marriage support rather than
  acceptability of the living arrangement), and `childless-by-choice.png`
  (41% of Mormons say a couple who choose not to have children is as
  good a way of life as any other, again lowest — next-lowest Hindu at
  59%, U.S. adults 80%, Protestants 79%, Catholics 73%). All three tie
  to the Church's family/marriage teaching (the Family Proclamation) —
  Mormons are the least-accepting group on all three adult-arrangement
  items, mirroring the pattern already shown for the child-focused qb12
  items. Mormon N is thin (88 total, ~83-87 valid per item) but clears
  the 30-respondent floor; flagged as directional in the method note.
  Row count landed at 14-15 (13-14 named religions + Mormon + a "U.S.
  adults" catch-all pinned to the bottom by sort_groups) rather than the
  usual ≤13 — this dataset's relig variable is already the coarsest
  available grouping (no RELTRAD-style split to collapse further), and
  all three PNGs render cleanly with no label overlap or clipping.
  Remaining untouched candidates if this dataset gets a third pass: the
  qj22/qj29/qj31/qj32 Pope Francis and Catholic-Church-reform batteries
  and qn3/qp27 Catholic-identity and sin batteries are all Catholic-only
  (no cross-tradition LDS comparison, weak fit for this site); qa3a-c
  (favorability of groups/institutions, item content not yet checked)
  and qf2/qf5/qf6/qh3 (importance of religion, prayer style, childhood
  religion — likely near-duplicates of items already shipped elsewhere
  from other datasets, check first) are the only remaining candidates
  with a plausible religion breakout.

- **pew-mormon-survey-2011** (2011 National Survey of Mormons) — 2026-08-31:
  had 9 charts, all previously mined but never logged here. Added 3 more
  this pass, following the dataset's existing by-activity-level (q406)
  chart convention (tithing, ordination, food storage) since this survey
  interviewed Mormons only, with no other-tradition comparison group —
  `book-of-mormon-origin-by-activity.json` (92% of Mormons overall say
  the Book of Mormon was written by ancient prophets and translated by
  Joseph Smith rather than written by Joseph Smith himself, from q408,
  ranging 56%→98% by activity level; checked against overlap with the
  shipped pew-religious-knowledge-2010 `book-of-mormon-knowledge` chart —
  distinct construct, that one is a factual-knowledge quiz item, not a
  belief item, and asked of the general public not Mormons themselves),
  `temple-recommend-by-activity.json` (66% of Mormons overall hold a
  current temple recommend, from q419, ranging 2%→90% by activity level
  — the Church's own worthiness-interview gate for temple worship, a
  sharper engagement marker than attendance or activity self-report
  alone), and `daily-prayer-by-activity.json` (84% of Mormons overall
  pray at least once a day outside of religious services, from q412,
  ranging 38%→96% by activity level; checked against the shipped
  pew-rls-2007 `daily-prayer` chart — distinct construct, that one is a
  cross-tradition RELTRAD breakout of the general population, this one
  is an activity-level breakout within Mormons only). All three at
  n=1,006-1,011 total respondents, comfortably clearing the floor at
  every activity level (smallest cell: 46 "not at all active"). Wave's
  remaining untouched battery worth checking for a future pass: q409c
  (belief the LDS/Mormon Church president is a prophet of God — a
  natural sibling to this pass's core_beliefs.py trio), q421a-d (how
  similar own religion is seen to Catholic/Evangelical/Jewish/Muslim
  faiths — more a social-distance item than a belief/practice one, check
  fit first), and q303-q311 (perceived societal acceptance/political
  friendliness toward Mormons — check for overlap with the already-
  shipped `president_readiness_by_party` chart, which likely already
  covers q311, before using q303-q310).

- **pew-religious-knowledge-2010** (2010 U.S. Religious Knowledge Survey,
  oversampled Mormons) — 2026-08-31: had 6 charts, all knowledge-quiz items
  broken out by present religion (qn20). Added 2 more this pass, same
  construction — `college-religion-courses.json` (65.8% of Mormons have
  ever taken a college-level religion course, highest of any tradition by
  27 points over 2nd-place Jewish at 39.2% and well above the 29.8%
  national average, plausibly reflects the Church's institute-of-religion
  program pairing CES religion classes with secular college coursework for
  many Latter-day Saint young adults) and `ten-commandments-knowledge.json`
  (85.3% of Mormons correctly pick the Golden Rule as the option that is
  NOT one of the Ten Commandments, highest of any group by 11 points over
  2nd-place Agnostics at 74.2%, a general Bible-literacy item rather than
  an LDS-specific one but fits this dataset's existing knowledge-item
  convention). Checked and skipped for near-duplicate overlap: qn34a
  (read scripture outside services, weekly+ — same construct already
  shipped as pew-rls-2023-24's `practice-pracb` chart) and qn34b/qn53
  (reading about own religion / childhood religious-ed attendance — close
  enough to w44-2018's `learns-about-own-religion-weekly` and
  `religious-ed-4plus-years` charts to skip). Dataset has a large
  remaining battery of general Bible/world-religion knowledge items with
  no LDS-specific angle (qn35-40, qn44, qn46-48, qn55, qn60-63); qn61
  (Darwin/evolution) and qn9 (New Deal, a non-religion item) checked this
  pass and dropped as unremarkable. Consider this dataset close to fully
  mined.

- **pew-atp-w132-2023** (American Trends Panel, Wave 132, spirituality
  battery) — partial, third pass 2026-08-31: had 3 charts (beyond-this-world,
  religious-community, has-cross). Added 2 more this pass, both by F_RELIG —
  `spirituality-important.json` (66.5% of Mormons call spirituality "very
  important" in their life, highest of any Christian tradition and
  essentially tied with Muslims at 66.7% for the highest of any group in the
  wave) and `tattoo-piercing-spiritual.json` (only 6.5% of Mormons have a
  tattoo or piercing "for spiritual purposes," lowest of any Christian
  tradition — Protestant 8.3%/Catholic 7.8%/Orthodox 10.4% — essentially
  tied with Atheists at 6.0% and above only Muslims at 4.3% among all 12
  groups; ties to the LDS body-as-temple/tattoo counsel). Checked
  SPIRTHINGS_a (jewelry, Mormon 10.2% — thin, no clear doctrinal story) and
  SPIRTHINGS_d (home shrine/altar/icon, Mormon 11.2% — not the lowest,
  Protestant is lower at 7.2%, undercuts an LDS-distinctiveness story) and
  dropped both; also checked LIFESPIR_W132 (became more/less spiritual over
  lifetime, Mormon 50.1% — solidly mid-pack, no distinctive story) and
  dropped it. Wave's DTHLKE_c (dead can provide guidance/protection) is
  still untouched but flagged in the prior pass as overlapping W143's
  shipped "ancestors' spirits" chart — check closely before using. Consider
  this wave close to fully mined; only DTHLKE_c remains as a live candidate,
  and it's a marginal one.

- **pew-faith-in-flux-2008** (2008 Conversion Recontact Survey) — 2026-08-31:
  had 5 charts (never previously logged here, hence appearing "untouched" by
  this log's own summary at the top - it wasn't). Added 2 more this pass.
  `joining-decision-maker.png` (q15, the joining-side mirror of the
  existing leaving-decision-maker chart's q2 - 81% of people who became
  their current religious identity say it was mostly their own decision,
  18% mostly their parents'/family's; n=399 valid, a subset of the full
  2,867 since q15 is only asked of respondents who report a specific age
  of becoming CURREL) and `ever-identified-with.png` (the q22 battery,
  "have you ever identified with X at any point in your life," a single-
  population ranking across 12 named identities with the Mormon row
  highlighted via `highlight_rows` rather than `group_identity` - Mormon
  is the LEAST-often-passed-through identity in the battery at 2.7%,
  vs. 34.3% for "nothing in particular," 27.5% for Nondenominational
  Christian, and 13.3% for Baptist; read alongside the already-shipped
  reasons-joined-lds chart's 38-respondent LDS-convert base, this is
  further evidence LDS identity is rarely a way station people pass
  through on a longer path of religious searching - people who try it
  tend to arrive there directly). Checked and skipped for duplicate/weak-
  fit risk: q19a-e/q20a-e (general religious-skepticism agree/disagree
  battery, no clean LDS angle without re-deriving finalgrp subgroups
  already too thin), q7/q8/q10/q11 (childhood/teen religious-practice
  frequency, would need a by-group breakout and the only LDS-sized
  subgroup, former/current Mormons, is already too thin at n=26-38 per
  the existing charts' own notes). Remaining untouched material: q3oe/
  q16oe (open-ended coded reasons for leaving/joining, likely overlaps
  the existing q4/q17-battery reason charts once decoded), q5k-s (forced-
  choice framing of the same q4 reasons, redundant with reasons-left-
  religion), q1/q1a/q14/q14a (age and life-stage when leaving/joining, a
  demographic item with no direct religious-content angle). Consider this
  dataset close to fully mined.

- **pew-atp-w143-2024** (American Trends Panel, Wave 143, February 2024 —
  religion/politics + Israel-Hamas war) — 2026-08-31: had 11 charts, all
  previously built but never logged here (cross-referenced against
  `data-explorer.ts`'s graphics array to confirm). Added 2 more this pass,
  same F_RELIG group-set/`binary_by_group` construction as the existing
  holiday_batch*.py scripts — `believes-in-reincarnation.png` (only 14.0% of
  Mormons believe people will be reborn in this world again and again, tied
  with Atheists for the lowest of any group — Buddhist 67.0%/Hindu 65.9% at
  the top — ties to the LDS doctrine of one mortal probation rather than
  reincarnation) and `consults-fortune-teller.png` (5.9% of Mormons consult
  a fortune teller, horoscope, or other way to see the future, 2nd-lowest
  after Jewish's 5.6% and essentially tied with Protestant's 6.2% — ties to
  LDS counsel against seeking guidance through divination/fortune-telling).
  Both from BELIEVE_REIN_W143/PRACTICE_FUTR_W143, checked against the
  existing 11 charts for overlap (none — those cover fasting, candles,
  discrimination-perception items, president-belief items, afterlife,
  ancestors' spirits, and wearing religious items) and confirmed no
  existing "reincarnation" or "fortune teller/horoscope/divination" chart
  anywhere on the site. All groups clear the 30-valid floor at n=57-4,354.
  Wave's remaining untouched battery is almost entirely Israel-Hamas-war/
  politics content with no religious-tradition breakout angle (SYMP_W143,
  HMSACC/HMSVAL/ISRACC/ISRVAL, FUNDISR/AIDGZ, LAND_RSLV, etc.) or
  Catholic-specific (CCHRCH_*, PPLFAV_a Pope Francis, POPE_CHANGE); the only
  other live candidate is BELIEVE_SPEL_W143 (belief spells/curses/magic can
  influence people's lives) but it lacks as clean an LDS doctrinal tie as
  this pass's two items, and RELIGCONFLICT_W143 (conflict between own
  beliefs and mainstream culture) has Mormons mid-pack at 58.1%, no
  distinctiveness story. Consider this wave close to fully mined.

- **pew-rls-2007** (2007 U.S. Religious Landscape Survey) — third pass,
  2026-08-31: had 8 charts. Added 2 more from the prior pass's remaining-
  battery list, both broken out by RELTRAD, continental-US main survey —
  `share-faith-nonbelievers.json` (q42d, 47.8% of Mormons share their
  faith with non-believers or people from other religious backgrounds at
  least monthly, 4th of 11 named traditions behind Jehovah's Witness
  86.4%/Historically Black Protestant 56.8%/Evangelical Protestant 53.9%,
  ties to LDS full-time and everyday member-missionary practice;
  Unaffiliated has no valid cases, the item isn't meaningfully asked of
  them) and `angels-demons-active.json` (q39b, 91.6% of Mormons completely
  or mostly agree angels and demons are active in the world, 2nd only to
  Jehovah's Witness at 96.3% and above Historically Black Protestant
  90.2%/Evangelical Protestant 89.8%, ties to LDS scripture's angelic-
  ministration accounts, e.g. Moroni's visits to Joseph Smith, and belief
  in a personal, active adversary). Both PNGs read cleanly at 12-13 rows,
  no label collision. Checked q46/q47 (conflict between devout religion
  and modern society) this pass and dropped it: Mormon at 37.9% is
  mid-pack, close to Orthodox 38.0%/Catholic 36.1%, no distinctiveness
  story. Remaining untouched candidates from the prior pass's list: q37/q38
  (scripture literalism, likely near-duplicate of 2014's
  scripture-word-of-god — check first), q42d's siblings weren't checked
  individually, q43a (spiritual peace, q43c already checked and dropped),
  q55a-c (family religious practices with children, likely near-duplicate
  of 2014's qk10a/qk10b family-scripture-prayer chart). Consider this
  dataset close to fully mined.

- **pew-rls-2014** (2014 Religious Landscape Study) — fourth pass, 2026-08-31:
  had 11 charts. Added 2 more from the prior passes' remaining-battery lists,
  both broken out by RELTRAD, using the short canonical group labels per this
  dataset's own row-label-collision fix — `preserve-traditional-beliefs.json`
  (qh4, 72.8% of Mormons say their own church or denomination should preserve
  its traditional beliefs and practices rather than adjust or modernize them,
  highest of any tradition — Jehovah's Witness 2nd at 69.3%, Evangelical
  Protestant 3rd at 64.9% — ties to the LDS teaching that core doctrine is
  eternal and unchanging even as the Church receives continuing revelation on
  its application) and `scripture-literalism.json` (qg7b, a skip-gated
  follow-up asked only of respondents who already call their own scripture
  the word of God in qg7 — among that subset, only 37.9% of Mormons say
  scripture is meant literally, word for word, near the bottom of Christian
  traditions and well below Historically Black Protestant 71.7%/Evangelical
  Protestant 65.2%, despite the already-shipped qg7 chart showing 93.8% of
  Mormons calling scripture the word of God — a genuinely distinct construct
  from that chart, not a duplicate, and plausibly reflects LDS doctrine of
  imperfect ancient-text transmission (Articles of Faith 1:8, "as far as it
  is translated correctly") alongside ongoing modern revelation). Both at
  12-13 rows with no label collision (checked by reading each PNG directly).
  Remaining untouched candidates from prior passes' lists: qm5a/b/d (church
  too focused on rules/money-power/politics — still needs an overlap check
  against the 2023-24 wave's public-life battery before use), qi2t/qi2u
  (dietary restrictions, eating beef/pork — thin doctrinal tie, not really a
  Word of Wisdom item), and qk10b-d (Sunday school, religious homeschooling,
  volunteering with kids). Consider this dataset close to fully mined after
  this pass.

- **pew-black-faith-2021** (Pew's "Faith Among Black Americans," fielded
  2019-2020) — fifth chart, 2026-08-31: did a fresh cross-reference of every
  `data/` folder against `data-explorer.ts`'s `DATASETS` array first (no
  dataset with zero graphics or unmentioned-anywhere-in-this-log turned up —
  pew-rls-2023-24, ryan-burge, and state-of-theology are simply undocumented
  here despite being heavily charted in earlier sessions, confirmed by
  grepping their many existing imports/imageSrc entries). Fell back to the
  single most defensible remaining item from this dataset's own prior-pass
  notes: the untouched CHURCHLOOK battery ("how important would each of the
  following be in choosing a new congregation"). Checked all five sub-items
  by RELIGMOD (34-valid-N floor already established for this dataset/file);
  CHURCHLOOK_a/b (welcoming, inspiring sermons) show Mormons mid-pack with
  no distinctive story, and CHURCHLOOK_d/e (senior leaders/congregants
  share your race) repeat the same Black-church-specific racial framing
  already flagged as a weak LDS fit for this dataset's COMMINFL1/BLKEQL1_c
  items — skipped all four. CHURCHLOOK_c ("belongs to your denomination")
  had a genuine story and became `denomination-loyalty.json`
  (`denomination_very_important`, RELIGMOD, n=33 valid Mormon respondents):
  47.5% of Black Mormons say it's very important that a new congregation
  belong to their own denomination, 2nd only to Jehovah's Witness at 64.6%
  and well above Protestant 32.7%/Catholic 31.6%/Unaffiliated 20.1% — ties
  to the Church's restorationist, exclusive-priesthood-authority claim
  (not one interchangeable denomination among many). Also checked
  ESSENT_a/ESSENT_b/ESSENT_f (believing in God / attending services /
  avoiding premarital sex essential to being a moral/religious person) and
  dropped all three: Mormon lands mid-pack on each (34.7%-42.5%), no
  highest/lowest story despite ESSENT_f's superficial Law-of-Chastity tie.
  This dataset's remaining untouched material (PERSDO1_a-e,
  TYPEGODSUM/GODBELIEFSMOD_b/d, CLERGYSSM, ESSENTCHURCH_a-g, "all
  respondents.sav" Black-vs-non-Black comparison) is either likely
  duplicative of already-shipped items, weak-fit, or unchecked pending a
  future pass — this pass built exactly the one defensible chart the
  remaining battery supported rather than forcing a full batch.

- **pew-rls-2023-24** (2023-24 Religious Landscape Study) — backfill entry,
  2026-08-31: heavily charted across many prior sessions but never logged
  here. Already has 20+ shipped graphics spanning
  `switching-generalized.json` (retention/switching), `birth-decade-
  distribution.json`, `childhood-formation.json` (CHATTEND/CHIMPREL/
  CHEDU2), `family-household.json`, `practice.json` (attendance/prayer/
  membership/Bible-importance batteries, by both the full RELTRAD-style
  frame and a generalized group set), `beliefs.json` (soul/heaven/hell/
  evolution), `spiritual-experience.json`, `public-life.json`, two
  `holiday-batch*.json` files, and `stay-home-parent-gender.json`. This
  dataset has its own `docs/datasets/pew-rls-2023-24/GRAPHICS_TODO.md`
  work-queue file — checked directly: its Pending section is empty of
  buildable items, only a "Blocked" list of five ideas confirmed to have
  no matching variable in the public-use file (denomination-level
  detail, "absolutely clear standards of right and wrong," "moral
  without believing in God," favorability toward other groups, "religion
  and science are compatible" — all checked against the actual 654-
  variable codebook, not assumed). Consider this dataset fully mined;
  any future pass should re-check the codebook directly rather than
  trust this note growing stale, but as of this backfill there is
  nothing queued.

- **ryan-burge** (curated LDS-relevant extracts from Ryan Burge's public
  GitHub repos: CCES 2016, CES stacked 2006-2018, VOTER Survey Panel,
  US Religion Census 2010 county file, plus thin tier-2 files) —
  backfill entry, 2026-08-31: heavily charted across many prior sessions
  but never logged here. Already has 20+ shipped graphics: CCES-2016-by-
  religion (8 charts: immigration select-all battery, abortion, same-sex
  marriage, attendance distribution), pid-by-gender and pid-over-time
  (CES stacked), and the full 23-graphic VOTER Survey Panel set (stranger-
  in-my-own-country, feeling-thermometer matrices, issue importance, and
  all 20 ideas from `docs/datasets/ryan-burge/VOTER_PANEL_IDEAS.md` —
  retention, religiosity trajectory, vote-switching, vote regret, trust in
  government, child-rearing values, sexism/Muslim-distrust/immigration/
  trade/promises/media/orgs/volunteering/pride heatmaps, military
  household rate, populist distrust, gay-marriage shift). This dataset's
  own `docs/datasets/ryan-burge/GRAPHICS_TODO.md` work-queue file's
  Pending section is explicitly empty — "every item that was queued here
  has shipped" — and it directly instructs against pulling more variables
  from the 867-variable VOTER Survey Panel without being asked. The only
  genuinely untouched material is the tier-1 `us_religion_census_2010_
  county.DTA` aggregate file (county-level LDS congregation/adherent
  counts, not survey microdata — a different chart shape than this
  project's per-respondent bars) and several tier-2 small-n files
  (Faith Matters 2006/2011 at n=49-53, ANES 2016 at n=52, GSS 2016 at
  n=23-31) flagged in the dataset's own `INVENTORY.md` as underpowered
  alone. Consider this dataset fully mined for now.

- **state-of-theology** (Ligonier/LifeWay State of Theology survey,
  2022/2025 waves, via the evangelical-quiz belief-modeling pipeline) —
  backfill entry, 2026-08-31: unlike every other dataset in this log,
  this one is charted automatically by construction —
  `stateOfTheologyGraphics()` in `src/lib/data-explorer.ts` maps over
  every item in `src/lib/evangelical-quiz/data.json` (`QUIZ_DATA.items`)
  and produces one graphic per item, reading its own `pending_items`
  field (confirmed empty, 0 items) for anything not yet modeled. Checked
  directly: `data.json` currently has 36 items and
  `public/data-explorer/state-of-theology/` has exactly 36 PNGs — full
  1:1 coverage, nothing to backfill. Any future expansion of this
  dataset means adding new items to the quiz's own belief-modeling
  pipeline (`scripts/evangelical-quiz/build_data.py`), not building a
  standalone Data Explorer chart — a different, heavier kind of work than
  this log otherwise tracks. Consider this dataset fully mined as a
  Data Explorer target.

- **pew-rls-2014** (2014 Religious Landscape Study) — fifth chart,
  2026-08-31: housekeeping pass on pew-rls-2023-24/ryan-burge/state-of-
  theology (see the three backfill entries above) found no defensible
  untouched item in any of the three — pew-rls-2023-24 and ryan-burge
  both have their own GRAPHICS_TODO.md files with empty Pending sections,
  and state-of-theology is auto-generated with 1:1 item-to-chart
  coverage already. Fell back to this dataset's own remaining-battery
  list from prior passes: `qk10b` (send child(ren) to Sunday school or
  another religious education program), the untouched sibling of the
  already-shipped `qk10a` "pray or read Scripture with your kids" chart
  from the same battery. 86.8% of Mormon parents send their kids to
  Sunday school/religious ed, highest of any of the 12 RELTRAD groups by
  a wide margin (2nd-place Evangelical Protestant 77.0%), n=242 valid —
  comfortably above the 30-respondent floor. Maps directly onto the
  Church's Primary program (ages 3-11) and youth Sunday School classes, a
  distinct formal-religious-education construct from qk10a's family-
  devotional framing, so not a duplicate despite sharing a battery.
  Computed by `scripts/pew-rls-2014/sunday_school_children.py` →
  `docs/datasets/pew-rls-2014/sunday-school-children.json`, rendered by
  `scripts/pew-rls-2014/render_sunday_school_children_chart.py` →
  `public/data-explorer/pew-rls-2014/sunday-school-children.png` (12
  RELTRAD rows + "All parents," checked by reading the PNG directly — no
  label collision). Wired into `src/lib/data-explorer.ts`
  (`sundaySchoolChildrenGraphic()`). Remaining untouched candidates from
  prior passes' notes: qk10c (religious homeschooling — likely a much
  thinner Mormon N given how rare it is), qk10d (volunteer work with
  kids — weaker doctrinal tie), qm5a/b/d, qi2t/qi2u.

- **pew-catholic-family-2015** (2015 Survey of U.S. Catholics and Family
  Life) — fourth chart, 2026-08-31: checked several other datasets'
  remaining-battery notes first and rejected them — pew-black-faith-2021's
  PERSDO1_a/c/d (meditate, burn candles/incense, pray at home altar) all
  land Mormons mid-pack with no distinctive story once actually computed
  (checked by weighted crosstab, not assumed), and PERSDO1_e (consult a
  diviner) has Mormons *higher* than most Christian groups at n=33 — a
  counter-doctrinal, thin-N result not worth shipping. Landed instead on
  this dataset's own unchecked qf6 item ("when you pray, do you mainly say
  memorized prayers ... or have a personal conversation with God"), broken
  out by present religion (relig, same general-public + Catholic-oversample
  sample as this folder's other three scripts). `prayer-style.json`:
  89.8% of Mormons say they mainly have a personal conversation with God
  rather than memorized prayers, 2nd only to Jehovah's Witness (96.1%,
  thinner n=31) among 12 named groups clearing the 30-floor, well above
  Protestant (83.6%) and far above Catholic (45.9%)/Orthodox (63.0%) —
  ties directly to LDS teaching that personal prayer is an informal,
  individual conversation rather than fixed liturgy, with no standard
  congregational prayer text outside the sacrament prayers. Mormon n=87
  valid (unweighted). Computed by
  `scripts/pew-catholic-family-2015/prayer_style.py` →
  `docs/datasets/pew-catholic-family-2015/prayer-style.json`, rendered by
  `scripts/pew-catholic-family-2015/render_prayer_style.py` →
  `public/data-explorer/pew-catholic-family-2015/prayer-style.png` (13
  rows, checked by reading the PNG directly — no label collision). Wired
  into `src/lib/data-explorer.ts` (`prayerStyleGraphic()`). This dataset's
  remaining untouched candidates (qa3a-c favorability of Pope
  Francis/Obama/Putin — political, weak fit; qf2/qf5 importance-of-
  religion/prayer-frequency — likely near-duplicates of items already
  shipped elsewhere; qh3 childhood religion — demographic, no belief
  content) all look thin or duplicative; consider this dataset close to
  fully mined.

- **pew-mormon-survey-2011** (2011 National Survey of Mormons) — 13th
  chart, 2026-08-31: read this log in full and cross-referenced `data/`
  against `data-explorer.ts`'s `DATASETS` array — no untouched dataset
  turned up, and every other family (pew-rls-2023-24, ryan-burge,
  state-of-theology) is confirmed fully mined via its own
  GRAPHICS_TODO.md/auto-generation note. Checked this dataset's own
  remaining-candidate list from its most recent pass: q421a-d ("is [X]
  religion similar to your own") is a social-distance item with no
  belief/practice content, and q303-q310 (perceived societal awareness/
  fairness/friendliness toward Mormons) mostly duplicate the already-
  shipped `president-readiness-by-party` construct or read as thin
  political-perception items — both skipped. Landed on q409c ("do you
  believe the president of the LDS/Mormon Church is a prophet of God"),
  the one item in the q409 core-belief battery not yet used anywhere on
  the site (q409a/b/d already shipped as a single-population ranking in
  `core-beliefs.json`; q409e already shipped in `ordination-by-
  activity.json`). Built it by activity level (q406), matching this
  dataset's existing by-activity convention (`book-of-mormon-origin-by-
  activity.json`, `temple-recommend-by-activity.json`, `daily-prayer-by-
  activity.json`) rather than repeating core_beliefs.py's single-ranking
  shape — a foundational LDS truth claim (living prophetic leadership)
  checked against real engagement data. `prophet-belief-by-activity.json`:
  99.2% of "Very active" Mormons believe the Church president is a
  prophet of God, falling to 96.1% Somewhat active, 89.3% Not too active,
  and just 46.4% Not at all active (95.1% among all Mormon adults) — a
  strong, clean activity gradient. All cells clear the 30-valid floor
  (smallest: n=49, Not at all active). Computed by
  `scripts/pew-mormon-survey-2011/prophet_belief_by_activity.py` →
  `docs/datasets/pew-mormon-survey-2011/prophet-belief-by-activity.json`,
  rendered by
  `scripts/pew-mormon-survey-2011/render_prophet_belief_chart.py` →
  `public/data-explorer/pew-mormon-survey-2011/prophet-belief-by-
  activity.png` (5 rows, checked by reading the PNG directly — no label
  collision). Wired into `src/lib/data-explorer.ts`
  (`prophetBeliefByActivityGraphic()`). With q421/q303-310 both weak
  fits, consider this dataset fully mined.

- **pew-atp-w70-2020** (American Trends Panel, Wave 70, July 2020 —
  religion during COVID) — ninth chart, 2026-08-31: re-read this log in
  full and cross-referenced `data/` against `data-explorer.ts`'s
  `DATASETS` array (no untouched dataset found). Checked several
  candidates from prior passes' remaining-battery lists before landing
  one: w114-2022's ESSENT_h/ESSENT_j (family traditions / community
  belonging, by F_RELIG) both land Mormons squarely mid-pack (47.6%/
  42.4%, no highest/lowest story — checked by weighted crosstab, not
  assumed) and were dropped; w117-2022's SNSPOST3_W117 (posts about
  religion on social media, by F_RELTRAD) has Mormons 4th of 16 groups
  at 38.6%, too close to the Evangelical/Historically-Black-Protestant
  cluster (~41%) for a clean distinctiveness story, dropped; this
  dataset's own COVIDVOL2_b_W70 (turned to a religious org for help with
  bills/housing/food, the receiving-side mirror of the already-shipped
  `religious-org-giving-covid` chart) has Mormons at just 5.0%, but
  that's mid-pack-low rather than a clean lowest (Buddhist 1.1%, Orthodox
  and Other World Religions both 0%), dropped. Landed on COVIDLESSON1_W70
  ("do you believe there's a lesson or set of lessons for humankind to
  learn from the coronavirus outbreak"), by F_RELTRAD — a belief/
  meaning-making item, distinct in kind from this folder's existing
  coping-*behavior* charts (worship, prayer, scripture, giving).
  `covid-lesson-belief.json`: 93.4% of Mormons believe there's a lesson,
  tied with Historically Black Protestant for the highest of any
  tradition in the wave, well above Catholic/Mainline Protestant (~87%),
  Jewish (86.5%), Evangelical Protestant (86.2%), and Unaffiliated
  (84.6%) — ties to LDS providential theology (God's hand active in the
  affairs of mankind; D&C 122:7's "all these things shall give thee
  experience"). Mormon n=167 valid, comfortably above the 30 floor.
  Computed by `scripts/pew-atp-w70-2020/covid_lesson_belief.py` →
  `docs/datasets/pew-atp-w70-2020/covid-lesson-belief.json`, rendered by
  `scripts/pew-atp-w70-2020/render_covid_lesson_chart.py` →
  `public/data-explorer/pew-atp-w70-2020/covid-lesson-belief.png` (7
  RELTRAD rows + "All U.S. adults," checked by reading the PNG directly —
  no label collision). Wired into `src/lib/data-explorer.ts`
  (`covidLessonBeliefGraphic()`). `tsc --noEmit` clean. Committed and
  pushed as `e735dca`. Wave's only remaining untouched item is
  COVIDLESSON2_W70 (whether that lesson was specifically sent by God —
  Mormon 64.1%, 4th highest, a weaker/more crowded story than
  COVIDLESSON1); consider this wave fully mined after this pass. Broader
  note: after 25+ passes across this session, essentially every dataset
  in `data/` is now at or very near saturation — every remaining
  candidate item checked this pass and in prior passes' notes either
  lands mid-pack (no highest/lowest story) or duplicates an already-
  shipped construct. This pass found exactly one defensible item; the
  site appears to be approaching a genuine mining plateau, though a few
  single-item candidates (COVIDLESSON2_W70 among them) remain if a future
  pass wants to push further into thinner territory.

- **pew-hispanics-religion-2007** (Pew Hispanic Center/Pew Forum Survey of
  Latinos, 2006) — sixth chart, 2026-09-06: re-read this log's plateau-check
  conclusion and re-verified it against the current `data/` folder list and
  `data-explorer.ts`'s `DATASETS` array first — no new or unmined dataset
  has appeared since the 2026-08-31 plateau check. Went back to this
  dataset's own prior-pass remaining-candidate list (qn14_d, qn25, qn53) and
  checked all three directly against the real .sav file rather than
  trusting the old notes. Dropped qn14_d (favorability toward Mormons rated
  by other groups) as too close in framing to the already-shipped
  w114-2022 `relfav-mormons` chart, and dropped qn53 (crucifix/religious
  objects at home) once computed — Mormon n=16, under the 30-valid floor.
  Built `born-again-identity.json`/`.png` from qn25 ("would you describe
  yourself as a born-again or evangelical Christian"), broken out by the
  survey's own recoded `relig`: 61.9% of Latino Mormons accept the
  "born-again" label (n=32 valid, just clears the floor), 2nd only to
  Protestants (83.0%) and far above Catholics (30.2%) and Jehovah's
  Witnesses (25.4%). This isn't a duplicate of the already-shipped
  pew-rls-2014 `born-again-identity` chart (general U.S. population, where
  only 24.0% of Mormons overall accept the label) — it's a genuinely
  different population with a strikingly different result, worth reading
  side by side as evidence that Latino Mormon converts carry over an
  evangelical-style self-identification much more than Mormons in the
  general population do. Computed by
  `scripts/pew-hispanics-religion-2007/born_again_identity.py` →
  `docs/datasets/pew-hispanics-religion-2007/born-again-identity.json`,
  rendered by
  `scripts/pew-hispanics-religion-2007/render_born_again_identity_chart.py`
  → `public/data-explorer/pew-hispanics-religion-2007/born-again-identity.png`
  (4 rows, checked by reading the PNG directly — no label collision). Wired
  into `src/lib/data-explorer.ts` (`bornAgainIdentityHispanicsGraphic()`).
  `tsc --noEmit` clean. This was the last concretely open candidate noted
  for this dataset from its own prior passes; with all three of qn14_d/
  qn25/qn53 now checked and resolved (two dropped, one shipped), consider
  this dataset fully mined.

- **Plateau check, 2026-08-31 (26th+ pass)** — read this entire log in full
  and re-checked the last pass's one flagged open candidate,
  COVIDLESSON2_W70 ("do you believe any of the lessons humankind should
  learn from COVID were sent to us by God," ATP W70), by computing the real
  weighted crosstab by F_RELTRAD directly from `ATP W70.sav` rather than
  trusting the prior note: Mormon = 64.4% (n=156 valid), which lands 4th of
  16 groups — behind Historically Black Protestant (74.6%), Muslim (69.5%),
  and Evangelical Protestant (66.0%) — confirming the prior pass's read that
  this is a crowded mid-upper-pack result with no highest/lowest
  distinctiveness story, not worth shipping as a chart. Also did the full
  final cross-reference requested: every one of the 28 folders under
  `data/` maps to a slug (or, for `ryan-burge`, multiple sub-dataset slugs)
  already present in `src/lib/data-explorer.ts`'s `DATASETS` array — no
  dataset was found sitting entirely unmined and unlisted. With
  COVIDLESSON2_W70 (the only concretely open candidate carried forward from
  the prior pass) checked and rejected, and every dataset's own
  remaining-battery notes in this log already exhausted or explicitly
  marked "close to/fully mined" across 25+ prior passes, this pass found
  zero defensible new charts. **Conclusion: the Data Explorer has reached
  its natural mining plateau for this session.** No chart was built. Future
  passes should not re-check pew-rls-2023-24, ryan-burge, state-of-theology,
  the nine no-usable-breakout cross-national datasets, or any dataset marked
  "fully mined" / "close to fully mined" above without first identifying a
  genuinely new angle (e.g. a newly released Pew wave, a newly added data
  file) rather than re-scanning the same exhausted batteries.
