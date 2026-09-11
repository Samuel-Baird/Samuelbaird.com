# Latter-day Saints in Brazil

Three angles on the Church in Brazil, the country that in 2025 became the
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

## Recommended citation

> Compiled from Wikipedia's "The Church of Jesus Christ of Latter-day
> Saints in Brazil," cumorah.com's LDS Growth Case Studies, the Church's
> official facts-and-statistics pages (2025), and this site's own weighted
> tabulation of the 2022 Brazilian Census (IBGE) Pessoas microdata.
