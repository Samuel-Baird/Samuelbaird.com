# Ten largest U.S.-rooted churches, projected to 2035

A second kind of "mixed data" entry alongside
[us-membership-growth-2000-2025](../us-membership-growth-2000-2025/README.md)
and [worldwide-membership-history](../worldwide-membership-history/README.md)
— except this one compares **across** ten denominations rather than
tracking one body over time. Modeled after Ryan Burge's GSS-based
American-religion projections
(<https://gist.github.com/ryanburge/e785275206cd12584b73eb4ec9b3ad52>), but
applied here to individual denominations' own reported membership rather
than survey-tradition shares.

## The ten bodies

Catholic Church, United Methodist Church, The Church of Jesus Christ of
Latter-day Saints, Evangelical Lutheran Church in America (ELCA), Lutheran
Church–Missouri Synod (LCMS), Orthodox Christian churches (combined
estimate), Episcopal Church, Presbyterian Church (USA), Church of God in
Christ (COGIC), and Presbyterian Church in America (PCA).

## Method

`build_data.py` holds every reported point and its citation. For each
body, an ordinary-least-squares line is fit through its own reported
membership figures and extended to 2035 — a simple straight-line
extrapolation, not a demographic model. It cannot see an inflection (a
schism, a policy vote, an accelerating or decelerating rate) that hasn't
happened yet in the data. **Catholic Church is a special case**: its full
1990–2020 series is dominated by a 2000–2010 jump that reads as an
Official Catholic Directory reporting-convention change rather than real
growth, so its fit uses only the 2010 and 2020 points instead.

Every entry carries a `confidence` field:

| Confidence | Meaning |
| --- | --- |
| `high` | A clean, consistent multi-point series from one source lineage |
| `medium` | Usable but sparse, or complicated by a known one-time shock |
| `low` | Sparse and/or internally inconsistent sourcing — shown, but flagged everywhere (starred on the chart, noted in alt text, and here) |

## Sources, by denomination

- **Catholic Church** — CARA (Georgetown), <https://cara.georgetown.edu/faqs>;
  Wikipedia, "Catholic Church in the United States." Sources disagree by
  5–15M in the same year depending on methodology (registered vs.
  self-identified counts) — the weakest series in this set.
- **United Methodist Church** — General Commission on Archives & History,
  <https://gcah.org/history/timelines/membership-statistics>; UMC.org,
  "United Methodists at a Glance"; General Council on Finance and
  Administration 2023 figure via juicyecumenism.com (Nov. 2024). Includes
  the 2019–2023 disaffiliation schism (~7,600 churches left in one wave).
- **LDS Church** — Wikipedia, "Membership history of the Church of Jesus
  Christ of Latter-day Saints." **Worldwide, not U.S.-only** — see this
  site's own `us-membership-growth-2000-2025` dataset for why a clean
  U.S.-only annual series doesn't exist.
- **ELCA** — So What Faith, "ELCA Membership Cut in Half" (2024),
  sowhatfaith.com; ELCA, "Summary of Congregational Statistics as of
  12/31/2023," resources.elca.org.
- **LCMS** — LCMS statistical yearbook (1993, via secondary compilation);
  Mighty Fortress Substack, "The Brisk Decline of the LCMS" (2010, 2020);
  LCMS Inc. Annual Report 2024. Only 4 usable points — no reliable 1990 or
  2000 figure was found.
- **Orthodox Christian (combined estimate)** — ASARB 2000 study via
  orthodoxhistory.org; 2010 figure averages two conflicting estimates
  (799,400–1,044,000, per orthodoxhistory.org and usreligioncensus.org);
  2020 U.S. Religion Census Appendix F (Orthodox Christian Groups).
  Sparse, self-reported/estimated, and internally inconsistent between
  sources for the same year.
- **Episcopal Church** — The Living Church, "Facing Episcopal Church
  Decline" and "TEC's Latest Numbers: The Good News and the Bad News,"
  livingchurch.org. Only 3 data points; the Church did not report a 2024
  baptized-membership topline at all, citing "parochial report confusion."
- **Presbyterian Church (USA)** — So What Faith / Protestia compilation,
  "PCUSA Membership: 30 Years of Decline" (2023) and "The PCUSA Is Missing
  2.6 Million People"; Presbyterian Outlook, "PCUSA 2022 Statistical
  Report," pres-outlook.org. The steepest relative decline in this set —
  see the chart's own caveat about what a straight-line fit implies by the
  late 2030s.
- **Church of God in Christ** — denominational self-reports (1997, 2003,
  2016). These figures (~5.2–5.5M) diverge roughly 5–6x from the
  independent U.S. Religion Census, which counted ~624,000 in 2010 and
  ~920,000 in 2020. This is the lowest-confidence series in the whole set,
  shown here per the denomination's own reporting rather than the census
  figures — a genuinely unresolved discrepancy, not a rounding difference.
- **Presbyterian Church in America** — PCA Historical Center,
  <https://www.pcahistory.org/main/pcastats.html>; Graphs About Religion,
  "A Deep Dive into the Presbyterian Church in America" (2025). The one
  denomination in this set that has grown steadily throughout the period.

## Regenerating

```bash
python scripts/ten-largest-us-churches-2035/build_data.py
python scripts/ten-largest-us-churches-2035/render_chart.py \
  --out public/data-explorer/ten-largest-us-churches-2035/projected-2035.png
```

`build_data.py` is the single source of truth for every number and its
citation — never hand-edit `denominations.json`. The render script uses a
new shared shape, `render_dumbbell_log` in
`scripts/flagship-charts/common.py`: a log-scale dumbbell chart (gray dot
= last reported figure, triangle = 2035 projection), required here because
these ten bodies span roughly 400K to 70M members — on a linear axis the
nine smaller bodies would collapse to indistinguishable points next to the
Catholic Church.
