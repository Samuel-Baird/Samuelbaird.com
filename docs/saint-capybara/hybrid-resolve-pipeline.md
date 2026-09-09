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
in `brand.md` sec 8; this doc's tooling list below reflects it. The
sign-of-the-cross outro is also no longer rendered per-project — see
"The shared outro cache" below.

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

0. **`tools/capy_outro.py --build`** (once per voice/theme change, not
   per project) — builds and caches the fixed sign-of-the-cross outro.
   See "The shared outro cache" below. `capy_tts.py`/`capy_beat_plates.py`/
   `capy_caption_cards.py`/`capy_render_beat_clips.py` below all skip the
   four fixed outro beats (`outro-01..04`) automatically once a cache
   exists for the project's voice; if none exists yet, step 4
   auto-builds it (or errors, with `--no-auto-build`).
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
   - **HOST** (`narration`, `outro`): parchment+vignette background (or,
     for `stage: freeze`, a full-bleed blurred/dimmed last-clip-frame
     background) with a large centered sprite.
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
   own audio for `clip` beats; `audio/<id>.norm.wav` with its pad
   trimmed back off — see below — for narration-family beats), and
   writes `frames/beat_<id>.mp4` plus `frames/beat_clips_manifest.json`.
   The four fixed outro beats collapse into one copied
   `frames/beat_outro.mp4` (see below) instead of four fresh renders.
5. **Import + assemble in Resolve** (via the davinci-resolve MCP —
   there is no wrapper script for this step, drive the MCP directly
   following the checklist below). Note the beat count is now
   N−3 (the four outro beats collapse to the one cached clip).
6. **Metadata-strip remux**: Resolve's render doesn't give fine enough
   control for the anonymity requirements in `brand.md` sec 10, so
   finish with one `ffmpeg -i <resolve-output> -c copy -map_metadata -1
   -fflags +bitexact -metadata title="<title>" <slug>.mp4` pass, then
   `tools/capy_check_brand.py --project <dir> --mp4 <final path>` before
   calling a render final.

## The shared outro cache

The four fixed sign-of-the-cross beats (`outro-01..04`) are byte-for-byte
the same rendering work in every project — same plates, same caption
timing, same wording — except for Kokoro's own waveform, which is
length-deterministic but not bit-deterministic. `tools/capy_outro.py`
renders them **once per (voice, speed, theme)** and caches the result
under `D:\saint-capybara\cache\outro\<key>\outro.mp4` (a content-addressed
key over the voice, the four beats' text/pose, every layout/caption/font/
sprite value that could change a pixel, and this tool's own version — see
its docstring). `capy_tts.py`/`capy_beat_plates.py`/
`capy_caption_cards.py` skip `outro-01..04` by default
(`capy.beats.is_fixed_outro`, matched by id **and** pose, so a
per-project *outro-lead* beat like `n05`/`n09` — `kind: outro` but a
different id/pose — is never swept into the cache and renders normally).
`capy_render_beat_clips.py` resolves (auto-building if missing) and
copies the cached `outro.mp4` into `frames/beat_outro.mp4`, writing one
merged manifest entry that lists all four beat ids and the cache key.

Run `python tools/capy_outro.py --build` once after choosing/changing the
locked voice (`brand.md` sec 6); `--verify` checks duration, the mp4 tag
allow-list, and PNG metadata; `--print-key` shows the current key without
building; `--gc` deletes stale keys. A project never needs to build the
cache itself unless `--no-auto-build` is passed to
`capy_render_beat_clips.py`.

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
   "1920"`, `timelineFrameRate: "30"`, and **`restore: false`** — without
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
   each beat clip as its own `Video + Audio` still/clip. `beat_outro.mp4`
   has no numeric suffix so it can never trigger this grouping. If it
   happens anyway, `media_pool.delete_clips` (confirm-gated) the grouped
   item and re-import one at a time — deleting a Media Pool reference
   does not touch the file on disk.
4. **Build the timeline**: `media_pool.create_timeline_from_clips` with
   `clip_ids` in beat order (the simple end-to-end append mode — no
   `record_frame` math needed since beat clips play back to back with no
   gaps by construction). Well under the ~65-70 raw-entry cap for a
   10-14 beat video (N−3 after the outro collapses to one clip), so one
   call suffices.
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
