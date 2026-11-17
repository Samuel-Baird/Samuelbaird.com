# Pew Research Center — Global Restrictions on Religion (2007-2022)

A country/year-level cumulative dataset, not survey microdata: 198
countries and territories, rated annually 2007-2022 on two 0-10 indexes —
the Government Restrictions Index (GRI, 20 measures of how governments
restrict religious belief and practice, e.g. banning faiths, prohibiting
conversion, favoring one religion) and the Social Hostilities Index (SHI,
13 measures of religion-related hostility by private individuals and
groups, e.g. mob violence, harassment over religious attire, religion-
related armed conflict). It is the basis of Pew's Dec. 2024 report
["Government Restrictions on Religion Stayed at Peak Levels Globally in
2022"](https://www.pewresearch.org/religion/2024/12/18/government-restrictions-on-religion-stayed-at-peak-levels-globally-in-2022/).

## No LDS-specific breakout

Unlike this site's other Pew datasets, this one carries no per-respondent
religion variable — it rates countries and governments, not individuals.
The dataset does include a "which religious groups were harassed"
variable (`GRI_Q_11_*`), but it's broken out only by broad tradition
(Christianity, Islam, Buddhism, Hinduism, Judaism, folk religions, other,
unaffiliated) — not by denomination, so there is no Latter-day-Saint-
specific figure anywhere in this public release. The one defensible
flagship chart here is therefore a worldwide trend affecting Christians
(and everyone else) globally, not a by-group comparison.

## What's in here

Raw data lives in `data/pew-global-restrictions-religion/` (gitignored,
not committed):

| File | What it is |
| --- | --- |
| `PublicDataset_ReligiousRestrictions_2007to2022.csv` / `.dta` | Country-year ratings, 2007-2022, N=3,164 rows |
| `README.txt` | Pew's own dataset readme |
| `Religious Restrictions Codebook.pdf` | Full methodology + variable definitions |
| `Religious Restrictions Dataset Note.txt` | Notes on rounding/revision discrepancies vs. earlier published reports |

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-global-restrictions-religion`),
using the shared chart shape in `scripts/flagship-charts/common.py`:

- `gri-trend.json` (global median GRI score by year, 2007-2022) —
  computed by `build_gri_trend.py`, rendered by
  `render_gri_trend_chart.py`. The median (not mean) across all
  197-198 rated countries/territories each year, matching how Pew's own
  published reports summarize the global trend given the right-skewed
  country-level distribution. Every year is a real Pew-coded rating —
  none are interpolated.

Regenerate with:

```
python scripts/pew-global-restrictions-religion/build_gri_trend.py
python scripts/pew-global-restrictions-religion/render_gri_trend_chart.py \
  --out public/data-explorer/pew-global-restrictions-religion/gri-trend.png
```

Further charts from this dataset (e.g. an SHI trend, or a regional
breakout) should follow the same two-stage pattern.
