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
