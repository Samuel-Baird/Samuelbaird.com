# How evangelical are you?

A survey-scored quiz at [`/how-evangelical`](../../src/app/how-evangelical/page.tsx),
unlisted (not in the nav, not in `sitemap.ts`) and shared by direct link. Answers
score entirely client-side; the app ships with a probability blob baked in and
makes no network calls.

## The pipeline

```
workbook.xlsx  --build_data.py-->  src/lib/evangelical-quiz/data.json  --imported by-->  the app
```

`build_data.py` is the only thing that touches the raw survey percentages.
Everything downstream — the React components, the scoring functions in
`src/lib/evangelical-quiz/scoring.ts` — works off the finished blob and never
sees a percentage cell.

### Regenerating the data

```bash
python scripts/evangelical-quiz/build_data.py \
  --xlsx "path/to/How_Evangelcal_are_you_.xlsx" \
  --out src/lib/evangelical-quiz/data.json
```

Standard library only — nothing to `pip install`. Run with `--report-only` to
see what the workbook contains (item count, which groups are present, which
rows don't sum to ~100) without writing anything:

```bash
python scripts/evangelical-quiz/build_data.py --xlsx workbook.xlsx --report-only
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
feel; there's no data-derived value for it.

**5. Reporting: percentile, not probability.** We don't convert the score to
"87% likely evangelical" — an uncalibrated, meaningless number for this kind
of test. Instead, at build time we draw `SIM_N` synthetic respondents by
sampling each answer independently from the `All U.S. adults` distribution,
score every one with the same weights, sort the results, and store
`PCTL_STEPS + 1` evenly spaced breakpoints. At runtime, a reader's score is
binary-searched into that curve to produce "you answered more like an
evangelical than N% of Americans."

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
| `EVANGELICAL_SHARE` | `0.25` | Assumed evangelical share of U.S. adults, used to back "not Evangelical" out of "All U.S. adults." |
| `PROB_FLOOR` | `0.02` | Floor on every probability before taking a log. |
| `NEG_FLOOR` | `0.005` | Floor for a not-Evangelical cell that goes negative. |
| `SHRINKAGE` | `2.5` | Divides the summed score to correct for correlated items. The one constant meant to be hand-tuned. |
| `SIM_N` | `20000` | Synthetic respondents drawn for the percentile curve. |
| `SIM_SEED` | `20250825` | Fixed seed — reruns on unchanged data produce byte-identical breakpoints. |
| `TIE_MARGIN` | `0.25` | Log-likelihood gap (nats) below which the top two traditions are reported as a tie. |

To retune, edit the constant in `build_data.py` and re-run the build — never
hand-edit `data.json`.

## Files

- `build_data.py` — parses the workbook, validates it, derives weights, runs
  the simulation, emits `src/lib/evangelical-quiz/data.json`.
- `src/lib/evangelical-quiz/types.ts` — the blob's shape and the app's types.
- `src/lib/evangelical-quiz/scoring.ts` — pure scoring functions (`scoreAnswers`,
  `percentileOf`, `matchTradition`, `breakdown`), each mirroring a step above.
- `src/lib/evangelical-quiz/self-test.ts` — the sanity checks called out in
  the build spec: weights finite, percentiles monotonic, and answering the
  modal evangelical response to every question scores in the top decile. Run
  `runEvangelicalQuizSelfTest()` from the browser console on `/how-evangelical`
  in a dev build.
- `src/components/evangelical-quiz/` — the landing, question, and results
  screens, plus the share button and the sourcing disclosure aside.
- `src/app/how-evangelical/page.tsx` — the route.

## Status

As of the last data pull, only the `arian` item (2022 wave — Arianism, the
last year that statement was fielded) has real numbers; the other 35 items in
the workbook are defined (statement text, year, group rows) but blank. The
app runs correctly against however many items have data — it's a fully
working one-question quiz right now, and becomes the full 36-question quiz
the moment the rest of the workbook is filled in and rebuilt. Nothing in
`src/` needs to change for that to happen.

Because so few items currently have data, `runSelfTest`'s "modal-evangelical
answers match Evangelical tradition" and "...score high" checks legitimately
fail against `arian` alone — Black Protestant respondents affirm that
statement even more heavily than evangelicals do (56% vs. 48% strongly
agree), so a 1-item match correctly doesn't favor Evangelical. That's real
survey noise from an n=1 test, not a bug; expect both checks to pass once
enough items are loaded that doctrinally central statements (Trinity,
resurrection, salvation through Christ alone) dominate the sum.

Also outstanding: `SurveyWaveMeta.sampleSize` / `.marginOfError` in
`src/lib/evangelical-quiz/survey-meta.ts` are `null` — the honesty-requirement
footer needs the real sample size and margin of error for the 2025 and 2022
waves from Ligonier/Lifeway's published methodology, which weren't in the
workbook.
