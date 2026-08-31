# Study graphics — pipeline style contract

Per-study downloadable PNGs for the **studies** section (`/studies/[slug]`),
the studies-side counterpart of the Data Explorer's per-dataset graphics.
Same canvas (1080×1350, 9×11.25in at 120dpi), same fonts, same shared
helpers (`scripts/chart_style.py`), and — wherever the shape fits — the same
render functions as the one-off flagship datasets
(`scripts/flagship-charts/common.py`). Read `BRANDING_AND_DESIGN.md`'s
"Charts" section and `docs/CHARTS.md` first; everything there (32pt titles,
16pt INK subtitles/footnotes, 24pt row labels, black bar/segment/swatch
outlines, per-group identity colors, `sort_groups` row order, the
one-bold-line `@ithinkisam | data: <short title>` caption, `MIN` font
floors, "open the PNG and check for overlap every time") applies here
unchanged.

## Layout

```
docs/study-data/<study-slug>/data.json          # every number, transcribed, with provenance
scripts/study-graphics/<study-slug>/render_*.py # reads ONLY that data.json
public/study-graphics/<study-slug>/*.png        # committed 1080×1350 renders
src/lib/study-graphics.ts                       # registry; imports the same data.json
```

The registry entry's alt text is built from the same JSON the render script
reads, so image and alt can never drift (`docs/CHARTS.md`'s rule for the
Data Explorer pipeline, carried over verbatim).

**sys.path note:** these scripts sit three levels below the repo root (one
deeper than `scripts/pew-rls/`), so the import shim is:

```python
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))                       # chart_style
sys.path.insert(0, str(SCRIPTS_DIR / "flagship-charts"))   # common (render shapes)
```

## Transcription JSON: "nothing hand-typed" without microdata

Data Explorer charts compute their JSON from source microdata. Most studies
publish only tables/toplines, so this pipeline's rule is the practical
equivalent: **no number appears in two places.** Each study gets one
committed `docs/study-data/<study-slug>/data.json` holding every charted
number, with a `sources` array citing exactly where each series was
transcribed from (table, page, or figure of the publication — precise
enough that someone with the source can re-check each number). Render
scripts `json.load` that file and never carry a numeric literal;
`src/lib/study-graphics.ts` imports the same file for titles'/alt text's
numbers. The transcription is the one hand-typed step, so verification
means auditing the JSON against the publication, not diffing scripts.

## Reuse the flagship shapes

`scripts/flagship-charts/common.py` is the shared shape library for this
pipeline too: `render_magnitude_bar` (with `group_identity`,
`highlight_rows`, or an explicit `row_colors` map), `render_paired_bar`
(subject group vs. a baseline population — added for
`pew-mormons-in-america-2012`), `render_100_stack`, and the timeseries
shapes. Add a genuinely new shape to `common.py` (per its own docstring),
not as a fork inside a study folder; keep study render scripts thin
callers.

## Current-vs-former group colors

Some studies compare religious-*status* groups (`Latter-day Saint` vs.
`Former Latter-day Saint`, etc.) that `chart_style.GROUP_COLORS` doesn't
cover. Convention, first used by
`byu-studies-63-4-religion-and-perfectionism`:

- A current-member group uses its locked `GROUP_COLORS` hex as usual.
- A **"Former X"** group takes a *lighter shade of X's own color family*
  (e.g. Former Latter-day Saint `#7FA3C8`, a lighter LDS blue) — the same
  same-family-different-shade approach the Evangelical/Mainline/HBP trio
  used to extend Protestant's amber. Never `--oxblood`: former-member
  status is not a "decline/negative" signal.
- A combined category (e.g. `Atheist/agnostic`) takes the darker anchor of
  its pair (`Atheist`'s hex).
- Named catch-alls (`Other Christian`, `Other religion`) stay
  `CONTEXT_GRAY` per the site-wide tier-1 rule; a "Former other …" row is
  a lighter shade of that gray (`#B3AFA5`).

Pass these as `render_magnitude_bar(row_colors=...)`. If a shade defined
here gets reused by a second study, promote it to `chart_style.py` so it
stays locked site-wide.

## When a study duplicates a Data Explorer dataset

Don't re-render charts the Data Explorer already has (Ligonier State of
Theology, the Pew RLS studies, the Church News article's U.S.-total
series). Give the registry entry a `dataExplorerSlug` instead — the study
page renders a callout linking to that dataset's `/graphics` page. A study
can carry both its own PNGs *and* a cross-link (the Church News entry
does).

## Checklist per study

1. Transcribe `docs/study-data/<slug>/data.json` with `sources`.
2. Write `scripts/study-graphics/<slug>/render_*.py` (copy an existing one
   in this folder as the starting point).
3. Run it; open every PNG at full size *and* ~1/3 scale; check overlap,
   spillover, caption, outlines, colors.
4. Audit 2–3 numbers per chart against the cited source location.
5. Add the registry entry (builder functions reading the same JSON) in
   `src/lib/study-graphics.ts`.
6. `npm run build` + `npm run lint`.

Sync contract: this file joins the `chart_style.py` sync list — a change to
that module updates this STYLE.md together with the other pipeline
STYLE.mds.
