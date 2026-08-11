# Constructing a timeline

How to build a new source timeline, and the analytical rules every timeline in
this repo follows. Read [`SOURCING.md`](./SOURCING.md) first for how sources are
found and graded; [`SCHEMA.md`](./SCHEMA.md) is the field-by-field contract.

---

## 1. The four rules

These are what separate a timeline from a quote collection. They apply to every
timeline, whatever the topic.

### No retrojection

Tag a source for **what it states**, not for what later frameworks read into
it. A text that describes many worlds under one God is not evidence of a
succession of Gods. A text asserting eternal, uncreated intelligences is not
articulating a three-stage intelligence → spirit → body model just because a
later writer harmonised the two.

When a later source *does* read a framework back into an earlier one, that
interpretive move is itself the datum. Log it on the later source, with a
`citesId` link to the earlier one.

### Referent discipline

Where a claim's subject is ambiguous, record who it is actually about. In the
eternal-increase timeline this is the `referent` field — Father, Son,
ambiguous, or n/a — and it is the single most important control in the dataset,
because several load-bearing "God was once a man" texts ground themselves in
*Christ's* mortality. A being who was mortal, is now God, and has a Father above
him fits the Son perfectly and requires no theogony for the Father.

A new timeline on a different topic needs its own version of this axis: the
question is always "what is the ambiguity that a careless reading would collapse,
and how do I make it visible per quote?"

### Original vs. citation

Type every source as a **first attestation** (`original`) or as a **later source
quoting one** (`citation`, with `citesId` naming what it quotes). Collapsing
citations then answers a question no flat list can: *what is actually attested,
independently, and when?*

The payoff is concrete. In the eternal-increase timeline, collapsing citations
and filtering to explicit backward-regress claims leaves four originals, the
latest from 1859 — every later appearance is a citation of an 1844 sermon.

### Quote-level tagging

One talk or manual can make several distinct doctrinal moves. Give each excerpt
its own `categories`, its own `referent`, and — where provenance differs within
a source — its own hearsay grade. The 2014 "Becoming Like God" essay carries
three quotes because it performs three different rhetorical operations on two
different originals.

---

## 2. Designing the category set

Categories are the analytical spine. Get them wrong and the timeline argues for
a conclusion instead of showing evidence.

**Make each category a claim a source could make, not a conclusion you hold.**
`RETREAT-REFRAME` describes what a text does to an earlier teaching; it does not
assert that a retreat was wrong or dishonest.

**Include the counter-position.** An axis that can only record affirmations will
always look one-sided. `DIVINE-PROGRESSION` covers both affirmations and
denials; `FATHER-ALWAYS-GOD` exists so the denial of divine becoming has
somewhere to live.

> A category with few sources is a finding, not a failure. `FATHER-ALWAYS-GOD`
> has four, and every one of them is complicated — the 1884 Joseph F. Smith
> passage states both directions of the axis five sentences apart, and the 1966
> Madsen one denies the *creedal* always-God position while asserting
> attainment. That the orthodox counter-position is this hard to attest cleanly
> is itself worth knowing, and worth chasing further.

**Answer the questions, on their own scales.** Being tagged with a claim does
not say which way a source leans on it. A category now decides which *questions*
a quote is asked; `bands` records what it answers, and every question keeps its
own ordered scale. Four rules:

- **A scale per question, because they do not all have two sides.** How many
  Gods stand above the Father takes four answers, and an unquantified chain is
  an *indefinite* claim, never an infinite one. Promoting it is the retrojection
  this project exists to avoid.
- **Keep questions apart even where the sources run them together.** Whether the
  Father was always God and whether he lived a mortal life are independent: this
  tradition already holds that Christ was God throughout his mortality, so
  "God once was as man now is" answers the mortality question and says nothing
  about the divinity one.
- **Silence is an answer.** A passage that raises a question by its tags and
  turns out not to speak to it is recorded as `not-addressed`. Leaving it blank
  would drop the quote out of that chart and quietly thin a band; the build
  refuses it.
- **Off-scale answers are drawn apart.** Declining to say sits genuinely between
  "not always God" and "always God", but nothing sits between an infinite
  regress and none — so on that question it is drawn below the scale rather than
  inside it.

**Distinguish explicit from euphemistic.** Nearly every taper story lives on
this boundary, so hold the canon to the same strict standard as everything else.
D&C 132 promises "a continuation of the seeds forever and ever" without naming
either the mechanism or the object, so it is tagged as euphemism — and the
citation links then show later curriculum *supplying* the explicit reading the
verse withholds.

**Split overlapping tags rather than stacking them.** When "God had a mortal
experience" and "God attained divinity" were both collapsed into one tag, the
distinction between a mortal probation and the attainment of godhood was
invisible. Three positions on one axis read better than one blurred tag.

**Group colours by family.** Related categories share a hue so the graph and
pills are scannable: one family per axis, warm colours for retreat/reframe,
neutral for structural tags.

---

## 3. Building a new timeline

Each timeline is a self-contained route folder, so it can be built, reviewed,
and deleted independently.

```
src/app/<topic>-timeline/
  page.tsx             server component: metadata, validation, page furniture
  timeline-explorer.tsx  "use client": filter state, era grouping, entry cards
  timeline-graph.tsx     "use client": dot-plot overview (copy or import)
  legend.tsx           scale and category reference
  constants.ts         category/hearsay/status/era metadata and colours
  schema.ts            zod schema + integrity checks
  sources.json         the data — the only file most edits touch
```

Steps:

1. **Write the question first.** One or two sentences naming what the timeline
   is measuring. If it cannot be stated crisply, the category set will drift.
2. **Draft the category set** against §2, including counter-positions.
3. **Seed 10–20 sources** spanning the full period before refining tags —
   category problems only surface against real material.
4. **Type every source** original or citation and wire up `citesId`.
5. **Add the integrity checks** to `parseSources()` (see below).
6. **Verify**, then publish. New timelines start unlisted; see §5.

Copy the eternal-increase folder as the starting point. Keep `sources.json` as
the only file that needs editing to add material — if adding a source requires
touching a component, the model is wrong.

### Validation is not optional

`parseSources()` runs at module scope of a statically prerendered page, so
anything it rejects **fails the build** rather than surfacing as a broken page.
Every timeline should reject at minimum:

- unknown category / hearsay / status / referent values (zod enums)
- malformed dates and URLs
- duplicate entry `id`s or `quoteId`s
- `citesId` values that resolve to nothing
- `hearsayByQuote` keys naming a quote that does not exist
- URLs on discovery-only hosts (see [`SOURCING.md`](./SOURCING.md) §1)

The point is that the data is hand-edited. A typo should stop a deploy, with
the offending JSON path named.

---

## 4. Presentation rules

- **Chronological, grouped by era.** Eras are computed from the date, never
  stored, so they disappear when filtering empties them. Keep era bounds
  contiguous — a gap silently drops sources.
- **Filters combine OR within a facet, AND across facets.** An empty facet
  means inactive, not "match nothing".
- **Both graphs reflect the filters, and their axes behave differently on
  purpose.** The distribution graph rescales to the sources in view, because it
  is answering "what is here" and wants the width spent on the material. The
  stance chart is pinned to the whole corpus on every question and under every
  filter, because it is answering "how settled was this" — and an autoscaling
  axis is actively misleading there. A question last raised in 2013 would
  otherwise redraw with its final dot against the right edge, looking current,
  when the fact worth seeing is the decade of silence after it. Fixing the axis
  also means the six questions share a ruler, so a gap on one tab is the same
  width as a gap on another.
- **Neither ever pads its stated range.** Whatever the axis spans, the caption
  reports the true first and last year of the data actually plotted.
- **Excerpts collapsed by default, expanded in print.** Do not use `<details>`
  for this: a closed `<details>` cannot be reliably forced open for printing.
  Render the excerpt always and toggle with `hidden` / `print:block`.
- **Every timeline carries the disclaimer** that categorisations are the
  author's analysis, not official characterisations.
- **Export respects the current filter state** so a filtered view can be pasted
  into a document with its provenance intact.

---

## 5. Publishing and privacy

Timelines are working research documents and start **unlisted**:

- no link from `site-nav.tsx` or `site-footer.tsx`
- omitted from `sitemap.ts`'s `staticRoutes`
- `robots: { index: false, follow: false }` in the page's `metadata`

Do **not** add the path to `robots.ts` — a `disallow` entry publishes the URL
in `robots.txt`, which is the opposite of unlisting it.

Treat the URL itself as the access control: anyone given the link can read the
page. When a timeline is ready to be public, add it to `sitemap.ts` and drop the
`robots` metadata in the same change.
