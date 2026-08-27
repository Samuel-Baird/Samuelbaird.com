# Pew Research Center — Religion in Latin America

More than 30,000 face-to-face interviews with non-institutionalized adults
across 18 Latin American and Caribbean countries plus Puerto Rico, fielded
Oct. 2013–Feb. 2014 under the Pew-Templeton Global Religious Futures
project. Fielded by Princeton Survey Research Associates International
(Costa Rica, El Salvador, Guatemala, Honduras, Mexico, Nicaragua, Panama)
and Ipsos Public Affairs (the remaining 12 countries/territories). Covers
religious affiliation, belief, practice, and social/political views.
Latter-day Saints are a small share of most national samples here, but the
dataset is large enough to compare the region's Catholic-to-Protestant
shift against how much smaller traditions like LDS appear by comparison.

## Recommended citation

> Pew Research Center. 2014. "Religion in Latin America: Widespread Change
> in a Historically Catholic Region."

- Report: <https://www.pewresearch.org/religion/2014/11/13/religion-in-latin-america/>

## What's in here

Raw microdata lives in `data/pew-latin-america-2014/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `Religion in Latin America Dataset.sav` | SPSS microdata, 19 countries/territories |
| `Religion in Latin America Codebook.docx` | Sample design per country, every variable/value label |

## Status

Five charts shipped, all by respondent's own current religion
(QCURRELrec), pooled across all countries surveyed, wired into the Data
Explorer entry (`src/lib/data-explorer.ts`, slug `pew-latin-america-2014`),
using the shared chart shape in `scripts/flagship-charts/common.py`:

- `mormons-as-christian.json` (share who consider Mormons to be followers
  of the Christian faith, Q63e) — computed by `mormons_as_christian.py`,
  rendered by `render_mormons_as_christian_chart.py`.
- `weekly-attendance.json` (share attending religious services weekly or
  more, Q45) — computed by `weekly_attendance.py`, rendered by
  `render_weekly_attendance_chart.py`.
- `religion-importance.json` (share saying religion is very important in
  their life, Q29) — computed by `religion_importance.py`, rendered by
  `render_religion_importance_chart.py`.
- `samesex-marriage.json` (support for same-sex marriage, Q15) — computed
  by `samesex_marriage.py`, rendered by `render_samesex_marriage_chart.py`.
- `witchcraft-belief.json` (share believing magic/sorcery/witchcraft can
  influence people's lives, Q60h, a syncretism indicator) — computed by
  `witchcraft_belief.py`, rendered by `render_witchcraft_belief_chart.py`.

Note: this dataset's only current-religion variable (QCURRELrec) folds
Mormons into "Other religion" - there's no way to isolate an LDS-specific
population share or attitude breakout here, which is why every chart in
this dataset (including the original mormons-as-christian.json) asks
"what do people of each religion think," not "what do Latin American
Mormons think."

Further charts from this dataset should follow the same two-stage
pattern.
