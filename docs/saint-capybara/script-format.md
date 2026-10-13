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
length: short                         # short (default) | long -- see "Long form" below
# long_form_requested: "2026-10-09: 'make this one long form'"   # required when length: long
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
`kind`, one of: `clip | narration | card | evidence | chart | excerpt`.
Each kind renders in one of three frame modes (`brand.md` sec 8) — CLIP
(`clip`), HOST (`narration`), CARD (`card`, `evidence`, `chart`,
`excerpt`) — chosen automatically by kind, not authored per-beat.

```yaml
- { id: c01, kind: clip, start: 12.4, end: 21.0, speed: 1.0, speaker: "Source video", captions: source, pose: listening }
  # `pose:` on a clip beat should reflect what the clip is actually saying,
  # not default to `listening` on every beat -- see brand.md's
  # "clip beats should react to what the source clip is actually saying"
  # note. Use `listening` only for genuinely neutral stretches; otherwise
  # pick from the same full-emotion roster narration beats use
  # (thoughtful/concerned/skeptical/surprised/confused/disappointed/amused,
  # respecting `sensitive: true`).

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
- `stage: freeze | blank | image | video` — what a HOST-mode beat's
  background shows, all full-bleed with the same blur/dim treatment
  except `blank` (2026-09-09: `image`/`video` added — "some background
  images while he's talking" / "he can also be in front of the original
  video being reacted to," both user-requested):
  - `blank` — parchment + vignette (the default when `stage:` is omitted).
  - `freeze` — the last clip's final frame, blurred/dimmed 55%.
    Video-mode only — lint error on any beat with no preceding `clip`
    beat.
  - `image` — an arbitrary project image via `background: images/x.png`
    (project-relative), same blur/dim treatment as `freeze`. Use this for
    a historical painting, photo, map, or sketch behind the sprite while
    he talks — see "Use real images, not just quote cards" below. Lint
    error if `background:` is missing.
  - `video` — the source video keeps *playing* behind the sprite (not a
    frozen frame) — "capybara reacting in front of the video." Defaults
    to picking up where the most recent preceding `clip` beat left off
    (`background_start` inferred); set `background_start: <seconds>`
    explicitly to start from a different point in `source/source.mp4`.
    Loops if the beat's narration runs longer than the remaining
    footage. Video-mode only — lint error with no preceding `clip` beat
    and no explicit `background_start` (there's nothing to composite).
    Composited live by `capy_render_beat_clips.py` (ffmpeg), same
    mechanism as CLIP mode's full-bleed source video — `capy_beat_plates.py`
    renders a transparent plate for these beats, not a baked-in still.
- `evidence.placement:` is deprecated (no-op, info-level lint) — every
  `evidence` beat now renders in CARD mode; there is no longer a separate
  "panel beside the sprite" slot to promote away from.
- `highlight: [word, ...]` — caption keyword(s) to color per
  `theme.yaml: captions.highlight_color`; never a loaded/charged word.
  Forbidden on `excerpt` beats (coloring the source's own words
  editorializes).

## The closing beat: "...God bless." (not a fixed structural sequence)

**Retired 2026-09-09 — there is no more mandatory sign-of-the-cross
outro.** An earlier version of this doc specified a fixed five-beat
`kind: outro` sequence (sign-father/sign-son/sign-holy/sign-spirit-amen/
prayerful poses, auto-appended by `capy.beats.load_beats()`, rendered
once and cached by `tools/capy_outro.py`). All of that — the `outro`
beat kind, the auto-append behavior, the shared cache — has been removed
from the codebase, not just deprecated. See git history if it's ever
needed for reference; don't reintroduce it without new, explicit user
direction.

**The rule now: every video's closing beat is an ordinary `narration`
beat whose text ends on "...God bless."** — hand-authored like any other
beat, no special kind, no shared/cached asset. Pick whatever pose fits
the moment (`encouraging` is a reasonable default). `capy_check_sources.py`
hard-errors if the last beat in `beats.yaml` doesn't end that way.

```yaml
  - id: n99
    kind: narration
    text: "REPLACE: closing line. God bless."
    function: closing
    pose: encouraging
    opinion: true
```

See "Closing conventions" below for what the closing beat should (and
shouldn't) say beyond that.

## Five recurring response formats

See also `docs/saint-capybara/apologetics-playbook.md`'s six-step
response structure (steelman → name the assumption → test whether it's
actually necessary → give the LDS position → positive evidence → compare
explanatory power) — these five beat-group *shapes* and that six-step
argument *arc* aren't competing systems; a beat group below is usually
where one or two of the six steps live.

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
- Close (the "...God bless." beat): 5-10s.
- Overall: 60-180s for a short; 180-1200s for long form (`length: long`,
  see "Long form" below) (`format.min_seconds`/`max_seconds`), enforced by
  `capy.beats.check_duration_budget()` — hard error normally, downgraded
  to a warning only when a tool is run with `--draft`.
- Target ~145 words per minute (`capy.beats.ESTIMATE_WORDS_PER_SECOND`) —
  use this to budget narration word counts before TTS exists.
- **If a topic doesn't fit in 180s while doing it justice, split into two
  slugs rather than compress.** Do not shorten evidence coverage just to
  hit the ceiling. Going long form is *not* the fix for an over-long
  short — see below.

### Long form (2026-10-09 user direction)

Instagram long-form videos (feed video, not a Reel) can run up to 20
minutes. They don't get promoted by the algorithm — they reach followers
only — so **long form is used only when the user explicitly says a video
should be long form.** Never pick it on the agent's own initiative, never
propose it as a way to fit an over-long short, and never infer it from a
topic being big.

- `length: long` plus `long_form_requested:` (the date and the user's own
  words) at the top of `beats.yaml`. Default budget becomes
  `min_seconds: 180`, `max_seconds: 1200`. `tools/new_project.ps1
  -Length long` writes both lines.
- Enforced by `capy.beats.validate_length()`: `length: long` without
  `long_form_requested:` is an error; a `length: short` video with
  `format.max_seconds` above 180 is an error (a short can't quietly drift
  long by editing its budget); nothing may exceed 1200s.
- Structure: 3-6 sections, each a complete response arc (the five
  response formats above, the playbook's six steps) with its own clip(s)
  and its own payoff — a long video is several strong segments, not one
  argument stretched. Open with the strongest segment, not background.
- Every short-form rule still applies per beat: clip ≤20s continuous,
  source time ≤30% of total runtime, pose change every 10-20s,
  response-to-clip alignment, one argument per beat group, the closing
  "...God bless." beat.
- Research and critique scale with it: every chosen claim goes through
  `/capy-research`, and `/capy-critique` runs on the whole script.
- Build: ~100+ beats exceeds Resolve's ~65-70-entry
  `create_timeline_from_clips` cap — assemble in batches (see
  `hybrid-resolve-pipeline.md` step 4).

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
- **The closing beat ("...God bless.") should not reference "sources are
  in the description."** State the closing line plainly; don't call out
  where citations live. (The actual sources still belong in the
  description text itself, per `research-protocol.md` — this is only
  about not narrating that fact out loud.)

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

## Response-to-clip alignment (2026-09-09 standing rule)

Every non-clip beat's response must actually be answering a claim
contained within its own most-recently-preceding `clip` beat's span — not
a claim from elsewhere in the source that got trimmed out when the clip
was tightened for length/budget. `capy_storyboard.py`'s "Original Video
Transcript" field always shows the most recent `clip` beat's text for
exactly this reason (see "`script.md` layout" below): if a response beat
doesn't actually match what that field displays, that is an authoring
bug, not a display quirk to shrug off. Caught 2026-09-09 on
`mark-driscoll`: a beat responding to "he calls this a cult, a
counterfeit Christ" was placed right after a clip beat that only covered
an earlier, different claim ("a different Jesus") — the cult/counterfeit
line had been trimmed out of the video entirely, so the response was
answering something the viewer never saw or heard.

Two ways to fix a mismatch like this:

1. **Add a `clip` beat for the claim actually being addressed** (the
   preferred fix, and what was done for the case above — a second short
   clip was inserted so "cult"/"counterfeit Christ" is shown on screen
   right before the beat responding to it). Re-check the source-time
   budget (30% of runtime) after adding one.
2. **If adding a clip isn't warranted** (the point is minor, or citing a
   fact about what the critic said elsewhere in the source rather than
   directly rebutting an on-screen claim), rephrase the response so it
   doesn't imply the viewer saw or heard something they didn't — say "he
   also says X elsewhere in the video" rather than "the very line he just
   quoted," which asserts something visibly false once you check it
   against what's actually on screen.

Before sending Gate A, walk every beat group and confirm its response
text is actually about the claim in its preceding clip beat, not a claim
that only exists in the full source transcript. This is exactly what the
Part A review checklist (`review-checklist.md`) should be doing already,
but it wasn't explicit as its own check before this — call it out
by name when doing that review.

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

## Use real images, not just quote cards (2026-09-09 user direction)

Pictures are great — especially primary-source document pages and
historical drawings/paintings/sketches/photos — and this pipeline
under-uses them relative to plain quote cards. Prefer a real image when
one is available and relevant:

- **`kind: evidence` with `evidence.image`** — a cropped receipt (GSA
  `get_page_image` for a manuscript/book page, a public-domain
  painting/photo/sketch/map) with a citation line. This is the strongest
  option when a real primary-source image exists — it's more convincing
  on screen than a typed quote card and doubles as the "receipt" the
  research protocol wants anyway.
- **`stage: image` on a `narration` beat** — a background image
  (same source types) behind the sprite while he's *talking*, not just
  during a dedicated evidence beat. Good for adding visual texture across
  a run of narration beats without breaking into CARD mode every time.
- Never fabricate or AI-generate a "historical" image, and never use a
  screenshot of a PDF reader, search results, or any desktop chrome
  (`brand.md` sec 10) — only clean crops/renders (GSA `get_page_image`) or
  images with a clear public-domain/fair-use basis, credited on screen.
- Still no image for its own sake — every image needs the same sourcing
  discipline as a quote (`research-protocol.md`), and a beat with nothing
  relevant to show should stay `blank`/`freeze`/CARD-with-quote rather
  than reaching for a decorative picture.

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

**Clip beats never get generated captions (2026-09-09 standing rule).**
Before ingesting any new video source, ask the user whether the source
video already has captions burned into its own footage, and pass the
answer to `capy_ingest.py --captions-in-source yes|no|unknown` (recorded
as `source_has_captions` in `source_info.json`, for the record). Either
way — captions already present, or genuinely none — **do not set
`captions: source` on a `clip` beat.** If the source already has its own
captions, adding ours would duplicate them on screen; if it doesn't, the
user's standing instruction is that the clip stays uncaptioned rather than
having Saint Capybara caption someone else's footage for them. Generated
captions are for **capybara-only clips** — `narration`/`card`/`evidence`/
`chart`/`excerpt` beats — only. `captions: source` still works
mechanically in `capy_caption_cards.py` (kept for older shipped projects,
e.g. `dont-read-the-bom`) but must not be used on any new beat;
`capy_check_sources.py` warns if it finds one.

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

Before this, run `/capy-critique` (`docs/saint-capybara/research-protocol.md`
sec 15; `review-checklist.md` Part A item 15). It fixes any BLOCKER finding
itself and produces `research/critique.md`, also mirrored to
`reviews/<slug>/critique.md` alongside `script.md`. **Prepend a short
critique summary before the fixed message below** — it is not part of the
fixed wording and may vary run to run, but it must always be present,
even when the critique found nothing:

> Critique before Gate A: *N* BLOCKER(s) found and fixed (beats: …).
> *M* MAJOR / *K* MINOR left for your review:
> - `<beat id>`: *finding* — suggested: "*rewrite*"

Then send the fixed message itself, unmodified:

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
