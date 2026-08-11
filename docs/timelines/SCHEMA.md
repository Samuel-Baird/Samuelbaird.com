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
  "bands": { "mortality": "probation", "divinity": "not-always-god" },
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
| `bands` | Record&lt;QuestionId, BandId&gt; | **yes, for every question raised** | What the quote answers, per question its categories raise. `not-addressed` where it turns out not to speak to one. See below. |
| `stanceNeedsReview` | boolean | no | The placement is not yet author-confirmed. Renders with a dashed ring; never hidden. |
| `note` | string | no | Why this excerpt is tagged as it is; where the plainest reading differs from the interesting one, say so here. |

### Questions and bands

A category says which questions a quote is *asked*; `bands` records what it
answers. Each question owns its own ordered scale, because they do not all have
two sides — see [`STANCE-TAXONOMY.md`](./STANCE-TAXONOMY.md) for every band and
its criteria.

Two consequences worth stating plainly:

- **Band values are only meaningful within their question.** `denies` means
  different things on different scales and `infinite` is meaningless on all but
  one, so a value that is legal somewhere is not thereby legal here.
- **`not-addressed` is an answer, not a gap.** A passage may raise a question by
  its tags and turn out not to speak to it — a mortality text that never touches
  the Father's divinity, most often. Recording that explicitly is what lets the
  build insist every raised question was decided.

Four build-time checks enforce it, all failing with the offending JSON path:

- an answer to a question the quote's categories never raise;
- a band the question does not define;
- a raised question left unanswered — a missing answer would not fail loudly,
  it would just drop the quote out of that chart and quietly undercount a band;
- `stanceNeedsReview` with nothing to review.

> **Known limitation.** `implied` is per-quote, so on a quote with several
> categories it marks all of them — and many quotes now carry two, so a quote
> with one category read-in and another stated outright is currently mismarked.
> Fixing it means moving the flag onto the category pair. `bands` is unaffected:
> it is keyed by question, not by category, so it does not need to move with it.

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
