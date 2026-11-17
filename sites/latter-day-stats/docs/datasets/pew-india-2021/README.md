# Pew Research Center — India Religion Survey (2019-2020)

Pew Research Center's massive face-to-face survey of religion in India:
29,999 adults (age 18+) interviewed across 26 states and three union
territories in 17 languages, fielded November 17, 2019-March 23, 2020
(interviews conducted under the direction of RTI International; computer-
assisted personal interviewing after random household selection). Six
groups were deliberately oversampled - Muslims, Christians, Sikhs,
Buddhists, Jains, and residents of the Northeast region - to guarantee
usable subgroup sample sizes: 22,975 Hindus, 3,336 Muslims, 1,782 Sikhs,
1,011 Christians, 719 Buddhists, 109 Jains, and 67 respondents who are
religiously unaffiliated or belong to another religion. Fielded as part of
the Pew-Templeton Global Religious Futures project.

Latter-day Saints are not a named category anywhere in this dataset (checked
every value-label table in the .sav for "mormon"/"latter" - none found), so
this dataset's usable religion angle for the site is Christianity broadly,
via India's ~2-2.5% Christian minority (N=1,011, plenty for subgroup
analysis on its own or as the subject of other groups' attitudes toward it).

Two Pew reports draw on this data:
- [Religion in India: Tolerance and Segregation](https://www.pewresearch.org/religion/2021/06/29/religion-in-india-tolerance-and-segregation/) (June 29, 2021) - the
  primary report, covering religious identity, practice, tolerance, and
  segregation.
- [How Indians View Gender Roles in Families and Society](https://www.pewresearch.org/religion/2022/03/02/how-indians-view-gender-roles-in-families-and-society/) (March 2, 2022) -
  a secondary report using the same fieldwork.

## What's in here

Raw microdata lives in `data/pew-india-2021/` (gitignored, not committed):

| File | What it is |
| --- | --- |
| `India Religion Public Data - Pew Research Center (All Vars).sav` | SPSS microdata, N=29,999 |
| `India Religion Public Data - Pew Research Center (All Vars).csv` | Same data, unlabeled CSV |
| `CODEBOOK_India.pdf` | Full questionnaire + methodology notes |
| `India recode syntax for public release.txt` | Pew's own SPSS recode syntax for the common break variables |
| `Pew India DDI metadata.xml` | DDI metadata for the public release |
| `READ ME.txt` | Pew's own dataset readme |

Respondent's own religion is `QRELSING` (Hindu/Muslim/Christian/Sikh/
Buddhist/Jain/other/none); the analysis weight is `weight`.

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-india-2021`), using the shared chart
shape in `scripts/flagship-charts/common.py`:

- `christian-neighbor-acceptance.json` (share willing to accept a Christian
  as a neighbor, `Q63c`, by the respondent's own religion) - computed by
  `christian_neighbor_acceptance.py`, rendered by
  `render_christian_neighbor_acceptance_chart.py`. `Q63c` is only asked of
  respondents who are *not* themselves Christian - the questionnaire's
  neighbor-acceptance battery (`Q63a`-`Q63g`) skips a respondent's own
  religion, confirmed against the raw missingness pattern (`Q63c` is null
  for exactly the 1,011 Christian respondents). So this chart's population
  is Hindus, Muslims, Sikhs, Buddhists, and Jains specifically being asked
  about Christians, not Christians' own self-report - a direct read on how
  tolerated India's Christian minority is among its other major religious
  communities, not a general "who's most accepting" item.

Further charts from this dataset should follow the same two-stage pattern
(an analysis script reading the raw .sav and writing a JSON aggregate to
`docs/datasets/pew-india-2021/`, then a render script producing the PNG).
