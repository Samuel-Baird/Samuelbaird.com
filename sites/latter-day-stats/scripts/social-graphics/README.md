# Social-media statistics graphics

R scripts that generate @ithinkisam's data-explainer graphics for social
posts — currently the State of Theology survey (Ligonier Ministries /
Lifeway Research). Each script renders a set of 1080×1350px (Instagram 4:5)
PNGs to a local output folder; rendered images aren't committed here, only
the generators.

Migrated from the retired `Samuel-Baird/ithinksam_statistics` repo
(2026-08-25) — this repo is now the single home for all of the project's
statistics work, social and website alike.

- [`state_of_theology_charts.R`](state_of_theology_charts.R) — one item per
  chart, compared across survey years (Evangelical vs. All U.S. adults).
- [`state_of_theology_groups.R`](state_of_theology_groups.R) — one item per
  chart, compared across religious traditions within a single wave.

## House style

The style for these scripts — for social posts — is documented in
[`STATISTICS_STYLE_GUIDE.md`](STATISTICS_STYLE_GUIDE.md): palette,
typography, `theme_burge()`, file naming, and the title/subtitle/caption
convention. **Keep new charts to that spec.** The point of writing it down
is that a chart made today and a chart made in six months look like the
same series. If you deliberately change the style, update that doc in the
same commit — an undocumented style stops being a style.

The website's Data Explorer uses a related but distinct style, documented
at [`../state-of-theology-graphics/STYLE.md`](../state-of-theology-graphics/STYLE.md) —
same palette and type, but neutral chart titles (the survey statement
itself, verbatim) and a white background instead of this style's cream.
See `STATISTICS_STYLE_GUIDE.md`'s closing section for why the two diverge
on those points and nothing else. The website's Python generator lives at
[`../state-of-theology-graphics/render_chart.py`](../state-of-theology-graphics/render_chart.py).
These R scripts remain the canonical generator for social posts.

## Requirements

R with `ggplot2`, `dplyr`, `tibble`, `forcats`, `ggtext`, `ragg`. Roboto
Condensed and Roboto Slab installed as system fonts (`ragg`/`systemfonts`
read the OS font list, not a bundled file — the website generator's
[`fonts/`](../state-of-theology-graphics/fonts/) directory has the .ttf
files if you need to install them).

## Adding a survey item

Add a row (or set of rows) to the script's `tribble()` data block and an
entry to its `items` list — see either script for the exact shape a new
item needs. Verify every percentage against a real source (the published
report, or the survey's own microdata — see
[`../evangelical-quiz/README.md`](../evangelical-quiz/README.md) for how
the microdata is fetched and verified) before it goes in; never estimate
or interpolate a number to fill a gap.
