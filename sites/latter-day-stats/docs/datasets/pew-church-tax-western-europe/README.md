# Pew Research Center — Being Christian in Western Europe (church-tax add-on)

Pew's "Being Christian in Western Europe" survey: 26,096 adults interviewed
by telephone (cellphone and landline) April–August 2017 across 15 Western
European countries plus Slovakia (16 total), under the direction of GfK
Belgium. The base survey covers religious affiliation, belief, and
practice; this dataset is the version augmented with three additional
church-tax items (`Q13`, `Q14a`, `Q14b`) that Pew added later for its 2019
report "In Western European Countries With Church Taxes, Support for the
Tradition Remains Strong." Church tax — a tax collected by the state and
remitted to registered churches, tied to baptismal/membership registration
— exists in only 9 of the 16 countries surveyed: mandatory in Austria,
Denmark, Finland, Germany, Sweden, and Switzerland; voluntary opt-in
programs in Italy, Portugal, and Spain. `Q13` was asked only in those 9
(confirmed against the codebook's own ASK instruction, not inferred from
missingness alone).

## What's in here

Raw microdata lives in `data/pew-church-tax-western-europe/` (gitignored,
not committed):

| File | What it is |
| --- | --- |
| `Western Europe Public Data_Church Tax Added.sav` | SPSS microdata, N=26,096 |
| `CODEBOOK_Church Tax.docx` | Pew's own codebook, incl. `country`/`weight`/`Q13`/`Q14a`/`Q14b` definitions and ASK instructions |

Note: the .sav's `country` variable includes Slovakia (added for a
separate report) and all 16 countries in the base survey, but only 9 of
them ever had `Q13` (the church-tax question) asked — restrict to
`COUNTRY_CODES` in `pays_church_tax.py` rather than iterating over every
country in the file.

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-church-tax-western-europe`), using
the shared chart shape in `scripts/flagship-charts/common.py`:

- `pays-church-tax.json` (share currently paying the church tax, `Q13`, by
  country) — computed by `pays_church_tax.py`, rendered by
  `render_pays_church_tax_chart.py`. Population is restricted to the 9
  countries where the church tax exists and `Q13` was asked; rows ordered
  by `sort_groups` so the "9-country average" row sinks to the bottom
  regardless of value.

Regenerate with:

```
python scripts/pew-church-tax-western-europe/pays_church_tax.py
python scripts/pew-church-tax-western-europe/render_pays_church_tax_chart.py \
  --out public/data-explorer/pew-church-tax-western-europe/pays-church-tax.png
```

Further charts from this dataset (e.g. `Q14a`'s "how likely to stop
paying" among current payers, or `Q14b`'s "have you ever paid" among
current non-payers) should follow the same two-stage pattern.
