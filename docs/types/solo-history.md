# Solo / history videos

Single presenter (one or two cameras) discussing history or doctrine, often
quoting sources. Leans into visuals: images while discussing history, quote
cards when quoting a source, a light music bed under narration. Runs the
full pre-production gate in `../pipeline.md` §1 before any timeline work.

## Image density

Target roughly one visual per topic beat — a new person, place, document, or
claim introduced in the narration — landing every 30-60 seconds rather than
constantly or only at document quotes. Camera-on-presenter is the default
between beats, not the fallback.

## Image sourcing (pre-production step)

1. Search public-domain / clearly-licensed sources first: Wikimedia Commons,
   Internet Archive, and any topic-relevant institutional archive (church
   history library, university special collections, etc. — check
   `docs/pipeline.md`-adjacent project notes for sources the user has used
   before on this topic).
2. For each beat needing a visual, either place a found image (with source
   URL and licence recorded) or add it to the script doc's visual wish-list
   for the user to supply. Never fabricate/generate an image to fill a gap,
   and never place an image without recording where it came from.
3. Source-document scans are especially valuable here and are often only in
   the user's possession — always check the wish-list rather than
   substituting a generic stand-in photo when a specific document is being
   quoted or discussed.

## Quote cards

Any time a specific source is quoted at length (a few sentences or more),
render a quote card per `../style-guide.md`'s single template — never a
per-video redesign. Short quotes (a few words, woven into the narration)
don't need a card. When quoting a specific named person, prefer showing a
photo of them (as an image beat, not a card) if one is available and
sourced.

## Music

Light, royalty-free background bed under the narration, ducked so it never
competes with speech, matched to the video's tone and pacing. Attribution
recorded in the script doc's trailing table (see `../script-doc-format.md`)
so it can go in the published description. This is a solo-history-only
default — not used for response or interview videos.

## Build

- Base track: presenter camera, cut only at blooper/retake points confirmed
  in the approved script (natural pacing otherwise — see
  `../style-guide.md` for the pause-trim threshold).
- Image/card track: stills placed per the approved script's beat list,
  duration capped against the next beat's record frame (see
  `../resolve-mcp-gotchas.md` on the overlap bug).
- Music track: single bed, volume-automated under narration.
- Bottom-left source credit burned into any image that needs one
  (`tools/burn_credit.py`), never a caption bar.

## QC

Frame-grab every image and card placement and read it at actual size —
catches auto-shrunk text that got too small and images placed with the
wrong crop.
