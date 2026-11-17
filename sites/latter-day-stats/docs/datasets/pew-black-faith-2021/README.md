# Pew Research Center — Faith Among Black Americans (2021)

A dedicated Pew survey of Black American religious life: 8,660 Black adults
surveyed via a combination of four probability-based samples (the Center's
American Trends Panel, its own ABS survey, NORC's AmeriSpeak panel, and
Ipsos's KnowledgePanel), online, by mail, and by live telephone. Responses
were collected Nov. 19, 2019-June 3, 2020 (most between Jan. 21 and Feb. 10,
2020). An additional 4,574 non-Black respondents were interviewed to
support general-population comparisons. Full report: ["Faith Among Black
Americans"](https://www.pewresearch.org/religion/2021/02/16/faith-among-black-americans/),
published Feb. 16, 2021.

Unlike Pew's American Trends Panel waves elsewhere in this repo, this
dataset carries no `F_RELTRAD` frame variable - religious affiliation is
captured by a simpler self-reported `RELIGMOD` ("What is your present
religion, if any?") with its own flat set of codes (Protestant, Roman
Catholic, Mormon/Church of Jesus Christ of Latter-day Saints, Jehovah's
Witness, Jewish, Muslim, Buddhist, Hindu, Atheist, Agnostic, Something
else, Nothing in particular).

## What's in here

Raw microdata lives in `data/pew-black-faith-2021/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `black faith all respondents.sav` | SPSS microdata, N=13,234 (8,660 Black + 4,574 non-Black) |
| `black faith black respondents.sav` | SPSS microdata, N=8,660 Black respondents only; used for all of the report's Black-American estimates |
| `Codebook v2.2.docx` | Pew's own codebook, incl. variable and value labels |

Note: use `black faith black respondents.sav` (and its own `WEIGHT`
variable) for any analysis restricted to Black Americans - it is the file
the published report itself used, not the "all respondents" file filtered
down. `MAINWEIGHT` and `ALTWEIGHT` in the "all respondents" file are for
different report-specific comparisons; see the codebook.

## Latter-day Saint breakout

`RELIGMOD` code 3.0 ("Mormon/Church of Jesus Christ of Latter-day Saints")
has an unweighted N of 34 among Black respondents in `black faith black
respondents.sav` - just over this repo's 30-valid-respondent floor, and
with zero missingness on the flagship chart's own analysis variable
(WOMLEAD), so the reported row clears MIN_VALID_N on the actual item, not
just the raw group count. Any further chart from this dataset that wants a
Black-LDS row should re-check valid N on its own analysis variable the same
way - a modest N=34 group can still drop below 30 once an item's own
"not answered" respondents are excluded.

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-black-faith-2021`), using the shared
chart shape in `scripts/flagship-charts/common.py`:

- `women-leaders.json` (share of Black Americans saying women should be
  allowed to serve as a congregation's senior religious leader, WOMLEAD, by
  religious affiliation) - computed by `women_leaders.py`, rendered by
  `render_women_leaders_chart.py`. Black Latter-day Saints (71.9%) read as
  distinctly lower than Black Protestants (88.0%), Catholics (90.2%), and
  the religiously unaffiliated (92.6%) - consistent with LDS polity
  reserving formal congregational leadership for ordained men. Jehovah's
  Witnesses (20.3%), a tradition with an even more restrictive stance, are
  included as comparative context.

Several other items were checked before picking WOMLEAD as the flagship
(see `women_leaders.py`'s own docstring): PERSBLV_e (religious duty to
convert nonbelievers) and ESSENT_b (importance of attending services)
also showed a reportable Mormon row but tracked closely with Protestants
and Jehovah's Witnesses rather than standing out on their own; WOMLEAD was
the one where the Mormon row was genuinely distinctive from the other
named-affiliation groups.

Further charts from this dataset should follow the same two-stage pattern.
