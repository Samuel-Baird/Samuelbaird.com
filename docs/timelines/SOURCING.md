# Sourcing rules for timelines

How to find, evaluate, and cite sources for any timeline in this repo. Read
this before adding an entry. The companion documents are
[`CONSTRUCTING.md`](./CONSTRUCTING.md) (how a timeline is built and tagged) and
[`SCHEMA.md`](./SCHEMA.md) (the exact data contract).

---

## 1. The one hard rule

**Never cite `mrm.org` on the site.**

[mrm.org](https://mrm.org/) (Mormonism Research Ministry) is a **discovery aid
only**. It is useful for locating primary material — it quotes and footnotes
heavily — but it is an advocacy site with a stated position, and publishing it
as a citation would misrepresent this project as sharing that position.

Use it to *find* a source, then **go read the original and cite the original**.
If the original cannot be located, the entry does not get added.

This is enforced mechanically, not by memory: `parseSources()` in
`src/app/eternal-increase-timeline/schema.ts` rejects any entry whose `url` is
on `mrm.org`, and the build fails. Do not work around the guard — if a claim
only exists on mrm.org, that is a finding about the claim, not a licence to
cite the aid.

The same reasoning applies to any partisan secondary site used for discovery
in future, in either direction. Add it to the guard rather than relying on
discipline.

---

## 2. Approved source hosts

Cite these directly.

| Source | Use for | Notes |
|---|---|---|
| [churchofjesuschrist.org](https://www.churchofjesuschrist.org/?lang=eng) | Scripture, General Conference, manuals, magazines, Gospel Topics essays | The canonical host for anything currently correlated. Prefer it over reprints elsewhere. |
| [Joseph Smith Papers](https://www.josephsmithpapers.org/) | Nauvoo-era discourses and documents | Always prefer the individual scribal account over an amalgam. See §4. |
| [bhroberts.org/archive](https://bhroberts.org/archive) | B. H. Roberts's corpus | The origin of the tripartite framework and much early-20th-century systematics. |
| [pulpit.restorationcommons.org/time](https://pulpit.restorationcommons.org/time/) | Searchable General Conference corpus over time | Excellent for establishing *absence* — when a phrase stopped being used. See §5. |
| [scripturalmormonism.blogspot.com](https://scripturalmormonism.blogspot.com/) | Topical source gathering, often with full citations | Secondary. Treat like mrm.org for discovery purposes — verify and cite the original — but it may be cited directly when the analysis itself is the datum, labelled `never-official`. |
| [archive.org](https://archive.org/) | Out-of-print originals: *Journal of Discourses*, Conference Reports, *The Seer*, discontinued manuals | Link to the page scan, not the search result. |

**Preference order** when the same text exists in several places:

1. The original printing or manuscript (JSP scan, archive.org page scan)
2. The Church's own current hosting of it
3. A scholarly reproduction
4. Anything else

---

## 3. Hearsay grading

The grade describes **how directly the text traces to the speaker**, nothing
else. It is not a measure of importance, and it is independent of whether the
Church currently teaches the material.

| Grade | Meaning | Typical example |
|---|---|---|
| **A** | First-person text by the speaker, published under their direction | A First Presidency statement; a signed article |
| **B** | Contemporaneous notes by trained scribes, amalgamated | The King Follett Discourse |
| **C** | Contemporaneous secondhand report, including shorthand edited for publication | Most of the *Journal of Discourses* |
| **D** | Later recollection, years after the fact | Lorenzo Snow's c. 1901 account of an 1840 insight |
| **E** | Attributed via tertiary compilation with no traceable original | Folklore; orphaned quotations |

Two rules that are easy to get wrong:

- **The *Journal of Discourses* is C, not E.** Most of it derives from George
  Watt's contemporaneous shorthand, edited for publication and in the early
  years reviewed by the speaker's office. That is secondhand with an editing
  layer. Reserve **E** for genuinely orphaned attributions.
- **A posthumous compilation is not A.** If someone else assembled it from
  sermon reports after the speaker died, it is **B** at best, however official
  the imprint. Melvin J. Ballard's *Sermons and Missionary Services* is the
  standing example.

When a single source's quotes do not share a provenance, do not average them —
use `hearsayByQuote` to grade the individual excerpt. The Snow couplet is the
model: the couplet as published doctrine is **A**, while the story of its 1840
origin is **D**.

---

## 4. Multi-witness originals

Where a discourse survives in several independent reports, record each in
`witnesses` and **check the disputed wording against every account before
relying on it**. Amalgamated texts — *History of the Church*, *Teachings of the
Prophet Joseph Smith*, magazine reprints — silently smooth real divergence
between scribes.

This is not hypothetical. In the King Follett Discourse, the familiar line "the
same as all Gods have done before you" is attested by **Clayton alone**;
Bullock has the weaker "same as all have done" with no "Gods", and Richards and
Woodruff do not record the passage at all. A tag resting on that phrase is
resting on one witness, and the quote note must say so.

Cite the individual scribal account as the entry `url`. File the amalgam as a
separate `citation` entry if its republication is itself interesting.

---

## 5. Establishing absence

"This stopped being taught" is a claim about the whole corpus, and it needs
corpus-scale evidence rather than a failure to recall an example. Use the
searchable General Conference archive at
[pulpit.restorationcommons.org/time](https://pulpit.restorationcommons.org/time/)
to check a phrase's frequency over time, and say in the note what was searched
and how large the corpus was.

Absence claims should be stated as what was checked, not as fact:

> A sweep of ~11,600 General Conference talks returns one unambiguous pulpit
> affirmation of divine progression.

is honest. "Never taught after 1970" is not, unless the sweep actually
supports it.

---

## 6. Placeholders and verification

An entry may be added before its excerpt is transcribed, but it must be
honest about it:

- Put the intended content in **square brackets** in the `excerpt` field.
- Set `needsVerification: true`, which renders a ⚠ badge.
- Say in the `notes` what specifically needs checking and against which
  edition or printing.

Bracketed placeholders are visible to readers by design. Clear them by reading
the original — never by paraphrasing a secondary source into quotation marks.

Set `needsVerification` whenever any of these is true:

- the excerpt is a placeholder,
- the wording came from a footnote or quotation rather than the source itself,
- the citation (chapter, page, talk title) is inferred rather than confirmed,
- the source has multiple editions and you have not established which one you
  are quoting.

---

## 7. Quoting fairly

- Mark elision with `...` and never elide across a change of subject in a way
  that alters the sense.
- Keep enough of the sentence for the claim to stand on its own.
- Preserve original spelling and punctuation in manuscript sources, using
  `[square brackets]` for editorial expansion — the scribal accounts in
  `content/versions/` show the house style.
- If a quote's plainest reading in context differs from the reading that makes
  it interesting, say so in the note. Several entries do this, and it is the
  single most valuable thing the notes carry.
