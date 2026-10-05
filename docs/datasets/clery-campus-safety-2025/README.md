# Clery Act campus crime data, 2022-2024 (2025 release)

On-campus reported rapes at U.S. four-year colleges, from the Department of
Education's Campus Safety and Security data
(https://ope.ed.gov/campussafety/#/datafile/list, `Oncampuscrime222324.xls`).
The raw .xls is not stored here; point `--src` at the unzipped
`Crime2025EXCEL` folder.

- `scripts/clery-campus-safety-2025/analyze.py` writes every JSON in this folder.
- `scripts/clery-campus-safety-2025/render.py` draws the nine PNGs (five national, four Utah-only).

Method notes:

- Institution = `UNITID_P` without its 3-digit campus suffix. Rapes are summed
  across campuses. Enrollment (`Total`) repeats on every campus row, so it is
  taken once, not summed.
- On-campus already includes residence halls. The residence-hall file is not added.
- A year counts if any of an institution's campus rows has data for it (`FILTER` = 1); branches opened later have
  blank years and must not drop the institution.
- Utah charts use every four-year institution with State = UT and 1,000+ students; the Utah median is over those.
- State maps (`render_state_map.py`): pooled rate per state = all reported on-campus rapes at the state's four-year
  institutions / their total enrollment x 10,000. Outlines come from `export-us-state-paths.mjs` (the site's Albers USA state map).
  Small states are dominated by one campus (e.g. Bennington College is 60% of Vermont's 2024 reports); `state-rates.json` records
  each state's largest contributor.
- Four-year = sector "4-year or above" (public, private nonprofit, for-profit).
- The file has one enrollment figure per institution; it is used for all three years.
- Rate per 10,000 = rapes / enrollment x 10,000. Percentile = share of
  institutions with a lower rate (ties count half).
- Rate charts use 1,000+ students (rate ranking, scatter) or 5,000+ (histogram,
  three-year chart). The scatter line is the pooled national rate times enrollment.
- These are reports, not incidence. The University of Utah's count jumps from 24 (2022) to
  172 (2023) and 140 (2024); the file does not say why.
