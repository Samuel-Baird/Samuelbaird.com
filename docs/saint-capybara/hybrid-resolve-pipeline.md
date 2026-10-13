# Saint Capybara — Resolve build pipeline

**Status: official (2026-09-09).** This is the only render method for
Saint Capybara now — the original ffmpeg-only compositor plan (per-beat
plates + libass-burned captions + `ffmpeg concat`, described in earlier
drafts of this pipeline) is retired. Do not resurrect it; every doc/tool
reference to it should point here instead. First proven end-to-end on
`two-takes-joseph-smith` and `joseph-smith-plural-marriage` (2026-09-09).

**Layout redesign, `theme.yaml: layout.version 2` (2026-09-09).** The
first two shipped videos exposed the v1 layout as designed for a 16:9
source that never materialized (all real sources are 1080×1920 portrait)
and had two real bugs: captions wrapped by character count, not measured
width, so long lines clipped off both edges of the frame; and punctuation
tokens from Kokoro/Whisper shipped as their own caption card (a beat's
narration could produce a caption whose entire text was a lone `,`). The
redesign — full-bleed CLIP video, a big HOST-mode sprite, no chips/
wordmark/hook-on-screen, measured-width captions — is described in full
in `brand.md` sec 8; this doc's tooling list below reflects it.

**The sign-of-the-cross outro is gone (2026-09-09).** An earlier version
of this doc described a shared, cached outro clip built by
`tools/capy_outro.py`. That tool and every reference to it below have
been removed — every video now just ends its closing `narration` beat on
"...God bless." like any other hand-authored beat. See git history if
the old mechanism is ever needed for reference.

## Why this exists

Saint Capybara videos are edited in DaVinci Resolve, like the other three
video types, but keep everything else about the brand: the character,
research rigor, brand/anonymity rules, and the standard sign-off
sequence. Getting there took one real pivot worth understanding before
touching this pipeline:

**Original plan (superseded):** composite each visual layer live on the
Resolve timeline — a background/sprite/wordmark "plate" track, a
per-caption-phrase track, the raw source clip on its own track. This
turned out to be impractical through the davinci-resolve MCP: Resolve
auto-detects sequentially-numbered same-prefix PNGs (`plate_c01.png`,
`plate_c02.png`, ...) as an *image sequence* rather than individual
stills, so even importing ~70-90 individual caption stills per video
needed one MCP call each (worth adding to `docs/resolve-mcp-gotchas.md`).

**What actually shipped:** pre-composite each **beat** (not each caption
phrase) into one self-contained MP4 — the beat's chrome plate, its
caption phrase overlays (each windowed with ffmpeg's `enable=between(t,
start,end)`), and its audio, all baked in with ffmpeg. The Resolve
timeline then holds one real, reorderable/trimmable clip per beat
(~14-18 per video) instead of ~90 individual stills across multiple
tracks — a human editor can still open the project and adjust cuts,
transitions, or ordering afterward, it's just that each "clip" arrives
pre-flattened rather than built from live layers.

## Tooling (in run order)

All of these are real, non-experimental tools now. Run in this order
after Gate A approval:

1. **`tools/capy_tts.py --project <dir>`** — real Kokoro narration per
   beat, using each beat's resolved voice (`capy.beats.resolve_voice`:
   an inline `voice:` override, else a `voices:` role — `excerpt` beats
   default to `voices.quote_default` — else the project's host
   `voice:`). Writes `audio/<id>.wav` (24kHz raw), `audio/<id>.timing.json`
   (per-word `{w,s,e}`), `audio/<id>.norm.wav` (48kHz stereo, two-pass
   loudness-normalized to -16 LUFS with head/tail padding — single-pass
   `loudnorm` measured off by ~5 LU on a real test clip, so this tool
   always does the two-pass measure-then-apply version), and
   `audio/<id>.meta.json` ({voice, speed} actually used, so a voice
   change is detected even though the wav/timing files still exist).
2. **`tools/capy_beat_plates.py --project <dir>`** — one full-canvas
   PNG per beat (`frames/plate_<id>.png`) via `capy.plates.render_plate`,
   which picks one of three frame modes per beat kind (`capy.layout.
   Theme.mode_for`) — see `brand.md` sec 8:
   - **CLIP** (`clip` beats): the plate is a *pure overlay*, fully
     transparent except the small corner sprite — no chip, no hole
     concept. The real source video fills the whole canvas, composited
     underneath by ffmpeg in step 4.
   - **HOST** (`narration`): parchment+vignette background by
     default, or (`stage:` `freeze` / `image` / `video` — see
     `script-format.md`) a full-bleed blurred/dimmed background from the
     last clip frame, a supplied project image, or the source video
     playing live, with a large centered sprite. `stage: video`'s plate
     is transparent like CLIP mode — the live video is composited in
     step 4, not baked into the PNG here.
   - **CARD** (`card`, `evidence`, `chart`, `excerpt`): the card/chart/
     evidence/pull-quote content on the upper ~2/3 of the frame, a
     medium sprite bottom-left.
   No wordmark, no "SOURCE"/"Source video" chip, no hook-on-screen —
   only captions and card/quote text are ever drawn. Use `--clean` to
   delete stale `plate_*.png`/`beat_*.mp4` before a re-render.
3. **`tools/capy_caption_cards.py --project <dir>`** — one transparent
   PNG per caption phrase group (`captions/<id>_<n>.png`), timed from
   `audio/<id>.timing.json` (narration-family beats) or the Whisper
   transcript (`clip` beats), laid out by `capy.text.fit_text` —
   measured-width wrap with a shrink-to-fit floor, never a character
   count, so a long line is never clipped at the frame edge (the shipped
   `two-takes-joseph-smith` bug). Adjacent punctuation tokens are glued
   onto the previous word first (`capy.captions.attach_punctuation`) so
   a caption is never just a lone `,`. Falls back to an evenly-spaced
   draft-timing mode (flagged in the manifest, not on screen) when real
   timing isn't available yet — re-run after `capy_tts.py`.
4. **`tools/capy_render_beat_clips.py --project <dir>`** — the
   compositing step: for each beat, ffmpeg composites the plate, the
   real source video (for `clip` beats: cover-cropped full-bleed for a
   9:16-or-narrower source, or fit inside the letterbox band over a
   blurred/darkened cover copy for a 16:9-or-wider source — never plain
   black bars), and the caption overlays (each windowed to its own
   `[start, end)`), muxes in the beat's audio (the trimmed source clip's
   own audio, two-pass loudness-matched to the same target as
   narration — see "Audio consistency" below — for `clip` beats;
   `audio/<id>.norm.wav` with its pad trimmed back off — see below — for
   narration-family beats), and writes `frames/beat_<id>.mp4` plus
   `frames/beat_clips_manifest.json`.
5. **Import + assemble in Resolve** (via the davinci-resolve MCP —
   there is no wrapper script for this step, drive the MCP directly
   following the checklist below).
6. **Metadata-strip remux**: Resolve's render doesn't give fine enough
   control for the anonymity requirements in `brand.md` sec 10, so
   finish with one `ffmpeg -i <resolve-output> -c copy -map_metadata -1
   -fflags +bitexact -metadata title="<title>" <slug>.mp4` pass, then
   `tools/capy_check_brand.py --project <dir> --mp4 <final path>` before
   calling a render final.

## Audio consistency

**All audio in the final video must sit at the same loudness target
(`theme.yaml: audio.target_lufs`, -16 LUFS) — narration and the reacted-to
source clip alike.** Found and fixed 2026-09-09: `capy_tts.py` has always
loudness-normalized narration (two-pass `loudnorm`, since single-pass
measured off by ~5 LU on a real test clip — the reason `capy_tts.py`
never uses single-pass), but `capy_render_beat_clips.py`'s `clip`-beat
branch originally muxed the source video's own audio through **raw,
unnormalized** — on `dont-read-the-bom-polygamy`'s real source this
measured **-33 LUFS**, roughly 17 LU quieter than the -16 LUFS narration,
audibly "the reacted-to clip goes quiet" on every cut back to it.

Fixed by giving `clip`-beat audio the same two-pass treatment
(`measure_loudnorm()` + `loudnorm_apply_filter()` in
`capy_render_beat_clips.py`, chained before `atempo` when a beat's
`speed != 1.0`) — every beat's audio, clip or narration, now normalizes
to the same target before it ever reaches the Resolve timeline. This is
a standing requirement for the whole type, not a one-off fix: if
`capy_render_beat_clips.py` or its audio filter chain is ever refactored,
keep both branches loudness-matched to `theme.yaml: audio.target_lufs`.

### A padding detail worth knowing

`audio/<id>.norm.wav` carries `head_pad_seconds` (0.25s, `theme.yaml:
audio.head_pad_seconds`) of silence on both ends — useful for a
standalone audio file, but 16 narration beats × 0.5s of dead air pushed
a real video ~9s over the 180s ceiling budgeted without it. In a
single-track hard-cut assembly that padding isn't needed, so
`capy_render_beat_clips.py` trims it back off (`atrim` in the audio
filter graph) when building each beat's MP4 — the standalone
`audio/<id>.norm.wav` file is left untouched for anyone who wants it as
a deliverable on its own.

## Resolve build checklist (via the davinci-resolve MCP)

Read `docs/resolve-mcp-gotchas.md` in full before this step. The
specifics that mattered in practice, building the two videos above:

1. **Create the project**: `project_manager.safe_project_create` with
   `allow_non_mcp_name: true` (the safe wrapper defaults to requiring an
   `_mcp_`-prefixed name otherwise) and the project named after the
   slug.
2. **Set the timeline format**: `project_manager.safe_set_project_settings`
   with `timelineResolutionWidth: "1080"`, `timelineResolutionHeight:
   "1920"` (**`"1920"` / `"1080"` for a `long-youtube` video** — match
   `beats.yaml`'s `format`), `timelineFrameRate: "30"`, and **`restore:
   false`** — without
   that flag the wrapper silently reverts resolution changes (frame rate
   alone stuck; width/height didn't) even though it reports `success:
   true` and each field's own `write`/`readback` looks correct. Verify
   with `project_settings.get_setting` after, don't trust the write
   response alone.
3. **Import media pool items one file per call.** Resolve's importer
   groups sequentially-numbered same-prefix files (`beat_c01.mp4`,
   `beat_c02.mp4`, ... — or `plate_c01.png` etc. from the earlier,
   superseded approach) into a single "image/clip sequence" item instead
   of individual clips whenever more than one such sibling is passed to
   the same `media_pool.safe_import_media` call. One path per call keeps
   each beat clip as its own `Video + Audio` still/clip. If grouping
   happens anyway, `media_pool.delete_clips` (confirm-gated) the grouped
   item and re-import one at a time — deleting a Media Pool reference
   does not touch the file on disk.
4. **Build the timeline**: `media_pool.create_timeline_from_clips` with
   `clip_ids` in beat order (the simple end-to-end append mode — no
   `record_frame` math needed since beat clips play back to back with no
   gaps by construction). Well under the ~65-70 raw-entry cap for a
   10-16 beat video, so one call suffices. A long-form video
   (`video_type: long-instagram` up to 20 min, or `long-youtube` with no cap, often
   100+ beats) is not: create the
   timeline from the first ~20 beats, then `media_pool.append_to_timeline`
   the rest in ~20-beat batches, saving and re-reading the item count
   after each batch (`docs/pipeline.md` §3).
5. **Verify before rendering**: `project_manager.save`, then
   `timeline.get_start_frame`/`get_end_frame` (duration = end − start,
   confirm it matches the beat-clip manifest's summed duration) and
   `timeline.detect_gaps_overlaps` (expect zero of each).
6. **Render**: `render.set_format_and_codec` (`mp4`/`H264`),
   `render.set_settings` with `TargetDir`/`CustomName`, `render.add_job`,
   `render.start`. Poll `render.get_job_status` — completion percentage
   can sit at one value for 20-30s on a several-minute render before
   jumping, that's normal, not a stall (cross-check
   `resolve_control.runtime_mode`'s `database_attached` if truly
   suspicious of a wedge). **Always finish with `render.verify_output`**
   (pass `expected_duration_seconds` from the timeline) rather than
   trusting `JobStatus: Complete` alone — see that tool's own
   documentation of the near-empty-stub failure mode.
7. Then the metadata-strip remux and brand lint from the tooling list
   above.

**A render can come out wrong even when the timeline API says it's
correct (2026-09-09, hit on `dont-read-the-bom`'s first re-render after a
mid-session project switch).** A rendered file had two beats' audio play
out of order with one truncated mid-sentence, even though
`timeline.detect_gaps_overlaps`, `get_start_frame`/`get_end_frame`, and a
full `timeline_item.get_name` walk of every clip all reported the correct
order and duration immediately after — and `render.verify_output`
doesn't catch it either, since duration/frame-count still matched.
Re-rendering (same timeline, no other changes) produced a correct file.
**Verify a render's actual audio content, not just its duration/frame
count**, whenever the session did anything unusual around the render
(switching projects, several render jobs in one session, a drift warning
on project load) — the cheapest check is `tools/transcribe.py` on the
exported file, diffed by eye against the beat narration text; a
duration/frame-count match alone is not sufficient evidence the content
is right.

**Second occurrence (2026-09-09) needed a different fix.** After editing
one beat's text and regenerating its audio/plate/caption/clip, a full
delete-timeline + delete-clips + fresh reimport + fresh timeline +
re-render — the standard rebuild procedure above — reproduced the *old,
pre-edit* audio for that one beat across three consecutive renders, even
though `beat_<id>.mp4` was independently confirmed correct on disk each
time. Total duration/frame count matched every time; only that one
beat's audio content was stale. **Renaming the file** (e.g. `beat_n03.mp4`
-> `beat_n03_v2.mp4`) **before reimporting** fixed it immediately —
something in Resolve was caching by clip name/position, surviving even a
full media-pool purge. If a plain re-render doesn't clear a content
mismatch, rename the specific stale beat's file next, rather than
re-rendering the same names again.

## Known gaps / open questions

- Evidence-card and quote-card rendering (`capy/plates.py: draw_card`,
  `draw_bar_chart`, `_paste_evidence`) now sit in the CARD-mode layout
  (medium sprite, card on top) and use `capy.text.fit_text` for the
  quote/attribution text, verified against the layout redesign's mock
  sheet and one real project (`two-takes-joseph-smith`) — visually
  reviewed 2026-09-09, reads well against the finalized sprite art.
- The 16:9-or-wider CLIP-mode letterbox path (blurred cover background +
  fitted foreground) has only been exercised against a synthetic
  `testsrc2` frame (`capy_storyboard.py --mock`) — every real source so
  far has been 1080×1920 portrait. Review the first real landscape
  source once one exists.
- No automated silence/pacing check on the assembled beat clips yet
  (mouth-flicker-in-pauses, the old ffmpeg plan's QC item, doesn't apply
  the same way here since there's no mouth-flicker frame system in the
  finalized-art pipeline at all — sprites are static per pose).
- `saint-capybara-deadpan.png` has no alpha channel (a baked-in solid
  background instead of real transparency) — `capy.sprites.render_sprite`
  detects this and raises rather than compositing a black square, but
  the pose is effectively unusable until the art is regenerated from the
  master prompt. `factual_failure` currently only resolves to
  `disappointed`.
- **Reconsider live layers on the Resolve timeline (2026-09-09 user
  feedback, not yet acted on).** The current "what actually shipped"
  approach (above) pre-composites the sprite, captions, and source video
  into one flat MP4 per beat, specifically because live per-layer
  compositing hit the Resolve-importer image-sequence-grouping problem
  (see "Why this exists" above). The user's complaint on
  `bom-1837-wording-change`: with everything baked into one flat clip
  per beat, the sprite can't be moved, resized, or otherwise adjusted
  after the fact except by re-running the whole render pipeline and
  re-tuning `theme.yaml` numbers blind — there's no way to just drag the
  capybara in the Resolve UI the way an editor would expect. The user
  wants the sprite (at minimum) on its own timeline layer/track, separate
  from the source/background video, so it's independently
  movable/resizable per-project or per-beat in Resolve itself.
  **This is a real architecture trade-off to revisit, not a bug** — the
  original "Original plan (superseded)" section above already describes
  the live-layer approach and why it was dropped (Resolve auto-groups
  sequentially-numbered same-prefix stills into one Media Pool item
  instead of individual clips). That grouping problem is a real blocker
  for the *caption*-stills layer specifically (~90 individual stills per
  video), but may be more tractable for just the *sprite* layer alone
  (one sprite plate per beat, ~13-18 per video, well within the
  one-file-per-call workaround already used elsewhere in this pipeline
  for beat-clip import) — worth a scoped experiment: sprite on its own
  video track via individual per-beat sprite PNGs (already produced by
  `capy_beat_plates.py`, just not currently kept as a separate importable
  asset since they're baked into `beat_<id>.mp4`), background/source clip
  on a track below, captions can stay baked into the background track for
  now if the caption-stills grouping problem remains unsolved. Do **not**
  apply this to already-shipped videos without explicit direction — this
  is a forward-looking pipeline change, evaluate and prototype on a new
  project first.
