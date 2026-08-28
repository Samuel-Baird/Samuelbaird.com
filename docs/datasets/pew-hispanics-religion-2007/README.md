# Pew Hispanic Center / Pew Forum on Religion & Public Life — Survey of Latinos (2006)

A telephone survey of 4,016 U.S. Hispanic adults, conducted August 10–October
4, 2006, in English and Spanish, by the Pew Hispanic Center and the Pew Forum
on Religion & Public Life. The sample deliberately oversampled 2,000
non-Catholic respondents (drawing on a re-contact sample from prior ICR
studies) so the survey could examine religious switching — especially
Catholic-to-evangelical/Pentecostal conversion — among Latinos in detail; the
dataset's `newweight` variable corrects for that oversample. It underlies the
report ["Changing Faiths: Latinos and the Transformation of American
Religion"](https://www.pewresearch.org/race-and-ethnicity/2007/04/25/changing-faiths-latinos-and-the-transformation-of-american-religion/)
(April 25, 2007). The survey's own recoded religion variable (`relig`)
carries an explicit Mormon category (34 unweighted respondents), just over
this pipeline's 30-valid-respondent floor — thin, but usable.

## What's in here

Raw microdata lives in `data/pew-hispanics-religion-2007/` (gitignored, not
committed):

| File | What it is |
| --- | --- |
| `Pew Hispanic Center - Pew Forum Religion Survey Data 5-1-2008.sav` | SPSS microdata, N=4,016 |
| `Codebook.doc` | Full variable/value-label codebook |
| `hispanics-religion-07-topline-final-feb08.pdf` | Weighted toplines for every question |
| `Readme.txt` | Pew's own readme — documents a post-publication data correction (affects `denom` and several `qn*` items) and a `reltrad` variable that does NOT match the one used in the "Changing Faiths" report (a recoding syntax to reproduce the report's own `reltrad` is included, if ever needed) |
| `Survey Methodology.pdf` | Sample design, weighting |

Two weight variables exist: `newweight` (the main survey weight, used here)
and `F1406_weight` (a separate recontact-survey weight for a Catholic-only
follow-up wave — not used by anything in this folder).

## Status

One chart shipped, wired into the Data Explorer entry
(`src/lib/data-explorer.ts`, slug `pew-hispanics-religion-2007`):

- `latino-religious-converts.json` (share who converted to their current
  religion rather than being raised in it, `qn30`, by religious group —
  Catholic, Protestant, Jehovah's Witness, Mormon, Jewish; Muslim and
  Orthodox dropped for falling under the 30-valid-respondent floor) —
  computed by `latino_religious_converts.py`, rendered by
  `render_latino_religious_converts_chart.py`. Mormon highlighted in
  `--accent` blue. This doubles as the survey's real headline finding
  (Catholics essentially never convert INTO Catholicism among Latinos —
  2.2% — while Protestants and Jehovah's Witnesses are roughly half
  converts) and as the LDS-specific breakout: 42.5% of Latino Mormons are
  converts, comparable to Protestants' 48.6%.

Regenerate with:

```
python scripts/pew-hispanics-religion-2007/latino_religious_converts.py
python scripts/pew-hispanics-religion-2007/render_latino_religious_converts_chart.py \
  --out public/data-explorer/pew-hispanics-religion-2007/latino-religious-converts.png
```

Further charts from this dataset should follow the same two-stage pattern
(see `scripts/pew-atp-w70-2020/blm_sermons.py` for the canonical worked
example).
