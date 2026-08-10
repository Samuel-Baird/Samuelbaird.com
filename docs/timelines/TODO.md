# Timeline backlog

Working list for the source-timeline project. See
[`CONSTRUCTING.md`](./CONSTRUCTING.md) for how a new timeline is built and
[`SOURCING.md`](./SOURCING.md) for where material comes from.

---

## Planned timelines

### The Family: A Proclamation to the World
Break the 1995 proclamation into its constituent claims and trace each
backwards and forwards independently, since they have quite different
pedigrees and quite different afterlives.

Suggested axes:
- **Heavenly Parents** — literal parentage vs. stated mechanism; how the
  proclamation's phrasing compares with 1909 ("begotten and born") and 1916
  ("literal Parent")
- **Eternal gender** — "gender is an essential characteristic of individual
  premortal, mortal, and eternal identity"; what "gender" meant in 1995 usage,
  and the 2019–21 handbook and style-guide shifts around sex vs. gender
- **Procreative power reserved to marriage** — continuity with earlier
  teaching, and its relationship to the eternal-increase material
- **Divine design of family roles** — "preside", "nurture", "equal partners";
  the internal tension is the interesting part
- **Drafting history and status** — read in a Relief Society meeting rather
  than presented for common consent; how its authority has been described since
  (compare the "not a revelation" characterisations with later citation as one)

Overlaps the eternal-increase timeline at the Heavenly Parents axis; link the
shared entries via `citesId` rather than duplicating them.

### "Doctrine" — how leaders have defined and used the term
A meta-timeline: not what was taught, but what counted as teaching.

Suggested axes:
- **Definitional statements** — explicit attempts to say what doctrine *is*
  (the 2007 Newsroom "Approaching Mormon Doctrine" statement is a hinge)
- **Sources of authority** — standard works, official declarations, unanimous
  First Presidency and Twelve statements, General Conference, manuals
- **Speaking as a man** — the distinction between a leader's opinion and
  doctrine, and who is entitled to draw it
- **Retirement mechanisms** — how a former teaching stops being doctrine
  (Kimball's 1976 Adam–God repudiation is the clearest worked example)
- **Correlation** — the institutional apparatus and its effect on what
  circulates

This one is unusually well suited to
[pulpit.restorationcommons.org](https://pulpit.restorationcommons.org/time/):
the frequency of "doctrine" and its qualifiers over the Conference corpus is
itself evidence.

### Baptismal regeneration
Whether baptism effects remission, and what the ordinance is understood to *do*.

Suggested axes:
- **Efficacy** — remission at baptism vs. baptism as witness of a remission
  already received
- **Necessity** — for salvation, for exaltation, for Church membership
- **Agent and authority** — priesthood requirement, rebaptism practice
- **Infant baptism** — Moroni 8 and its polemical context
- **Rebaptism** — the 19th-century practice for renewal, healing, and
  reconsecration, and its disappearance (a good `RETREAT-REFRAME` case)
- **Comparative** — where the Latter-day Saint position sits relative to the
  Protestant/Catholic sacramental debate the term "baptismal regeneration"
  comes from

---

## Eternal increase timeline — open items

### Placeholders to transcribe
Bracketed excerpts currently on the page, each needing the original read:

- `fp-repudiation-1865` — exact wording of the First Presidency/Twelve
  disavowal of *The Seer*
- `bh-roberts-tripartite` — the intelligence → spirit → body passage from
  *The Seventy's Course in Theology* (bhroberts.org)
- `fp-1925` — whether "begotten and born of heavenly parents" survives the
  condensation; the URL still points at the 1909 reprint and must be replaced
- `mcconkie-mormon-doctrine` — "God of Gods" / "Eternal Progression" entries,
  2nd ed.
- `mcconkie-heresies-1980` — the BYU fireside text
- `ensign-2002-origin-of-man` — confirm the reprint is complete and unabridged
- `snow-couplet-q4` — the 1840 origin narrative in Snow's own words
- `seminary-2014` / `cfm-2025` — **the highest-value pair.** Same scripture
  block eleven years apart; the exact lesson text on both sides is the
  strongest original contribution the timeline has.

### Unresolved analytical questions

- **`FATHER-ALWAYS-GOD` has zero sources.** The counter-position exists as a
  category with nothing in it. Either the denial genuinely is not made in these
  terms — itself a finding worth stating — or it exists and has not been found.
  Look in the same places the `DIVINE-PROGRESSION` denials came from
  (Joseph Fielding Smith, McConkie, mid-century institute manuals), and in
  discussions of creedal vs. Latter-day Saint conceptions of God.
- **`fp-1909-q2` tag.** Now `FORWARD-EUPHEMISM`. The excerpt as transcribed
  runs forward (man evolving into a God); confirm the *Improvement Era* wording
  and move it to `FATHER-MORTAL-EXPERIENCE` if it contains a backward clause.
- **`js-1842-discourse` provenance.** Transcribed from a Joseph Smith Papers
  footnote to the Bullock King Follett report, not read off the discourse page.
  Confirm the reporter and document ID; the hearsay grade of `C` depends on it.
  This entry currently carries the earliest Father-referent backward-explicit
  claim in the dataset, so it is load-bearing.
- **`by-chain` caution.** Confirm the *Journal of Discourses* citation for the
  "origin of the Gods" caution and the chapter in the 1997 Brigham Young manual
  that reprints it.
- **`oaks-2019`** — verify the talk and exact wording.
- **`young-father-mother-1862` title** reads as an inversion of what the quote
  says. The tagging is right; the headline is ambiguous standing alone.

### Sources still to chase

- Joseph F. Smith, *Gospel Doctrine*, on spirit birth (early 1900s)
- Hugh B. Brown / David O. McKay-era Conference uses of "eternal increase"
- *Encyclopedia of Mormonism* (1992): "God the Father", "Spirit Body",
  "Eternal Progression" — a semi-official 1990s snapshot
- Blake Ostler, "The Idea of Pre-existence in the Development of Mormon
  Thought", *Dialogue* 15.1 (1982) — the standard tripartite/viviparous taxonomy
- Charley Harrell, *"This Is My Doctrine"* (2011), chapter on theogony
- The fuller-transcript question on the 1997 *Time* interview

---

## Platform work

- **Extract the shared timeline engine.** `timeline-graph.tsx`, the filter
  logic, and the entry card are all generic over the schema; the second
  timeline should import them rather than copy the folder. Worth doing *when*
  the second timeline exists, not before — one instance is not yet a pattern.
- **Move `implied` onto the category pair** so a quote can mark one category
  implied and another stated (see [`SCHEMA.md`](./SCHEMA.md)).
- **Timeline index page** once there is more than one, listing them with their
  question and source count. Unlisted like the timelines themselves.
- **Cross-timeline citation.** The Family Proclamation and eternal-increase
  timelines share entries; decide whether `citesId` can cross timeline
  boundaries or whether shared sources move to a common file.
- **Graph refinements** — optional density/heat mode for large datasets. The
  colour key shipped: `timeline-graph.tsx` now draws one below the axis, keyed
  to the swimlanes rather than to all fifteen categories, so it stays legible
  however many categories are in view.

## From the August 2026 citation-graph audit (decisions for the maintainer)

- **sourceType flips recommended, not applied:** `doxey-eternal-marriage-1969`
  → citation (its own notes say the lesson is built on quoted authorities;
  counterweight: flipping rolls a 1969 Relief Society attestation out of the
  collapse view). `ttf-2004` and `eternal-family-2022` → citation, both
  blocked on missing originals (`dc-131`; the 1843 Manuscript History
  statement) — do not repoint at dc-132 as a substitute. `seminary-2025`'s
  existing dc-132 target has the same latent mis-aim (the lesson is on 131).
- **Citation→citation edges are currently impossible by invariant** — all 75
  edges point at originals, and the collapse view drops citation→citation
  rollups silently. Two real quotations are withheld because of it
  (`emsm-2003` → fp-1925, `seminary-2014` → mcconkie-mormon-doctrine). If the
  invariant should bend, bend it deliberately in the explorer, not via a data
  patch.
- **A `dby` node?** Three entries route text through the *Discourses of
  Brigham Young* compilation (doxey-1969, tpby-1997, young-father-mother-1862)
  with no entry making that intermediary visible.
- Full rationales: `graph-patches.json` in the research workspace archive.
