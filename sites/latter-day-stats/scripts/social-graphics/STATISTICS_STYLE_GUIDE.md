# Social-media statistics graphics — style guide
 
Modeled on Ryan Burge's posting style (graphsaboutreligion.com / @ryanburge),
adapted for LDS-focused data posts.
 
## File naming
`YYYY-MM-DD_short-slug.R`
e.g. `2026-08-23_lds-retention-by-generation.R`
One file per post. No subfolders needed unless a post needs a saved dataset.
 
## Visual identity (locked — reuse across posts)
 
**Format:** 1080×1350 (4:5, Instagram portrait). `ggsave(width = 9, height = 11.25, dpi = 120)`
via `ragg::agg_png`, `bg = paper`.
 
**Palette:**
```r
ink   <- "#1A1A1A"   # text
paper <- "#F7F5F0"   # background
grid  <- "#D9D5CC"   # gridlines / dashed bridge segments
amber <- "#C9721C"   # primary series / emphasis
teal  <- "#2C7B8C"   # secondary series
muted <- "#6E6A63"   # subtitle/caption text
```
Two-group comparisons: `pal <- c("Group A" = amber, "Group B" = teal)`.
 
**Fonts:** Roboto Condensed (body/axis), Roboto Slab bold (title). Rendered via
`ragg` + `systemfonts` — no `showtext`. Confirm both are installed locally
before running (Claude Code / local machine, not this chat).
 
**`theme_burge()`** — reuse verbatim from `arianism_line.R`/`arianism_bars.R`
(paper background, no vertical gridlines, horizontal gridlines in `grid`,
bold Roboto Slab title, `element_markdown()` subtitle/caption via `ggtext`,
legend off, title/caption pinned to plot edge with `*.position = "plot"`).
 
**Title/subtitle/caption convention:**
- Title: for a per-statement chart (one slide, one survey item), the
  statement itself, quoted verbatim (`"There is one true God in three
  persons..."`) — not a punchy claim. This replaced the older "short,
  punchy claim" rule (`"America's Arianism problem"`) after it was found
  to duplicate the survey question that was also sitting in the subtitle:
  one slide, two places making the same statement, is clutter. A punchy
  claim is still fine for a slide that *isn't* about one measured
  statement — a hook card, an intro/closing text card — since there's no
  single question for the title to quote there.
- Subtitle no longer repeats the quote (see above) — just the direction
  line ("Share who strongly agree or somewhat agree, {year}") and, where a
  chart uses more than one series, a markdown-colored legend key
  (`<span style='color:...'>■ Group</span>`) built with
  `element_markdown()` — no separate ggplot legend.
- Caption (`cap_txt`) holds, in order: any asterisked methodology footnotes,
  then the dataset/methodology line in **bold**, sample size + margin of
  error if known, then `@ithinkisam` in the accent color on its own line.
  This replaces the old plain-text `caption = "Data: SOURCE (YEAR)"` — the
  citation is now the last line of `cap_txt`, styled, not a separate footer.
**Two chart forms per topic when it fits:** a line chart (trend over time,
dashed "bridge" segment for a discontinuous first wave) and a dodged bar
chart, both built off the same tidy `tribble()`/data frame and same
`theme_burge()`. Not mandatory for every post — use whichever form suits
the data — but default to line for time series, bars for categorical
comparison.
 
## Script structure
1. **Data** — small time series/category data can be hand-entered via
   `tribble()` (see example) when pulling from a published report table;
   pull from a full survey file with `recode()`/`case_when()` + `wt =` when
   working from raw microdata.
2. **Wrangle** — flag any discontinuous/asterisked points (`lab = if_else(...)`),
   relevel factors so the emphasis group plots first (`fct_relevel()`).
3. **Plot** — `ggplot()` + `theme_burge()`, direct `geom_text()` labels,
   no default legend (folded into the subtitle instead).
4. **Save** — `ggsave(..., device = ragg::agg_png, width = 9, height = 11.25, dpi = 120, bg = paper)`.
## Post write-up (outside the R file, wherever the post itself is published)
- Short paragraph of interpretation, Burge-style: one stat up front, one
  paragraph of "why this matters," done. No long lit review.
- The image's own caption now carries the data source, sample size, and
  `@ithinkisam` handle — no separate text footer needed under the post.
- Still link back to the code in the post text itself:
  `Code: github.com/Samuel-Baird/latter-day-stats/blob/main/scripts/social-graphics/YYYY-MM-DD_slug.R`
- If more than one dataset feeds a chart, stack each as its own line inside
  `cap_txt`, same as the methodology/margin-of-error lines.
## Package stack (default)
`tidyverse`, `scales`, plus `socsci` (Burge's own package,
`remotes::install_github("ryanburge/socsci")`) if using weighted crosstabs
(`ct()`, `mean_ci()`, `frcode()`).

## This guide is for social posts specifically

Everything above — the palette, the fonts, `theme_burge()`, the file
naming — is also the base for a *separate* website style used on
the site's Data Explorer, documented at
[../state-of-theology-graphics/STYLE.md](../state-of-theology-graphics/STYLE.md).
That doc departs from this one on two points, both website-specific:

- **Title wording.** Here (social), a per-statement chart's title is now
  the survey statement itself, quoted verbatim — same as the website's
  *measurement* title (see "Title/subtitle/caption convention" above). The
  remaining latitude this guide keeps over the website: a slide that isn't
  about one measured statement (a hook card, an intro/closing text card)
  *may* still use a short, punchy claim ("Evangelicals won", "Still the
  beam") — that's a judgment call per post, not a requirement every such
  slide needs a claim. The website has no equivalent slide type, so it has
  no equivalent exception; every website chart title is either a
  measurement title or a plain, verifiable-from-the-chart *factual-summary*
  title — spin, judgment words, and unplotted claims stay banned there. See
  `state-of-theology-graphics/STYLE.md`'s "Titles: accurate, not editorial"
  for the full website rule. Don't pull the website's spin ban back into a
  social hook/text-card title, and don't treat "punchy is fine for a hook
  card" as license to editorialize a per-statement chart on either side.
- **Background.** Here, `paper` is the cream `#F7F5F0`. On the website it's
  pure white. Everything else in the palette is shared between the two.

If the shared parts (palette, type, `theme_burge()`) ever change, update
both docs together.
