# How evangelical are you?

A survey-scored quiz at [`/how-evangelical`](../../src/app/how-evangelical/page.tsx),
unlisted (not in the nav, not in `sitemap.ts`) and shared by direct link. Answers
score entirely client-side; the app ships with a probability blob baked in and
makes no network calls.

## The pipeline

```
workbook.xlsx  --+
                  +--build_data.py-->  src/lib/evangelical-quiz/data.json  --imported by-->  the app
responses-2025.csv --+
```

`build_data.py` is the only thing that touches the raw survey percentages
(from the workbook) or the raw respondent microdata (from the CSV).
Everything downstream — the React components, the scoring functions in
`src/lib/evangelical-quiz/scoring.ts` — works off the finished blob and never
sees a percentage cell or a respondent row.

### Regenerating the data

```bash
python scripts/evangelical-quiz/build_data.py \
  --xlsx "path/to/How_Evangelcal_are_you_.xlsx" \
  --csv data/state-of-theology/responses-2025.csv \
  --out src/lib/evangelical-quiz/data.json
```

Standard library only — nothing to `pip install`. `--csv` defaults to
`data/state-of-theology/responses-2025.csv` (gitignored, like the rest of
`/data/`); pass `--fetch` to download it there automatically from
`thestateoftheology.com` if it's missing. Run with `--report-only` to see
what the workbook and microdata contain (item count, which groups are
present, which rows don't sum to ~100, per-group percentile landmarks)
without writing anything:

```bash
python scripts/evangelical-quiz/build_data.py --xlsx workbook.xlsx --csv responses-2025.csv --report-only
```

The build refuses to emit a blob if zero items have usable data, and it never
touches the `total_check` column — that's a spreadsheet convenience formula,
not data.

## Adding a question

1. Add five rows to the workbook — one per group (`Evangelical`,
   `Black Protestant`, `Mainline`, `Roman Catholic`, `All U.S. adults`) — with
   a new `item_id`, the `statement` text, the `year`, and the five response
   percentages. Column order is `strongly_disagree, somewhat_disagree,
   not_sure, somewhat_agree, strongly_agree`, matching the State of Theology
   explorer's own layout — paste straight across.
2. If the source only publishes collapsed agree/disagree totals, put those
   totals in `strongly_agree` / `strongly_disagree`, leave both `somewhat_`
   columns at `0`, and leave `not_sure` as given. The build detects this
   automatically (every group's `somewhat_` columns are exactly 0) and
   degrades that item to a 3-option scale rather than inventing a split.
3. Re-run `build_data.py`. That's a data change, not a code change — nothing
   in `src/` needs editing, and every item in the workbook is asked (there is
   no separate "question set" list to update).
4. Check `--report-only` output: the item should move from "unusable" to the
   per-item weights table, with no ERROR or WARNING lines against it.

A row is unusable if any group is entirely blank, if a filled row is missing
a cell, or if a filled row's five percentages sum outside 98–102. The
`--report-only` output says which and why.

## The math

All of this runs once, in `build_data.py`; the client only sums numbers the
build already computed.

**1. Per-answer weight.** For question *i* and response *r*:

```
w[i][r] = ln( P(r | Evangelical) / P(r | not Evangelical) )
```

A reader's score is the sum of `w[i][r]` over every question they answered,
then divided by `SHRINKAGE` (step 4). Positive means "answered like an
evangelical on net"; nothing is hard-coded about which direction any single
question points — it falls out of whichever way the survey numbers land, which
is why an orthodox answer can score as *less* evangelical when rank-and-file
evangelicals affirm the heresy at a higher rate than the general public (see
`arian` — Arianism — in the data; it's already a live example).

**2. Deriving "not Evangelical."** "All U.S. adults" includes evangelicals,
which drags every ratio toward 1. We back them out:

```
P(r | not Evangelical) = ( P(r | all) - w·P(r | Evangelical) ) / (1 - w)
```

where `w` = `EVANGELICAL_SHARE`, the assumed evangelical share of the
population. Any cell that goes negative (possible when `P(r|Evangelical)` is
much larger than `P(r|all)`) is clamped to `NEG_FLOOR` and the item's
distribution is renormalized.

**3. Smoothing.** Every probability — evangelical, not-evangelical, all,
per-tradition — is floored at `PROB_FLOOR` before any log is taken, then
renormalized. This is what keeps `ln(x)` finite when a cell is near zero.

**4. Shrinkage.** The 36 statements are correlated (calling abortion a sin and
calling sex outside marriage a sin come from the same underlying belief), so
summing raw log-likelihood ratios overstates confidence — naive Bayes assumes
independence these items don't have. The summed score is divided by
`SHRINKAGE` to correct for that. This is the one constant meant to be tuned by
feel; there's no data-derived value for it. Note that `SHRINKAGE` is
rank-preserving — dividing every score by the same constant never changes
who scores higher than whom — so it has **no effect on any percentile**. It
only scales the stored `score` value and the per-question breakdown numbers
on the results screen.

**5. Reporting: percentile, not probability — against real respondents.**
We don't convert the score to "87% likely evangelical" — an uncalibrated,
meaningless number for this kind of test. Nor do we compare the score to a
synthetic population (an earlier version of this quiz did: it drew 20,000
simulated respondents by sampling each answer *independently* from the `All
U.S. adults` distribution, which ignores how real answers correlate and
produces a percentile curve about 3× too narrow — a consistent evangelical
would saturate at the 100th percentile even though real evangelical
respondents span a real range).

Instead, at build time we score the **actual 3,001 respondents** of the
State of Theology 2025 survey — the same microdata the workbook's own
percentages were computed from — with the exact weights above, using each
respondent's own survey weight (`WT`). `arian` (2022-only) is excluded from
every respondent's score, since none of them were asked it. Sorting the
weighted scores and walking the cumulative weight gives `PCTL_STEPS + 1`
evenly spaced, deterministic breakpoints (no RNG — the same input always
produces byte-identical output) — see `reference.groups.all.curve` in the
blob. At runtime, a reader's score (also with `arian` excluded — see
`scoring.ts:percentileScore`) is binary-searched into that curve to produce
"you answered more like an evangelical than N% of Americans," and that
sentence is now literally true.

We do the same thing separately for each religious tradition the survey
distinguishes (`reference.groups.evangelical`, `.black_protestant`,
`.mainline`, `.catholic`, `.other_none`, plus the complement
`.non_evangelical` and the belief-based `.evangelical_by_belief` — see
"Reference population" below), so the results screen can also say "more
evangelical than N% of Catholics," etc.

**6. Tradition match.** Separately from the evangelical score, for each
tradition *G* ∈ {Evangelical, Black Protestant, Mainline, Roman Catholic}:

```
score[G] = sum over answered i of ln( P(r_i | G) )
```

Highest wins the headline; the runner-up is always shown. If the top two are
within `TIE_MARGIN` (in nats), the results screen reports a tie instead of a
false-precision winner — subgroup sample sizes in a survey like this are
small enough that a narrow margin isn't a real signal. "All U.S. adults" is
the reference distribution used to build the not-Evangelical baseline; it is
not itself a match candidate.

## Tunable constants

All defined at the top of `scripts/evangelical-quiz/build_data.py` and
mirrored into `data.json.constants` so the shipped app and whatever produced
it can never quietly disagree:

| Constant | Default | Meaning |
|---|---|---|
| `EVANGELICAL_SHARE` | `0.25` | Assumed evangelical share of U.S. adults, used to back "not Evangelical" out of "All U.S. adults." Matches the 2025 microdata's own RELTRAD=1 share (798/3001 = 0.266). |
| `PROB_FLOOR` | `0.02` | Floor on every probability before taking a log. |
| `NEG_FLOOR` | `0.005` | Floor for a not-Evangelical cell that goes negative. |
| `SHRINKAGE` | `2.5` | Divides the summed score to correct for correlated items. Percentile-neutral (see step 4 above) — hand-tune it for the displayed score/breakdown numbers, not to move the percentile. |
| `PCTL_STEPS` | `200` | Breakpoints stored per percentile curve: 0, 0.5, 1.0 ... 100. |
| `CROSSCHECK_TOL` | `1.5` | Percentage points; how far a CSV-recomputed group percentage may drift from the workbook's own cell before the build fails. Workbook cells are whole-number rounded, so ~1pt of drift is expected noise — a real item/column mismatch shows up as tens of points off, not this. |
| `TIE_MARGIN` | `0.25` | Log-likelihood gap (nats) below which the top two traditions are reported as a tie. |

## Reference population

The percentile curves in `data.json.reference` are built from
`data/state-of-theology/responses-2025.csv` (gitignored; fetch with
`--fetch` or download manually from `CSV_URL` in `build_data.py`) — one row
per respondent (n=3,001) to the 2025 State of Theology survey, with a survey
weight (`WT`) and, per respondent, a `RELTRAD` religious-tradition code and
an `EVB` belief-based-evangelical flag.

**`RELTRAD` codes**, verified by `crosscheck_workbook()` at every build
(reproducing the workbook's own published group percentages from the CSV,
cell by cell, within `CROSSCHECK_TOL`): `1` = Evangelical (n=798), `2` =
Black Protestant (n=103), `3` = Mainline (n=222), `4` = Roman Catholic
(n=683), `5` = Other faiths & the unaffiliated (n=1,195). These five values
partition every respondent exactly once, and match this build's own
`Evangelical` / `Black Protestant` / `Mainline` / `Roman Catholic` workbook
groups — i.e. the same "Evangelical" definition drives both the item
weights and the group percentile curve.

**`EVB`** is a separate, belief-based definition: it flags respondents who
strongly agree with all four "NAE Lifeway Research Evangelical Beliefs
Definition" statements (`bible_highest_authority`, `evangelism_important`,
`cross_only_sacrifice`, `christ_alone_salvation`; n=637). It is **not** the
group these four items' own weights are computed against — see "Found
already in the workbook" below — so it's shipped as its own curve
(`evangelical_by_belief`) rather than folded into `RELTRAD`'s Evangelical.

`crosscheck_workbook()` runs on every build (including `--report-only`) and
fails the build if any item/group cell it can check drifts by more than
`CROSSCHECK_TOL`. This is what actually proves the CSV's 35 `Qxx_y` columns
line up with the right item in the right order, and that `RELTRAD` means
what the table above says it means — a wrong mapping would show up as a
wild, tens-of-points mismatch, not the ~1pt rounding noise a correct mapping
produces.

To retune, edit the constant in `build_data.py` and re-run the build — never
hand-edit `data.json`.

## Files

- `build_data.py` — parses the workbook, validates it, derives weights, scores
  the respondent microdata to build the empirical percentile curves, emits
  `src/lib/evangelical-quiz/data.json`.
- `src/lib/evangelical-quiz/types.ts` — the blob's shape and the app's types.
- `src/lib/evangelical-quiz/scoring.ts` — pure scoring functions (`scoreAnswers`,
  `percentileScore`, `percentileOf`, `groupPercentiles`, `matchTradition`,
  `breakdown`), each mirroring a step above.
- `src/lib/evangelical-quiz/self-test.ts` — the sanity checks called out in
  the build spec: weights finite, every reference curve monotonic, and
  answering the modal evangelical response to every question scores in the
  top decile against both the all-Americans and the Evangelical curve. Run
  `runEvangelicalQuizSelfTest()` from the browser console on `/how-evangelical`
  in a dev build.
- `src/components/evangelical-quiz/` — the landing, question, and results
  screens, plus the share button and the sourcing disclosure aside.
- `src/app/how-evangelical/page.tsx` — the route.

## Status

STALE (kept for provenance): as of 2026-08-25 the full workbook has since
been delivered — all 36 items have data for all five groups and the quiz
runs complete. The paragraphs below describe the partial state and how the
2025 Evangelical / All U.S. adults numbers were first sourced.

### The arian question (2022 wave)

`arian` ("Jesus is the first and greatest being created by God") is the one
statement not from the 2025 wave: it was **dropped from the 2025 survey**,
and it's included here deliberately anyway — it's theologically interesting
(the one item where the orthodox answer scores as *less* evangelical), using
the 2022 wave, the last time it was asked. The quiz flags this on the
question and results screens; the graphic's caption cites the 2022 wave
honestly rather than borrowing 2025's sample size.

In the question order it's placed with the deity-of-Christ items (via
`PLACE_BEFORE` in `build_data.py` — question order otherwise follows
workbook row order), immediately before "Jesus was a great teacher, but he
was not God," rather than tacked on at the end where the workbook appends
its rows.

`arian` (2022 wave) has real numbers, verified and unchanged. As of 2026-08-25,
the `Evangelical` and `All U.S. adults` rows for all 35 2025-wave items are
also filled — every item is still missing `Black Protestant`, `Roman
Catholic`, and (for most) `Mainline`, so the app still runs as a 1-question
quiz until those land too. `EVANGELICAL_SHARE` (0.25) is already the source's
own reported evangelical share of U.S. adults (798/3001 in the 2025 raw
microdata), so no change needed there.

### Where the 2025 Evangelical / All U.S. adults numbers came from

Pulled directly from Lifeway Research's own public data behind
thestateoftheology.com — not transcribed from the PDF report, computed from
the underlying respondent-level microdata the site's own data explorer reads:

- `https://thestateoftheology.com/assets/data/us/responses-2025.csv` — one row
  per respondent (n=3,001), raw 1–5 codes per statement (`Q21_1`..`Q30_4`,
  10 screens of 3–4 statements each) plus a survey weight (`WT`).
- Value coding (1=Strongly Agree, 2=Somewhat Agree, 3=Somewhat Disagree,
  4=Strongly Disagree, 5=Not Sure) and the `Qxx_y` → item order were confirmed
  by reproducing the "All U.S. adults" weighted percentages in the published
  research report byte-for-byte (every one of the 35 items matched the
  report's own charts to within rounding).
  Report: `https://research.lifeway.com/wp-content/uploads/2025/09/Ligonier-State-of-Theology-2025-White-Paper.pdf`
- **"Evangelical" here is `RELTRAD=1`** — the survey's denominational/tradition
  classification (see "Reference population" above) — **not** the CSV's
  separate belief-based `EVB` flag. (An earlier draft of this README claimed
  the opposite; see "Correction" immediately below.) `EVB` respondents
  strongly agree with all four "NAE Lifeway Research Evangelical Beliefs
  Definition" statements (white paper, p.24 — exactly
  `bible_highest_authority`, `evangelism_important`, `cross_only_sacrifice`,
  and `christ_alone_salvation` in this workbook) and are shipped separately
  as the `evangelical_by_belief` reference curve.

**Correction (2026-08-25):** an earlier version of this README claimed the
workbook's `Evangelical` column *was* the `EVB` flag, and warned that the
four NAE-definition statements above were therefore tautological — 100%
strongly-agree by construction, producing circular, oversized weights. That
claim was checked numerically against the CSV and is **wrong**: the
workbook's `Evangelical` percentages match `RELTRAD=1` respondents (e.g.
`bible_highest_authority` workbook `[3,6,0,23,68]` vs. a fresh weighted
`RELTRAD=1` crosstab `[3.3,5.7,0.0,23.3,67.8]`), not `EVB=1` (which would be
`[0,0,0,0,100]` by construction). The four items' actual weights are
ordinary — `cross_only_sacrifice`'s max `|w|` (2.56) is in line with
`second_coming` (2.51) and `god_perfect` (2.40) — so no capping or special
handling was needed after all. Left here, corrected, as provenance rather
than deleted, since the original reasoning was sound *if* the premise had
been true — the premise just didn't hold for the data actually shipped.

To reproduce or extend: the same CSV/report pairing exists for 2014, 2016,
2018, 2020, and 2022 at `.../assets/data/us/responses-{year}.csv` and
`.../wp-content/uploads/.../Ligonier-State-of-Theology-{year}-*.pdf` — useful
if a future item needs a different wave's numbers.

### Found already in the workbook, not touched

While filling the above, the workbook already had `Black Protestant` data for
the first 12 items and a leftover `Other`-group row (values blank) after each
of the last 5 items, plus `Black Protestant` / `Mainline` / `Roman Catholic`
rows hidden throughout — none of this was present when this quiz was first
scoped (see prior session), so something filled part of the sheet in the
interim. Left entirely alone; flagged to the user directly rather than
guessed at or cleaned up unasked.

Also outstanding: `SurveyWaveMeta` for the 2022 wave in
`src/lib/evangelical-quiz/survey-meta.ts` still has `sampleSize` /
`marginOfError` as `null` — the 2025 wave's methodology is now filled in.
