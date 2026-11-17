# VOTER Survey Panel: 20 graphic ideas for LDS-focused analysis

**Status: all 20 built, 2026-08-26.** This started as a brainstorm list,
not a backlog — nothing here was ever queued as a formal `GRAPHICS_TODO.md`
item — but the user asked for all twenty built, so every idea below now
links its shipped PNG and the scripts that produced it. Kept here (rather
than folded into `GRAPHICS_TODO.md`) since it's still useful as a
map of what's in the panel beyond what got built; see
`data/ryan-burge/reference/voter_survey_panel_variable_list.tsv` for the
full 867-variable list if you want to keep exploring past this list.

What makes this panel different from every other dataset this project has
used (Pew RLS, CCES 2016, CES stacked) is that **it's the same ~8,000
people re-interviewed across multiple waves** — so it can answer "how did
this person's views change," not just "how do groups compare right now."
Six ideas below (1/2/3/5/20) lean into that: every respondent's group is
fixed at their `religpew_baseline` (~2011) identity and tracked forward
through 2016/2017 regardless of whether they still identify with that
religion later — genuinely something a repeated cross-section (Pew RLS,
CCES) can't do.

**Wave-scope correction, found while building idea 3**: the actual
`voter_survey_panel.dta` file only contains **baseline (~2011), 2012,
2016, and 2017** waves (confirmed via `pyreadstat` column-metadata
inspection, not assumed) — not the fuller 2011–2020 range the dataset's
own top-level description mentions for the wider VOTER Survey program.
Idea 3 below is scoped to 2012 → 2016, not → 2020 as originally drafted.

Every idea cites real variable names confirmed to exist in the file. Build
details, design decisions (cutpoints, polarity handling, thin-group
exclusions), and exact population definitions are documented in each
`scripts/ryan-burge/voter_ideas_*.py` compute script's own docstring —
not repeated here.

1. **Religious retention panel.** ✅ Built —
   [line chart](../../../public/data-explorer/voter-survey-panel/idea-retention.png).
   `religpew_baseline` → `religpew_2016` → `religpew_2017`, all nine
   religion groups (not just LDS): of each tradition's baseline members,
   what share still identify with it by 2016 and by 2017.
2. **Longitudinal religiosity trajectory.** ✅ Built — two line charts:
   [religion "very important"](../../../public/data-explorer/voter-survey-panel/idea-religimp-trend.png),
   [pray daily](../../../public/data-explorer/voter-survey-panel/idea-prayer-trend.png).
   Baseline cohort tracked forward through 2016/2017.
3. **Vote-switching, 2012 → 2016** (corrected from → 2020 - see the
   wave-scope note above). ✅ Built —
   [paired bar](../../../public/data-explorer/voter-survey-panel/idea-vote-2012-2016.png),
   Republican vote share by baseline cohort, 2012 vs. 2016.
4. **2016 vote regret.** ✅ Built — two bars:
   [wished they'd voted](../../../public/data-explorer/voter-survey-panel/idea-wished-voted.png),
   [regret their vote](../../../public/data-explorer/voter-survey-panel/idea-vote-regrets.png).
5. **Trust in government over time.** ✅ Built —
   [line chart](../../../public/data-explorer/voter-survey-panel/idea-trustgovt-trend.png).
   Baseline cohort tracked forward.
6. **Authoritarian child-rearing values.** ✅ Built —
   [bar chart](../../../public/data-explorer/voter-survey-panel/idea-self-reliance.png)
   (`SOCIAL_CONFORMITY_3_2016`, obedience vs. self-reliance).
7. **Gender-role attitudes.** ✅ Built —
   [heatmap](../../../public/data-explorer/voter-survey-panel/idea-sexism.png),
   all six `sexism*_2016` items.
8. **Muslim-surveillance and distrust battery.** ✅ Built —
   [heatmap](../../../public/data-explorer/voter-survey-panel/idea-muslim-distrust.png),
   the three `muslim_distrust_*_2017` proposals.
9. **Immigration attitudes, multi-item index.** ✅ Built —
   [heatmap](../../../public/data-explorer/voter-survey-panel/idea-immigration.png)
   (contribution, naturalization, and four 1-10 economy/crime/culture/
   security sliders, each independently rescaled to a 0-100 share).
10. **Racial resentment battery.** ✅ Built — two bars:
    [slavery's legacy](../../../public/data-explorer/voter-survey-panel/idea-race-slave.png),
    [reverse discrimination](../../../public/data-explorer/voter-survey-panel/idea-reverse-discrimination.png).
11. **Trade/tariff attitudes.** ✅ Built —
    [heatmap](../../../public/data-explorer/voter-survey-panel/idea-trade.png),
    `tradepolicy_2016` + the five `free_trade_*_2016` items (each rescaled
    onto a consistent "good for consumers" share - see
    `voter_ideas_matrices.py`'s own polarity note).
12. **Which Trump promises mattered.** ✅ Built —
    [heatmap](../../../public/data-explorer/voter-survey-panel/idea-promises.png),
    the four `promise_*_2017` items (importance only, not the parallel
    `promise_success_*` battery — kept to one dimension for scope).
13. **Generalized social trust.** ✅ Built —
    [bar chart](../../../public/data-explorer/voter-survey-panel/idea-trust-people.png)
    (`trust_people_2016`).
14. **Media diet by religion.** ✅ Built —
    [heatmap](../../../public/data-explorer/voter-survey-panel/idea-media.png),
    all seven `enews_show_*_baseline` programs (the Sunday-show/local-news
    items from the original idea were dropped for scope; evening network
    news alone already tells the story).
15. **Military household rate.** ✅ Built —
    [bar chart](../../../public/data-explorer/voter-survey-panel/idea-military.png),
    a derived "any" flag across `milstat_1`-`milstat_4_2016`.
16. **Civic organization membership.** ✅ Built —
    [heatmap](../../../public/data-explorer/voter-survey-panel/idea-orgs.png),
    all 20 named `org_membership_*_baseline` organizations.
17. **Volunteering by cause.** ✅ Built —
    [heatmap](../../../public/data-explorer/voter-survey-panel/idea-volunteering.png),
    all 17 `volunteerorg2_*_baseline` cause types.
18. **National pride battery.** ✅ Built —
    [heatmap](../../../public/data-explorer/voter-survey-panel/idea-pride.png),
    all three `proud*_2016` dimensions.
19. **Populist elite-distrust sentiment.** ✅ Built —
    [bar chart](../../../public/data-explorer/voter-survey-panel/idea-rigged-elites.png)
    (`RIGGED_SYSTEM_6_2016`).
20. **Gay marriage attitude shift, baseline → 2016.** ✅ Built —
    [paired bar](../../../public/data-explorer/voter-survey-panel/idea-gaymar-shift.png).

All 23 PNGs are wired into `/data-explorer/voter-survey-panel/graphics` via
`src/lib/data-explorer.ts`. Computed by `scripts/ryan-burge/voter_ideas_bars.py`,
`voter_ideas_matrices.py`, and `voter_ideas_longitudinal.py` (shared group
definitions in `voter_ideas_common.py`); rendered by
`render_voter_ideas_bars.py`, `render_voter_ideas_matrices.py` (reuses
`render_heatmap()` from the already-shipped `render_voter_matrices.py`),
and `render_voter_ideas_longitudinal.py`.
