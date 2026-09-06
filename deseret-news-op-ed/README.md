# Deseret News op-ed graphics

Charts for the op-ed *"Thirty Years After the Family Proclamation, the Data
Shows Three Americas"* (draft in `data/family-proclamation-oped-draft.md` at
the repo root's gitignored `data/` folder). Everything here is computed from
Pew Research Center's three Religious Landscape Study public-use files and
rendered with the shared house style in `dn_style.py`.

These are Latter-day Stats charts that borrow the Deseret News **color
scheme** so they sit comfortably on the paper's pages. They are not Deseret
News graphics: no Deseret News logo, wordmark, beehive, or "period" device
appears, and the credit line on every chart reads "Chart: Latter-day Stats".

## What's in the folder

| Path | What it is |
| --- | --- |
| `out/01_divergence.png` / `.svg` | Christian / unaffiliated / Latter-day Saint share of U.S. adults, 2007 -> 2014 -> 2023-24 (line chart, top of piece) |
| `out/02_parents_practice.png` / `.svg` | Parents of minor children doing at least one of three religious practices with them (the centerpiece) |
| `out/03_completed_fertility.png` / `.svg` | Number of children ever born, Christians vs. religiously unaffiliated adults born 1960s-70s (distribution) |
| `out/04_transmission.png` / `.svg` | Share of adults raised highly religious who are still highly religious, by birth decade |
| `out/05_denominational_decline.png` / `.svg` | 2007 vs. 2023-24 dumbbell: evangelical, mainline, SBC, UMC, Latter-day Saints (optional substitute for 01) |
| `out/06_lds_family_formation.png` / `.svg` | Married share and 3+-children share, Latter-day Saints vs. all Christians vs. unaffiliated |
| `data/oped_data.json` | Every number the charts use, with unweighted n's and Pew's published comparison figures |
| `compute_data.py` | Rebuilds `data/oped_data.json` from the microdata |
| `render_NN_*.py` | One render script per chart; each reads the JSON at runtime |
| `dn_style.py` | Palette, fonts, canvas, header/footer/legend helpers |
| `fonts/` | Static instances of the open substitute typefaces (see below) |

PNGs are 2400 x 1600 px (12 x 8 in at 200 dpi, a 3:2 web graphic); SVGs are
the same drawing as vectors for the art desk.

## Regenerate

From the repo root (the microdata lives in the gitignored `data/` junction):

```bash
python deseret-news-op-ed/compute_data.py
cd deseret-news-op-ed && for f in render_0*.py; do python "$f"; done
```

## Style: Deseret News palette, open typefaces

Colors are the five in the Deseret News Brand Guide v.02 (Aug 2019) plus two
derived neutrals:

| Role | Hex | Guide name |
| --- | --- | --- |
| Emphasis series (Latter-day Saints), value chips | `#ffd217` | Deseret Yellow |
| Dark neutral series (Christians / religiously affiliated) | `#424242` | Gray 1 |
| Light neutral series (religiously unaffiliated) | `#8c8c8c` | derived |
| Primary text | `#1e1e1e` | Gray 2 / off-black |
| Secondary text | `#5f5f5f` | derived |
| Chip tracks, table stripes | `#f2f2f2` | "White" |
| Gridlines | `#e3e3e3` | derived |

The guide's typefaces are licensed (Poynter Old Style, Benton Sans), so the
charts use open stand-ins with the same roles: **Newsreader** for the serif
display/text face, **Libre Franklin** (an open Franklin Gothic revival; Benton
Sans is a Franklin Gothic descendant) for labels, and **Oswald** for the big
condensed numerals the guide reserves for infographics. Font files in
`fonts/` are static weight instances generated from the Google Fonts
variable masters so matplotlib can select weights.

Chart form follows the site's dataviz rules: emphasis form (one hue plus
grays), color follows the entity in every chart, text never wears a series
color, a legend row whenever two or more series are drawn, solid hairline
gridlines, bars from zero, direct labels only on the values that matter.

## Sources

- Pew Research Center. 2008. "U.S. Religious Landscape Survey." Continental
  U.S. telephone file, N = 35,556 (`data/pew-rls-2007/`).
- Pew Research Center. 2015. "2014 Religious Landscape Study." N = 35,071
  (`data/pew-rls-2014/`).
- Pew Research Center. 2025. "2023-24 Religious Landscape Study (RLS)
  Dataset." doi: 10.58094/3kwb-bf52. Public-use file, N = 36,908
  (`data/pew-rls-2023-24/`).
- Published comparison figures: Pew's overview report *Decline of
  Christianity in the U.S. Has Slowed, May Have Leveled Off* (Feb. 26, 2025)
  and its chapter *Religion, fertility and child-rearing*.

Each wave is weighted by its own full-sample weight. Population shares keep
don't-know/refused in the denominator, matching how Pew reports "62% of U.S.
adults are Christian".

## Chart-by-chart notes

**01 Divergence.** Christian 78.4 -> 70.7 -> 62.1; unaffiliated 16.1 -> 22.8
-> 29.4; Latter-day Saints 1.67 -> 1.63 -> 1.50 (unweighted LDS n = 581 /
664 / 565). Pew rounds the Latter-day Saint share to 2% in all three waves;
the chart shows one decimal because a 1.7 -> 1.5 drift is real information
even though it is inside sampling error.

**02 Parents and religious practice.** Base is all parents/guardians of a
child under 18 at home (`CHILDREN = 1`); "at least one" of `KIDACT_A`
(pray/read scripture), `KIDACT_B` (Sunday school or religious education),
`KIDACT_C` (homeschool or religious school). Latter-day Saints 84.4%
(n = 195), all Christians 70.2% (n = 4,969), unaffiliated 20.7% (n = 2,679).
Pew's published figures are 84% and 70%. The three component items under
each bar use the same all-parents base, which reproduces Pew's published
58% (pray/scripture) and 48% (religious education) for Christian parents.

**03 Completed fertility.** The public file has no exact age (only
`BIRTHDECADE`) and caps `FERTREC` at "4 or more", so Pew's published averages
for ages 40-59 (Christians 2.2, unaffiliated 1.8) cannot be reproduced. The
chart shows the full 0/1/2/3/4+ distribution for adults born in the 1960s and
1970s (about ages 44-64 when surveyed): all Christians 15/15/33/22/15
(n = 7,327), unaffiliated 24/16/34/15/10 (n = 3,070); 37% vs. 26% have three
or more. The rows are Christians rather than "religiously affiliated" so the
chart matches Pew's published 2.2 (a Christians-only average) and the
Christians-vs-unaffiliated framing of charts 01, 02 and 06; the JSON also
carries the all-affiliated row (15/15/33/21/15, n = 8,011, 36% with 3+) if
that framing is preferred - a one-line switch in `render_03_completed_fertility.py`.
Floor means (4+ counted as 4) are 2.07 (Christians) vs. 1.72.

**04 Transmission.** Pew's definitions, verified against its report:
"highly religious upbringing" = attended weekly or more (`CHATTEND` 1-2) and
religion very important to the family (`CHIMPREL_B = 1`); "highly religious
now" = attends weekly or more (`ATTNDPERRLS` 1-2) and religion very
important (`RELIMP = 1`). By birth decade, oldest to youngest: 51.1, 39.0,
34.8, 34.1, 30.6, 28.9, 27.6. Born 1940s or earlier is Pew's "74 and older"
(51%), born 2000s is its "18-24" (28%); the PUF reproduces both exactly.
Among adults raised Latter-day Saint *and* highly religious, 69% are still
highly religious (n = 354) - not on the chart, but usable in the text.

**05 Denominational decline.** Evangelical 26.3 -> 23.1, mainline 18.1 ->
11.5, Latter-day Saints 1.67 -> 1.50 from the microdata. Southern Baptist
Convention (6.7 -> 5.3 -> 4.4) and United Methodist Church (5.1 -> 3.6 ->
2.7): the 2007 and 2014 values are computed from `denom`/`DENOM`; the 2023-24
values are Pew's published figures because the 2023-24 public file withholds
denomination detail (`DENOM`, `FAMILY`, `PROTFAM` are restricted-use and
blank).

**06 LDS family formation.** Currently married: Latter-day Saints 68.1%
(n = 558), all Christians 55.6%, unaffiliated 42.0%. Three or more children
among adults born 1960s-70s: Latter-day Saints 67.5% (n = 171, small), all
Christians 36.9%, unaffiliated 25.8%.

## Where the op-ed draft and the data disagree

Fix these in the text before submission; the charts use the corrected values.

1. **"Among American parents with no religious affiliation, 9% do at least
   one."** Wrong. 9% is Pew's figure for religious *education alone*
   (`KIDACT_B`). Unaffiliated parents doing *at least one* of the three
   practices is **21%** (20.7%). The honest contrast is 84 against 21, not 84
   against 9.
2. **"Religiously affiliated Americans ... average 2.2 children; the
   religiously unaffiliated average 1.8."** Pew's published 2.2 is for
   *Christians* ages 40-59, not all religiously affiliated (non-Christian
   religions average 1.8, Jews 2.0). Either say "Christians" or cite the
   distribution chart instead.
3. **"Latter-day Saints have held steady at 2%."** True at Pew's rounding.
   Unrounded, the public files give 1.7% (2007), 1.6% (2014), 1.5% (2023-24)
   - a drift inside sampling error, but "held near 2%" is safer than "held
   steady". Chart 01 shows the decimals.
4. **"The United Methodist Church nearly halved."** 5.1% -> 2.7% is a 47%
   relative decline, so this holds. Southern Baptists 6.7% -> 4.4% is a 34%
   decline. Evangelicals overall fell 12% and Latter-day Saints 10% on the
   same basis, which is why chart 05 does not say Latter-day Saints "declined
   least".
5. **"Monthly worship attendance dropped from roughly 54% to 33%."** Holds:
   54.5% of all adults attended at least monthly in 2007 (`q20`), 32.6% in
   2023-24 (`ATTNDPERRLS`, which asks about *in-person* attendance - a
   wording change worth a hedge).
   **"Even among Americans who stayed Christian, daily prayer fell from 58%
   to 44%."** Misattributed. 58% -> 44% (57.8 -> 43.9) is daily prayer among
   *all U.S. adults*. Among Christians it fell from 66% to 60% (`q41` 2007,
   `PRAY` 2023-24, "several times a day" or "once a day"). Rewrite as "daily
   prayer among all Americans fell from 58% to 44%; even among Christians it
   slipped from 66% to 60%."
6. Pew's published "highly religious" transmission figures (51% / 28%) are
   confirmed, and the definition is now documented (see chart 04).
