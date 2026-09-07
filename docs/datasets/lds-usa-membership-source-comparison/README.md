# U.S. LDS membership, by source (raw ingestion, not reconciled)

This folder holds a **source-preserving** collection of reported U.S.
membership figures for The Church of Jesus Christ of Latter-day Saints,
pulled from four separate reporting bodies. Each source has its own CSV
file. **The files are deliberately not merged or reconciled** — where
sources disagree, or where the same nominal year yields different numbers
in different files, both values are kept, side by side, with notes
explaining what's going on. Building a single canonical annual series is
a separate, later step (see `../us-membership-growth-2000-2025/` for an
existing example of that kind of merged series) — this folder is the raw
material for that step, not a replacement of it.

This was compiled by four parallel research passes (one per source) in
September 2026, largely via the Wayback Machine, secondary compilations,
and the U.S. Religion Census's own reporting tool. See each file's
"Known gaps and access problems" note below for what could and couldn't
be independently verified from a primary scan/page.

## Files

| File | Source | Earliest year | Latest year | Observations |
| --- | --- | ---: | ---: | ---: |
| [church_newsroom_usa_membership.csv](church_newsroom_usa_membership.csv) | Church Newsroom | 2010 | 2025 | 12 |
| [church_almanac_usa_membership.csv](church_almanac_usa_membership.csv) | Deseret News Church Almanac | 1973 | 2010 | 14 |
| [arda_yearbook_usa_membership.csv](arda_yearbook_usa_membership.csv) | Yearbook of American and Canadian Churches via ARDA | 1925 | 2010 | 65 |
| [us_religion_census_lds_membership.csv](us_religion_census_lds_membership.csv) | U.S. Religion Census | 1952 | 2020 | 7 |

## Column meanings

| Column | Meaning |
| --- | --- |
| `year` | The calendar/statistical year the number is believed to represent — preferred over publication year wherever the source states or strongly implies it. Where this had to be inferred rather than stated outright, the `notes` column says so explicitly. |
| `membership` | Integer count, no thousands separators. |
| `geography` | Almost always `United States`; the Religion Census file spells it `United States (national total)` to flag that it's a genuine national total, not a state-sum. |
| `statistic_type` | The source's own term — `membership` (Newsroom, Almanac), `inclusive membership` (ARDA/Yearbook), or `adherents` (Religion Census). These are **not** interchangeable definitions; see "Membership vs. adherents" below. |
| `reporting_date` | An exact "as of" date, when the source states one (e.g. `2011-01-01`). Blank when the source gives only a year or gives no date at all. |
| `publication_year` | The year of the almanac edition, webpage snapshot, or report the figure was pulled from — distinct from `year` wherever the two differ. Blank where a single per-row edition/year couldn't be pinned down (mainly some Almanac and all ARDA rows; see notes). |
| `source_name` | One of the four source labels in the table above. |
| `source_url` | Direct URL used (a Wayback Machine URL where the live page no longer shows historical data). |
| `source_detail` | Page/table/edition/snapshot-date detail sufficient to relocate the exact figure. |
| `notes` | Ambiguity, derivation, discrepancy, or discontinuity flags. Never used to "correct" a value — only to explain it. |

## Membership vs. denomination-reported membership vs. adherents

These are genuinely different things, and the files use each source's own
term rather than normalizing them:

- **Church Newsroom** and the **Deseret News Church Almanac** both report
  the Church's own official **membership** count — everyone on the
  Church's membership records (essentially, everyone ever baptized or
  born to member parents and not since removed), regardless of activity
  level. This is the largest and most commonly cited number.
- **ARDA / Yearbook of American and Canadian Churches** reports
  **"inclusive membership"** — full communicant/confirmed members plus
  other baptized, non-confirmed, or non-communicant members, as
  self-reported by the denomination to the National Council of Churches
  for its annual Yearbook. In practice this tracks fairly close to the
  Church's own membership figure for LDS specifically, but it's a
  separately-submitted number with its own reporting chain, not a copy of
  the Church's Newsroom/Almanac figure.
- **U.S. Religion Census** reports **"adherents"** — a
  congregation-survey-based estimate methodology, not the Church's own
  membership roll. Critically, the Religion Census's own 2000 figure
  (4,224,026) is *dramatically* lower than the Church's own contemporaneous
  membership claim (~5.2 million) for the same nominal year — this is a
  real definitional gap, not a data error, and it should not be "fixed."
  By 2010 the two methodologies happen to converge on the same number
  (6,144,582), which appears to be coincidental convergence rather than a
  sign the definitions became identical.

## Known reporting discontinuities

- **ARDA/Yearbook** has several sharp single-year spikes or dips relative
  to their neighbors — most notably **1966** (2,480,899, versus 1,789,175
  in 1965 and 1,891,965 in 1967) and smaller dips at **1931**, **1952**,
  and **1999**. These are retained exactly as ARDA presents them and
  flagged in `notes`; they are very likely transcription or reporting
  errors somewhere in the original Yearbook data, but no correction has
  been applied.
- **ARDA/Yearbook 2010** (6,157,238) and the **U.S. Religion Census 2010**
  (6,144,582) differ by about 12,700 despite both nominally describing the
  same year — different source, different methodology, not reconciled.
- The **Church Almanac's 2010/2012-edition figure** (6,144,582) carries a
  flagged printing-error caveat: the secondary compiler who checked the
  print edition directly (rickety.us) states that the 2012 Almanac's page
  324 "incorrectly used totals from the 2011 Almanac" — meaning this
  number may be a reprint of the prior year's total rather than a
  genuinely updated one. Retained as reported.
- The **Church Newsroom** country page stopped printing an explicit
  "as of" date on the page itself somewhere around 2013–2014; from then
  until a 2025-era redesign, only the raw count was shown, with no stated
  reference date. Every `year` value for that stretch in
  `church_newsroom_usa_membership.csv` is an *inferred* year (based on the
  Church's typical ~2-year lag between the counted year and when Newsroom
  posts the update), not a value stated by the page — flagged per-row.

## Which years could not be recovered, and why

- **Church Newsroom**: the `facts-and-statistics/country/united-states`
  URL path does not exist in the Wayback Machine before **February 2012**
  — the page/URL structure itself is that recent, so no amount of further
  Wayback searching under this exact path will surface earlier figures.
  Recovering a pre-2012 U.S.-specific Newsroom number would require
  locating a differently-structured lds.org/Newsroom page, which was out
  of scope for this pass.
- **Deseret News Church Almanac**: every scanned edition checked
  (archive.org's 1999–2000, 2001–2002, 2007, and 2008 items;
  archiveviewer.org's Church History Library viewer; HathiTrust) was
  either lending-restricted, returned no visible page content, or blocked
  full-text search (403s). **No original Almanac page image or OCR text
  was actually read** for this ingestion — every figure in
  `church_almanac_usa_membership.csv` comes from a secondary compilation
  (cumorah.com or rickety.us) that itself cites a specific Almanac
  edition/page. This is a meaningfully weaker chain of custody than the
  other three files, and is called out per-row. Getting real page images
  would require either institutional HathiTrust/library access or a
  different digitized copy than the ones tried here.
- **Deseret News Church Almanac**, years **1974–1972 [sic: pre-1973]** and
  most years between 1973 and 2007 that aren't listed: no secondary
  compilation found gave a citable Almanac figure for these years. The
  Almanac was published annually from 1974 on, so most of that run's
  editions have not yet been recovered into this file.
- **ARDA/Yearbook**: the series is exactly as ARDA published it — years
  absent (e.g. 1926–28, 1930, 1932, 1934, 1936, 1938, 1940, 1942–43, 1945,
  1948–49, 1951, 1954, 1969, 1984, 1986, 1988, 1998, and everything after
  2010) are gaps in ARDA's own compiled chart, not omissions introduced
  here. No interpolation was performed. ARDA's page does show separate
  2020 figures sourced from ASARB (the Religion Census body) rather than
  the Yearbook, so those were excluded from this file as a different
  source under a different methodology (they overlap with, but aren't
  identical to, `us_religion_census_lds_membership.csv`).
- **U.S. Religion Census**: all seven historically-surveyed census years
  (1952, 1971, 1980, 1990, 2000, 2010, 2020) were recovered directly from
  the source's own reporting tool. No known census year is missing, though
  earlier ad hoc church-membership studies before 1952 (if any exist)
  were not investigated. Note the 2010 PDF URL given in the original task
  brief (`2010_US_Religion_Census.pdf`) 404'd during research; the figure
  instead came from USRC's own live "Single-year report" tool, a
  first-party source for the same data.

## Ambiguous statistical years

- **Church Newsroom, 2010–2022ish**: as described above, most `year`
  values in this range are inferred from the Church's typical reporting
  lag, not stated on the page. Treat these as "best guess, not certain."
- **Deseret News Church Almanac**: the Almanac's own reporting lag
  appears to have grown over time — the earliest recovered edition (1974)
  reported data for the immediately preceding year (1973), while by the
  2010s editions the lag had grown to roughly two years (the 2012 edition
  reporting a January 1, 2011 figure). This is based on only two anchor
  points and is a tentative pattern, not an established rule — don't
  assume it holds for every unrecovered edition in between.
- **A 2000-nominal-year Church Almanac figure was explicitly excluded**
  from `church_almanac_usa_membership.csv`: an encyclopedia source quoted
  a very different figure (~4.42 million) for "2000," but its methodology
  and whether it's actually Almanac-derived at all could not be confirmed
  — rather than include a probably-mislabeled row, it was left out
  entirely. If you find a directly Almanac-sourced 2000 figure, add it as
  its own row rather than replacing the cumorah.com-sourced 5,210,000 row
  already present.

## Raw source preservation

Not done in this pass — no HTML/PDF snapshots were downloaded to a
`raw/` folder. Every row's `source_url` points either directly at a live
page/PDF or at a specific Wayback Machine capture, which should remain
independently re-fetchable; if that stops being true for any row, this
folder should gain a `raw/` subfolder for the sources most at risk of
disappearing (in particular, the cumorah.com and rickety.us
Almanac-compilation pages, which are personal sites with no institutional
backing).

## Regenerating

These CSVs are generated by a one-off script rather than hand-edited
directly, so that they can be regenerated if new rows are added or a
provenance detail needs fixing:

```bash
python scripts/lds-usa-membership-source-comparison/build_csvs.py
```

`build_csvs.py` is the single source of truth for every row in this
folder's four CSVs — never hand-edit the CSVs directly; add or correct a
row in the script and re-run it instead.
