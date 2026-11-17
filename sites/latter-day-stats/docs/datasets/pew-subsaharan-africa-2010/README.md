# Pew Research Center — Tolerance and Tension: Islam and Christianity in Sub-Saharan Africa (2010)

A face-to-face general-population survey of 25,091 adults across 19
sub-Saharan African countries, fielded December 2008–April 2009 by the
Pew Forum on Religion & Public Life (funded by The Pew Charitable Trusts
and the John Templeton Foundation), interviewing in more than 60
languages/dialects. The 19 countries together hold roughly three-quarters
of sub-Saharan Africa's population. Unlike most datasets in this
pipeline, it carries no U.S./LDS-specific frame variable — Latter-day
Saints are not a named category anywhere in the questionnaire (checked
across all 779 variable labels: no "mormon"/"latter" hits) — so this
dataset's value to the site is as a general Christianity-in-Africa
cross-country comparison, not an LDS-specific one. It covers religious
identity, tolerance between faiths, Pentecostal/Charismatic belief and
practice, prosperity-gospel-adjacent beliefs, traditional/spirit beliefs,
and views on national identity and religious law.

The raw file's name (`2020update7.31.sav`) is misleading — it is a later
re-release of the original 2008-09 fieldwork, not a 2020 survey; the
report itself published April 15, 2010.

## What's in here

Raw microdata lives in `data/pew-subsaharan-africa-2010/` (gitignored,
not committed):

| File | What it is |
| --- | --- |
| `2020update7.31.sav` | SPSS microdata, N=25,091, 779 variables (Q1–Q28+) |
| `Codebook - 2020 update draft 7.31.doc` | Pew's own codebook (legacy binary .doc; variable/value labels embedded in the .sav itself were used instead of parsing this file) |

Weight variable: `WEIGHT`. Country variable: `COUNTRY` (19 labeled
codes: Botswana, Cameroon, Chad, Democratic Republic of the Congo,
Djibouti, Ethiopia, Ghana, Guinea Bissau, Kenya, Liberia, Mali,
Mozambique, Nigeria, Rwanda, Senegal, South Africa, Tanzania, Uganda,
Zambia). Religious identity: `Q32` ("What is your present religion, if
any?" — code `1.0` = Christian, `2.0` = Muslim).

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-subsaharan-africa-2010`), using
the shared chart shape in `scripts/flagship-charts/common.py`:

- `charismatic-christians.json` (share of self-identified Christians who
  also describe themselves as a "Charismatic Christian," Q36D, by
  country) — computed by `charismatic_christians.py`, rendered by
  `render_charismatic_christians_chart.py`. Population is Christians
  within each country (Q36D's own skip pattern), not each country's
  general population. Djibouti (n=24 valid Christian respondents) is
  dropped under the site's 30-respondent floor; of the 18 remaining
  countries, only the top 12 by value are charted (Mozambique, Kenya,
  Chad, Cameroon, Liberia, and Tanzania are omitted for space — noted in
  both the JSON's `countries_omitted_low_rank` and the chart's method
  text) to stay within this pipeline's established row-count precedent.

Further charts from this dataset (e.g. Pentecostal identification,
belief in witchcraft/evil spirits, Muslim-vs-Christian views on shared
questions) should follow the same two-stage pattern.
