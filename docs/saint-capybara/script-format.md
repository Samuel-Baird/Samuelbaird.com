# Saint Capybara — script format

This is the exact contract between `script/beats.yaml` (the single source
of truth, hand-edited YAML) and everything downstream: `tools/capy/beats.py`
(schema/validation/durations), `tools/capy_check_sources.py`,
`tools/capy_check_brand.py`, `tools/capy_storyboard.py` (renders
`script/script.md`, the human-reviewable document for Gate A), and, once
approved, the post-Gate-A build tools — `tools/capy_tts.py`,
`tools/capy_beat_plates.py`, `tools/capy_caption_cards.py`,
`tools/capy_render_beat_clips.py` — documented end to end in
`docs/saint-capybara/hybrid-resolve-pipeline.md`.

## Files

```
script/
  beats.yaml           the single source of truth (hand-edited)
  script.md            rendered FROM beats.yaml for human review (Gate A)
  pronunciations.yaml  per-project pronunciation overrides/additions
```

`script.md` is generated, never hand-edited directly for content — the user
edits it with lightweight directives (see "User edit directives" below) and
those are read back into `beats.yaml`; anything else they write is a note
the agent must read and act on by asking or by editing `beats.yaml`
directly, but never by silently rewriting the user's own words.

## Top-level fields

```yaml
version: 1
slug: adam-god-claim
title: "Did Brigham Young teach Adam was God?"
hook: "He said WHAT about Adam?"     # title/description only (2026-09-09) -- never rendered on screen
summary: "..."                        # for the description (Step 7, post-Gate-A)
format: { width: 1080, height: 1920, fps: 30, min_seconds: 60, max_seconds: 180 }
voice: { name: am_michael, speed: 0.95 }   # host voice
voices:                                     # article-mode `excerpt` beats only, see below
  quote_male: { name: am_michael, speed: 1.0 }
  quote_female: { name: af_heart, speed: 1.0 }
  quote_default: quote_male
sensitive: false
music: null
tags: [ldshistory]
beats: [ ... ]
```

- `sensitive: true` forbids the `amused`/`happy` poses on every beat in
  this video (see `capy/poses.py: SENSITIVE_FORBIDDEN`) and triggers the
  sensitive-topic handling rules in `research-protocol.md`.
- `music` stays `null` in v1 — no music bed for this type.

## Beat fields (mirrors `capy/beats.py` exactly)

Every beat has `id` (unique, short, prefixed by kind: `c01` clip, `n01`
narration, `q01` card, `e01` evidence, `ch01` chart, `x01` excerpt) and
`kind`, one of: `clip | narration | card | evidence | chart | excerpt |
outro`. Each kind renders in one of three frame modes (`brand.md` sec 8)
— CLIP (`clip`), HOST (`narration`, `outro`), CARD (`card`, `evidence`,
`chart`, `excerpt`) — chosen automatically by kind, not authored per-beat.

```yaml
- { id: c01, kind: clip, start: 12.4, end: 21.0, speed: 1.0, speaker: "Source video", captions: source, pose: listening }

- id: n01
  kind: narration
  text: "That quote is real. It comes from the Journal of Discourses, volume one."
  pose: reading_source            # explicit pose, OR:
  function: evidence              # rhetorical function -> resolved via FUNCTION_TO_POSE
  stage: freeze                   # freeze | blank -- video-mode only, see field notes
  evidence: { image: images/jd1-p50.png, credit: "Journal of Discourses 1:50 (1852)", crop: [120,340,900,700] }
  highlight: [real]
  sources: [jd-1-50]
  opinion: false

- id: q01
  kind: card                      # narration + quote card (CARD mode)
  text: "Here is the full sentence."
  pose: explaining_quote
  card: { quote: "...", attribution: "Brigham Young, Journal of Discourses 1:50", source: jd-1-50 }
  sources: [jd-1-50]

- { id: e01, kind: evidence, text: "...", pose: pointing, evidence: { image: images/x.png, credit: "..." }, sources: [x] }

- { id: ch01, kind: chart, text: "...", pose: teaching, chart: { type: bar, title: "...", data: [["1850s", 4]], credit: "..." }, sources: [x] }

- id: x01                          # article/text-source mode only, see "Excerpt fairness" below
  kind: excerpt
  text: "The church's response, she wrote, was [...] a pattern critics have long described."
  para: 12                        # int, or [12, 13] across one paragraph boundary
  pose: reading
  voice: quote_female             # a `voices:` role, or an inline {name, speed} -- see the top-level voices: block
```

Field notes:
- `pose` vs `function`: name a literal pose when the beat needs something
  specific; otherwise set `function` and let `FUNCTION_TO_POSE` (see
  `brand.md` sec 5) pick the default, skipping any pose in
  `SENSITIVE_FORBIDDEN` when `sensitive: true`.
- `sources: [id, ...]` must resolve against `research/sources.yaml`.
  Every factual beat needs at least one, unless `opinion: true`.
  (`excerpt` beats don't take `sources:` — the quoted source is implied
  and validated against `source/source.md` instead, see below.)
- `stage: freeze | blank` — what a HOST-mode beat's background shows
  (freeze = the last clip's final frame, full-bleed, blurred and dimmed
  55%; blank = parchment + vignette). `freeze` is video-mode only — it is
  a lint error on any beat with no preceding `clip` beat (an article
  project has none, so its narration beats should omit `stage:` or use
  `blank`).
- `evidence.placement:` is deprecated (no-op, info-level lint) — every
  `evidence` beat now renders in CARD mode; there is no longer a separate
  "panel beside the sprite" slot to promote away from.
- `highlight: [word, ...]` — caption keyword(s) to color per
  `theme.yaml: captions.highlight_color`; never a loaded/charged word.
  Forbidden on `excerpt` beats (coloring the source's own words
  editorializes).

## The mandatory sign-of-the-cross outro (fixed, not authored per-video)

**This is a structural rule of the Saint Capybara type, not a per-video
creative choice like Gate B decisions are.** Every video ends on exactly
this five-beat sequence, automatically appended by
`capy.beats.load_beats()` (which calls `ensure_mandatory_outro()`) if a
`beats.yaml` doesn't already end with it — you do not need to hand-write
it, and `capy_check_sources.py` hard-errors if it's missing or altered:

```yaml
  - { id: outro-01, kind: outro, pose: sign-father,      text: "In the name of the Father," }
  - { id: outro-02, kind: outro, pose: sign-son,          text: "and of the Son," }
  - { id: outro-03, kind: outro, pose: sign-holy,         text: "and of the Holy" }
  - { id: outro-04, kind: outro, pose: sign-spirit-amen,  text: "Spirit," }
  - { id: outro-05, kind: outro, pose: prayerful,         text: "Amen." }
```

**Locked wording is "Holy Spirit," not "Holy Ghost"** (corrected
2026-09-09 — a real wording fix, not a style preference; "Holy Ghost" was
wrong and must not be reused anywhere in this brand). **"Holy" and
"Spirit" are two separate beats/poses**, not one — `sign-holy` on "Holy",
a quick cut to `sign-spirit-amen` on "Spirit" (both are short single-word
beats so the cut reads as fast by construction, no extra timing tuning
needed), then **"Amen" is its own fifth beat on the ordinary `prayerful`
pose** (a normal, calm prayer posture — not another sign-of-the-cross
gesture; the `sign-spirit-amen` pose's name is a filename leftover from
the old 4-beat wording and is now on the "Spirit" beat only, "Amen" no
longer shares it). The five poses and their order are fixed. Wording may
be adjusted slightly per-project for natural TTS phrasing (e.g. splitting
differently around a comma) but the overall line and the
one-pose-per-clause structure must not change —
`capy.beats.has_outro_sequence()` checks pose+kind+order, not verbatim
text, but a script editor should not rewrite these beats' meaning.
`kind: outro` durations use TTS length with a 1.2s floor (see
`capy/beats.py: OUTRO_MIN_SECONDS`).

**Rendered once, not per-video.** Because the wording (and therefore the
plates/captions) of these five beats never changes, they are rendered
once per (voice, speed) and cached — see
`docs/saint-capybara/hybrid-resolve-pipeline.md` "The shared outro
cache". This is invisible to script-writing: `beats.yaml` still carries
these five beats exactly as shown, `capy_storyboard.py` still previews
them at Gate A, and `capy_check_sources.py` still errors if they're
missing or malformed. A *different*, per-project beat right before this
sequence (the "outro-lead," e.g. `n05` with `pose: encouraging`) is
ordinary hand-written narration and is never part of the cache.

**Any change to the locked voice or its speed invalidates the cache** (it's
keyed on `(voice, speed, theme)`) — run `tools/capy_outro.py --build
--force` after changing `capy.beats.DEFAULT_VOICE`, per `brand.md` sec 6.

## Five recurring response formats

Most response-format videos combine 2-4 of these beat groups (never force
all five into one video):

1. **"Is this true?"** — clip beat of the claim, then a narration/evidence
   beat citing a primary source that confirms or corrects the quote.
2. **"What the source actually says"** — card beat with the full
   quotation in context (a `card` kind quoting more than the critic did).
3. **"Does the Church teach this?"** — narration beat distinguishing
   scripture / official statement / current handbook-practice / leader
   teaching / older historical belief / individual speculation (see
   `research-protocol.md`'s doctrine-vs-opinion tiers) — never collapse
   these into one undifferentiated "the Church teaches."
4. **"Historical context"** — narration/evidence beat placing the claim in
   the century/decade it belongs to; no retroactive vocabulary.
5. **"Same standard?"** — a symmetry/consistency check against how the
   same kind of claim would be judged elsewhere. Never the majority of a
   video's runtime — it's a supporting move, not the main argument.

## Duration budget

- Hook: title/description text only (never on screen — see the
  top-level `hook:` field note above); no on-screen time budget.
- Clip / excerpt: 5-25s.
- Response: 25-150s across 2-4 evidence beats.
- Close (pre-outro): 5-10s.
- Outro (fixed, see above): typically ~4-6s total across the 4 beats.
- Overall: 60-180s (`format.min_seconds`/`max_seconds`), enforced by
  `capy.beats.check_duration_budget()` — hard error normally, downgraded
  to a warning only when a tool is run with `--draft`.
- Target ~145 words per minute (`capy.beats.ESTIMATE_WORDS_PER_SECOND`) —
  use this to budget narration word counts before TTS exists.
- **If a topic doesn't fit in 180s while doing it justice, split into two
  slugs rather than compress.** Do not shorten evidence coverage just to
  hit the ceiling.

## Closing conventions (2026-09-08)

- **Don't add a closing beat that generically re-validates critics** (e.g.
  "some criticism is legitimate, worth sitting with") once the video has
  already substantively addressed and re-sourced the specific claim in
  question — the response itself is the demonstration that the criticism
  had merit; restating that as a separate meta-point is redundant, not
  additional charity. This doesn't change the standing rule against
  polemics/ad hominem (`brand.md` sec 2) — it's specifically about not
  *closing* on a validation that repeats what the video already showed.
  A framing beat that critiques response *quality* (e.g. noting a
  question wasn't actually answered) is a different thing and is fine.
- **The outro-lead narration (the beat right before the mandatory
  sign-of-the-cross sequence) should not reference "sources are in the
  description."** State the closing line plainly; don't call out where
  citations live. (The actual sources still belong in the description
  text itself, per `research-protocol.md` — this is only about not
  narrating that fact out loud.)

## One-argument rule

Each response beat group should make one argument, not stack three
half-finished ones. If a claim has two independent problems (e.g. "the
quote is misattributed" AND "even if attributed correctly it's taken out
of context"), give each its own beat group in sequence, not a single
beat trying to do both.

## Clip fairness

- Use the critic's own words; keep qualifiers ("I think," "it seems") —
  never strip hedges to make a claim sound more confident than it was.
- One continuous span per clip beat; never splice or reorder within a
  clip beat.
- ≤20s continuous per clip beat (warning above that in `capy.beats.validate`).
- Source clip time totals ≤30% of the video's total runtime (enforced by
  `capy_check_sources.py`, together with any `excerpt` beats — see below).
- **Source title/creator lives in the video description, not on
  screen** (changed 2026-09-09 — the v1 "Source video" label chip is
  removed as part of the layout redesign, `brand.md` sec 8). The
  original creator's clip is still shown verbatim on screen; only the
  attribution chip moved off-frame.

## Excerpt fairness (article/text-source mode)

The `excerpt` beat is the article-mode analog of a `clip` beat: the
source's own words, quoted verbatim. See `docs/types/saint-capybara.md`
and `docs/saint-capybara/research-protocol.md` for the full article-mode
workflow (ingest, paragraph-anchored claims triage); this section is
just the fairness rules `capy_check_sources.py` enforces on `excerpt`
beats specifically:

- Verbatim, including hedges — same rule as clips.
- One anchored span per excerpt beat (`para:`, a single paragraph number
  or a `[a, b]` pair across one boundary); never combine non-adjacent
  paragraphs into one excerpt.
- `[...]` marks any internal omission and is shown on the card exactly
  where it occurs — never at the very start or end of the excerpt (trim
  the beat to the words actually quoted instead).
- ≤60 words per excerpt (warning above that; ≤100 is a hard error).
- Excerpt time totals, combined with any `clip` beats, ≤30% of the
  video's runtime.
- Publication/headline/date on screen at least once — automatic via the
  excerpt card's attribution line (`capy.source.attribution_line`); the
  byline is deliberately omitted from that line by default (it goes in
  the description) unless the beat sets `cite_byline: true`.
- The excerpt beat precedes the response beats it's answering, the same
  steelman-first ordering a clip beat follows.

## Sprite selection defaults

See `brand.md` sec 5's `FUNCTION_TO_POSE` table. Defaults only — a literal
`pose:` always wins. Hold ≥3s + 0.15s/word on any evidence/image beat so a
phone viewer can actually read it (`capy.beats.estimate_hold_seconds`).

**Pose changes every 10-20s (2026-09-09 user direction — "the capybara
needs to move more").** The current renderer draws one static sprite pose
per beat (no intra-beat pose animation), so the only way to satisfy this
is authoring: **no single beat's estimated duration should run past ~20s
without a pose change.** A narration point that would naturally run
25-40s straight through (e.g. laying out context + evidence + a
follow-up point) should be split into 2-3 separate beats at its natural
clause/sentence breaks, each with its own — still function-appropriate,
still `SENSITIVE_FORBIDDEN`-respecting — pose, rather than one beat
carrying a long, visually static block. This is a pacing/authoring rule,
not a lint-enforced one (there's no `capy_check_sources.py` check for it
yet); watch for it manually against each beat's estimated duration in
`script.md` before Gate A.

## Caption rules

Max 2 lines, wrapped by **measured pixel width** against a 960px budget
(`capy.text.fit_text` — never a character-count guess; the earlier
~34-char estimate is what produced a shipped caption clipped off both
frame edges), shrinking the font size to a floor before ever allowing a
third line. At most one highlighted keyword per caption phrase group (a
name, date, number, or key term — never a loaded word, and never on an
`excerpt` beat, whose `highlight:` is forbidden). Must be legible on a
phone without pausing. See `capy/captions.py: group_phrases()` for the
chunking algorithm and `capy/text.py: fit_text()` for the wrap/shrink.

## `script.md` layout and user-edit directives

`capy_storyboard.py` renders `script/script.md` from `beats.yaml` as a
numbered, human-readable walk-through. **Per-beat field order (locked
2026-09-09 — user direction, "so I can better understand what Saint
Capybara is responding to in review"):**

```
## NN. `beat-id` (kind, ~Ns)
Original Video Transcript:
Pose:
Narration:
Sources:
Notes:
```

- **Original Video Transcript** comes first, before Pose. For a `clip`
  beat, it's the verbatim transcript text spanning that beat's
  `start`–`end` (pulled from `transcripts/source.json`, not just the
  timestamps — the reviewer should never have to look the words up
  separately). For a response beat (`narration`/`card`/`evidence`/etc.),
  it repeats the transcript text of the most recent preceding `clip`
  beat, so the response is never separated from the claim it's answering
  by a page-scroll — blank/`(none yet)` only for beats before the video's
  first clip. Video-source projects only; article-source projects use
  the per-`excerpt`-beat `¶N` anchor into `source/source.md` instead,
  which already serves the same purpose.
- **Pose** — the resolved pose name.
- **Narration** — the beat's own text (or `Clip:`/`Card quote:` etc. for
  kinds that don't carry plain narration).
- **Sources** — the `sources:` list, if any.
- **Notes** — always present, always blank, for the user to write into.

The user may write, inline, one of these directives against a beat and
return the file:

- `DROP` — remove this beat entirely.
- `SPLIT` — split this beat into two at a marked point (the user indicates
  where in their edited text).
- `MOVE AFTER Bxx` — reorder this beat to follow beat `Bxx`.
- Any other free-text note — read it, and either make the requested change
  to `beats.yaml` or ask a clarifying question. **Never silently rewrite
  the user's own narration text** — if their edit changes meaning in a way
  that affects sourcing/lint (e.g. removes a hedge, strengthens a claim),
  flag it rather than accepting it silently.

Only the fields governed by directives above are ever changed automatically
from a `script.md` edit; anything else the user writes gets a response, not
a silent edit.

## Gate A — the fixed wording

**This exact message (or a close paraphrase preserving every clause) is
what the agent sends when a project reaches Gate A. No TTS, no clip
cutting, and no rendering happen before the user replies with approval.**

Also push a copy of `script/script.md` to this repo under
`reviews/<slug>/script.md`, commit, and push before sending the Gate A
message, so the message can link a readable, **editable** GitHub URL
instead of only a local file path — see `docs/pipeline.md` §1 step 4a for
why (a standing user preference, not specific to this video type) and,
critically, **link the branch, not the commit SHA** (same section) so the
user can actually use GitHub's edit button on it. Confirm the repo
remote is still private first (`docs/saint-capybara/brand.md` §9-10).

> **Saint Capybara — script ready for review (Gate A)**
>
> `script/script.md` and `frames/storyboard.png` are ready for your review.
> This is a hard stop: **no narration audio will be recorded, no clips will
> be cut, and no video will be rendered until you approve this script.**
>
> Please review for: factual accuracy, tone, whether the response is fair
> to the source video, and any wording you want changed. Reply with your
> edits (see `script-format.md` for the `DROP`/`SPLIT`/`MOVE AFTER Bxx`
> directives, or just describe what you want changed in plain language),
> or reply "approved" to proceed to voice recording and rendering.
