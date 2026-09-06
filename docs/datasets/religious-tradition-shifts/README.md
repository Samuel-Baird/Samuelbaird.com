# Religious Tradition Shifts, 2007-2023-24

A "mixed data" Data Explorer entry: it stitches together two different Pew
Religious Landscape Study waves — the 2007 continental-U.S. telephone survey
and the 2023-24 public-use file — to compare every one of Pew's 15 RELTRAD
religious traditions against itself across 16 years, not just the handful of
Christian denominations this site's other RLS graphics (and the Deseret News
op-ed set in `deseret-news-op-ed/`) focus on.

## Why this is possible from the public files

`RELTRAD` (Pew's religious-tradition classification) is public, fully
populated, and coded identically across all three RLS waves — confirmed
directly against each wave's own value-label table. Unlike `DENOM`/`FAMILY`
(restricted-use in the 2023-24 file), RELTRAD includes every tradition,
Christian and non-Christian: Evangelical, Mainline, and Historically Black
Protestant, Catholic, Latter-day Saint, Orthodox Christian, Jehovah's
Witness, Other Christian, Jewish, Muslim, Buddhist, Hindu, Other World
Religions, Other Faiths, and Religiously unaffiliated.

## Regenerate

```bash
python scripts/religious-tradition-shifts/compute_shifts.py
python scripts/religious-tradition-shifts/render_chart.py \
  --out public/data-explorer/religious-tradition-shifts/shifts-2007-2023.png
```

## Method

Share of ALL U.S. adults (don't-know/refused kept in the denominator, same
convention as every other share on this site), weighted by each wave's own
weight variable. 2007 is the continental-U.S. main survey only (N=35,556);
2023-24 is the public-use file (N=36,908).

**Read the small groups with caution.** Jehovah's Witness, Buddhist, Hindu,
Orthodox Christian, and the three "Other" catch-alls have a few hundred
unweighted respondents or fewer in one or both waves — the chart marks these
with an asterisk. Evangelical, Mainline, Historically Black Protestant,
Catholic, and Religiously unaffiliated have thousands of respondents in both
waves and are precise.

**Mode change caveat.** 2007 was random-digit-dial telephone; 2023-24 was
mostly online and mail. Pew ran a bridge study to measure the mode effect
and flags this as a caveat for any cross-wave comparison (see the 2023-24
RLS dataset's own `methodology` entry in `src/lib/data-explorer.ts`) — a
change in reported share isn't necessarily a change in the underlying
population.

## Numbers (2007 -> 2023-24, share of all U.S. adults)

| Tradition | 2007 | 2023-24 | Relative change | n (2007 / 2023-24) |
| --- | --- | --- | --- | --- |
| Religiously unaffiliated | 16.09% | 29.41% | +82.8% | 5,048 / 10,729 |
| Evangelical Protestant | 26.28% | 23.08% | -12.2% | 9,472 / 8,298 |
| Catholic | 23.86% | 18.89% | -20.8% | 8,054 / 6,958 |
| Mainline Protestant | 18.08% | 11.49% | -36.5% | 7,470 / 5,333 |
| Historically Black Protestant | 6.92% | 5.39% | -22.1% | 1,995 / 1,468 |
| Other Faiths | 1.23% | 1.91% | +56.2% | 449 / 761 |
| Jewish | 1.72% | 1.68% | -2.2% | 682 / 850 |
| Latter-day Saint | 1.67% | 1.50% | -9.9% | 581 / 565 |
| Muslim* | 0.44% | 1.18% | +168.3% | 116 / 273 |
| Buddhist* | 0.74% | 1.07% | +44.3% | 411 / 348 |
| Hindu* | 0.41% | 0.93% | +125.7% | 257 / 247 |
| Orthodox Christian* | 0.58% | 0.72% | +25.5% | 363 / 225 |
| Other Christian* | 0.33% | 0.63% | +94.8% | 129 / 226 |
| Jehovah's Witness* | 0.71% | 0.42% | -41.2% | 215 / 113 |
| Other World Religions* | 0.13% | 0.30% | +124.6% | 42 / 99 |

*Fewer than 300 unweighted respondents in a wave — the relative-change
percentage is real but noisy; treat as directional, not precise.

## Using this to choose which churches to feature next

This backlog item was built to survey the whole landscape before picking the
next single-denomination deep-dive (in the spirit of
`ten-largest-us-churches-2035` or a future one-off chart). At a glance:

- **Growing fastest, off a real base:** Muslim, Hindu, and Other World
  Religions roughly doubled or more, but every one of them is a small-n
  group — a good candidate for a dedicated chart that pulls in a
  larger-sample source (e.g. an ACS or Pew ATP wave) rather than resting on
  RLS alone.
- **Largest declines among sizable groups:** Mainline Protestant (-36.5%)
  and Historically Black Protestant (-22.1%) are both precise (thousands of
  respondents) and substantial — strong candidates for their own
  denomination-level follow-up, similar to `ten-largest-us-churches-2035`'s
  United Methodist Church row.
- **Held roughly steady:** Jewish and Latter-day Saint are the two
  Judeo-Christian traditions with the smallest relative change in either
  direction, both precise enough to trust.
