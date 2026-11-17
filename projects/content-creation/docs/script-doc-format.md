# Script document format

The pre-production deliverable for response and solo-history videos:
`script\<slug>-script.docx`, built by `tools/build_script_docx.py`. Word
format (not PDF/markdown) so the user can edit it directly — delete a
marker to reject it, retype text, drag/reorder images — using Word's normal
editing, no special tooling required on their end.

## Header

A table at the top of the document:

| Field | Value |
|---|---|
| Slug | project slug |
| Type | response / solo-history |
| Sources | each source file, its duration, and its role (e.g. "external mic", "camera A") |
| Whisper model | model used for this transcript |
| Generated | date |

## Body

One paragraph per transcript beat (a beat is a sentence or short group of
sentences the flagging pass treated as a unit), in source order, each
prefixed with its source timestamp:

```
[03:41] Full text of the beat as transcribed...
```

### Flag markup

- **CUT** (confident — repeat take, false start, explicit self-correction):
  the flagged span is struck through and highlighted red, with a trailing
  inline note: `«CUT: repeated take, see 03:41–03:52»`. Default action if
  left alone: **excluded** from the build.
- **CHECK** (possible — pacing gap, swallowed-retake signal, near-duplicate
  phrasing): the flagged span is highlighted yellow (not struck through),
  with a trailing note: `«CHECK: 2.1s pause mid-sentence»`. Default action
  if left alone: **kept** — CHECK is a flag for the user's attention, not a
  proposed cut, since it's lower-confidence than CUT.

To accept a CUT (keep the cut), leave it as-is. To reject a CUT (keep the
footage), delete the strikethrough/highlight/note so the text reads as
plain, unmarked text — the ingest step (`pipeline.md` §2) treats unmarked
text as "keep." Same mechanism for CHECK: delete the highlight/note to mark
it as reviewed-and-fine; leave it to flag the concern (but note CHECK never
excludes footage on its own — it's advisory only, unlike CUT).

### Image and quote-card blocks

Placed inline at the beat where they belong, as a bordered block:

```
┌─────────────────────────────────────┐
│ [thumbnail, ~4in wide]               │
│ Caption: what the image shows        │
│ Source: <URL>   Licence: <licence>   │
│ On screen: ~25s                      │
└─────────────────────────────────────┘
```

Quote cards use the same block shape but show the rendered card image
itself (from `tools/make_quote_card.py`) rather than a source photo, so the
user is reviewing the actual on-screen result, not a placeholder.

## Trailing tables

- **Visual wish-list** — beats that need an image the automated search
  didn't find: beat timestamp, what's needed, why. The user fills these in
  by supplying files or approving a substitute before returning the doc.
- **Music pick** (solo-history only) — proposed track, source, licence,
  attribution text for the description.

## Ingest contract

`pipeline.md` §2 depends on this format staying stable: timestamps must
stay in `[mm:ss]` at the start of a paragraph, CUT/CHECK markers must use
Word's real strikethrough and highlight formatting (not just colored plain
text, so the ingest script can detect them programmatically), and image
blocks must keep their caption/source/licence lines in that order.
