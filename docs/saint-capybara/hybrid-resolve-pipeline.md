# Saint Capybara — hybrid Resolve pipeline

**Status: TEST / EXPERIMENTAL (2026-09-08). Not yet used for a real
render. This document and the tooling it describes are being actively
tested and may change.** The rest of the Saint Capybara docs
(`brand.md`, `research-protocol.md`, `script-format.md`) describe the
stable, agreed-upon parts of the type; this one doesn't have that status
yet.

## Why this exists

The original plan (see the pipeline-plan history) built Saint Capybara
around an all-ffmpeg compositor: PIL-rendered plates per beat, `subtitles=`
burned captions via libass, `xfade`/`concat` assembly. One project asked
instead for a **hybrid** approach: edit in DaVinci Resolve like a normal
response video (source clip + reaction beats), but keep the character,
research rigor, and sign-off sequence. This doc is the architecture for
that hybrid, and the tooling below is what exists so far to support it.

## Track plan

A 1080x1920 Resolve timeline, built from one project's `script/beats.yaml`:

- **V1 "source"** — the real source clip, Transform+Cropped into the
  1080x608 stage rectangle (`assets/saint-capybara/theme.yaml: layout.stage`),
  one entry per `clip` beat. Its own embedded audio plays as-is — no
  separate audio track needed for clip beats.
- **V2 "plates"** — one full-canvas still per beat, rendered by
  `tools/capy_beat_plates.py` (reusing `capy/plates.py`'s existing
  background/card/chart/evidence/sprite/wordmark drawing, now pointed at
  the finalized AI-generated sprite art instead of the retired code-drawn
  renderer). For `clip` beats this plate has the stage rectangle punched
  fully transparent so V1 shows through; for every other beat kind it's
  the complete rendered content.
- **V3 "captions"** — one still per caption phrase group, rendered by
  `tools/capy_caption_cards.py` (reuses `capy/captions.py`'s
  `group_phrases()` chunking, just renders to a transparent PNG instead of
  an ASS event — `docs/resolve-mcp-gotchas.md` documents Resolve's
  `insert_title` as unreliable and SRT import as UI-only, so stills are the
  same "don't fight the Text+ API" pattern this repo already uses for the
  other brand's quote cards/credits).
- **A1 "narration"** — one clip per narration-family beat, from
  `audio/<id>.norm.wav` once `capy_tts.py` has rendered it (post-Gate-A —
  `capy_tts.py --project` intentionally refuses to run before that gate,
  see its own `main()`).

This simplifies an earlier 4-5-track sketch (background / evidence-panel /
sprite / captions as separate live-composited layers) down to 3 video
tracks + 1 audio track by pre-flattening everything that isn't the live
source clip into one PNG per beat — much less Resolve-side compositing to
get wrong, and it reuses `capy/plates.py` almost as-is.

## Build mechanics (once tooling below produces a complete, non-"pending" plan)

Follow `docs/resolve-mcp-gotchas.md` throughout — this hasn't been
exercised against Resolve yet, so treat every point below as a checklist,
not a claim that it's been proven to work for this hybrid case specifically:

- `append_to_timeline` with explicit `record_frame`s, not
  `create_timeline_from_clips` (can't target a specific track).
- Cap every still's placed duration at the next beat's record frame
  before appending (overlapping placements silently drop the later one).
- Batch in ~20-beat chunks per track.
- After every batch: save, re-read the timeline's item count, re-append
  anything short (an errored append can appear in-session and still be
  discarded by the save).
- Finish with `timeline.detect_gaps_overlaps`.
- Final metadata strip: Resolve's render doesn't give fine enough control
  for the anonymity requirements in `brand.md` §10, so run one
  `ffmpeg -i out.mp4 -c copy -map_metadata -1 -fflags +bitexact final.mp4`
  remux pass after Resolve's render, then re-probe tags before calling a
  render final.

## Tooling status

| Tool | Status | What it does |
|---|---|---|
| `tools/capy_beat_plates.py` | built, tested against a real project (no Resolve needed) | Renders `frames/plate_<id>.png` per beat + `frames/plates_manifest.json`. |
| `tools/capy_caption_cards.py` | built, tested | Renders `captions/<id>_<n>.png` per caption phrase + `captions/manifest.json`. Runs in a DRAFT mode (evenly-spaced pseudo-timing, visibly marked on each card) before real TTS timing exists, real mode once `capy_tts.py` has produced `audio/<id>.timing.json`. |
| `tools/capy_resolve_build_plan.py` | built, tested | Computes the full track/record-frame layout as `frames/resolve_build_plan.json`. **Makes zero Resolve/MCP calls** — pure planning artifact, reports "pending" for anything not yet rendered so it can't be mistaken for a build-ready plan. |
| An actual `append_to_timeline` build script that consumes `resolve_build_plan.json` and drives the davinci-resolve MCP | **not built** | This is the step that actually touches Resolve. Needs Gate A approval on the script content first (per every Saint Capybara video), separately from approval of this architecture itself. |

## Known gaps / open questions

- Evidence-card and quote-card rendering (`capy/plates.py: draw_card`,
  `draw_bar_chart`, `_paste_evidence`) were written for the retired
  ffmpeg-plate pipeline and are being reused as-is here — they haven't
  been visually reviewed against the finalized sprite art's actual style
  (warmer, gradient-shaded, not flat pixel fill) sitting in the same
  frame. Worth a look once a real project's plates are reviewed end to
  end.
- No `--execute` build script exists yet, by design — see the table
  above.
- This hasn't been validated against Resolve at all (no timeline has
  actually been built this way). The gotchas doc's guidance is being
  followed proactively, not because it's been confirmed to apply
  identically to this stills-heavy, mostly-transparent-track approach.
