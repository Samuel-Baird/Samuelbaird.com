# Pew Research Center — 2023-24 Religious Landscape Study (RLS)

Pew's national cross-sectional survey of U.S. adults on religious identity,
belief, and practice. N = 36,908, fielded July 17, 2023 – March 4, 2024 by
NORC on an address-based sample, in English and Spanish, by web, paper, and
inbound phone.

## Recommended citation

> Pew Research Center. 2025. “2023-24 Religious Landscape Study (RLS)
> Dataset.” doi: 10.58094/3kwb-bf52.

Cite it this way anywhere the site uses these numbers. The Data Explorer
entry (`src/lib/data-explorer.ts`, slug `pew-religious-landscape-study`)
carries the same string so the public page and this folder can't drift.

- Dataset and documentation: <https://www.pewresearch.org/religious-landscape-study/>
- DOI: <https://doi.org/10.58094/3kwb-bf52>
- First release from the survey: [“Decline of Christianity in the U.S. Has
  Slowed, May Have Leveled
  Off”](https://www.pewresearch.org/religion/2025/02/26/decline-of-christianity-in-the-us-has-slowed-may-have-leveled-off/)
  (Feb. 26, 2025) — Appendix B is where the evangelical / mainline /
  historically Black Protestant assignment rules are written down.

## What's in here

| Path | What it is |
| --- | --- |
| `source/readme.txt` | Pew's own readme shipped with the public-use file |
| `source/codebook.xlsx` | Pew's codebook: every variable, every value label |
| `source/how-the-rls-categorizes-religion.pdf` | DENOM → FAMILY → RELTRAD, plus PROTFAM |
| `source/methodology-report.pdf` | Sampling, weighting, response rates |
| `source/questionnaire-web-phone.pdf` | CAWI/CATI instrument (English + Spanish specs) |
| `source/questionnaire-paper-english.pdf` | Paper instrument, English |
| `source/questionnaire-paper-spanish.pdf` | Paper instrument, Spanish |
| `codebook.json` | `source/codebook.xlsx` flattened to one object per variable |
| `switching-rates.json` | Weighted raised-vs-current religion shares (`FRMREL`/`CURREL`/`RELTRAD`), with bootstrap standard errors, for the Data Explorer's net-change graphic |

`codebook.json` is generated, not hand-written — regenerate it with:

```bash
python scripts/pew-rls/extract_codebook.py \
  docs/datasets/pew-rls-2023-24/source/codebook.xlsx \
  docs/datasets/pew-rls-2023-24/codebook.json
```

(Standard library only. An `.xlsx` is a zip of XML, so nothing to install.)

`switching-rates.json` reads the microdata directly — `FRMREL`, `CURREL`,
`RELTRAD`, `WEIGHT`, and all 500 `REPWT_*` replicate weight columns — and
needs `data/pew-rls-2023-24/` populated (see "What's deliberately not in
here," below) plus `pandas`/`numpy`. Regenerate it, then the PNG that reads
it, with:

```bash
python scripts/pew-rls/switching_rates.py
python scripts/pew-rls/render_switching_chart.py \
  --out public/data-explorer/pew-religious-landscape-study/switching-rates.png
```

See [`scripts/pew-rls/STYLE.md`](../../scripts/pew-rls/STYLE.md) for the
chart's palette and layout — an extension of
[`state-of-theology-graphics/STYLE.md`](../../scripts/state-of-theology-graphics/STYLE.md)'s
house style for a decline/net-change chart, which that doc doesn't cover.

## What's deliberately *not* in here

The microdata itself — `2023-24 RLS Public Use File Feb 19.csv` (239 MB) and
the SPSS `.sav` (119 MB). Both exceed GitHub's 100 MB per-file limit and
would need Git LFS; neither is needed to build the site.

On the repo owner's machine they sit, along with the rest of Pew's download
exactly as Pew ships it, in `data/pew-rls-2023-24/` — inside the working
tree but gitignored, so the files are one `cd` away without ever being
staged. Anyone else: download them from Pew's [Religious Landscape Study
page](https://www.pewresearch.org/religious-landscape-study/) into that same
path and every script here will find them.

Pew also ships two versions of the file. Everything here documents the
**public-use file (PUF)**, which withholds a set of sensitive variables —
including `DENOMREC2`, `FAMILY`, `PROTFAM`, `CURREL2`, `STATE`, and
`REGION`. Those columns are present in the PUF's CSV header but empty. The
value labels for them *are* in the codebook, which is why the taxonomy below
could be built from the PUF documentation alone. The restricted-use file
(RUF), with the real values, is meant to reach ICPSR under a data use
agreement.

Weighting, if you ever analyze the microdata: `WEIGHT` for national and
state estimates (with `REPWT_001`–`REPWT_500` as replicate weights),
`WEIGHT_MSA` for the 34 metro areas. Pew's Stata setup line:

```stata
svyset [pweight=weight], bsrweight(repwt_001-repwt_500) vce(bootstrap)
```

## How the site uses it

The quiz's optional demographic intake
(`src/lib/evangelical-quiz/demographics.ts`) mirrors the RLS instrument, so
answers collected here can be read against Pew's national numbers without a
recoding step in between:

| Site field | RLS variable |
| --- | --- |
| Religion | `FAMILY` (all 52 substantive categories: RELTRAD, with Protestant, other-faiths, and unaffiliated detail) |
| Birth cohort | `BIRTHDECADE` |
| Gender | `GENDER` |
| Hispanic origin | `HISP` |
| Race | `RACECMB` |
| Education | `EDUCREC` |
| Marital status | `MARITAL` |
| State | `STATE` |
| Country | *(none — see below)* |

`FAMILY` is the level Pew calls a "family of denominations" — one step
coarser than `DENOMREC2` (298 denominations in `DENOM`, coarsened to 86
codes) and one step finer than `RELTRAD` (16 traditions). It is the finest
level a person can reasonably pick for themselves off a list: Pew's own
interviews get there by branching questions and then a back-coding pass,
which a single dropdown can't reproduce.

Two places where the site's list departs from `FAMILY`, both documented in
the TypeScript:

- `prefer_not_to_say` has no `FAMILY` code. Pew has a nonresponse code
  (999) instead; declining to answer and failing to be coded aren't the
  same thing.
- `atheist_agnostic` is retired, not deleted. It predates this taxonomy and
  is still referenced by rows recorded before the switch; `FAMILY` splits it
  into Atheist (301) and Agnostic (302).

Two places where the site asks *more* than the RLS does, both because its
readers are not Pew's sample:

- **Country of residence** has no RLS counterpart at all — the study surveys
  U.S. adults, so residence is assumed. This site's readers are not all
  American, and recording "not the U.S." beats recording a blank state. The
  state question is asked only when the country is the United States, both
  in the intake and in `validateDemographics`.
- **The 2010s and 2020s birth cohorts** extend past `BIRTHDECADE`, which
  stops at the 2000s because Pew surveys adults. The site's own floor is 13+
  (COPPA, migration 0037). Both carry a null RLS code, so rows in those
  cohorts fall outside any comparison with Pew's numbers rather than
  silently distorting one.
