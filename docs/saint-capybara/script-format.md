# Saint Capybara — script format

This is the exact contract between `script/beats.yaml` (the single source
of truth, hand-edited YAML) and everything downstream: `tools/capy/beats.py`
(schema/validation/durations), `tools/capy_check_sources.py`,
`tools/capy_check_brand.py`, `tools/capy_storyboard.py` (which also renders
`script/script.md`, the human-reviewable document for Gate A), and
`tools/capy_render.py` (not built yet — post-Gate-A).

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
hook: "He said WHAT about Adam?"     # chip over the stage, first 3s
summary: "..."                        # for the description (Step 7, post-Gate-A)
format: { width: 1080, height: 1920, fps: 30, min_seconds: 60, max_seconds: 180 }
voice: { name: am_michael, speed: 0.95 }
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
narration, `q01` card, `e01` evidence, `ch01` chart) and `kind`, one of:
`clip | narration | card | evidence | chart | outro`.

```yaml
- { id: c01, kind: clip, start: 12.4, end: 21.0, speed: 1.0, speaker: "Source video", captions: source, pose: listening }

- id: n01
  kind: narration
  text: "That quote is real. It comes from the Journal of Discourses, volume one."
  pose: reading_source            # explicit pose, OR:
  function: evidence              # rhetorical function -> resolved via FUNCTION_TO_POSE
  stage: freeze                   # freeze | blank
  evidence: { image: images/jd1-p50.png, credit: "Journal of Discourses 1:50 (1852)", crop: [120,340,900,700], placement: panel }
  highlight: [real]
  sources: [jd-1-50]
  opinion: false

- id: q01
  kind: card                      # narration + quote card on the stage
  text: "Here is the full sentence."
  pose: explaining_quote
  card: { quote: "...", attribution: "Brigham Young, Journal of Discourses 1:50", source: jd-1-50 }
  sources: [jd-1-50]

- { id: e01, kind: evidence, text: "...", pose: pointing, evidence: { image: images/x.png, credit: "...", placement: stage }, sources: [x] }

- { id: ch01, kind: chart, text: "...", pose: teaching, chart: { type: bar, title: "...", data: [["1850s", 4]], credit: "..." }, sources: [x] }
```

Field notes:
- `pose` vs `function`: name a literal pose when the beat needs something
  specific; otherwise set `function` and let `FUNCTION_TO_POSE` (see
  `brand.md` sec 5) pick the default, skipping any pose in
  `SENSITIVE_FORBIDDEN` when `sensitive: true`.
- `sources: [id, ...]` must resolve against `research/sources.yaml`.
  Every factual beat needs at least one, unless `opinion: true`.
- `stage: freeze | blank` — what the stage shows on a narration beat that
  isn't itself an evidence/card/chart beat (freeze = last clip frame,
  dimmed 45%; blank = parchment background).
- `evidence.placement: panel | stage` — `panel` keeps Saint Capybara on
  screen with the receipt beside him in the character+panel band; `stage`
  promotes the receipt to the full stage (use when the document needs to
  actually be read).
- `highlight: [word, ...]` — caption keyword(s) to color per
  `theme.yaml: captions.highlight_color`; never a loaded/charged word.

## The mandatory sign-of-the-cross outro (fixed, not authored per-video)

**This is a structural rule of the Saint Capybara type, not a per-video
creative choice like Gate B decisions are.** Every video ends on exactly
this four-beat sequence, automatically appended by
`capy.beats.load_beats()` (which calls `ensure_mandatory_outro()`) if a
`beats.yaml` doesn't already end with it — you do not need to hand-write
it, and `capy_check_sources.py` hard-errors if it's missing or altered:

```yaml
  - { id: outro-01, kind: outro, pose: sign-father,      text: "In the name of the Father," }
  - { id: outro-02, kind: outro, pose: sign-son,          text: "and of the Son," }
  - { id: outro-03, kind: outro, pose: sign-holy,         text: "and of the Holy Ghost," }
  - { id: outro-04, kind: outro, pose: sign-spirit-amen,  text: "Amen." }
```

The four poses and their order are fixed. Wording may be adjusted slightly
per-project for natural TTS phrasing (e.g. splitting differently around a
comma) but the overall line and the one-pose-per-clause structure must not
change — `capy.beats.has_outro_sequence()` checks pose+kind+order, not
verbatim text, but a script editor should not rewrite these beats' meaning.
`kind: outro` durations use TTS length with a 1.2s floor (see
`capy/beats.py: OUTRO_MIN_SECONDS`).

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

- Hook: 0-5s, claim visible on screen by 3s.
- Clip: 5-25s.
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
- Source clip time totals ≤30% of the video's total runtime.
- Source title/creator visible on screen at least once (a caption or a
  label chip), so the video is legibly a response to a specific source.

## Sprite selection defaults

See `brand.md` sec 5's `FUNCTION_TO_POSE` table. Defaults only — a literal
`pose:` always wins. Hold ≥3s + 0.15s/word on any evidence/image beat so a
phone viewer can actually read it (`capy.beats.estimate_hold_seconds`).

## Caption rules

Max 2 lines, ~34 characters per line, at most one highlighted keyword per
caption phrase group (a name, date, number, or key term — never a loaded
word). Must be legible on a phone without pausing. See
`capy/captions.py: group_phrases()` for the exact chunking algorithm.

## `script.md` layout and user-edit directives

`capy_storyboard.py` renders `script/script.md` from `beats.yaml` as a
numbered, human-readable walk-through: per beat, the id/kind, the pose
name, the narration text (or clip in/out + speaker), any citation text
that will appear on screen, and a blank "Notes" line. The user may write,
inline, one of these directives against a beat and return the file:

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
message, so the message can link a readable GitHub URL instead of only a
local file path — see `docs/pipeline.md` §1 step 4a for why (a standing
user preference, not specific to this video type). Confirm the repo
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
