# Pew Research Center — Spirit and Power: A 10-Country Survey of Pentecostals (2006)

Pew Forum on Religion & Public Life's cross-national study of "renewalist"
Christianity — Pentecostals and Charismatics — surveyed 10,000+ respondents
across ten countries (Brazil, Chile, Guatemala, India, Kenya, Nigeria, the
Philippines, South Africa, South Korea, and the United States) between May
and September 2006. Each country fielded a general-public sample plus an
oversample of renewalists (Pentecostals/Charismatics) to support
within-group analysis; the derived `renewalist`/`sample` variables let you
restrict to the general public only when computing a population-level
share. Report published October 5, 2006.

## What's in here

Raw microdata lives in `data/pew-10-country-religion-2007/` (gitignored,
not committed):

| File | What it is |
| --- | --- |
| `pew forum 10-country religion survey data.sav` | SPSS microdata, N=11,028 (7,475 general public + 3,553 renewalist oversample, pooled across 10 countries) |
| `Background and Codebook.doc` | Variable/value-label documentation |
| `Questionnaire.doc` | Full survey instrument |
| `Topline Survey Results.pdf` | Weighted toplines, per-country field dates and sample sizes |

Note: several per-country questions are stored as country-suffixed
variables (e.g. `q3US`, `q3bra`, `q3chi`, ...) rather than one pooled
column — check the codebook before reusing a question across countries.
`country` (1–10) and `sample` (1=General Public, 2=Renewalist oversample)
are the two variables every chart needs to scope its population correctly;
`GPWGT` is the general-public weight, `PENTWGT` the renewalist-oversample
weight.

Checked value labels for "mormon"/"latter" per the registration brief:
`q3<country>` (self-reported religious affiliation) does carry a "Mormon"
code in five of the ten countries (US, Chile, Guatemala, Philippines,
South Korea), but counts are only 1–21 respondents per country — far under
this pipeline's usual 30-respondent floor — so there's no usable
Latter-day Saint breakout in this dataset, as expected for a
Pentecostal-focused survey.

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-10-country-religion-2007`), using
the shared chart shape in `scripts/flagship-charts/common.py`:

- `renewalist-share.json` (share of the general public who are
  Pentecostal or Charismatic Christians, by country, on the survey's own
  `renewalist` derived variable) — computed by `renewalist_share.py`,
  rendered by `render_renewalist_share_chart.py`. Population is each
  country's general-public sample only (`sample==1`), excluding the
  renewalist oversample; weighted by `GPWGT`.

Further charts from this dataset (e.g. speaking in tongues, divine
healing, or prosperity-gospel belief items — Q6b, Q14a, Q17f/Q17g) should
follow the same two-stage pattern.
