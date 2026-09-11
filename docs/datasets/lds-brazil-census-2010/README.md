# Latter-day Saints in Brazil — the 2010 Census

Three charts built entirely on IBGE's **2010** Census religion table, which —
unlike the 2022 Census used by `lds-brazil-2022/smaller-faiths-by-state-2022.json`
— published "Igreja de Jesus Cristo dos Santos dos Últimos Dias" as its own
real, government-tabulated category. Every number on this page is a genuine
LDS-specific count, not a mixed-bucket proxy.

## Why a separate dataset from `lds-brazil-2022`

The earlier `lds-brazil-2022` dataset's third chart (`smaller-faiths-by-state-2022.png`)
uses the 2022 Census's "Outras religiosidades" bucket — explicitly **not**
LDS-specific, since IBGE's 2022 microdata only breaks religion into 9 broad
groups. This dataset's three charts are the opposite: real LDS-specific
counts from a different census year (2010), a different source table, and a
meaningfully different framing. Splitting them into their own dataset keeps
that distinction from getting blurred on a single page — every chart here
says "2010 Census" and "LDS-specific" in its own title/subtitle/caption.

## What's in here

- **`lds-by-state-2010.json`** — all 27 states/DF, ranked by LDS
  self-identification as a % of each state's own population. Built by
  `scripts/lds-brazil-census-2010/build_lds_by_state_2010.py`.
- **`self-id-vs-membership-2010.json`** — a two-bar comparison of the
  226,509 people who told the 2010 Census taker they were Latter-day Saint
  against the Church's own reported 1,138,740 membership total for Brazil
  that same year. Built by
  `scripts/lds-brazil-census-2010/build_self_id_vs_membership_2010.py`.
- **`top-cities-2010.json`** — the municipalities (population 50,000+) with
  the highest LDS self-identification share, top 12. Built by
  `scripts/lds-brazil-census-2010/build_top_cities_2010.py`.

## Source and verification

IBGE's SIDRA aggregate table 137 ("População residente, por religião"),
classification 133 (Religião), category 100423 ("Igreja de Jesus Cristo dos
Santos dos Últimos Dias"), queried live against the public API at
apisidra.ibge.gov.br this session:

- National, all census years: `https://apisidra.ibge.gov.br/values/t/137/n1/all/v/93/p/all/c133/100423`
  — confirms 1991 and 2000 both return `"..."` (suppressed/not disclosed) at
  this category; only 2010 has a real national figure (226,509).
- State level (n3), 2010: `.../n3/all/v/93/p/2010/c133/100423` (LDS counts)
  and `.../n3/all/v/93/p/2010/c133/0` (total population) — all 27 states/DF
  returned real values for both.
- Municipality level (n6), 2010: `.../n6/all/v/93/p/2010/c133/100423` and
  `.../n6/all/v/93/p/2010/c133/0` — of 5,565 municipalities, 4,548 come back
  suppressed at this category (normal for small towns); 470 have both a real
  count and population ≥ 50,000.

Church membership figure (1,138,740, Brazil, 2010): cumorah.com's LDS Growth
Case Studies (Matt Martinich), "Expanding LDS Outreach in Brazil" — the same
figure already cited for 2010 in `docs/datasets/lds-brazil-2022/membership-by-year.json`.

## What was checked and NOT built

The original brief for this batch proposed a 1991–2010 LDS-specific growth
line. That isn't buildable: the national-level query above confirms 1991 and
2000 both return `"..."` at category 100423 — IBGE never disclosed an
LDS-specific figure for those years, at the national level or below. No such
chart is included here, and no other figure (e.g. a different, unverified
secondary source's number for an earlier year) was substituted in to fill
that gap.

## Notes on individual charts

**`lds-by-state-2010.png`.** Ranked by *share* of each state's population,
not raw count — São Paulo has the most members in absolute terms (65,556)
but a lower share (0.159%) than several smaller states. The top state by
share, verified independently against the live API, is **Amazonas**
(0.245%), fractionally ahead of Rio Grande do Sul (0.245%) — essentially a
statistical tie at the top, both far ahead of São Paulo's absolute lead.

**`self-id-vs-membership-2010.png`.** Deliberately does *not* assert a cause
for the ~5:1 gap between the two bars. Membership records can include people
who are inactive, moved away, never really engaged after baptism, declined
to state a religion to a census taker, or reflect record lag — this chart
states what each bar measures (told the census taker vs. on Church rolls),
not why they differ.

**`top-cities-2010.png`.** Restricted to municipalities with 2010 population
≥ 50,000, specifically to avoid the small-town noise that would otherwise
dominate a raw ranking (many very small towns return a real but tiny LDS
count against an equally tiny population, producing spuriously huge
percentages). Sant'Ana do Livramento, RS tops the list at 1.04%; 5 of the
top 10 are in Rio Grande do Sul, including border cities with Uruguay
(Sant'Ana do Livramento, Uruguaiana) — consistent with the Church's history
of early missionary concentration in southern Brazil.

## Recommended citation

> 2010 Brazilian Census (IBGE), SIDRA aggregate table 137, and cumorah.com's
> LDS Growth Case Studies (Matt Martinich), "Expanding LDS Outreach in
> Brazil."
