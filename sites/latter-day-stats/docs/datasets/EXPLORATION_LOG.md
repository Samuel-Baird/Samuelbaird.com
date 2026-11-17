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

- **pew-black-faith-2021** (Pew's "Faith Among Black Americans," fielded
  2019-2020) — seventh chart, 2026-09-06: picked a dataset different from the
  most recent shipped pass (pew-hispanics-religion-2007's sixth chart) per
  this iteration's instructions. Re-read this dataset's own prior-pass notes
  and confirmed the six existing charts (women-leaders, convert-duty,
  god-responds, turned-to-church-for-help, denomination-loyalty, and
  job-skills-essential — the last of these was already live in
  `data-explorer.ts` but had never been logged here; corrected that omission
  now) before picking a new item. Checked this dataset's remaining PERSDO1
  battery directly against the real .sav file: PERSDO1_a/c/d/e (meditate,
  burn candles/incense, pray at a home altar, consult a diviner) were all
  checked and dropped in an earlier pass per this log's own notes, but
  PERSDO1_b ("read scripture outside of religious services") had never been
  checked. Computed it by RELIGMOD, weighted by WEIGHT, same construction as
  denomination-loyalty.py: Black Mormons read scripture outside of religious
  services at least weekly at 69.9% (n=33 valid, just over the 30 floor) —
  the highest of any tradition in the wave, edging out Jehovah's Witnesses
  at 68.8% and well above Protestants (51.8%) and Catholics (30.3%) — ties to
  the LDS emphasis on daily personal and family scripture study (e.g. Come,
  Follow Me home study). Also checked PERSDO2_a (prayer/scripture-study
  groups, Mormon 42.9% n=34, 2nd to JW's 56.3% — a real but less clean
  story, dropped in favor of the cleaner PERSDO1_b result), ESSENTCHURCH_d
  (help the needy with bills/housing/food — Mormon mid-pack at 53.7%, no
  distinctive story, dropped), and GODBELIEFSMOD_b/d (God directs/judges
  everything — Mormon mid-to-low on both, no distinctive story, dropped).
  Built `scripture-reading.json`/`.png` via
  `scripts/pew-black-faith-2021/scripture_reading.py` →
  `docs/datasets/pew-black-faith-2021/scripture-reading.json`, rendered by
  `scripts/pew-black-faith-2021/render_scripture_reading_chart.py` →
  `public/data-explorer/pew-black-faith-2021/scripture-reading.png` (7 rows,
  checked by reading the PNG directly — no label collision). Wired into
  `src/lib/data-explorer.ts` (`scriptureReadingBlackFaithGraphic()`).
  `tsc --noEmit` clean; verified the PNG serves 200 OK at 1080x1350 from the
  local dev server. This dataset's remaining untouched candidates
  (TYPEGODSUM, CLERGYSSM, ESSENTCHURCH_a/b/e/f/g, and the still-unused "all
  respondents.sav" Black-vs-non-Black comparison sample) are either
  weak-fit (political/racial framing already flagged elsewhere in this log)
  or unchecked pending a future pass; consider this dataset close to fully
  mined.

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

- **pew-black-faith-2021** (Pew's "Faith Among Black Americans," fielded
  2019-2020) — sixth chart, 2026-09-06: re-read this log's plateau-check
  conclusion in full first and confirmed no new dataset had appeared since
  2026-08-31 (28 `data/` folders, all still mapped in `data-explorer.ts`),
  and that the most recent pass (pew-hispanics-religion-2007's sixth chart)
  was a different dataset. Checked this dataset's own long-untouched
  ESSENTCHURCH_a-g battery ("how important is it for houses of worship to do
  each of the following"), never used by any prior pass, by computing the
  real weighted crosstab by RELIGMOD for every sub-item rather than trusting
  old notes. Dropped ESSENTCHURCH_a (moral guidance, Mormon 60.9% mid-pack,
  below Protestant 74.2%/Jehovah's Witness 80.2%), ESSENTCHURCH_d (help the
  needy with bills/housing/food, Mormon 53.7% mid-pack, and thematically
  close to the already-shipped `turned-to-church-for-help.json`),
  ESSENTCHURCH_e (community/fellowship, Mormon 64.9% mid-pack), and
  ESSENTCHURCH_f/g (racial affirmation / political sermons, same
  Black-church-specific racial/political framing already flagged as a weak
  LDS fit for this dataset's COMMINFL1/BLKEQL1_c/CHURCHLOOK_d/e items). Also
  spot-checked CLERGYSSM (same-sex-marriage-officiant item, Mormon 43.8% -
  no clean story, close to the national average, and thematically
  overlapping the site's existing SSM-favorability charts) and TYPEGODSUM
  (belief in a personal God, Mormon 74.8% - solidly mid-pack behind
  Jehovah's Witness 96.7%/Protestant 87.9%) and dropped both. Landed on
  ESSENTCHURCH_c ("teach practical job and life skills"): Mormons rate this
  "essential" at 70.5%, the highest of any group by a wide margin — next is
  Muslim at 50.9%, then Protestant 47.5%, with Catholic/Jehovah's Witness/
  Unaffiliated all clustered at 40-41% and "All Black Americans" at 45.3%.
  This is a genuine LDS-institution-vs-data story: the Church runs practical
  self-reliance/vocational programs as a congregational function (ward/stake
  Self-Reliance Initiative career workshops and employment resource centers,
  the Perpetual Education Fund, BYU-Pathway Worldwide) rather than treating
  job/life-skills instruction as outside a house of worship's remit, and
  Black Mormons are far more likely than any other named tradition to see
  that as essential rather than merely a nice-to-have. Mormon n=33 valid
  (unweighted), just over this dataset's established 30-floor, using the
  "black faith black respondents.sav" file per this folder's established
  convention. Computed by
  `scripts/pew-black-faith-2021/job_skills_essential.py` →
  `docs/datasets/pew-black-faith-2021/job-skills-essential.json`, rendered by
  `scripts/pew-black-faith-2021/render_job_skills_essential_chart.py` →
  `public/data-explorer/pew-black-faith-2021/job-skills-essential.png` (7
  rows, checked by reading the PNG directly — no label collision). Wired
  into `src/lib/data-explorer.ts` (`jobSkillsEssentialGraphic()`).
  `tsc --noEmit` clean; PNG confirmed served at 200 OK, 1080x1350, via the
  dev server. This dataset's remaining untouched material (PERSDO1_a/c/d
  already checked and dropped in an earlier pass as mid-pack/counter-
  doctrinal, PERSDO1_b likely a near-duplicate of already-shipped scripture-
  reading items, and the "all respondents.sav" Black-vs-non-Black comparison
  sample) is thin or duplicative — consider this dataset fully mined.

- **pew-rls-2014-recontact** (2014 RLS recontact survey) — third pass,
  2026-09-06: the two most recently shipped commits were both
  pew-black-faith-2021 (job-skills-essential, then scripture-reading) with
  pew-hispanics-religion-2007 before that, so per this iteration's
  instructions picked a different dataset. Re-read this dataset's own
  remaining-candidate list from its second pass: qb16 (parental disagreement
  about religion growing up — a demographic/family-conflict item with no
  clean LDS doctrinal angle, skipped without computing) and qc1a/b/d
  (reasons for looking for a new congregation — flagged as likely under the
  30-floor given sibling item qc3's Mormon n=29, not checked further).
  Landed on qb21 ("do you CURRENTLY think of yourself as belonging to more
  than one religion, or not") by reltrad — checked first for overlap against
  the already-shipped `raised-interfaith.json` (qb19, "raised in more than
  one religion" growing up) and confirmed it's a genuinely distinct
  construct: current self-identification vs. childhood upbringing. Computed
  the real weighted crosstab directly from the .sav file for all 15 reltrad
  codes before committing to the chart; only 7 groups (Evangelical/Mainline/
  Historically Black Protestant, Catholic, Mormon, Jewish, Unaffiliated) plus
  "All U.S. adults" clear the 30-valid floor (Orthodox n=17, Muslim n=15,
  Buddhist n=27, Jehovah's Witness n=18 all excluded). `current-
  multireligious.json`: only 4.0% of Mormons currently think of themselves
  as belonging to more than one religion, tied for lowest with Historically
  Black Protestant (4.2%) among groups clearing the floor and well below
  Mainline Protestant (7.6%)/Catholic (7.0%)/Unaffiliated (6.5%) — plausibly
  reflects LDS restorationist theology's exclusive-priesthood-authority
  claim ("the only true and living church," D&C 1:30) discouraging
  simultaneous identification with another faith tradition. Mormon n=61
  valid (unweighted), comfortably above the 30 floor. Computed by
  `scripts/pew-rls-2014-recontact/current_multireligious.py` →
  `docs/datasets/pew-rls-2014-recontact/current-multireligious.json`,
  rendered by
  `scripts/pew-rls-2014-recontact/render_current_multireligious_chart.py` →
  `public/data-explorer/pew-rls-2014-recontact/current-multireligious.png`
  (8 rows, checked by reading the PNG directly — no label collision). Wired
  into `src/lib/data-explorer.ts` (`currentMultireligiousGraphic()`).
  `tsc --noEmit` clean; PNG confirmed served at 200 OK, 1080x1350, via the
  dev server (in-app page hydration couldn't be visually confirmed this pass
  due to the known hidden-browser-pane-blocks-hydration issue, but no server
  errors and a clean PNG fetch). This dataset's remaining candidates
  (qb16, qc1a/b/d) are both weak-fit or likely underpowered — consider this
  dataset fully mined.

- **pew-rls-2014** (2014 Religious Landscape Study) — sixth pass, 2026-09-06:
  the three most recently shipped commits were pew-rls-2014-recontact,
  pew-black-faith-2021 (x2), and pew-hispanics-religion-2007, so per this
  iteration's instructions picked a dataset outside that exclusion list.
  Went back to this dataset's own long-flagged qm5a/b/d "critique of
  religious institutions" battery (churches too focused on rules / too
  concerned with money and power / too involved in politics) — flagged as
  an open candidate across several prior passes but never actually checked
  because it needed an overlap review against the 2023-24 wave's
  public-life battery first. Did that check directly against
  `scripts/pew-rls/public_life.py`: that battery's RELINST_E/F/G items ask
  the *positive*-framed counterparts (religious orgs protect/strengthen
  morality, bring people together, help the poor), not this negative
  "too many rules/too much money and power/too political" framing —
  confirmed genuinely distinct, not a duplicate. Computed all three qm5
  sub-items by RELTRAD directly from the .sav file (full sample, all 12
  groups clear the 30-valid floor at n=629-8144) and found a striking,
  consistent pattern: Mormons are the single lowest-agreeing group of all
  12 traditions on all three items. Built all three as a tight thematic
  cluster — `church-too-many-rules.json` (28.3% of Mormons agree churches
  focus too much on rules, lowest of any tradition, next-lowest Jehovah's
  Witness 38.9%), `church-too-much-money-power.json` (36.9% of Mormons
  agree churches are too concerned with money and power, lowest of any
  tradition, next-lowest Muslim 44.0%), and
  `church-too-involved-politics.json` (30.7% of Mormons agree churches are
  too involved with politics, lowest of any tradition, next-lowest
  Evangelical Protestant 35.6%) — read together, a consistent story that
  Latter-day Saints are markedly less inclined than any other tradition to
  criticize religious institutions on any of these three dimensions,
  plausibly reflecting a comparatively high baseline of institutional
  trust in the Church's own leadership and covenant-based commandments
  being understood as a path to blessing rather than excessive
  restriction. Computed by
  `scripts/pew-rls-2014/church_too_many_rules.py`,
  `church_too_much_money_power.py`, and `church_too_involved_politics.py` →
  `docs/datasets/pew-rls-2014/church-too-*.json`, rendered by the three
  matching `render_church_too_*_chart.py` scripts (short RELTRAD labels,
  matching this dataset's established row-label-collision fix) →
  `public/data-explorer/pew-rls-2014/church-too-*.png` (13 rows each,
  checked by reading all three PNGs directly — no label collision on any).
  Wired into `src/lib/data-explorer.ts` (`churchTooManyRulesGraphic()`,
  `churchTooMuchMoneyPowerGraphic()`, `churchTooInvolvedPoliticsGraphic()`).
  `tsc --noEmit` clean; all three PNGs confirmed served at 200 OK,
  1080x1350, via the local dev server. This dataset's remaining untouched
  candidates from prior passes' notes (qi2t/qi2u dietary restrictions,
  qk10c/qk10d Sunday-school siblings) are both thinner/weaker-fit;
  consider this dataset fully mined after this pass.

- **pew-rls-2007** (2007 U.S. Religious Landscape Survey) — 11th chart,
  2026-09-06: the four most recently shipped commits were pew-rls-2014
  (church-too-* trio), pew-rls-2014-recontact, and pew-black-faith-2021
  (x2), all excluded per this iteration's instructions, so picked a
  different dataset. Re-checked this dataset's own remaining-candidate
  list from prior passes directly against the real continental-US .sav
  file rather than trusting old notes: q37/q38 (scripture literalism)
  skipped without computing as too close to 2014's already-shipped
  `scripture-word-of-god`/`scripture-literalism` pair (same construct,
  same RELTRAD frame, just an earlier year of the same three-wave RLS
  series); q55a/b (family scripture/Sunday-school practices with
  children) skipped for the same reason against 2014's
  `family-scripture-prayer`/`sunday-school-children` charts. Checked the
  untouched q43 "spiritual experiences" battery's three unused sub-items
  directly: q43a (deep sense of spiritual peace and well-being, weekly+)
  computed at Mormon 72.5% but dropped as a near-duplicate of the
  already-shipped pew-rls-2023-24 `spiritual-peace.png` (same "deep sense
  of spiritual peace and well-being" wording, just a different wave);
  q43b (sense of wonder about the universe, weekly+) computed at Mormon
  41.2%, squarely mid-pack among the 12 RELTRAD groups, no
  highest/lowest story, dropped. q43d ("have you ever experienced or
  witnessed a divine healing of an illness or injury") had never been
  checked and cleared both tests — built `divine-healing-witnessed.json`:
  69.4% of Mormons say yes, the highest of any of the 12 RELTRAD groups
  by 13 points over 2nd-place Historically Black Protestant (56.1%) and
  well above Evangelical Protestant (51.6%)/Catholic (28.3%)/Mainline
  Protestant (29.1%), against a 37.2% "All U.S. adults" baseline — ties
  directly to LDS priesthood healing blessings (anointing with oil and
  the laying on of hands, D&C 42:43-44/James 5:14-15), administered by
  any worthy Melchizedek Priesthood holder rather than reserved to
  clergy, plausibly explaining both the high witnessed-rate and
  Jehovah's Witness's outlying low 7.7% (a tradition with its own
  distinct theology of healing through faith alone, no ordinance).
  Mormon n=572 valid (unweighted), comfortably above the 30-respondent
  floor. Computed by `scripts/pew-rls-2007/divine_healing_witnessed.py`
  (using `chart_style.sort_groups` for row order, a small convention
  update from this folder's older manual-sort scripts) →
  `docs/datasets/pew-rls-2007/divine-healing-witnessed.json`, rendered by
  `scripts/pew-rls-2007/render_divine_healing_chart.py` →
  `public/data-explorer/pew-rls-2007/divine-healing-witnessed.png` (13
  rows, checked by reading the PNG directly — no label collision, long
  RELTRAD "...Churches" labels wrap cleanly at this row count). Wired
  into `src/lib/data-explorer.ts` (`divineHealingWitnessedGraphic()`).
  `tsc --noEmit` clean; PNG confirmed served at 200 OK, 1080x1350, via
  the local dev server, and the `/data-explorer` page loads without
  error. This dataset's remaining untouched material (q37/q38, q55a-c)
  is now confirmed duplicative of 2014-wave charts rather than merely
  suspected; consider this dataset fully mined.

- **pew-atp-w132-2023** (American Trends Panel, Wave 132, spirituality
  battery) — sixth/seventh chart, 2026-09-06: the five most recently
  shipped commits were pew-rls-2007, pew-rls-2014, pew-rls-2014-recontact,
  pew-black-faith-2021, and pew-hispanics-religion-2007 — all excluded per
  this iteration's instructions, so picked a different dataset. This log's
  own entry for this dataset was stale: it said "had 1 chart" but a check
  of `data-explorer.ts` and `scripts/pew-atp-w132-2023/` found the dataset
  already had 5 shipped charts (an older, never-logged commit `1097185`
  had added `spirituality-important.json`/`SPIRIMP_W132` and
  `tattoo-piercing-spiritual.json`/`SPIRTHINGS_b` - both items this log's
  stale entry still listed as "remaining candidates"). Backfilled the
  dataset's own `README.md` Status section to list all 5 pre-existing
  charts accurately before adding more. From the wave's untouched six-part
  "Do you believe people who have died can..." (DTHLKE) battery, checked
  all six sub-items directly by weighted F_RELIG crosstab (this wave has
  no F_RELTRAD) rather than trusting the old candidate list, and shipped
  two as a tight cluster: `dead-aware-living.json` (DTHLKE_a, "be aware of
  things going on among the living" - 89.9% of Latter-day Saints say
  definitely/probably true, highest of any named tradition by a wide
  margin over 2nd-place Catholic at 73.6%, ties to LDS spirit-world
  doctrine in D&C 138 and to temple/family-history work done on behalf of
  the dead) and `reunited-with-loved-ones.json` (DTHLKE_f, "be united with
  other loved ones who have already died" - 98.4% of Latter-day Saints say
  definitely/probably true, highest of any named tradition over 2nd-place
  Orthodox Christian at 95.2%, maps directly onto LDS eternal-marriage/
  family-sealing doctrine in D&C 132). Both Mormon n=170-175 valid,
  comfortably above the 30-floor. Checked the battery's other four
  sub-items and skipped them: DTHLKE_c ("provide assistance, protection or
  guidance") confirmed as the item this log had already flagged as
  overlapping `pew-atp-w143-2024`'s shipped `believe-ancestor-spirits.json`
  help/harm framing; DTHLKE_b ("communicate with the living") is
  thematically too close to this pass's own DTHLKE_a pick from the same
  battery; DTHLKE_d (dead can harm the living) is a negative-framing
  sibling with a weaker doctrinal tie; DTHLKE_e (reincarnation) likely
  duplicates `pew-atp-w143-2024`'s already-shipped
  `believes-in-reincarnation.json`. Also checked and dropped
  `SPIRTHINGS_c`/`SPIRTHINGS_a` (crystals/jewelry for spiritual purposes -
  Mormon 8.1%/mid-pack, no distinctive story once computed) and
  `LIFESPIR_W132` (became more/less spiritual over time - Mormon 50.1%,
  essentially tied with Protestant 51.2%, no distinctiveness story).
  Computed by `scripts/pew-atp-w132-2023/dead_aware_living.py` and
  `reunited_with_loved_ones.py` → `docs/datasets/pew-atp-w132-2023/dead-
  aware-living.json`/`reunited-with-loved-ones.json`, rendered by the
  matching `render_*_chart.py` scripts (manual `\n` subtitle breaks added
  after the first render caught a clipped subtitle on the one-line-title
  chart — this dataset's existing scripts hadn't needed one since their
  titles wrap to two lines on their own) → `public/data-explorer/pew-atp-
  w132-2023/dead-aware-living.png`/`reunited-with-loved-ones.png` (13 rows
  each, checked by reading both PNGs directly — no label collision or
  clipping after the subtitle fix). Wired into `src/lib/data-explorer.ts`
  (`deadAwareLivingGraphic()`, `reunitedWithLovedOnesGraphic()`).
  `tsc --noEmit` clean; both PNGs confirmed served at 200 OK, 1080x1350,
  via the local dev server, and the dataset's page loads with no console
  errors (only benign dev-server HMR websocket noise, unrelated to this
  change). Remaining untouched candidates, now narrowed to genuinely thin
  material: `DTHLKE_b`/`DTHLKE_c`/`DTHLKE_d`/`DTHLKE_e` (all checked and
  dropped this pass, see above), `SPIRTHINGS_a`/`SPIRTHINGS_c` (checked and
  dropped this pass), `LIFESPIR_W132` (checked and dropped this pass) -
  consider this dataset fully mined.

- **pew-atp-w114-2022** (American Trends Panel, Wave 114, September 2022)
  — fifth chart, 2026-09-06: the six most recently shipped commits were
  pew-atp-w132-2023, pew-rls-2007, pew-rls-2014, pew-rls-2014-recontact,
  pew-black-faith-2021, and pew-hispanics-religion-2007, all excluded per
  this iteration's instructions. Confirmed against `data-explorer.ts`
  that this dataset genuinely had only 4 graphics entries (matching this
  log's own prior "partial" note, not stale this time). From this
  dataset's own remaining-candidate list (other ESSENT_* sub-items,
  RELFAV_* sub-items, REL4_*, CHRNAT1a/b), checked every unused ESSENT_*
  sub-item directly by weighted F_RELIG crosstab (this wave has no
  F_RELTRAD frame variable): ESSENT_g (patriotic, Mormon 37.9% — highest
  among Christian groups but the framing is politically coded and weak
  doctrinally), ESSENT_h (family traditions, Mormon 50.3% — basically
  tied with Catholic 50.5%, no distinctive story), ESSENT_i (moral life,
  Mormon 79.9% — mid-pack, Muslim/Orthodox both higher), and ESSENT_j
  (community, Mormon 44.4% — mid-pack) were all checked and dropped as
  thin or non-distinctive. ESSENT_a ("believing in God" essential to
  faith identity) cleared both tests: 91.3% of Mormons say so, 2nd only
  to Muslims (96.7%) among the 8 groups this item was piped to, and the
  highest of any Christian tradition (Protestant 87.3%, Orthodox 81.1%,
  Catholic 77.8%) — ties directly to LDS teaching on a personal, living
  God with a corporeal form (D&C 130:22) and the First Vision. Confirmed
  distinct from pew-rls-2014's already-shipped "absolutely certain God
  exists" chart, which measures certainty of God's existence in the
  abstract rather than centrality to one's own faith identity. Mormon
  n=190 valid (unweighted), comfortably above the 30-respondent floor.
  Also checked and dropped REL4_c ("do you know a Mormon" by F_RELIG) as
  a weaker fit — it measures other groups' social contact with Mormons,
  not an LDS belief/practice item. CHRNAT1a/b (Christian nationalism
  awareness/favorability) also skipped as politically coded with no
  clean doctrinal tie. Computed by
  `scripts/pew-atp-w114-2022/essent_believe_god.py` (following this
  folder's existing `essent_attend.py`/`essent_jesus.py` pattern exactly)
  → `docs/datasets/pew-atp-w114-2022/essent-believe-god.json`, rendered
  by `scripts/pew-atp-w114-2022/render_essent_believe_god_chart.py` →
  `public/data-explorer/pew-atp-w114-2022/essent-believe-god.png` (8
  rows, checked by reading the PNG directly — no label collision or
  clipping). Wired into `src/lib/data-explorer.ts`
  (`essentBelieveGodGraphic()`). `tsc --noEmit` clean; PNG confirmed
  served at 200 OK, 1080x1350, via the local dev server, and the
  dataset's page loads with no console errors (only benign dev-server HMR
  websocket noise). Remaining untouched candidates for this dataset: the
  rest of RELFAV_* (views of Evangelicals/Catholics/Jews/Muslims/
  Atheists/Mainline Protestants, but these ask how *other* groups view
  those traditions, not distinctively about Mormons — weaker fit unless a
  clear angle emerges), REL4_* (checked and dropped this pass), and
  CHRNAT1a/b (checked and dropped this pass) — this dataset is close to
  fully mined.

- **pew-atp-w117-2022** (American Trends Panel, Wave 117, religion &
  technology) — second pass, 2026-09-06: excluded the seven datasets
  freshly mined earlier this session (pew-atp-w114-2022, pew-atp-w132-2023,
  pew-rls-2007, pew-rls-2014, pew-rls-2014-recontact, pew-black-faith-2021,
  pew-hispanics-religion-2007) and confirmed against `data-explorer.ts`
  that this dataset genuinely had 4 graphics entries (matching the prior
  pass's own note). Worked through the prior pass's own remaining-
  candidate list from its untouched religion-and-tech battery, checking
  each item's F_RELTRAD-conditioned Mormon N before charting: dropped
  `ATTENDPREF_W117` (Mormon n=65, above the floor but thin and a
  preference/hypothetical framing) and `COVIDCONG2_W117` (n=108 but asks
  whether *the respondent's own congregation* streams services — an
  infrastructure fact about the ward, not a personal belief/practice, weak
  doctrinal tie). Shipped 3 tight, well-powered charts from the remaining
  candidates, all broken out by F_RELTRAD — `watch-religion-videos.json`
  (APPUSE2_b_W117, "watch religion-focused online videos... for example on
  YouTube or TikTok" — 51.0% of Latter-day Saints, highest of any
  tradition, narrowly ahead of Historically Black Protestant at 49.1% and
  well above Evangelical Protestant at 40.0%; n=197), `posts-about-
  religion.json` (SNSPOST3_W117, among social media users, posts/shares
  about their religion online — 57.1% of Latter-day Saints, highest of any
  tradition, narrowly ahead of Evangelical Protestant 55.6%/Historically
  Black Protestant 55.4%; n=106), and `reads-religion-books.json`
  (NONTECH2_b_W117, collapsed from its 7-point frequency scale to "at
  least weekly" — 59.0% of Latter-day Saints, highest of any Christian
  tradition and 2nd only to Jewish at 73.6% [n=55, clears the 30 floor];
  n=159). All three read as a coherent "religion & technology" cluster
  distinct from the four already-shipped charts in this dataset
  (in-person attendance, watching full services online, in-person study
  groups, following own leaders online) — this pass adds video-watching,
  social posting, and book-reading as three more distinct behaviors, with
  Latter-day Saints coming out highest or near-highest on all three.
  Computed by `scripts/pew-atp-w117-2022/watch_religion_videos.py`,
  `posts_about_religion.py`, and `reads_religion_books.py` (following this
  folder's existing `nontech_prayer_groups.py`/`follows_own_leaders.py`
  pattern exactly) → `docs/datasets/pew-atp-w117-2022/watch-religion-
  videos.json`/`posts-about-religion.json`/`reads-religion-books.json`,
  rendered by the matching `render_*_chart.py` scripts →
  `public/data-explorer/pew-atp-w117-2022/watch-religion-videos.png`/
  `posts-about-religion.png`/`reads-religion-books.png` (9 rows each,
  checked by reading all three PNGs directly — no label collision or
  clipping). Wired into `src/lib/data-explorer.ts`
  (`watchReligionVideosGraphic()`, `postsAboutReligionGraphic()`,
  `readsReligionBooksGraphic()`). `tsc --noEmit` clean; all three PNGs
  confirmed served at 200 OK, 1080x1350, via the local dev server, and the
  dataset's page loads with no console errors (only benign dev-server HMR
  websocket noise). This wave's remaining untouched items —
  `NONTECH2_a_W117` (religious radio, likely thin/dated medium),
  `APPUSE2_c_W117`/`APPUSE2_d_W117` (seeing/posting online prayer
  requests, not yet checked), and `NONTECH2_c_W117` (duplicate of the
  already-shipped `nontech-prayer-groups.json`'s NONTECH1_c item on the
  frequency scale rather than yes/no framing, skip) — are thin or
  redundant; consider this dataset close to fully mined.

- **pew-atp-w70-2020** (American Trends Panel, Wave 70, July 2020 —
  religion during COVID) — third pass, 2026-09-06: excluded the eight
  datasets freshly mined this session (pew-atp-w117-2022,
  pew-atp-w114-2022, pew-atp-w132-2023, pew-rls-2007, pew-rls-2014,
  pew-rls-2014-recontact, pew-black-faith-2021, pew-hispanics-
  religion-2007) and confirmed against `data-explorer.ts` that this
  dataset genuinely had 9 graphics entries. Worked through the prior
  pass's own remaining-candidate list: checked `COVIDVOL2_b_W70`
  ("turned to a RELIGIOUS organization for help with bills, housing or
  food" during COVID) and dropped it — Mormon 5.0%, essentially tied
  with Catholic (5.1%) and Unaffiliated (5.0%), no distinctive story.
  Shipped one chart from `COVIDLESSON2_W70` ("do you believe any of the
  lessons humankind should learn from COVID were sent to us by God,"
  asked only of the subset who first said yes to `COVIDLESSON1_W70`,
  already charted as this folder's `covid-lesson-belief.json` — this is
  a distinct attribution-to-God construct, not a duplicate):
  `covid-lesson-from-god.json` — 64.4% of Latter-day Saints who believe
  there's a COVID lesson also believe it was sent by God, 3rd of 7
  traditions behind Historically Black Protestant (74.8%) and
  Evangelical Protestant (66.4%), but well clear of Catholic (48.3%),
  Mainline Protestant (46.2%), Unaffiliated (26.8%), and Jewish (25.7%)
  — reads as the three traditionally most providence-minded Christian
  groups clustering well above everyone else, ties to LDS providential
  theology (an active God who intervenes in human affairs, e.g. D&C
  1:17). Mormon n=156 valid, comfortably above the 30-respondent floor.
  Computed by `scripts/pew-atp-w70-2020/covid_lesson_from_god.py`
  (following this folder's existing `covid_lesson_belief.py` pattern
  exactly) → `docs/datasets/pew-atp-w70-2020/covid-lesson-from-god.json`,
  rendered by `scripts/pew-atp-w70-2020/render_covid_lesson_from_god_chart.py`
  → `public/data-explorer/pew-atp-w70-2020/covid-lesson-from-god.png` (8
  rows, checked by reading the PNG directly — no label collision or
  clipping). Wired into `src/lib/data-explorer.ts`
  (`covidLessonFromGodGraphic()`). `tsc --noEmit` clean; PNG confirmed
  served at 200 OK, 1080x1350, via the local dev server, and the
  dataset's page (`/data-explorer/pew-atp-w70-2020`) returns 200 with the
  correct title and no non-benign console errors (only dev-server HMR
  websocket noise). Note: the page's own graphic list is empty for a
  non-admin/unauthenticated request in this local environment because
  `graphic_posts` publish-gating (migrations 0049/0051/0054) defaults any
  row-less graphic to hidden — this affects every graphic on every
  dataset locally, not something introduced by this pass, and is outside
  this log's scope (a separate admin-side publish step). Remaining
  untouched items in this wave: `COVIDVOL2_b_W70` (checked and dropped
  this pass), `COVIDCONG2/3/4_W70` (house-of-worship operating status —
  infrastructure facts about the respondent's own congregation, not a
  personal belief/practice, weak fit per prior pass's note), and
  `COVIDRF_W70` (whether houses of worship should follow the same
  social-distancing rules as other businesses — politically coded policy
  question, no clean doctrinal tie); consider this dataset fully mined.

- **pew-catholic-family-2015** (2015 Survey of U.S. Catholics and Family
  Life) — fourth pass, 2026-09-06: excluded the nine datasets freshly
  mined earlier this session (pew-atp-w70-2020, pew-atp-w117-2022,
  pew-atp-w114-2022, pew-atp-w132-2023, pew-rls-2007, pew-rls-2014,
  pew-rls-2014-recontact, pew-black-faith-2021,
  pew-hispanics-religion-2007) and confirmed against `data-explorer.ts`
  that this dataset genuinely had 10 graphics entries (matching the prior
  pass's own note of 9 plus the third pass's `prayer-style.json` add).
  Checked the prior pass's own remaining-candidate list directly against
  the .sav metadata: `qa3a-c` (favorability of Pope Francis/Obama/Putin)
  confirmed thin/politically coded with no doctrinal tie, skipped; `qh3`
  (childhood religion) would only support a retention/switching angle
  already well covered by the RLS family, skipped. Shipped 1 chart from
  `qf2` ("how important is religion in your life"), general public by
  present religion (relig), same construction as `prayer_style.py`:
  `religious-importance.json` — 81.4% of Mormons say religion is "very
  important" in their life, 2nd only to Jehovah's Witness (87.9%, n=32)
  among named traditions and well above Protestant (73.1%) and far above
  Catholic (62.5%), consistent with LDS emphasis on religion as daily
  lived practice. Mormon n=88 valid, above the 30-respondent floor.
  Checked against overlap with this dataset's own charts (none) and
  against CHIMPREL-style "importance growing up" items shipped elsewhere
  on the site (distinct construct: present-day importance, not
  childhood). Also checked `qf5` (prayer frequency, several times a day)
  — Mormon 62.1%, a decent secondary story, but skipped to avoid
  crowding this dataset's page with a second prayer-adjacent chart next
  to the already-shipped `prayer-style.json` (qf6); flagged as a live
  candidate for a future pass if this dataset is revisited. Computed by
  `scripts/pew-catholic-family-2015/religious_importance.py` (following
  this folder's existing `prayer_style.py` pattern exactly) →
  `docs/datasets/pew-catholic-family-2015/religious-importance.json`,
  rendered by
  `scripts/pew-catholic-family-2015/render_religious_importance.py` →
  `public/data-explorer/pew-catholic-family-2015/religious-importance.png`
  (14 rows, matching this dataset's own established group-set size in
  `prayer-style.json`; checked by reading the PNG directly — no label
  collision or clipping). Wired into `src/lib/data-explorer.ts`
  (`religiousImportanceGraphic()`). `tsc --noEmit` clean; PNG confirmed
  served at 200 OK, 1080x1350, via the local dev server, and the
  dataset's page (`/data-explorer/pew-catholic-family-2015`) returns 200
  with the correct title. Remaining untouched candidates: `qf5` (prayer
  frequency, checked and deliberately deferred this pass, see above).
  Consider this dataset close to fully mined.

- **pew-mormon-survey-2011** (2011 National Survey of Mormons) — 14th
  chart, 2026-09-06: excluded the ten datasets freshly mined this session
  (pew-atp-w70-2020, pew-atp-w117-2022, pew-atp-w114-2022,
  pew-atp-w132-2023, pew-rls-2007, pew-rls-2014, pew-rls-2014-recontact,
  pew-black-faith-2021, pew-hispanics-religion-2007,
  pew-catholic-family-2015) and confirmed against `data-explorer.ts` that
  this dataset genuinely had 13 graphics entries (matching the prior
  pass's own "13th chart" note). First checked `pew-atp-w162-2025` as an
  alternative target — re-read its full `.sav` variable list directly
  (not trusting the prior pass's note) and confirmed the remaining battery
  is Catholic-specific, foreign-policy content, or general
  societal-perception items (`RELIG_INFL1/2_W162`, `SOCTRUST2_W162`) with
  no personal belief/practice angle and no clean distinctiveness story
  (computed `RELIG_INFL2_W162` by `RELIG_W162` directly: Mormon 67.8% say
  the influence change is a "bad thing," but the item doesn't condition on
  whether the respondent thinks religion is gaining or losing influence,
  so "bad thing" is ambiguous and not a defensible chart); also confirmed
  `RELSCHL2_W162` (years of religious education) would be a near-duplicate
  of the already-shipped `pew-atp-w44-2018` "religious-ed-4plus-years"
  construct. Returned to `pew-mormon-survey-2011` and re-read its own
  `.sav` variable list in full: of the q409 core-belief battery, q409a/b/d
  are already in `core-beliefs.json`, q409c in
  `prophet-belief-by-activity.json`, and q409e in
  `ordination-by-activity.json`; q409g (reincarnation) was checked and
  skipped as a near-duplicate of the already-shipped
  `pew-atp-w143-2024` `believes-in-reincarnation.png` (identical
  construct, Mormons already reported there at 14.0%). That left q409f
  ("do you believe in yoga, not just as exercise, but as a spiritual
  practice") as the one item in that battery not yet used anywhere on the
  site. Built `yoga-by-activity.json`/`.png` by activity level (q406),
  matching this dataset's established by-activity convention exactly
  (same construction as `prophet_belief_by_activity.py`): 27.4% of "Very
  active" Mormons believe in yoga as a spiritual practice, rising to 42.1%
  Somewhat active and 49.1% Not too active before dipping to 34.1% Not at
  all active (32.6% among all Mormon adults) — a mostly-monotonic gradient
  reading as more-engaged members being less likely to treat yoga as a
  spiritual (rather than merely physical) practice, plausibly tied to
  Word of Wisdom-era counsel favoring revealed worship over substitute
  spiritual practices. All activity-level cells clear the 30-valid floor
  (smallest: n=45, Not at all active). Computed by
  `scripts/pew-mormon-survey-2011/yoga_by_activity.py` (following this
  folder's existing `prophet_belief_by_activity.py` pattern exactly) →
  `docs/datasets/pew-mormon-survey-2011/yoga-by-activity.json`, rendered
  by `scripts/pew-mormon-survey-2011/render_yoga_chart.py` →
  `public/data-explorer/pew-mormon-survey-2011/yoga-by-activity.png` (5
  rows, checked by reading the PNG directly — no label collision or
  clipping). Wired into `src/lib/data-explorer.ts`
  (`yogaByActivityGraphic()`). `tsc --noEmit` clean; PNG confirmed served
  at 200 OK, 1080x1350, via the local dev server, and the dataset's page
  (`/data-explorer/pew-mormon-survey-2011`) returns 200 with the correct
  title. Remaining battery: q421a-d (religious-similarity-to-other-faiths,
  a social-distance item, checked and skipped by a prior pass),
  q303/q305/q309/q310 (societal-perception items, checked and skipped by
  a prior pass as thin/politically coded or duplicative), and q200a-e
  (life-priority ranking items with no cross-tradition comparison
  available in this Mormon-only survey — a candidate for a future pass if
  broken out by activity level, but not built this pass to avoid a
  circular "more-active members rate religion as more important" result).
  Consider this dataset close to fully mined.

- **pew-atp-w162-2025** (American Trends Panel, Wave 162, February 2025 —
  Catholicism/religion's place in American life) — 7th chart, 2026-09-06:
  excluded the eleven datasets freshly mined earlier this session (see this
  log's own recent entries) and re-verified via `data-explorer.ts` that this
  wave genuinely had 6 graphics entries already. Re-read the prior pass's own
  "essentially fully mined" note and its two flagged leftovers directly
  against the `.sav` file rather than trusting the writeup: RELART_W162 (has
  religious objects/artwork displayed at home) had been dismissed as "too
  close to the shipped devotion-to-saints chart," but on inspection
  devotion-to-saints is `PRACTICEA_SAINTS_W162`, an active devotional-
  practice frequency item, a genuinely different construct from RELART's
  passive home-display yes/no — not a duplicate. Also checked
  PRACTICEA_OTHSCRPT_W162 (the other flagged leftover, "reads the Bible,
  Torah, Quran or other scripture") directly: confirmed it's part of a
  randomized split-form battery with PRACTICEA_BIB_W162 (Catholics get 100%
  BIB-wording, 0% OTHSCRPT-wording; other groups get a random mix) — a real
  mode-effect risk for a cross-tradition bar chart, so left it unbuilt as a
  weaker candidate than a prior pass's write-up implied. Built
  `religious-objects-home.json`/`.png` from RELART_W162 by present religion
  (RELIG_W162, full sample, no split-form issue, all 135 unweighted Mormon
  respondents asked): 78.2% of Latter-day Saints have religious objects or
  artwork displayed at home, 2nd only to Catholics at 79.7% (Hindu's 88.9%
  excluded, n=9, below the 30-valid floor) and well above Protestants at
  53.9% — notable because the item's own example wording (cross, crucifix,
  pictures of Jesus or the saints) is Catholic/Christian-coded, yet Mormons
  essentially match Catholics on it. All included groups clear the 30-valid
  floor (smallest: Buddhist n=31). Computed by
  `scripts/pew-atp-w162-2025/religious_objects_home.py` (following this
  folder's existing `wear_religious_items.py` pattern exactly) →
  `docs/datasets/pew-atp-w162-2025/religious-objects-home.json`, rendered by
  `scripts/pew-atp-w162-2025/render_religious_objects_home_chart.py` →
  `public/data-explorer/pew-atp-w162-2025/religious-objects-home.png` (10
  rows, checked by reading the PNG directly — no label collision or
  clipping). Wired into `src/lib/data-explorer.ts`
  (`religiousObjectsHomeGraphic()`). `tsc --noEmit` clean; PNG confirmed
  served at 200 OK, 1080x1350, via the local dev server, and the dataset's
  page (`/data-explorer/pew-atp-w162-2025`) returns 200 with the correct
  title. Remaining battery is almost entirely Catholic-specific
  (CATHESSENT_*, CATHATTEND*, CCHRCH_*, parish/Mass items) plus the
  split-form-risky PRACTICEA_OTHSCRPT_W162 flagged above. Consider this wave
  fully mined.

- **pew-religious-knowledge-2010** (2010 U.S. Religious Knowledge Survey,
  oversampled Mormons) — 9th chart, 2026-09-06: excluded the twelve
  datasets freshly mined this session (pew-atp-w70-2020, pew-atp-w117-2022,
  pew-atp-w114-2022, pew-atp-w132-2023, pew-atp-w162-2025, pew-rls-2007,
  pew-rls-2014, pew-rls-2014-recontact, pew-black-faith-2021,
  pew-hispanics-religion-2007, pew-catholic-family-2015,
  pew-mormon-survey-2011). Confirmed against `data-explorer.ts` this
  dataset genuinely had 8 graphics entries (matching the prior pass's own
  note). Also checked `ryan-burge`'s own `GRAPHICS_TODO.md` first — its
  Pending section is explicitly empty and its own workflow note says not
  to pull more VOTER Survey Panel variables without being asked, so ruled
  that whole family out for this pass. Read this dataset's full `.sav`
  variable list directly (not trusting the prior pass's bucket note that
  the remaining battery has "no LDS-specific angle") and found qn48a/b/d —
  the same "identify this famous person's religion" battery as the
  already-shipped Joseph Smith item (qn48c) — had three untouched
  sub-items: Mother Teresa (Catholic), the Dalai Lama (Buddhist), and
  Maimonides (Jewish). Computed all three by respondent's own religion
  (qn20) to compare: Dalai Lama put Mormons mid-pack (57.9%, no story);
  Maimonides had a real story (Mormons highest of the Christian traditions
  at 32.7%) but its own Mormon cell is thin at n=57; Mother Teresa gave the
  cleanest, most robust result. Built `mother-teresa-knowledge.json`/`.png`
  — the mirror-image of the shipped Joseph Smith chart: instead of asking
  who knows a fact about Latter-day Saints, this asks how well Latter-day
  Saints know a fact about another tradition. 96.7% of Mormons correctly
  identify Mother Teresa as Catholic, 2nd only to Atheists (97.6%) and
  above Agnostics (95.3%), Protestants (92.1%), and Catholics themselves
  (91.8%) — general religious-literacy comparison with LDS as one point
  among several (pattern 3), not an LDS-specific item, but a genuine
  cross-tradition comparison per this project's own quality bar. Mormon
  n=199 valid, well above the 30-respondent floor. Computed by
  `scripts/pew-religious-knowledge-2010/mother_teresa_knowledge.py`
  (following this folder's existing `joseph_smith_knowledge.py` pattern
  exactly, including its 30-valid-respondent floor and weighting) →
  `docs/datasets/pew-religious-knowledge-2010/mother-teresa-knowledge.json`,
  rendered by
  `scripts/pew-religious-knowledge-2010/render_mother_teresa_chart.py` →
  `public/data-explorer/pew-religious-knowledge-2010/mother-teresa-knowledge.png`
  (8 rows, matching the Joseph Smith chart's own group-set size; checked by
  reading the PNG directly — no label collision or clipping). Wired into
  `src/lib/data-explorer.ts` (`motherTeresaKnowledgeGraphic()`), inserted
  directly after `josephSmithKnowledgeGraphic()` in the graphics array.
  `tsc --noEmit` clean; PNG confirmed served at 200 OK, 86,678 bytes,
  1080x1350, via the local dev server, and the dataset's page
  (`/data-explorer/pew-religious-knowledge-2010`) returns 200 with the
  correct title (full client-side hydration could not be checked this pass
  — the Browser pane reported itself hidden even after fronting the tab,
  the known "hidden pane = no hydration" gotcha; relied on PNG/page
  status-code checks only, same bar prior passes used). Remaining
  candidates: Dalai Lama and Maimonides sub-items from the same qn48
  battery (checked this pass, see above — Dalai Lama has no distinctive
  story, Maimonides has a real story but a thin n=57 Mormon cell, live
  candidate for a future pass if this dataset is revisited); qn35-40, 44,
  46-47, 55, 60, 62-63 remain a general Bible/world-religion knowledge
  battery with no religious-tradition breakout angle checked yet at the
  individual-item level. Consider this dataset close to fully mined.

- **pew-atp-w143-2024** (American Trends Panel, Wave 143, February 2024 —
  religion/politics + Israel-Hamas war) — 12th chart, 2026-09-06: excluded
  the thirteen datasets freshly mined earlier this session (see this log's
  own recent entries) and confirmed against `data-explorer.ts` this dataset
  genuinely had 11 graphics entries (matching the prior pass's own note).
  Re-checked this dataset's own remaining-candidate list directly against
  the real `.sav` file rather than trusting the old writeup: computed
  `BELIEVE_SPEL_W143` ("spells, curses or other magic can influence
  people's lives") by weighted F_RELIG crosstab. A prior pass had flagged
  this item as lacking as clean a doctrinal tie as its two shipped
  siblings, but the actual numbers support a real story once computed:
  Mormon 25.5% is the lowest of the wave's four named Christian traditions
  (Protestant 30.0%, Catholic 31.4%, Orthodox Christian 58.5%), ties to
  Book of Mormon/Doctrine and Covenants counsel against sorcery and
  divination (e.g. Alma 1:32, D&C 63:17 numbering sorcerers among "the
  wicked and adulterous"). Checked for overlap against
  pew-latin-america-2014's existing "magic, sorcery, or witchcraft" chart
  first — similar wording, but that dataset folds Mormons into an
  undifferentiated "Other religion" bucket with no Mormon-specific data
  point, so not a duplicate; this is the first chart on the site with an
  actual Latter-day Saint belief-in-magic figure. Mormon n=167 valid,
  comfortably above the 30-respondent floor. Built
  `believe-spells-magic.json`/`.png` via
  `scripts/pew-atp-w143-2024/believe_spells_magic.py` (reusing
  `holiday_batch.py`'s `binary_by_group` helper, same F_RELIG group set as
  every other chart in this folder) →
  `docs/datasets/pew-atp-w143-2024/believe-spells-magic.json`, rendered by
  `scripts/pew-atp-w143-2024/render_believe_spells_magic_chart.py` →
  `public/data-explorer/pew-atp-w143-2024/believe-spells-magic.png` (13
  rows, checked by reading the PNG directly — no label collision or
  clipping). Wired into `src/lib/data-explorer.ts`
  (`w143BelieveSpellsMagicGraphic()`), inserted after
  `w143FortuneTellerGraphic()` in the graphics array. `tsc --noEmit`
  clean; PNG confirmed served at 200 OK, 101,844 bytes, 1080x1350, via the
  local dev server, and the dataset's page
  (`/data-explorer/pew-atp-w143-2024`) returns 200. This was the only
  concretely open candidate left for this wave per the prior pass's own
  note (`RELIGCONFLICT_W143` already checked and dropped as mid-pack
  no-story); consider this dataset fully mined.

- **faith-matters-2006** (Faith Matters Survey 2006, Putnam & Campbell's
  *American Grace* survey, `data/ryan-burge/tier2-small-n/faith_matters_2006.DTA`,
  via Ryan Burge) — first pass, 2026-09-06: every dataset above was marked
  fully/close-to-fully mined, so this pass opened the one file the ryan-burge
  entry flagged as "underpowered alone" and checked that claim against the
  real .dta with pyreadstat rather than trusting it. The survey's own
  `reltrad` variable (unlike standard 7-cat RELTRAD) keeps Mormon as its own
  category (code 6, n=53 unweighted), so any item asked of the **full sample**
  (~3,100) clears the 30-valid floor (42-53 LDS valid); the survey's
  split-sample battery (~1,550 asked: grace before meals `grace`, religious
  abstinence from food/drink/tobacco `tetotl`, morality of homosexuality
  `okgay`, feeling God's love `godslov`, God's-law-vs-society `GOD_SOC`) leaves
  LDS at n=21-30 and was checked and deliberately NOT charted. Duplicate check
  dropped two otherwise strong full-sample items: `whohvn` (good person of
  another faith can attain salvation, LDS 96%) duplicates the live "Can other
  faiths lead to eternal life?" chart, and `ftmormn` (0-100 thermometer toward
  Mormons) duplicates pew-atp-w44-2018's `warmth-toward-mormons`. Registered a
  new Dataset `faith-matters-2006` (fielder ICR, sourceUrl ARDA FTHMATT) and
  built 4 charts, all weighted by `weight`, DK/refused excluded, rows via
  `chart_style.sort_groups`, colors via `color_for_group` (survey labels
  mapped to site spellings; its "Evangelical Protestant/Other Protestant"
  category is labeled "Evangelical Protestant"): `convert-ok.png` (CONV_OK:
  85.9% of LDS say it's okay for religious people to try to convert others,
  highest of 8 traditions by 21 points over Evangelical 64.8%, vs 43.4% of all
  adults — missionary work), `religious-giving-1000-plus.png` (giverel: 67.3%
  of LDS households gave $1,000+ to religious causes in 2006 dollars, highest
  by 29 points over Jewish 38.4%/Evangelical 36.4%, vs 26.9% overall — tithing;
  n=45), `marry-within-faith.png` (wedinrel, parents only: 53.1% of LDS say
  it's very important their children marry within the faith, highest by 20
  points over Evangelical 33.5%, vs 22.4% overall — temple marriage; n=42),
  `talk-religion-daily.png` (talkrel: 46.3% of LDS talk about religion with
  family/friends roughly daily, highest by 10 points over Historically Black
  Protestant 36.7%, vs 18.4% overall). Compute
  `scripts/ryan-burge/faith_matters_2006.py` → 4 JSONs
  `docs/datasets/ryan-burge/faith-matters-*.json`; render
  `scripts/ryan-burge/render_faith_matters_2006_charts.py` →
  `public/data-explorer/faith-matters-2006/`. Wired into
  `src/lib/data-explorer.ts` (`faithMatters*Graphic()`), `tsc --noEmit` clean,
  PNGs read directly (9 rows, "Historically Black Protestant" wraps cleanly, no
  collisions) and served 200 from the dev server. Verification gotcha: the
  graphic pages 500'd on the local dev server because a *different* concurrent
  session's uncommitted birth-decade work in `data-explorer.ts` references
  `BIRTH_DECADE_SELECTED_GROUP_ORDER` before its declaration (a TDZ error at
  module load) — not this change; verified the wiring instead by loading a
  copy of the staged file (HEAD + only this pass's hunks) with tsx and
  confirming `getGraphic("faith-matters-2006", "convert-ok")` resolves.
  Staged `data-explorer.ts` via a plumbing blob (HEAD + own insertions) so
  the other session's hunks were not swept into this commit. Remaining
  full-sample candidates worth a future look here: `FTH_DEED` (salvation by
  deeds/faith/mixture — LDS 43% deeds, 40% mixture, a 3-way stacked shape,
  not a magnitude bar), `trthrel` (one religion is true, LDS 27.6% highest but
  a thin construct), `relonfam` (religion very important in career/family
  decisions, LDS 70%), `pray` (several times a day, LDS 58%), `literal`, and
  `obednce`. Faith Matters 2011 (`faith_matters_2011.DTA`, LDS n=49,
  `RELTRA11==6`) is a re-interview of many 2006 respondents plus a fresh
  sample — usable as a replication wave but not poolable with 2006 without
  double-counting panelists.

- **faith-matters-2011** (Faith Matters Survey 2011, the second *American
  Grace* wave, `data/ryan-burge/tier2-small-n/faith_matters_2011.DTA`, via
  Ryan Burge) — first pass, 2026-09-06: the prior pass (faith-matters-2006)
  left this wave flagged as a replication file; opened it and diffed its 496
  variables against 2006's to chart only items **new in 2011** rather than
  re-running 2006's battery under a different year. Structure gotchas
  recorded in the compute script's docstring: the .dta has 4,069 rows but
  only 2,322 are 2011 interviews (1,361 recontacts + 751 fresh + 210 youth,
  `SAMPLE11`); the rest are 2006 dropouts with no 2011 data — filter on
  `WGTTOT11` non-null. `RELTRA11` keeps Mormon separate (code 6, n=49) and
  adds an "Other Protestant/Christian" catch-all (code 8) split out of 2006's
  combined evangelical category. Duplicate check dropped `GRACE11` (site
  already has "Always say grace before meals") and `TRUST11` ("Most people
  can be trusted" is live from the VOTER panel); `BJEW11`/`BMUSL11`
  (Jewish/Muslim close friend) are n=9 for LDS, unusable; `WHOHVN11`
  duplicates "Can other faiths lead to eternal life?". Built 4 charts,
  weighted by `WGTTOT11`, new Dataset `faith-matters-2011` (ARDA
  `FTHMAT11`; also confirmed 2006's `FTHMATT` id against ARDA's own catalog):
  `world-ending-soon.png` (WRLDEN11: 41.6% of Latter-day Saints believe the
  world is soon coming to an end — 4th of 9, *below* Historically Black
  Protestant 52.6% and Evangelical 49.4%, vs 30.8% overall; the story is that
  "Latter-day" Saints are not the most apocalyptic tradition),
  `salvation-through-deeds.png` (FTHDEE11: 72.8% of LDS say the path to
  salvation comes through actions or deeds, highest of any Christian
  tradition — Catholic 63.9%, Evangelical 23.6% — vs 48.1% overall; faith-vs-
  works distinctiveness. NOTE: this file's value labels for codes 2/3 are
  swapped relative to 2006 — the marginals prove code 2 is really "faith" —
  so only code 1 is charted), `mosque-in-community.png` (BLDMUS11,
  split-sample, LDS n=34: 68.0% would not be bothered by / would welcome a
  large mosque, 4th of 9, well above Evangelical 48.1%; religious-liberty
  angle), `religion-too-little-influence.png` (RELINF11: 62.3% of LDS say
  organized religion has too little influence on American politics, highest,
  vs Evangelical 54.2% and 32.7% overall). Compute
  `scripts/ryan-burge/faith_matters_2011.py` → `docs/datasets/ryan-burge/
  faith-matters-2011-*.json`; render
  `scripts/ryan-burge/render_faith_matters_2011_charts.py` →
  `public/data-explorer/faith-matters-2011/`; wired in
  `src/lib/data-explorer.ts` (`faithMatters2011*Graphic()`, reusing
  `faithMattersAlt`). `tsc --noEmit` clean; PNG read directly (10 rows incl.
  two gray "Other" catch-alls, no collisions). Same verification gotcha as
  the previous pass: the other concurrent session's uncommitted
  `BIRTH_DECADE_SELECTED_GROUP_ORDER` TDZ bug still 500s every Data Explorer
  page locally, so the wiring was verified by tsx-loading a staged copy (HEAD
  + this pass's hunks only) and `data-explorer.ts` was staged as a plumbing
  blob again. Remaining 2011 candidates (all full-sample, LDS n=47-49, but
  each a cross-wave near-duplicate of a construct already live from RLS or
  the 2006 set, so low priority): `DECFAM11` (religion very important in
  career/family decisions, LDS 83.7% highest), `EXPGOD11` (experienced God's
  presence, LDS 60%, mid-pack), `BLDXCH11` (church-building analogue to the
  mosque item, ~92% everywhere, no spread), `RELCH511` (religiosity changed
  in last 4-5 years, LDS 16%), `GODSOC11` (split-sample, n=38).
  Consider both Faith Matters waves fully mined for magnitude-bar purposes;
  the only untouched shape is a 3-way faith/deeds/mixture stack, blocked by
  the 2011 label ambiguity above.

- **anes-2016** (American National Election Studies 2016 Time Series,
  `data/ryan-burge/tier2-small-n/anes_2016.dta`, via Ryan Burge) — first
  pass, 2026-09-06: the last never-charted survey file with a usable LDS
  sample (INVENTORY.md: `V161264x==301`, 52 pre-election, 43 with a
  post-election interview). Read all 1,836 variable labels with pyreadstat
  and picked one tight cluster: the post-election moral-traditionalism /
  gender-role battery, which is the closest thing in `data/` to the
  Proclamation on the Family's teachings on gender roles and the home.
  Group set: `V161265x` (major religion summary) with LDS pulled out of
  "Other religion"; Black Protestant (31 pre, <30 post) dropped, not shown;
  ANES's "Undifferentiated Christian" kept as its own row, labeled
  "Christian (no denomination given)" (falls to `color_for_group`'s MUTED
  fallback since it's not a palette group). Weighted by `V160102` (post-
  election full-sample weight). Duplicate check: the site's existing "Is a
  stay-at-home parent better for kids?" (Pew ATP) is a different item (any
  parent at home, ungendered) from ANES's gendered breadwinner question, so
  both stand. Built 4 charts under new Dataset `anes-2016`:
  `man-works-woman-home.png` (V162230x: 62.2% of Latter-day Saints say it's
  better if the man is the achiever outside the home and the woman takes
  care of the home and family, highest by 17 points over Evangelical 45.5%,
  vs 35.7% overall), `working-mother-bond.png` (V162229x: 81.0% of LDS say
  it's harder for a working mother to bond with her child, highest by 18
  points, vs 58.5% overall), `traditional-family-ties.png` (V162210: 73.8%
  of LDS agree the country would have fewer problems with more emphasis on
  traditional family ties, highest but only narrowly over Evangelical 70.9%,
  vs 60.0% overall), `newer-lifestyles.png` (V162208: 62.1% of LDS agree
  newer lifestyles are contributing to the breakdown of society, 2nd behind
  Evangelical 68.5%, vs 50.0% overall). LDS n=42-43 on every item. Compute
  `scripts/ryan-burge/anes_2016_family_values.py` →
  `docs/datasets/ryan-burge/anes-2016-*.json`; render
  `scripts/ryan-burge/render_anes_2016_family_values_charts.py` →
  `public/data-explorer/anes-2016/`; wired in `src/lib/data-explorer.ts`
  (`anes2016*Graphic()`). `tsc --noEmit` clean; PNG read directly (9 rows,
  the parenthesized "Christian (no denomination given)" label wraps to two
  lines cleanly, no collisions); PNG served 200. Same local-verification
  gotcha as the two previous passes (the other session's uncommitted
  `BIRTH_DECADE_SELECTED_GROUP_ORDER` TDZ bug still 500s every Data Explorer
  page locally), so wiring was verified by tsx-loading the staged copy and
  `data-explorer.ts` was staged as a plumbing blob with only this pass's
  hunks. Remaining ANES 2016 candidates: `V162209` (be more tolerant of
  other moral standards — LDS 30/43 agree, a mirror-image of this cluster,
  skipped to keep it to four), `V162018c` (gave money to a religious org in
  past 12 months, LDS 31/43 = 72% unweighted — real but overlaps the
  Faith Matters $1,000+ giving chart in construct), `V161243` (Bible
  literalism, LDS 12/52 literal — RLS already covers this construct), the
  post-election group thermometers (`V162095`-`V162113`, e.g. LDS warmth
  toward Muslims/Christian fundamentalists/gay men and lesbians — the VOTER
  panel already has FT-by-religion heatmaps), `V161230` gay adoption and
  `V161228x` transgender bathroom policy (political; CCES same-sex marriage
  already live). Consider this dataset close to fully mined for the site's
  purposes; the thermometers are the only distinct shape left.

- **cces-2016** (CCES 2016, Ryan Burge's 33-variable extract,
  `data/ryan-burge/tier1-strong/cces2016_small_cces.csv`, LDS n=870) —
  second pass, 2026-09-06: with every small-n file now charted, went back
  to the largest LDS sample in `data/` and checked which of its 33 columns
  the first pass (9 charts: immigration x4, abortion x2, same-sex marriage,
  attendance, union) had left untouched: 2016 presidential vote (`vote16`,
  CC16_410a), the four gun items (CC16_330a/b/d/e), `ideo5`, and the
  economy/police items. Built 4 charts, same population/unweighted
  conventions as `cces2016_by_religion.py` (the file has no weight column):
  `vote-2016.png` — a four-segment **nominal** distribution stack (Trump /
  Clinton / McMullin / Other candidate) among voters naming a candidate:
  Latter-day Saints split Trump 50% / Clinton 20% / McMullin 14% / other 16%,
  and McMullin is under 1% in every other group — the famous 2016 LDS
  third-party story, verified in microdata; `gun-background-checks.png`
  (LDS 80.3% support, LOWEST of 12 groups, vs 88-96% everywhere else),
  `gun-assault-ban.png` (LDS 48.0%, lowest, vs Protestant 62.4% and 63-88%
  for everyone else), `gun-concealed-carry.png` (LDS 57.9% support easier
  permits, HIGHEST, vs Protestant 43.2%). CC16_330b (prohibit publishing gun
  owners' names) skipped for its double-negative wording. Duplicate check:
  the site's only 2016-vote-adjacent chart is the VOTER panel's 2012→2016
  switching chart, a different survey and construct. Compute
  `scripts/ryan-burge/cces2016_vote_guns.py` (imports the first pass's
  helpers rather than copying them) → `docs/datasets/ryan-burge/
  cces2016-vote-guns.json`; render `scripts/ryan-burge/
  render_cces2016_vote_guns_charts.py` reuses
  `render_cces2016_by_religion_charts.py`'s own `render_magnitude_bar` and
  `render_distribution_stack` — the latter gained optional
  `seg_colors`/`seg_text_colors`/`handle` parameters (default behavior
  unchanged; the existing `attend-distribution.png` re-rendered
  pixel-identical) so a nominal scale like vote choice doesn't get the
  ordinal blue ramp. Vote segment colors follow
  `render_pid_by_gender_chart.py`'s documented party convention (`--accent`
  Clinton, `--honey` Trump, bar-safe gray for other) plus
  `chart_style.DIV_POS_GREEN` for McMullin — named tokens, no hand-picked
  hex. Wired into the existing `cces-2016` Dataset (now 13 graphics;
  `cces2016Vote2016Graphic()` + three `cces2016Gun*Graphic()`), `tsc
  --noEmit` clean, vote PNG read directly (12 rows, all segment labels ≥8%
  print, legend 2x2 clear of caption), PNGs served 200. Same
  local-verification gotcha as the three previous passes (other session's
  uncommitted TDZ bug 500s every Data Explorer page); verified via tsx on
  the staged copy and staged `data-explorer.ts` as a plumbing blob.
  Remaining CCES 2016 candidates: `ideo5` (5-point ideology distribution by
  religion — real but near-duplicates the CES `pid-over-time` partisanship
  story), CC16_330b (skipped, see above), `natecon`/`econfuture`/`mymoney`
  (retrospective/prospective economy, 2016-specific and partisan-coded),
  `police` (feel safe around police — no religious angle). Consider this
  dataset fully mined.

- **pew-rls-2014** (2014 Religious Landscape Study) — seventh pass,
  2026-09-06: first re-verified the log's standing claim that the nine
  cross-national datasets have no usable LDS breakout by scanning every
  value label in the Latin America 2014, Sub-Saharan Africa 2010, and
  10-country 2007 .sav files for a Mormon code: Latin America has none at
  all, Africa's `denom` code 11 has n=15 pooled across 19 countries, and
  the 10-country file has 50 Mormons scattered across five countries with
  country-specific weights — claim holds, don't re-check. Then re-examined
  this dataset's own "thinner/weaker-fit" leftovers (qi2t/qi2u): they are
  "do you ever eat beef/pork," not a Word of Wisdom item — the prior pass
  was right to skip them. But the same qi2 practice battery had two items
  never charted anywhere on the site (duplicate-checked against every
  scripture/prayer-group/practice title): `qi2g` and `qi2c`. qi2a/qi2b are
  already live under the 2023-24 wave's "Prayer or scripture study groups,
  weekly+"/"Read scripture outside of services, weekly+" and were skipped as
  same-construct duplicates; qi2d (pray in tongues, Christians only,
  Mormon 10.6%, mid-pack) and qi2m (home shrine, Buddhists only) dropped.
  Built `share-faith-weekly.png` (qi2g, affiliated adults only — the
  unaffiliated were not asked and drop out under the 30 floor: 33.3% of
  Mormons share their faith with non-believers at least weekly, 4th of 11
  behind Jehovah's Witness 77.4%, Historically Black Protestant 45.4%, and
  Evangelical 36.1%, vs 26.1% of all affiliated adults — a genuinely
  interesting non-highest result given the missionary program) and
  `meditate-weekly.png` (qi2c, full sample: 60.5% of Mormons meditate
  weekly+, 3rd of 12 behind JW 80.5% and Buddhist 66.7%, vs 41.1% overall;
  "pondering" as everyday LDS devotion). Mormon n=650-653. Compute
  `scripts/pew-rls-2014/share_faith_weekly.py` / `meditate_weekly.py`
  (this folder's template plus `chart_style.sort_groups` for group_order,
  same convention update pew-rls-2007's 11th chart made) → JSON in
  `docs/datasets/pew-rls-2014/`; render `render_share_faith_weekly_chart.py`
  / `render_meditate_weekly_chart.py` → `public/data-explorer/pew-rls-2014/`.
  Wired in (`shareFaithWeeklyGraphic()`, `meditateWeeklyGraphic()`; dataset
  now 19 graphics), `tsc --noEmit` clean, meditate PNG read directly (13
  rows, "Historically Black Protestant" wraps cleanly, no collisions), PNGs
  served 200. Same local-page 500 gotcha as every pass this session (other
  session's uncommitted TDZ bug), verified via tsx on the staged copy,
  `data-explorer.ts` staged as a plumbing blob. This dataset's qi2 battery
  is now fully used or deliberately skipped; remaining leftovers from prior
  notes (qk10c/qk10d Sunday-school siblings) are still weak-fit. Consider
  this dataset fully mined.

- **pew-rls-2014** (2014 Religious Landscape Study) — eighth pass,
  2026-09-06: instead of working from prior passes' leftover notes, dumped
  all 199 variable labels and cross-checked every substantive item against
  every live title on the site. Already-live constructs skipped: qa1
  happiness ("Who says they're very happy with life?"), qb30/qb30b
  evolution (two charts), qf5 congregation membership ("Member of a house
  of worship"), qi4a spiritual peace and qi4d meaning/purpose (2023-24
  wave), qk10a-d family practices (family-scripture-prayer /
  sunday-school-children / religious-school). Four full-sample items had
  never been charted and form one tight moral-and-family-outlook cluster,
  built as 4 charts (Mormon n=642-663, weighted by WEIGHT, DK/refused
  excluded, rows via `chart_style.sort_groups`):
  `children-without-marriage-worse.png` (qb1c: 84.2% of Mormons call "more
  people having children without getting married" a change for the worse,
  HIGHEST of 12, vs Evangelical 75.3% and 57.1% overall — the family
  proclamation's birth-within-marriage teaching in members' own social
  read), `absolute-standards-right-wrong.png` (qb2d: 57.5% of Mormons say
  there are clear and absolute standards for right and wrong, 2nd to
  Jehovah's Witness 58.0%, vs 33.4% overall), `guidance-religious-
  teachings.png` (qb31: 66.0% of Mormons look most to religious teachings
  for guidance on right and wrong, 2nd to JW 81.8%, above Evangelical
  61.2%, vs 34.1% overall), `very-satisfied-family-life.png` (qa2a: 78.1%
  of Mormons very satisfied with family life, HIGHEST of 12, vs 70.5%
  overall). Compute/render scripts are one-per-chart per this folder's
  convention (`scripts/pew-rls-2014/{children_without_marriage_worse,
  absolute_standards_right_wrong,guidance_religious_teachings,
  very_satisfied_family_life}.py` + matching `render_*_chart.py`), JSON in
  `docs/datasets/pew-rls-2014/`, PNGs in `public/data-explorer/pew-rls-2014/`;
  wired in (four builders sharing a small `rls2014PctAlt` helper; dataset
  now 23 graphics). `tsc --noEmit` clean; 3-line-title PNG read directly
  (13 rows, wraps cleanly, no collisions); PNGs served 200. Same local-page
  500 gotcha as every pass this session (other session's uncommitted TDZ
  bug), verified via tsx on the staged copy, `data-explorer.ts` staged as a
  plumbing blob. Genuinely remaining in this file after the full sweep:
  `qi4c` (feel a strong sense of gratitude weekly+, Mormon 599/661 ≈ 91%
  unweighted — probably highest, worth a chart), `qi4b` (sense of wonder
  weekly+, Mormon 337/661 ≈ 51%, mid-pack per the 2007 sibling check),
  `qb1b` (more women in the workforce a change for the better, Mormon
  ~49%), `qb1a` (immigrants — VOTER panel has a views-of-immigrants chart),
  `qb2a-c` (homosexuality accepted/discouraged, government aid to the
  poor, environmental regulation — political-values items, qb2a partly
  covered by same-sex-marriage charts), `qb20`/`qb21` (government size,
  abortion — CCES abortion charts exist), `qp99` (knows someone gay,
  Mormon 87%, no teaching angle), `qk10c` (religious/home school, Mormon
  11%). Of these only qi4c and qb1b/qb2a have a clean story; the rest are
  political or duplicative.

- **pew-rls-2007** (2007 U.S. Religious Landscape Survey) — 12th-15th
  charts, 2026-09-06: applied the previous pass's lesson to this file —
  dumped all 135 variable labels and cross-checked every substantive item
  against every live title, rather than trusting the "fully mined" note
  (which had only ever re-checked prior passes' own short candidate lists).
  Already-live constructs skipped: q10b/q10d (absolute standards, guidance
  on right and wrong — just shipped from 2014), q10c evolution, q3b family
  satisfaction (2014), q33/q35/q36 afterlife/heaven/hell, q34c
  reincarnation, q42a-d (2007 versions of already-shipped practice items),
  q43a/q43d, q55a-c, q40c (preserve-traditional-beliefs, 2014). Found a
  four-item religious-experience-and-exclusivity cluster never charted
  anywhere (Mormon n=509-579, weighted by `weight`, DK/refused excluded,
  rows via `chart_style.sort_groups`): `miracles-occur-today.png` (q39a:
  79.8% of Mormons COMPLETELY agree miracles still occur today as in ancient
  times, HIGHEST of 12 by 17 points over Evangelical 62.6%, vs 48.1%
  overall; top box used because completely-or-mostly is near-universal
  among Christians), `answer-to-prayer-weekly.png` (q43c: 36.6% of Mormons
  receive a definite answer to a specific prayer request at least weekly,
  4th of 12 behind JW 43.5%/Muslim 41.0%/HBP 40.0%, vs 26.7% overall —
  monthly+ would put Mormons first at 61.9% but the family's weekly+ top-box
  convention was kept), `one-true-faith.png` (q40a, affiliated only: 57.9%
  of Mormons say their religion is the one true faith leading to eternal
  life vs "many religions can," 2nd to JW 83.1%, 20 points above Evangelical
  37.9%; distinct from 2014's qh2 non-Christian follow-up chart),
  `one-true-interpretation.png` (q40b, affiliated only: 55.0% say there is
  only one true way to interpret their religion's teachings, 2nd to JW
  79.9%, vs 28.3% overall). One-script-per-chart per this folder's
  convention (`scripts/pew-rls-2007/{miracles_occur_today,
  answer_to_prayer_weekly,one_true_faith,one_true_interpretation}.py` +
  matching `render_*_chart.py`, stamped from the divine-healing template),
  JSON in `docs/datasets/pew-rls-2007/`, PNGs in
  `public/data-explorer/pew-rls-2007/`; wired in (four builders sharing
  `rls2007PctAlt`; dataset now 15 graphics). `tsc --noEmit` clean; the
  3-line-title PNG read directly (12 rows, long "...Churches" labels wrap
  cleanly); PNGs served 200. Same local-page 500 gotcha as every pass this
  session, verified via tsx on the staged copy, `data-explorer.ts` staged
  as a plumbing blob. Genuinely remaining after the full sweep — a good
  "religion in society" cluster for a future pass: `q28d` (participate in
  social activities at your place of worship monthly+, Mormon 68.4%
  HIGHEST vs 39.4% overall — ward activities), `q10a` (values threatened by
  Hollywood/entertainment industry, agree, Mormon 69.1% HIGHEST vs 43.0%),
  `q39c` (religion causes more problems than it solves, agree, Mormon 14.1%
  LOWEST vs 35.3%), `q46` (natural conflict between devout religion and
  modern society, Mormon 36%, mid-pack), `q28a` (choir/musical program
  weekly, Mormon 20%), `q9` (churches should express political views,
  Mormon 47%, mid), `q5a-g` (political-values pairs, largely duplicative of
  CCES/VOTER charts), `q1/q2` (satisfaction with country/personal life).

- **pew-rls-2014-recontact** (2014 RLS recontact survey) — fourth pass,
  2026-09-06: full sweep of all 69 variables against every live title (the
  prior pass's leftover list — qb16, qb21, qc1a/b/d — was either shipped
  already or n<30). Found a four-item marriage-and-family cluster never
  charted (weighted by `rweight`, this folder's 6-group set, DK/refused
  excluded, rows via `chart_style.sort_groups`):
  `parents-shared-upbringing.png` (qb3: 76.6% of Mormons say both parents
  shared their religious upbringing about equally vs mother or father
  more, HIGHEST by 15 points over Evangelical 61.1%, vs 59.0% overall —
  the proclamation's "equal partners"; n=54, those volunteering no
  religious upbringing excluded), `marriage-having-children.png` (qd1e:
  60.2% of Mormons say having children is very important for a successful
  marriage, HIGHEST, vs 42.1% overall; n=61), `marriage-adequate-income.png`
  (qd1a: 31.0% say an adequate income is very important, LOWEST of 6 vs
  47.0% overall — the counterpart: children over income; n=61),
  `spouse-talk-religion.png` (qd4, married/partnered only: 64.3% of Mormons
  talk about religion with their spouse "a lot," HIGHEST by 23 points over
  Evangelical 41.5%, vs 25.5% overall; n=43). Checked and dropped: qd1c/qd1d
  (sexual relationship, chores — no religious angle, LDS mid-pack), qb17/
  qb18 (childhood importance, duplicate construct), qc4*/qc5* congregation-
  shopping battery (Mormon n=30 asked, each cell 7-21 — and LDS wards are
  geographically assigned, so the item barely applies), qd8/qd9a (n<30).
  One-script-per-chart per this folder's convention
  (`scripts/pew-rls-2014-recontact/{parents_shared_upbringing,
  marriage_having_children,marriage_adequate_income,spouse_talk_religion}.py`
  + `render_*_chart.py`), JSON in `docs/datasets/pew-rls-2014-recontact/`,
  PNGs in `public/data-explorer/pew-rls-2014-recontact/`; wired in (four
  builders sharing `recontactPctAlt`; dataset now 12 graphics). `tsc
  --noEmit` clean, PNG read directly (7 rows, 2-line subtitle clear), PNGs
  served 200; same local-page 500 gotcha, verified via tsx on the staged
  copy. Process note: this pass staged and committed in ONE command, after
  the previous pass's staged files were swept into a concurrent session's
  commit (d8d003d) in the shared index. Consider this dataset fully mined:
  every remaining item is n<30 for Mormons or already live.

- **pew-rls-2007** (2007 U.S. Religious Landscape Survey) — 16th-18th
  charts, 2026-09-06: built the "religion in society" cluster the previous
  2007 sweep had queued (numbers verified then, re-computed now; Mormon
  n=535-570, weighted by `weight`, DK/refused excluded, rows via
  `chart_style.sort_groups`): `church-social-activities.png` (q28d,
  attenders only: 68.4% of Mormons take part in meals, club meetings, or
  other gatherings at their place of worship at least monthly, HIGHEST of 12
  by 13 points over Historically Black Protestant 55.0%, vs 39.4% overall —
  ward activity culture), `values-threatened-hollywood.png` (q10a: 69.1% of
  Mormons agree their values are threatened by Hollywood and the
  entertainment industry, HIGHEST by 13 points over JW 56.2%, vs 43.0%),
  `religion-causes-problems.png` (q39c: 14.1% of Mormons agree religion
  causes more problems in society than it solves, LOWEST of 12, vs
  Evangelical 21.1% and 35.3% overall). Checked and dropped: q46 (conflict
  between devout religion and modern society, Mormon 36%, mid-pack), q9
  (churches should express political views, Mormon 47%, mid), q28a (choir
  weekly, 20%, thin construct), q5a-g political pairs (CCES/VOTER cover
  these). One-script-per-chart (`scripts/pew-rls-2007/
  {church_social_activities,values_threatened_hollywood,
  religion_causes_problems}.py` + `render_*_chart.py`), JSON in
  `docs/datasets/pew-rls-2007/`, PNGs in `public/data-explorer/pew-rls-2007/`;
  wired in (three builders reusing `rls2007PctAlt`; dataset now 18
  graphics). `tsc --noEmit` clean; 13-row PNG with a 3-line subtitle read
  directly (tight but clean); PNGs served 200; same local-page 500 gotcha,
  verified via tsx on the staged copy; staged and committed in one command.
  After two full sweeps this dataset is now genuinely fully mined: every
  remaining substantive item is live, duplicative, mid-pack, or political.

- **pew-atp-w44-2018** (American Trends Panel Wave 44, February 2019 —
  religious knowledge) — second pass, 2026-09-06: first ATP wave to get a
  full variable sweep (113 vars) against every live title rather than a
  candidate-list check. Skipped as already live or no-spread: RELMATCH2a
  (Joseph Smith's religion — same construct as the 2010 knowledge survey's
  live "Who knows Joseph Smith was a Mormon?"; LDS 100%), TRINITY (96%
  everywhere, no spread), CHIMPRELa/b (duplicate of RLS childhood-
  importance), REL3c/REL4c (live), the 2019 knowledge items already in
  `knowledge-batch.json`. Dumping every remaining knowledge item's answer
  distribution for Mormons vs all adults showed a clear pattern — Latter-day
  Saints beat the national average on Bible/Christian-teaching items and
  trail it on other traditions' doctrines — so built a 5-chart second batch
  showing both sides (`knowledge_batch_2.py` imports the first batch's
  `knowledge_by_group` and 13-group set; weighted by WEIGHT_W44; each item's
  not-sure/refused excluded): `knows-sermon-on-mount-jesus.png` (SERMON:
  LDS 84.7% vs 72.3% overall), `knows-golden-rule-not-commandment.png`
  (COMMAND: LDS 76.7%, HIGHEST of 13, vs 63.5%), `knows-purgatory-
  purification.png` (PRGTRY: LDS 32.2%, LOWEST by a wide margin vs 67.7%
  overall — 61% of LDS chose "where evildoers go for eternal punishment"),
  `knows-prosperity-gospel.png` (PROSGOSP, half-sample: LDS 26.5% vs 44.7%),
  and `knows-about-mormonism.png` (RELTEACHc, not a quiz item: share saying
  they know "a lot" or "some" about Mormonism — Protestant 56%, Catholic
  49%, unaffiliated 55%, LDS 95%, vs 54.8% overall). LDS n=233-429. Rendered
  by `render_knowledge_batch_2.py` → `public/data-explorer/pew-atp-w44-2018/`;
  wired in (`w44SermonOnMountGraphic()` … `w44KnowsAboutMormonismGraphic()`,
  reusing `w44BatchAlt`; dataset now 16 graphics). `tsc --noEmit` clean;
  13-row PNG with 3-line subtitle read directly (clean); PNGs served 200;
  same local-page 500 gotcha, verified via tsx on the staged copy; staged
  and committed in one command. Remaining after the sweep: the other
  knowledge items are either near-universal (BIBFIG1/2, ATHKNW ~95%),
  mid-pack for LDS (AGKNW, JESNAZ, RELCOUNTRY*, JSBBTH, NUMREL*), or
  further examples of the same "weaker on other religions" pattern already
  shown (TURBAN/Sikhism LDS 38% vs 53%, HINDUTEXT, NBLTRTH, RELMATCH1b
  Kabbalah, RELMATCH2b Maimonides, HOLKNOW3 6 million: LDS 48% vs 63%);
  REL3a-i/REL4a-i/RELTEACHa-i as rated BY Latter-day Saints toward other
  groups is the one untouched shape (a "what Latter-day Saints think of
  others" reversal of the live warmth-toward-Mormons chart). Consider this
  dataset close to fully mined.

- **pew-atp-w143-2024** (American Trends Panel Wave 143, February 2024) —
  third pass, 2026-09-06: full sweep of all 140 variables against every live
  title. Skipped: RELIMPCT_SOC (religion helps vs hurts society — near-
  construct of the live 2007 "religion causes more problems" chart),
  NATCHRc3/CHRNATc (two live Christian-nation charts), AFTDTH (live
  definitely-life-after-death), the shipped BELIEVE_*/PRACTICE_*/DISCRRIM_*/
  PRES1_STRREL/SAMEREL items, the Israel-Hamas and internet-use batteries
  (no religious-practice angle), CCHRCH_* (Catholic-policy opinions),
  TOOFARCON/TOOFARLIB and BIBLE_INFL* (political framing), RELIG_INFL1
  (no spread), CHRASIDE (not asked of Mormons). Built a 4-chart
  religion-in-public-life cluster (F_RELIG group set, Mormon n=165-173,
  weighted by WEIGHT_W143, refused excluded, rows via sort_groups at
  render time as this folder's template does): `religious-disagreement.png`
  (RELIGDISAGREE: 73.2% of Mormons say the best thing to do when someone
  disagrees about religion is understand their beliefs and agree to
  disagree — effectively tied for highest with Orthodox 73.8% n=56, vs
  53.7% overall; only 20% would avoid the subject vs 41.5%),
  `religion-encourages-tolerance.png` (RELIMPCT_TOL: 84.4% say religion
  encourages tolerance, 2nd to Muslim 87.9%, vs 65.3%),
  `conflict-mainstream-culture.png` (RELIGCONFLICT: 58.1% feel a great deal
  or some conflict with mainstream culture, 4th of 12 behind Other/Atheist/
  Jewish, vs 49.5% — companion to the live religious-minority chart, kept as
  a mid-upper result because it completes that pairing),
  `president-stands-up.png` (PRES1_STAND: 46.9% say a president who stands
  up for people with their beliefs is very important, 3rd behind Muslim
  57.4%/Jewish 51.6%, vs 31.5% — completes the live PRES1 battery). One-
  script-per-chart from a scratch generator (`scripts/pew-atp-w143-2024/
  {religious_disagreement,religion_encourages_tolerance,
  conflict_mainstream_culture,president_stands_up}.py` +
  `render_*_chart.py`), JSON in `docs/datasets/pew-atp-w143-2024/`, PNGs in
  `public/data-explorer/pew-atp-w143-2024/`; wired in (four builders sharing
  `w143PctAlt`; dataset now 18 graphics). `tsc --noEmit` clean; 13-row PNG
  with 3-line subtitle read directly (clean); PNGs served 200; same
  local-page 500 gotcha, verified via tsx on the staged copy; staged and
  committed in one command. Remaining: RELIMPCT_SUP (religion encourages
  superstition — LDS 44% = national 43%, no story), PRES1_MORAL (moral life
  very important, LDS 73% vs 65%, thin spread), DISCRRIM_EVANG. Consider
  this dataset fully mined.

- **pew-atp-w132-2023** (American Trends Panel Wave 132, August 2023 —
  spirituality) — fourth pass, 2026-09-06: full sweep of all 140 variables
  against every live title. Skipped as live/duplicate-construct: RTWRNG_a
  (religious beliefs as guide to right and wrong — 2014 RLS chart shipped
  this session), SPIRACT1_a meditate (2014 RLS), SPIRCOM2a (sibling of live
  religious-community), SPIREXP_a/b/c (live spiritual-peace/wonder/beyond-
  this-world), RELEFFECT_d division (near-construct of W143 tolerance),
  GOD/GODBIBLE/BELIEVE_* (RLS belief charts), SOUL (96% of LDS, near-
  universal), DTHLKE_* (checked by the prior pass), the AI battery (no
  religious angle), WHYNONE_* (nones only). Built a 4-chart spiritual-
  meaning-and-trajectory cluster (F_RELIG group set, Mormon n=176-185,
  weighted by WEIGHT_W132, refused excluded, rows via sort_groups in the
  compute script since this folder's renders read group_order as-is):
  `spiritual-loved-ones-passed.png` (SPIRESSENT1_h, half-sample: 49.9% of
  Mormons say being connected with loved ones who have passed is an
  essential part of what being spiritual means, 3rd of 12 behind Muslim
  52.1%/Hindu 51.7% (n=69/79), vs 31.1% overall and Protestant 25.8% —
  eternal families; distinct from live reunited-with-loved-ones DTHLKE_f),
  `spiritual-following-faith.png` (SPIRESSENT1_b: 64.1% say following a
  religious faith is essential to being spiritual, 2nd to Muslim 66.5%, vs
  39.9%; only 4.5% call it unimportant), `felt-deceased-communicating.png`
  (SPIRSPEAK: 54.0% have felt someone who passed away communicating with
  them, HIGHEST of 12 named groups, vs 38.7%), `more-religious-over-
  lifetime.png` (LIFEDIR: 48.5% of current Mormons say they have become
  more religious over their lifetime, 2nd to Muslim 49.1%, twice the 24.4%
  national figure; only 18% say less religious vs 34%). One-script-per-
  chart from a scratch generator (`scripts/pew-atp-w132-2023/
  {spiritual_loved_ones_passed,spiritual_following_faith,
  felt_deceased_communicating,more_religious_over_lifetime}.py` +
  `render_*_chart.py`), JSON in `docs/datasets/pew-atp-w132-2023/`, PNGs in
  `public/data-explorer/pew-atp-w132-2023/`; wired in (four builders
  sharing `w132PctAlt`; dataset now 11 graphics). `tsc --noEmit` clean;
  13-row PNG with 3-line title read directly (clean); PNGs served 200; same
  local-page 500 gotcha, verified via tsx on the staged copy; staged and
  committed in one command. Remaining after the sweep: SPIRESSENT1_d
  (connected with God essential, LDS 81% vs 70% — same construct family as
  the two shipped, thinner spread), SPIRENC (encountered a spirit, LDS 55%
  vs 48%), SPIRENERGY_a-d (nature/objects/animals/graveyards have spirits,
  LDS 58% vs 49% on nature — an odd fit), ALTID_d (identify as spiritual),
  RELEFFECT_a/c (religion gives meaning / encourages doing right — likely
  LDS-high but close to the W143 tolerance chart). Consider this dataset
  fully mined.

- **pew-atp-w117-2022** (American Trends Panel Wave 117, November 2022 —
  religion and technology) — third pass, 2026-09-06: full sweep of all 150
  variables against every live title. Skipped: the election/vote-validation
  battery (VOTECHOICE2020 by religion is a real item — LDS 71.5% Republican
  among 155 validated voters — but political and cross-dataset-adjacent to
  the CCES 2016 vote chart; left for a future political pass), the
  online-watching follow-ups (ONLINE*/WATCH*/VIRSAT*/CNCTVIR, small
  subsamples, live watch-online-monthly covers the headline), NONTECH2_c
  (live), APPUSE1_a/b/d (meditation/gratitude/prayer apps — LDS 20/19/12%
  vs 19/19/15% nationally, no story, deliberately not charted), APPUSE2_c/d
  and PRAYGRP1_a (prayer requests online, online study groups — thin).
  Built a 4-chart cluster (F_RELTRAD 8-group set per this folder's
  template, Mormon n=163-197, weighted by WEIGHT_W117, refused excluded,
  rows via sort_groups in the compute script): `scripture-app.png`
  (APPUSE1_c: 58.6% of Mormons use an app or website that reminds or helps
  them read scripture, HIGHEST by 8 points over Historically Black
  Protestant 51.0%, nearly 3x the 21.9% national figure — Gospel Library /
  Come, Follow Me in the data), `religion-podcasts.png` (APPUSE2_a: 40.4%
  listen to religion-focused podcasts, HIGHEST, vs 15.5%),
  `search-religion-online.png` (PRAYGRP1_b: 53.1% go online to search for
  information about religion, HIGHEST, vs 31.6%), `connection-at-
  services.png` (CNCTPER, in-person attenders only: 45.4% feel a great deal
  of connection with others at services, in a three-way tie for highest
  with Jewish 45.5% (n=65) and Historically Black Protestant 45.4%, vs 34.9%
  of attenders; Orthodox dropped n<30). One-script-per-chart from a scratch
  generator (`scripts/pew-atp-w117-2022/{scripture_app,religion_podcasts,
  search_religion_online,connection_at_services}.py` + `render_*_chart.py`),
  JSON in `docs/datasets/pew-atp-w117-2022/`, PNGs in
  `public/data-explorer/pew-atp-w117-2022/`; wired in (four builders
  sharing `w117PctAlt`; dataset now 11 graphics). `tsc --noEmit` clean; PNG
  read directly (9 rows, clean); PNGs served 200; same local-page 500
  gotcha, verified via tsx on the staged copy; staged and committed in one
  command. Remaining: LEADERFOLLOW1 (follow celebrities/pastors online, LDS
  28% vs 14%, n=147 — a fair 5th but thinner construct), NONTECH1_a
  (religious radio, LDS 36% vs 25%), UNFOLREL (unfollowed someone over
  religion, LDS 18% vs 22%, no story), ATTENDPREF (n=65). Consider this
  dataset fully mined apart from the political vote-validation item.

- **pew-atp-w114-2022** (American Trends Panel Wave 114, September 2022 —
  religion and politics) — third pass, 2026-09-06: full sweep of all 166
  variables against every live title. Skipped: NATCHR*/CHRNAT* (two live
  Christian-nation charts; CHRNAT1b LDS n=54), DIVRELPOP (live "Religious
  diversity strengthens society" construct on another dataset), ESSENT_a/b/k
  (live), REL4_c (live knows-a-Mormon), KEEPOUT (LDS 45% say churches should
  express views vs 32% — real but mid-story; logged), the science/COVID/
  Ukraine/monkeypox/mental-health batteries (no religious-practice angle;
  MH_TRACK_d "hopeful most or all of the time" is LDS 26% vs 17% and worth
  a future wellbeing chart). Built 4 charts (F_RELIG frame, Mormon
  n=166-190, weighted by WEIGHT_W114, refused excluded, rows via
  sort_groups): `harder-for-religious.png` (REL2: 66.1% of Mormons say
  living in the U.S. is harder than 10 years ago for people with a strong
  religious faith, HIGHEST of 12, vs 48.1%), `churches-endorse-
  candidates.png` (CHURCH_CAND: 11.0% of Mormons say churches should come
  out in favor of candidates, LOWEST of any religious group — only atheists
  4% and agnostics 7% lower — vs 20.7%; the Church's political-neutrality
  policy in members' own views), `churches-too-much-influence.png`
  (CHURCHPOL: 22.0% say churches have too much influence in politics, 2nd
  lowest after Orthodox 20.1% n=49, vs 42.7%; distinct from the 2014 RLS
  agree/disagree item and Faith Matters 2011's too-little framing),
  `lds-views-of-groups.png` (RELFAV_a-f,i among LDS respondents only —
  the reverse of the live relfav-mormons chart, rows = rated groups, same
  DK-excluded convention as relfav_mormons.py: Jews 65%, mainline
  Protestants 61%, Catholics 60%, evangelicals 57%, Muslims 53%, atheists
  26%, own group 81% — each far above the corresponding national favorable
  share; the first "how Latter-day Saints view others" chart on the site).
  Three via a scratch generator (`scripts/pew-atp-w114-2022/
  {harder_for_religious,churches_endorse_candidates,
  churches_too_much_influence}.py`) plus hand-written
  `lds_views_of_groups.py`, each with `render_*_chart.py`; JSON in
  `docs/datasets/pew-atp-w114-2022/`, PNGs in
  `public/data-explorer/pew-atp-w114-2022/`; wired in (four builders sharing
  `w114PctAlt`; dataset now 9 graphics). `tsc --noEmit` clean; 7-row PNG
  read directly (identity colors per rated group, clean); PNGs served 200;
  same local-page 500 gotcha, verified via tsx on the staged copy; staged
  and committed in one command. Remaining: ESSENT_g/h/i/j (patriotic /
  family traditions / moral life / community as essential to faith — LDS
  38/50/80/44% vs 32/45/75/41%, thin spreads), KEEPOUT, MH_TRACK_d,
  RELFAV_* rated by other groups toward Evangelicals/Catholics/etc. (not
  Mormon-specific), REL1 (harder for non-believers, LDS 31% vs 36%).
  Consider this dataset fully mined apart from a possible wellbeing chart.

- **pew-atp-w162-2025** (American Trends Panel Wave 162, February 2025 —
  Catholics in America) — third pass, 2026-09-06: full sweep of all 131
  variables against every live title, and this one genuinely is nearly
  exhausted: ~90 of the variables are Catholic-only (CATH*, CCHRCH_*,
  PARISH*, MASS*, LATMASS, CONFESS/COMMUNION — LDS n=33-35 on the
  half-sample CCHRCH items), and the all-respondent items are almost all
  live constructs elsewhere — SOCTRUST2 (LDS 71% trust most people vs 56%,
  but "Most people can be trusted" is live from the VOTER panel),
  TRUSTFEDGOV (live VOTER trend), CHRELIG retention (raised-Mormon 198 →
  still 108, 55%; live retention charts), PRACTICEA_BIB/OTHSCRPT (scripture-
  reading construct live; n=35/100), RELIGCONFLICT (live), PRACTICEA_WEAR/
  CNDL/SAINTS/OBJ + RELART (live), RELIG_INFL1/2 (checked by the prior
  pass, ambiguous item), RELSCHL1/2 (W44 construct live), ABUSE1/ABUSE3
  (perceptions of Catholic abuse reports — LDS 43% say more common among
  priests vs 36%, a real but uncomfortable-fit item, not built), CATHASIDE
  (LDS 18.5% "Catholic in some way aside from religion," asked of non-
  Catholics — niche). Built the one clean remaining item:
  `pope-francis-favorable.png` (PPLFAV_a among those who had heard of him,
  RELIG_W162 frame per this folder's convention, LDS n=118, weighted by
  WEIGHT_W162: 62.8% of Latter-day Saints held a favorable opinion of Pope
  Francis in the last weeks of his papacy, 6th of 12 and just above the 62.0%
  national figure — well above Protestants 53.4% and far above Orthodox
  Christians 28.4% (n=41), below Catholics 80.8%; PPLFAV_PBen Benedict XVI
  shows no LDS story, 44% vs 45%). Hand-written
  `scripts/pew-atp-w162-2025/pope_francis_favorable.py` +
  `render_pope_francis_favorable_chart.py`, JSON in
  `docs/datasets/pew-atp-w162-2025/`, PNG in
  `public/data-explorer/pew-atp-w162-2025/`; wired in
  (`popeFrancisFavorableGraphic()`; dataset now 8 graphics). `tsc --noEmit`
  clean; 13-row PNG read directly (clean); PNG served 200; same local-page
  500 gotcha, verified via tsx on the staged copy; staged and committed in
  one command. Consider this dataset fully mined — the sweep found nothing
  else that is both LDS-usable and not already live.

- **pew-atp-w70-2020** (American Trends Panel Wave 70, July 2020 — religion
  during COVID) — fourth pass, 2026-09-06: full sweep of all 142 variables
  against every live title. Skipped: the contact-tracing/data-privacy/
  social-media batteries (no religious angle), SERMONISSUE_a/c-g (BLM-
  opposition, COVID-precaution, government-order, voting, abortion sermons —
  LDS mid-pack or thin; b is live), ATTENDFUT1 (post-outbreak attendance
  intentions — no story once non-attenders are separated: LDS 8% expect to
  attend less vs 9%), COVIDTHREAT_* (health-threat perceptions, no religious
  angle), SPIRIT1/SPIRIT2 non-devotional coping items (outdoors/exercise/
  phone/TV — LDS ≈ national), COVIDVOL1_c/COVIDVOL2_a-c (thin or checked
  earlier), CONGRESTRICT2_a/b/d (same direction as the charted c item with
  smaller gaps). Built a 4-chart COVID congregational-life cluster (this
  folder's 7-group F_RELTRAD set, weighted by WEIGHT_W70, refused excluded,
  rows via sort_groups): `sermon-about-trump.png` (SERMONTRUMP, monthly
  attenders, LDS n=103: 11.7% of Mormon attenders heard a sermon expressing
  support for, opposition to, or both about Donald Trump, LOWEST of 7 vs
  27.6% of all attenders; the Biden item runs 8.7% vs 20.4% and is not
  charted separately — the political-neutrality policy in what members
  actually hear at church, pairing with W114's endorsement chart),
  `restrict-attendance-covid.png` (CONGRESTRICT2_c, attenders, LDS n=96:
  85.8% say their house of worship should limit how many can attend, 2nd
  to Catholic 90.0%, vs 73.6%), `worship-rules-flexibility.png` (COVIDRF,
  full sample, LDS n=163: 34.3% say houses of worship should get more
  flexibility on distancing rules than other organizations, 2nd to
  Evangelical 36.9%, vs 19.4% — a religious-liberty stance sitting alongside
  strong in-congregation restriction support), `helped-neighbors-covid.png`
  (COVIDVOL1_a, full sample, LDS n=167: 48.8% helped friends or neighbors
  with groceries, errands or child care, HIGHEST (narrowly over
  Historically Black Protestant 48.1%), vs 38.8% — ministering during the
  first pandemic months). One-script-per-chart from a scratch generator
  (`scripts/pew-atp-w70-2020/{sermon_about_trump,restrict_attendance_covid,
  worship_rules_flexibility,helped_neighbors_covid}.py` + `render_*_chart.py`),
  JSON in `docs/datasets/pew-atp-w70-2020/`, PNGs in
  `public/data-explorer/pew-atp-w70-2020/`; wired in (four builders sharing
  `w70PctAlt`; dataset now 14 graphics). `tsc --noEmit` clean; PNG read
  directly (8 rows, 3-line subtitle, clean); PNGs served 200; same local-page
  500 gotcha, verified via tsx on the staged copy; staged and committed in
  one command. Consider this dataset fully mined. **Session status after
  this pass:** every ATP wave in `data/` (44, 70, 114, 117, 132, 143, 162)
  and every RLS file (2007, 2014, recontact) has now had a full
  variable-level sweep; the only datasets not yet swept this way are
  pew-mormon-survey-2011 (Mormon-only, by-activity charts) and
  pew-hispanics-religion-2007 (LDS n=34), plus W117's held-back
  VOTECHOICE2020 political item.

- **lds-brazil-2022** (compiled Brazil membership timeline + Church
  facts-and-statistics pages + 2022 Census/IBGE) — new dataset, 2026-09-11:
  three graphics, this site's first Brazil-specific entry. `membership-by-year.png`
  compiles a sparse 1940-2025 Brazil membership timeline (Wikipedia's
  "The Church of Jesus Christ of Latter-day Saints in Brazil" compiled
  timeline for 1940-1979/1989/1999/2009/2019, cumorah.com's "Expanding LDS
  Outreach in Brazil" case study for 2000/2010, the Church's own
  facts-and-statistics page for 2025's 1,573,360) — additional WebSearch/
  WebFetch against the Church newsroom country page (Wayback Machine
  unreachable from this environment), Wikipedia's broader membership-
  statistics article, and ldschurchgrowth.blogspot.com's annual
  country-by-country posts (2019/2021/2022/2024) did not turn up further
  real annual totals for the 2011-2018/2020-2024 gaps — those years are
  left as genuine gaps, not interpolated. `latin-america-comparison-2025.png`
  is a single-source-per-country snapshot (Brazil, Mexico, Peru, Chile,
  Argentina facts-and-statistics pages, Dec. 31, 2025): Brazil (1,573,360)
  narrowly overtook Mexico (1,572,287) by 1,073 members to become the
  largest Latter-day Saint population outside the U.S. `smaller-faiths-by-state-2022.png`
  is IBGE's 2022 Census "Outras religiosidades" ("Other religions") share
  by state, 10+ population, weighted by P0110, from a pre-computed
  tabulation cross-checked against the official report's own Roraima
  (~7.8%, computed 7.78%) and national (2.7%→4.0%, 2010→2022) figures —
  framed explicitly, in title/subtitle/caption and this dataset's README,
  as NOT an LDS-specific number, since IBGE's public microdata only
  breaks religion into 9 broad groups and has never released a granular
  breakout isolating LDS from that mixed bucket. Added a `row_label_fontsize`
  override param to `render_magnitude_bar` (scripts/flagship-charts/common.py,
  default unchanged/`MIN.LEGEND` for every other caller) since the
  27-state/DF chart's row labels overlapped at the pipeline's normal
  24pt floor. Hand-written `scripts/lds-brazil-2022/{build_membership_by_year,
  build_latin_america_comparison,build_smaller_faiths_by_state}.py` +
  matching `render_*_chart.py` scripts, JSON in `docs/datasets/lds-brazil-2022/`,
  PNGs in `public/data-explorer/lds-brazil-2022/`; wired in as a new
  single dataset with three graphics under the "Mixed Datasets" category.
  `tsc --noEmit` clean; all three PNGs read directly and visually checked.

- **lds-brazil-census-2010** (IBGE 2010 Census, SIDRA table 137) — new
  dataset, 2026-09-11, follow-up to lds-brazil-2022: three graphics, this
  site's second Brazil-specific entry. Unlike the 2022 Census, IBGE's
  **2010** Census religion table published "Igreja de Jesus Cristo dos
  Santos dos Ultimos Dias" as its own real, government-tabulated category
  (SIDRA table 137, classification 133, category 100423) - genuine
  LDS-specific counts, not a mixed bucket, hence a separate dataset from
  lds-brazil-2022 rather than a fourth chart bolted onto it. Verified live
  against apisidra.ibge.gov.br this session (not just taken from a prior
  brief): national query confirms 1991 and 2000 both return "..."
  (suppressed) at this category - only 2010 has a real figure (226,509) -
  so no 1991-2010 LDS-specific time series was built, per the "don't
  fabricate a series with no real data" instruction. `lds-by-state-2010.png`
  ranks all 27 states/DF by LDS share of each state's own population
  (not raw count - Sao Paulo has the most members absolutely but a lower
  share than several smaller states); Amazonas (0.245%) and Rio Grande do
  Sul (0.245%) are effectively tied at the top once computed to more
  precision than the source brief carried. `self-id-vs-membership-2010.png`
  is a two-bar comparison (226,509 self-identified to the census vs.
  1,138,740 on the Church's own 2010 membership rolls, the same figure
  already cited in lds-brazil-2022/membership-by-year.json) - framed
  factually as two different measures, not attributing the ~5:1 gap to a
  single cause. `top-cities-2010.png` ranks municipalities (population
  50,000+, to exclude small-town noise - 4,548 of 5,565 municipalities
  come back suppressed at this category, and most of the rest are tiny
  towns) by LDS share; Sant'Ana do Livramento, RS tops the list at 1.04%,
  and 5 of the top 10 are in Rio Grande do Sul, including two Uruguay
  border cities. Added a `value_decimals` param to `render_magnitude_bar`
  (scripts/flagship-charts/common.py, default 0/unchanged for every
  existing caller) since this dataset's state-level shares (0.03%-0.25%)
  would otherwise all round to "0%" under the pipeline's fixed `.0f`
  value-label format. Hand-written
  `scripts/lds-brazil-census-2010/{build_lds_by_state_2010,
  build_self_id_vs_membership_2010,build_top_cities_2010}.py` + matching
  `render_*_chart.py` scripts (the two-bar comparison reuses
  `render_magnitude_bar` at 2 rows rather than a new shape, following the
  latin-america-comparison-2025.png precedent for K-suffixed raw counts),
  JSON in `docs/datasets/lds-brazil-census-2010/`, PNGs in
  `public/data-explorer/lds-brazil-census-2010/`; wired in as a new
  single dataset with three graphics under the "Mixed Datasets" category.
  `tsc --noEmit` clean, `next build` clean, all three PNGs read directly
  and visually checked, dataset page verified in a local dev server (the
  `/graphics` subpage hit a pre-existing local-dev-only rendering quirk
  that also affects the already-shipped lds-brazil-2022/graphics page -
  not something this change introduced).

- **lds-brazil-2022** (organizational/administrative Church data - temple
  chronology + "Reaching the Nations" mission counts) - two more graphics,
  2026-09-11, third Brazil follow-up batch (after the two above):
  `temples-dedicated-by-year.png` and `missions-by-decade.png`, both added
  to the existing lds-brazil-2022 dataset (now 5 graphics) rather than a
  third new dataset slug, since both are Church-reported organizational
  stats in the same spirit as that dataset's existing membership/Latin-
  America charts. `temples-dedicated-by-year.png` is a cumulative count of
  all 12 currently-dedicated Brazil temples by dedication year, 1978-2026,
  cross-verified against the Church's official chronology and temple-list
  pages, with #12 (Belo Horizonte, Aug 16, 2026) confirmed via a direct
  search of Church Newsroom's own dedication article. The pace visibly
  accelerates: 22 years between temple #1 (1978) and #2/#3 (2000), then
  roughly one every 2-4 years, then 5 of the 12 dedicated in just the last
  4 years (2022-2026) - that "5" was independently recomputed from the
  full temple table in this pass (an `assert` in the build script checks
  it), not trusted from the source brief's own prose, per this session's
  own instruction to double-check after an earlier unrelated counting
  slip; it checked out at exactly 5. Two calendar years (2000, 2002 for
  the year-only view; more precisely 2000 twice and 2022 twice) had two
  dedications apiece, collapsed into one plotted point per year carrying
  that year's ending cumulative total. `missions-by-decade.png` is 8 real,
  sparse decade-by-decade mission counts, 1950-2025, quoted verbatim from
  cumorah.com's "Reaching the Nations" Brazil country report (1 in 1950 to
  27 in 2010) plus the Church's own current 2025 figure (37) - no
  interpolation, same pattern as this dataset's own membership-by-year.json.
  Notes in its subtitle that mission counts roughly doubled each decade
  through 1990 then grew far more slowly after 2000, a different shape
  than the membership curve's steady climb over the same period, without
  asserting a specific cause. Both use `render_timeseries`
  (scripts/flagship-charts/common.py) - the same shape as this dataset's
  membership-by-year chart - with non-default `y_step`/`y_label_divisor`/
  `y_label_suffix` since these are small whole-number counts (temples 1-12,
  missions 1-37), not the module's membership-scale default. The temples
  chart also needed `x_tick_step=10` rather than a denser step: with only
  10 plotted points several fall within 1-2 years of each other (2000/2002,
  then 2022/2023/2024/2026), and labeling every real year collided their
  4-digit x-axis labels into an unreadable run - `x_tick_step=10` keeps
  only round-decade labels plus the series' own forced first/last year,
  while every real point still gets its own plotted marker regardless of
  whether its year is separately labeled. Hand-written
  `scripts/lds-brazil-2022/{build_temples_dedicated_by_year,
  build_missions_by_decade}.py` + matching `render_*_chart.py` scripts,
  JSON in `docs/datasets/lds-brazil-2022/`, PNGs in
  `public/data-explorer/lds-brazil-2022/`; wired in as two more graphics
  on the existing dataset entry. `tsc --noEmit` clean, `next build` clean,
  both PNGs read directly and visually checked (including a re-render
  after the x-axis label-collision fix), dataset page verified in a local
  dev server - both PNGs served 200 directly; the `/graphics` subpage hit
  the same pre-existing local-dev-only rendering quirk already noted above
  for this dataset and lds-brazil-census-2010, confirmed again this pass
  by reproducing it on the latter's own `/graphics` page too - not
  something this change introduced.
