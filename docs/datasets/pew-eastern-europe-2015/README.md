# Pew Research Center — Central and Eastern Europe (2015-2016)

Pew's face-to-face survey behind the 2017 report "Religious Belief and
National Belonging in Central and Eastern Europe": more than 25,000 adults
interviewed June 2015-July 2016 in 17 languages, across 18 countries
(Armenia, Belarus, Bosnia, Bulgaria, Croatia, Czech Republic, Estonia,
Georgia, Greece, Hungary, Latvia, Lithuania, Moldova, Poland, Romania,
Russia, Serbia, Ukraine). The region is majority Orthodox Christian overall
(an estimated 57%), with a Catholic-majority cluster (Croatia, Hungary,
Lithuania, Poland) and the Czech Republic standing out as the one
majority-unaffiliated country surveyed. No Latter-day Saint category exists
in this dataset - confirmed by checking every variable/value label in the
.sav for "mormon"/"latter"; none appear, unsurprising for a region with a
negligible LDS presence.

Note: the raw .sav also carries a 19th country, Kazakhstan (COUNTRY code
12, N=1,692) - a majority-Muslim country from a related Pew Central Asia
project, not part of the 18-country CEE report cited here. Every script in
this folder excludes it.

## What's in here

Raw microdata lives in `data/pew-eastern-europe-2015/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `Eastern Europe Public Data_12.5 CHECKED.sav` | SPSS microdata, N=31,545 (18 report countries + Kazakhstan) |
| `CE Europe ordered questionnaire Public Release.docx` | Full survey instrument |

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-eastern-europe-2015`), using the
shared chart shape in `scripts/flagship-charts/common.py`:

- `religious-national-identity.json` (share saying it's "very important" to
  belong to their country's own dominant Christian tradition - Orthodox or
  Catholic, whichever the country's questionnaire inserted - to be truly a
  citizen, Q66c) - computed by `religious_national_identity.py`, rendered
  by `render_religious_national_identity_chart.py`.

Q66c reads: "Some people say that the following things are important for
being truly [survey country citizenship]. Others say that they are not
important. How important do you think each of the following is? ... To be
a [survey country's dominant denomination, e.g. Russian Orthodox, Greek
Orthodox, Polish Catholic]." Because the item swaps in each country's own
dominant church, the resulting percentages are directly comparable across
Orthodox-majority and Catholic-majority countries - this is the flagship
"does national identity fuse with religious identity" finding from Pew's
report, and it turned out to vary enormously by country rather than
tracking the Orthodox/Catholic divide cleanly (Bosnia and Romania, both
above 40%, sit closer to Orthodox-leaning Serbia and Greece than to
Catholic-leaning Croatia and Hungary, which sit in the 20s/high-teens).

18 countries is above this pipeline's ~12-row guideline for one clean
chart, so the shipped PNG shows the 6 highest- and 6 lowest-ranked
countries rather than all 18. The full country table (weighted "very
important" %, unweighted valid N):

| Country | Very important | n |
| --- | --- | --- |
| Armenia | 66.9% | 1,502 |
| Georgia | 64.0% | 1,487 |
| Serbia | 59.4% | 1,560 |
| Greece | 53.2% | 1,451 |
| Romania | 45.0% | 1,348 |
| Bosnia | 43.8% | 1,525 |
| Bulgaria | 38.1% | 1,591 |
| Croatia | 37.3% | 1,606 |
| Moldova | 35.6% | 1,798 |
| Poland | 31.1% | 1,445 |
| Russia | 27.8% | 2,383 |
| Lithuania | 27.4% | 1,546 |
| Ukraine | 22.5% | 2,299 |
| Hungary | 18.2% | 1,478 |
| Belarus | 17.3% | 1,492 |
| Czech Republic | 9.1% | 1,476 |
| Latvia | 6.3% | 1,563 |
| Estonia | 5.6% | 1,629 |

Region-wide (18 countries pooled, weighted): 33.1% say it's "very
important."

Further charts from this dataset should follow the same two-stage pattern:
an analysis script in `scripts/pew-eastern-europe-2015/` reading the raw
.sav with pyreadstat and writing a JSON aggregate to
`docs/datasets/pew-eastern-europe-2015/`, rendered by a matching
`render_*.py` using the shared shapes in `scripts/flagship-charts/common.py`.
