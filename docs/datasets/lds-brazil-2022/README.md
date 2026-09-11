# Latter-day Saints in Brazil

Five angles on the Church in Brazil, the country that in 2025 became the
nation with the most Latter-day Saints outside the United States.

## What's in here

- **`membership-by-year.json`** — a compiled historical membership timeline,
  1940-2025, built by `scripts/lds-brazil-2022/build_membership_by_year.py`.
  Not one survey's microdata: each point is a separately cited
  Church-reported (or Church-published rounded) figure, spaced irregularly
  rather than on a fixed annual grid. No point is interpolated — years with
  no findable real figure are simply omitted. See the "Sources, by year"
  table below.
- **`latin-america-comparison-2025.json`** — total Church membership,
  congregations, missions, and operating temples for the five largest
  Latter-day Saint populations in Latin America (Brazil, Mexico, Peru,
  Chile, Argentina), all as of Dec. 31, 2025, each pulled from that
  country's own Church facts-and-statistics page. Built by
  `scripts/lds-brazil-2022/build_latin_america_comparison.py`.
- **`smaller-faiths-by-state-2022.json`** — 2022 Brazilian Census (IBGE)
  data on the "Outras religiosidades" ("Other religions") share of each
  state's population age 10+, ranked. Built by
  `scripts/lds-brazil-2022/build_smaller_faiths_by_state.py` from a
  pre-computed weighted tabulation of the raw Census microdata.
- **`temples-dedicated-by-year.json`** — cumulative count of dedicated
  Brazil temples by dedication year, 1978-2026 (all 12 currently-dedicated
  temples), built by
  `scripts/lds-brazil-2022/build_temples_dedicated_by_year.py`. Every point
  is a real, exact dedication date, cross-verified against the Church's
  official chronology page and temple list. Counts only DEDICATED
  temples — those under construction or merely announced are noted
  separately, not plotted as completed milestones.
- **`missions-by-decade.json`** — real decade-by-decade Brazil mission
  counts, 1950-2025 (8 data points), built by
  `scripts/lds-brazil-2022/build_missions_by_decade.py`. Quoted directly
  from cumorah.com's "Reaching the Nations" Brazil country report plus the
  Church's current facts-and-statistics figure — same sparse,
  no-interpolation pattern as `membership-by-year.json`.

## Sources, by year (membership-by-year.json)

| Year(s) | Status | Source |
| --- | --- | --- |
| 1940, 1950, 1960, 1970, 1979, 1999, 2009, 2019 | reported | Wikipedia, "The Church of Jesus Christ of Latter-day Saints in Brazil," compiled historical timeline |
| 1989 | rounded | Same, published as a rounded number |
| 2000, 2010 | reported | cumorah.com LDS Growth Case Studies (Matt Martinich), "Expanding LDS Outreach in Brazil" |
| 2025 | reported | Church official facts-and-statistics page, as of Dec. 31, 2025 |

**Gaps not filled:** despite additional research (WebSearch/WebFetch against
the Church newsroom Brazil country page, Wikipedia's broader "Membership
statistics" article, and ldschurchgrowth.blogspot.com's annual
"Country-by-Country Membership Statistics" posts for 2019, 2021, 2022, and
2024), no further exact annual membership totals for Brazil were found for
1940-1970, 1980-1988, 1990-1998, 2001-2008, 2011-2018, or 2020-2024. The
Wayback Machine (web.archive.org) was not reachable from this research
environment, which would otherwise have been the next avenue for archived
Church newsroom country-page snapshots. The blogspot posts report Brazil's
*net numerical increase* for several individual years (e.g. +24,502 in
2019, +26,303 over 2020-2021, +16,283 in 2022, +30,865 in 2024) but not a
running total, so those weren't usable as standalone data points without
a verified prior-year baseline. No point is invented to fill these gaps —
the chart's line is intentionally irregular, wider between some points
than others, exactly reflecting what is and isn't documented.

## Latin America comparison — sources

All countries' facts-and-statistics pages, as of Dec. 31, 2025:

- <https://www.churchofjesuschrist.org/learn/facts-statistics/brazil?lang=eng>
- <https://www.churchofjesuschrist.org/learn/facts-statistics/mexico?lang=eng>
- <https://www.churchofjesuschrist.org/learn/facts-statistics/peru?lang=eng>
- <https://www.churchofjesuschrist.org/learn/facts-statistics/chile?lang=eng>
- <https://www.churchofjesuschrist.org/learn/facts-statistics/argentina?lang=eng>
- Secondary note on the overtake: <http://ldschurchgrowth.blogspot.com/2026/04/country-by-country-membership.html>

Headline: Brazil surpassed Mexico in total membership in 2025 (by 1,073
members) to become the country with the most Latter-day Saints of any
nation outside the United States.

## Smaller-faiths-by-state chart — critical framing note

**This chart is NOT an LDS-specific figure and must never be presented as
one.** IBGE's public 2022 Census microdata sorts religious affiliation into
only 9 broad groups. "Outras religiosidades" ("Other religions," religion
code 6) is a mixed catch-all bucket that includes Latter-day Saints
alongside Jehovah's Witnesses, Spiritualists, Jews, Muslims, Buddhists,
esoteric traditions, and more. IBGE has not published a more granular
breakout that would isolate any single smaller faith (including LDS) from
this bucket — checked against the public microdata, the SIDRA agregados
API, and the official "Censo Demográfico 2022 Religiões: Resultados
preliminares da amostra" report, all of which stop at these 9 groups.

Methodology: weighted tabulation of the 2022 Census Pessoas (persons)
microdata, weighted by the P0110 sample weight, restricted to population
age 10+ (religion was not asked of respondents under 10). Cross-checked
against the official report's own published figures: national "Outras
religiosidades" share of 2.7% (2010) → 4.0% (2022), and Roraima as the
highest single state at approximately 7.8% — this tabulation computed
7.78% for Roraima, a close match. (An earlier compilation note in this
project's research materials incorrectly conflated this 2.7%→4.0% pair
with the report's *separate* "Sem religião"/no-religion pair of
7.9%→9.3%; the corrected 2.7%→4.0% figures are what's used throughout this
dataset.)

## Temples dedicated by year — sources and verification

All 12 currently-dedicated Brazil temples with exact dedication dates,
cross-verified against both the Church's official chronology page
(<https://www.churchofjesuschrist.org/study/history/global-histories/brazil/br-chronology?lang=eng>)
and its temple list (<https://www.churchofjesuschrist.org/temples/list?lang=eng>).
The most recent (#12, Belo Horizonte) was confirmed via a direct search:
Church Newsroom, "President Oaks Dedicates the Belo Horizonte Brazil
Temple" (<https://newsroom.churchofjesuschrist.org/article/president-oaks-dedicates-belo-horizonte-brazil-temple>),
which explicitly states it as "the Church's 12th dedicated temple in
Brazil."

**The pace accelerates:** 22 years passed between temple #1 (Sao Paulo,
1978) and temples #2/#3 (Recife and Porto Alegre, both Dec. 2000); after
that, a temple roughly every 2-4 years; then 5 of the 12 — Rio de
Janeiro, Belem, Brasilia, Salvador, and Belo Horizonte — dedicated in
just the last 4 years (2022-2026). That count was independently
recomputed directly from the temple table during this session (not
carried over from an earlier draft) and confirmed as 5, not 6.

As of this writing, Brazil also has temples under construction (Natal,
Teresina, Santos, Joao Pessoa, Ribeirao Preto, Londrina) and announced
(Maceio, Campo Grande, Florianopolis, Sao Paulo East, Goiania, Vitoria) —
noted in the chart's subtitle as a passing count, but not plotted, since
the chart tracks only completed (dedicated) milestones.

## Missions by decade — sources and verification

Real decade-by-decade mission counts, quoted verbatim from cumorah.com's
"Reaching the Nations" Brazil country report (Matt Martinich) —
<https://cumorah.com/countries/viewReports/191/Brazil> — the same source
family already cited for the 2000/2010 membership figures above: "The
number of missions increased from one in 1950 to two in 1960, three in
1970, six in 1980, 12 in 1990, 26 in 2000, and 27 in 2010." The current
figure, 37 missions as of Dec. 31, 2025, comes from the Church's official
facts-and-statistics page (already cited above for the Latin America
comparison and 2025 membership total).

**A different shape than membership:** mission counts roughly doubled
each decade from 1950 to 1990 (1 → 2 → 3 → 6 → 12), then grew far more
slowly over the next 25 years (12 → 26 → 27 → 37) even as Brazil's
membership kept climbing steadily over that same period (see
`membership-by-year.json` above). Each mission likely covers a larger
member base today than in the growth-spurt decades — a genuinely
different curve shape than membership's, though no single cause is
asserted for it here.

## Recommended citation

> Compiled from Wikipedia's "The Church of Jesus Christ of Latter-day
> Saints in Brazil," cumorah.com's LDS Growth Case Studies and "Reaching
> the Nations" country report, the Church's official facts-and-statistics
> and temple/chronology pages (2025-2026), and this site's own weighted
> tabulation of the 2022 Brazilian Census (IBGE) Pessoas microdata.
