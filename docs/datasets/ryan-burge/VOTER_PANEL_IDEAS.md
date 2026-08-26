# VOTER Survey Panel: 20 graphic ideas for LDS-focused analysis

The `ryan-burge` `GRAPHICS_TODO.md` backlog is fully shipped — every item
ever queued there is built. Per that file's own workflow note, this is
**not a new backlog** and nothing here should be built without asking
first: it's a starting list for the user to pick from, or to use as a
jumping-off point for their own exploration of the panel
(`data/ryan-burge/reference/voter_survey_panel_variable_list.tsv` has the
full 867-variable list; `voter_survey_panel.dta` is the file itself).

What makes this panel different from every other dataset this project has
used so far (Pew RLS, CCES 2016, CES stacked) is that **it's the same
~8,000 people re-interviewed six times, 2011–2020** — so it can answer
"how did this person's views change," not just "how do groups compare
right now." Most of the ideas below lean into that, tracking the same LDS
panelists across waves rather than re-running a cross-sectional comparison
Pew RLS or CCES could already answer just as well.

Every idea below cites real variable names confirmed to exist in the file
(via `pyreadstat` metadata), not guessed from the codebook. None of these
have been checked for LDS sample size at the specific wave-pair/cross
proposed — that's the first thing to verify before scoping any of these
into an actual backlog item, the same way every shipped item in
`GRAPHICS_TODO.md` documents its own N.

1. **Religious retention panel.** `religpew_baseline` → `religpew_2016` →
   `religpew_2017`: of the same people who identified as LDS at baseline
   (~2011), what share still identify as LDS by 2016 and by 2017? A true
   individual-level retention rate, not the recalled/inferred switching
   rate Pew RLS's `FRMREL`/`CURREL` cross-tab already covers.
2. **Longitudinal religiosity trajectory.** `pew_religimp_baseline/2016/2017`
   and `pew_prayer_baseline/2016/2017` for the same LDS panelists — did
   devotion rise, fall, or hold steady across the Trump era specifically,
   tracked person-by-person rather than wave-average.
3. **Vote-switching, 2012 → 2016 → 2020.** Presidential vote-choice
   variables across waves, LDS only — Utah's unusually low 2016 Trump
   support (the McMullin effect) is well known at the state level; this
   panel can show whether the *same* LDS Trump-skeptics returned to the
   GOP by 2020 or stayed away.
4. **2016 vote regret, LDS specifically.** `wishvote2016_2017`,
   `regretvote2016_2017`, `redovote2016_2017` — did LDS respondents wish
   they'd voted differently, or would they redo the same choice, compared
   to other traditions.
5. **Trust in government over time.** `trustgovt_baseline/2016/2017`,
   same-person trend for LDS vs. other groups — not just "who trusts govt
   more," but whose trust moved and whose didn't.
6. **Authoritarian child-rearing values.** `SOCIAL_CONFORMITY_3_2016`
   (the classic political-science child-rearing/authoritarianism proxy:
   obedience vs. self-reliance) by religion.
7. **Gender-role attitudes.** The `sexism1_2016`–`sexism6_2016` battery
   (traditional roles, workplace discrimination, harassment) by religion.
8. **Muslim-surveillance and distrust battery.** `muslim_distrust_airport_2017`,
   `muslim_distrust_mosque_2017`, `muslim_distrust_vote_2017`,
   `muslim_describe_terrorism_2017` — how LDS compares to other Christian
   traditions here, a sharper cut than the single Muslim feeling
   thermometer already shipped.
9. **Immigration attitudes, multi-item index.** `immi_contribution_2017`,
   `immi_naturalize_2017`, `immi_makedifficult_2017`,
   `immigrants_economy_2017`/`_crime_2017`/`_culture_2017`/`_security_2017`
   — a richer immigration picture than the single stranger-in-my-own-
   country item already shipped.
10. **Racial resentment battery.** `race_slave_2016` (structural-inequality
    framing) and `reverse_discrimination_2016` (anti-white-discrimination
    framing) by religion — two different racial-attitude framings, not
    just one item.
11. **Trade/tariff attitudes.** `tradepolicy_2016`, `free_trade_1_2016`
    through `free_trade_5_2016` (jobs/wages/prices/quality/quantity
    effects) by religion — LDS's traditionally pro-business lean tested
    against Trump-era protectionism specifically.
12. **Which Trump promises mattered to LDS voters.** The `promise_*_2017`
    battery (the wall, ACA repeal, TPP withdrawal, reducing corruption) —
    importance *and* perceived success, by religion.
13. **Generalized social trust over time.** `trust_people_2016` ("most
    people can/can't be trusted") by religion — a different trust
    construct than institutional trust in item 5.
14. **Media diet by religion.** `enews_show_1_baseline`–`_7_baseline`
    (ABC/CBS/NBC/Fox/PBS/CNN/MSNBC), `sundaytalkshow_3_baseline` (Fox News
    Sunday), `localeve_baseline`/`localnewspaper_baseline` — does LDS skew
    toward particular news sources relative to other traditions.
15. **Military household rate.** `milstat_1_baseline`–`_5_baseline`
    (self/family currently serving or previously served) by religion —
    tests a real perception (LDS mission service culture correlating with
    broader civic/military service) against actual panel data.
16. **Civic organization membership.** `org_membership_*_baseline` (NRA,
    NOW, Rotary International, National Wildlife Federation, etc.) by
    religion — LDS's civic-engagement footprint beyond church itself.
17. **Volunteering by cause, not just yes/no.** `volunteerorg2_*_baseline`
    (immigrant/refugee assistance, environmental/animal care, healthcare,
    international organizations) by religion — where LDS volunteer effort
    actually goes, sharper than a single "volunteered in the past 12
    months" yes/no (already shipped for Pew RLS).
18. **National pride battery.** `prouddem_2016` (how democracy works),
    `proudgrp_2016` (fair/equal treatment of groups), `proudhis_2016`
    (America's history) by religion — three distinct pride framings, not
    one generic "patriotism" score.
19. **Populist elite-distrust sentiment.** `RIGGED_SYSTEM_6_2016`
    ("elites in this country don't understand the problems I am facing")
    by religion — how LDS populist sentiment compares to white
    evangelicals' well-documented version of this attitude.
20. **Gay marriage attitude shift, baseline → 2016.** `gaymar2_baseline`
    (~2011, pre-*Obergefell*) → `gaymar_2016` (post-*Obergefell*), same
    LDS panelists — an individual-level view of how much movement (or
    none) happened across a period of major national attitude change and
    the LDS Church's own evolving public position during it.
