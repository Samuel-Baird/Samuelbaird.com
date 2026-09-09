# Saint Capybara — Resolve build pipeline

**Status: official (2026-09-09).** This is the only render method for
Saint Capybara now — the original ffmpeg-only compositor plan (per-beat
plates + libass-burned captions + `ffmpeg concat`, described in earlier
drafts of this pipeline) is retired. Do not resurrect it; every doc/tool
reference to it should point here instead. First proven end-to-end on
`two-takes-joseph-smith` and `joseph-smith-plural-marriage` (2026-09-09).

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
   beat. Writes `audio/<id>.wav` (24kHz raw), `audio/<id>.timing.json`
   (per-word `{w,s,e}`), and `audio/<id>.norm.wav` (48kHz stereo,
   two-pass loudness-normalized to -16 LUFS with head/tail padding —
   single-pass `loudnorm` measured off by ~5 LU on a real test clip, so
   this tool always does the two-pass measure-then-apply version).
2. **`tools/capy_beat_plates.py --project <dir>`** — one full-canvas
   PNG per beat (`frames/plate_<id>.png`): background/vignette, sprite
   (from the finalized art directory, not the retired code-drawn
   renderer), card/chart/evidence content, hook chip (beat 1, auto-sized
   to fit), wordmark. `clip` beats get a fully transparent hole over the
   stage rectangle so the real source video shows through when
   composited in the next step.
3. **`tools/capy_caption_cards.py --project <dir>`** — one transparent
   PNG per caption phrase group (`captions/<id>_<n>.png`), timed from
   `audio/<id>.timing.json` (narration beats) or the Whisper transcript
   (`clip` beats). Falls back to an evenly-spaced, visibly-marked "(draft
   timing)" mode when real timing isn't available yet — never mistake a
   draft-timed render for the final cut; re-run after `capy_tts.py`.
4. **`tools/capy_render_beat_clips.py --project <dir>`** — the
   compositing step: for each beat, ffmpeg composites the plate, the
   real source video (for `clip` beats, scaled/cropped into the stage
   rectangle), and the caption overlays (each windowed to its own
   `[start, end)`), muxes in the beat's audio (the trimmed source clip's
   own audio for `clip` beats; `audio/<id>.norm.wav` with its pad trimmed
   back off — see below — for narration-family beats), and writes
   `frames/beat_<id>.mp4` plus `frames/beat_clips_manifest.json`.
5. **Import + assemble in Resolve** (via the davinci-resolve MCP —
   there is no wrapper script for this step, drive the MCP directly
   following the checklist below).
6. **Metadata-strip remux**: Resolve's render doesn't give fine enough
   control for the anonymity requirements in `brand.md` sec 10, so
   finish with one `ffmpeg -i <resolve-output> -c copy -map_metadata -1
   -fflags +bitexact -metadata title="<title>" <slug>.mp4` pass, then
   `tools/capy_check_brand.py --project <dir> --mp4 <final path>` before
   calling a render final.

`tools/capy_resolve_build_plan.py` (read-only track/record-frame
planner, makes no Resolve/MCP calls) is superseded by the beat-clip
approach — the per-beat MP4s make its multi-track math unnecessary. Kept
only as a duration/budget sanity check if useful; not part of the
required run order.

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
   each beat clip as its own `Video + Audio` still/clip. If this happens
   anyway, `media_pool.delete_clips` (confirm-gated) the grouped item and
   re-import one at a time — deleting a Media Pool reference does not
   touch the file on disk.
4. **Build the timeline**: `media_pool.create_timeline_from_clips` with
   `clip_ids` in beat order (the simple end-to-end append mode — no
   `record_frame` math needed since beat clips play back to back with no
   gaps by construction). Well under the ~65-70 raw-entry cap for a
   14-18 beat video, so one call suffices.
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
  `draw_bar_chart`, `_paste_evidence`) were written for the retired
  all-ffmpeg pipeline and are reused as-is here — not yet visually
  reviewed against the finalized sprite art's actual style (warmer,
  gradient-shaded, not flat pixel fill) sitting in the same frame.
- The hook-chip renderer (`capy/plates.py`, beat-1 hook text) now
  auto-shrinks/wraps to fit — fixed 2026-09-09 after a long hook
  overflowed the frame in the first real render. Re-check on a very
  long hook line; the wrap logic hasn't been stress-tested past two
  lines.
- No automated silence/pacing check on the assembled beat clips yet
  (mouth-flicker-in-pauses, the old ffmpeg plan's QC item, doesn't apply
  the same way here since there's no mouth-flicker frame system in the
  finalized-art pipeline at all — sprites are static per pose).
