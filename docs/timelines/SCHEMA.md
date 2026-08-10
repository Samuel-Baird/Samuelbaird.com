# Timeline data schema

The contract for a timeline's `sources.json`. The authority is the zod schema in
each timeline's `schema.ts` — this document explains the fields and the
reasoning. See [`SOURCING.md`](./SOURCING.md) for grading rules and
[`CONSTRUCTING.md`](./CONSTRUCTING.md) for the analytical model.

`sources.json` is an **array of source entries**. It is hand-edited and is the
only file that needs to change to add material.

---

## Source entry

```jsonc
{
  "id": "kfd-1844",
  "sourceType": "original",
  "citesId": ["sermon-grove-1844"],
  "date": "1844-04-07",
  "dateDisplay": "April 7, 1844",
  "datePrecision": "day",
  "title": "King Follett Discourse",
  "speaker": "Joseph Smith",
  "office": "President of the Church",
  "venue": "General Conference, Nauvoo",
  "url": "https://www.josephsmithpapers.org/...",
  "hearsay": "B",
  "hearsayByQuote": { "kfd-1844-q4": "D" },
  "correlationStatus": "historical-official",
  "referent": "father",
  "witnesses": [ /* … */ ],
  "quotes":    [ /* … */ ],
  "notes": "Source-level analysis.",
  "needsVerification": false
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | Stable, kebab-case, unique. Used as the DOM anchor and as the `citesId` target, so **renaming one breaks inbound links** — treat as permanent. |
| `sourceType` | `original` \| `citation` | yes | First attestation, or a later source quoting one. |
| `citesId` | string[] | for citations | Entry `id`s this source quotes. Every value must resolve or the build fails. An array because a source can cite several originals — the 2014 essay cites two. |
| `date` | `YYYY-MM-DD` | yes | Sort key only. Pad month/year precision with `-01` so string comparison sorts correctly. |
| `dateDisplay` | string | yes | What readers see. May be a range or a qualification: `"Sermon 1922; compilation published 1949"`. |
| `datePrecision` | `day` \| `month` \| `year` | yes | Records how much of `date` is real, since padding is invisible otherwise. |
| `title` | string | yes | |
| `speaker` | string | yes | Person or body. |
| `office` | string | yes | Office **at the time**, which is often the point. |
| `venue` | string | yes | Where it was said or published. |
| `url` | URL | yes | Prefer the original printing. Rejected if on a discovery-only host. |
| `hearsay` | `A`–`E` | yes | Source-level provenance grade. |
| `hearsayByQuote` | `{quoteId: grade}` | no | Per-quote override where provenance differs inside one source. Keys must name quotes on this entry. |
| `correlationStatus` | see below | yes | Whether the Church currently publishes it. |
| `referent` | `father` \| `son` \| `ambiguous` \| `n/a` | yes | Who the claim is about. Quotes may override. |
| `witnesses` | Witness[] | no | For multi-transcript originals. |
| `quotes` | Quote[] | yes, ≥1 | The evidence. |
| `notes` | string | yes | Source-level analysis: provenance, why a grade was chosen, what is still open. |
| `needsVerification` | boolean | no | Renders a ⚠ badge. See [`SOURCING.md`](./SOURCING.md) §6. |

### `correlationStatus`

An axis **independent of hearsay** — it records the Church's current
relationship to the text, not its provenance. A King Follett excerpt reprinted
in a 1971 *Ensign* is high-correlation despite B-tier hearsay.

| Value | Meaning |
|---|---|
| `current-correlated` | Currently published or hosted by the Church |
| `historical-official` | Was official; not currently republished |
| `discontinued` | Withdrawn or superseded (e.g. a manual out of print) |
| `never-official` | Never carried official standing (press interviews, commercial books) |

---

## Quote

```jsonc
{
  "quoteId": "kfd-1844-q1",
  "categories": ["FATHER-MORTAL-EXPERIENCE", "FATHER-BECAME-GOD"],
  "excerpt": "God himself was once as we are now, and is an exalted man...",
  "referent": "father",
  "implied": false,
  "stance": { "FATHER-MORTAL-EXPERIENCE": "affirms", "FATHER-BECAME-GOD": "affirms" },
  "note": "Per-quote analysis."
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `quoteId` | string | yes | Unique **across the whole file**, not just its entry. Convention: `<entryId>-q<n>`. |
| `categories` | CategoryId[] | yes | **May be empty** — a quote recorded as context for a neighbouring claim carries no categories and renders as `context`. |
| `excerpt` | string | yes | The quoted text. `[Square brackets]` mark a placeholder awaiting transcription. |
| `referent` | Referent | no | Overrides the entry's referent. Backward-direction quotes should always carry one. |
| `implied` | boolean | no | The categories are **read into** the quote rather than stated by it. Renders an "implied" marker. |
| `stance` | Record&lt;CategoryId, Stance&gt; | **yes, for claim categories** | `affirms` \| `hedges` \| `denies` — where the quote stands on the proposition behind each claim category it carries. See below. |
| `stanceNeedsReview` | boolean | no | The placement is not yet author-confirmed. Renders with a dashed ring; never hidden. |
| `note` | string | no | Why this excerpt is tagged as it is; where the plainest reading differs from the interesting one, say so here. |

### Stance

Stance answers *which way* a quote leans, which the category alone does not say.
It is judged against the written-out `proposition` of the category's **defining
subject** (`DEFINING_SUBJECT` in `schema.ts`, propositions in `SUBJECTS` in
`constants.ts`), never against the category name or the doctrine in general.
`hedges` covers euphemism, an explicit refusal to say, deliberate ambiguity, and
an affirmation withdrawn by its own qualification.

Twelve of the fifteen categories carry a stance. `RETREAT-REFRAME`,
`MANY-WORLDS` and `TRIPARTITE-FRAMEWORK` do not: the first describes an
operation on an earlier teaching, and the other two are explanatory frameworks,
so "affirming" them would say nothing about how settled a doctrine was.

**Subjects overlap on purpose.** A broad subject asks whether a whole position
was held; a narrow one asks after a single move inside it. "Was the Father once
a mortal man?" and "Is there a chain of Gods above the Father?" both read
`INFINITE-CHAIN`, and they should — the chain claim stops appearing after 1981
while the broad question still looks settled, which is exactly what the narrow
chart is for. Only the defining subject fixes what a recorded direction *means*;
another subject may read the same category only where its question takes that
direction the same way. Where it would not, that category needs its own stance
field rather than a second reading of this one.

Each subject also names its three bands in its own words (`bands` in
`SUBJECTS`). "Affirms" and "Denies" are accurate and say nothing; on the
Father's origin the same two bands are "Became God" and "Always God", which is
the actual disagreement.

Three build-time checks enforce it, all failing with the offending JSON path:

- every `stance` key must be a category **that quote actually carries**, and one
  that takes a stance at all;
- every stance-bearing category on a quote **must** have a stance — a missing
  one would not fail loudly, it would just drop the quote out of the certainty
  chart and quietly undercount a band;
- `stanceNeedsReview` requires a `stance` to review.

> **Known limitation.** `implied` is per-quote, so on a quote with several
> categories it marks all of them — and several quotes now carry two, so a
> quote with one category read-in and another stated outright is currently
> mismarked. Fixing it means moving the flag onto the category pair, at which
> point `stance` should move with it (see TODO).

---

## Witness

For discourses surviving in several independent reports. See
[`SOURCING.md`](./SOURCING.md) §4 — check disputed wording against every witness
before relying on it.

```jsonc
{
  "scribe": "William Clayton",
  "url": "https://www.josephsmithpapers.org/...",
  "note": "Contemporaneous longhand; sole witness to the \"all Gods\" wording."
}
```

`scribe` is required; `url` and `note` are optional.

---

## Integrity checks

Beyond field validation, `parseSources()` fails the build on:

| Check | Why |
|---|---|
| Unresolved `citesId` | The citation graph and collapse view would silently lose edges |
| Duplicate `id` | Anchors and citation targets become ambiguous |
| Duplicate `quoteId` | Quote anchors collide |
| `hearsayByQuote` key with no matching quote | A silently ineffective override — the misleading case, since the UI would show the unmodified grade |
| URL on a discovery-only host | See [`SOURCING.md`](./SOURCING.md) §1 |

Because parsing happens at module scope of a statically prerendered page, all of
these surface as **build failures naming the offending JSON path**, not as
runtime errors. To confirm the guard still works, corrupt a value deliberately,
run `npm run build`, and revert.

---

## Adding a source: checklist

1. Read the original; cite the original ([`SOURCING.md`](./SOURCING.md) §1–2).
2. Pick `sourceType`; wire `citesId` if it is a citation.
3. Grade `hearsay` by provenance — posthumous compilations are not `A`.
4. Split the material into quotes, one per distinct doctrinal move.
5. Tag each quote for **what it states** ([`CONSTRUCTING.md`](./CONSTRUCTING.md) §1).
6. Set `referent` on every backward-direction quote.
7. Write the `note`: why this grade, why this tag, what is still open.
8. Set `needsVerification` if anything is inferred or bracketed.
9. `npm run build` to confirm the data validates.
