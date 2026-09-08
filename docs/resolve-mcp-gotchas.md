# DaVinci Resolve MCP gotchas

Traps in the Resolve scripting API (surfaced through the `davinci-resolve`
MCP server) that are not documented anywhere obvious, gathered from prior
sessions and this server's own knowledge ledger
(`mcp__davinci-resolve__knowledge`, topic `api-limitations`). Read before a
build stage, not after something goes silently wrong.

## Building timelines

- **`create_timeline_from_clips` cap.** Fails opaquely ("requires
  start_frame/end_frame") past roughly 65-70 raw clip_info entries, even
  when every entry is valid. Batch in chunks of ~20 beats (40 raw entries
  once paired video+audio is counted).
- **`create_timeline_from_clips` also requires the Media Pool's *current
  folder* to already be the clips' folder** — a valid `clip_id` is not
  sufficient; call `media_pool.set_current_folder` first. Separately, this
  call's `clip_infos` shape has **no track field** — it cannot place clips
  on a specific track. Use it only for the initial flat build; for anything
  that needs a chosen track, use an empty `create_timeline` +
  `append_to_timeline` with `track_index` instead.
- **Incremental adds:** use `append_to_timeline` with positioned
  `clip_infos`, not `create_timeline_from_clips` again —
  `if_exists: "reuse"` silently no-ops and ignores new clip_infos rather
  than appending.
- **Overlapping records — earlier item wins, later is silently dropped.**
  `append_to_timeline` does not overwrite an overlapping record range on the
  same track; when two entries collide, the later append is dropped with no
  error, leaving the timeline silently short. This is almost certainly the
  root of the "still-image overlap/duration-clamping" behavior seen on the
  sacrament edit. **Always cap each placed clip's duration at the next
  beat's record frame before appending**, and verify afterward by comparing
  the returned item count against the number of clip_infos sent, then run
  `timeline.detect_gaps_overlaps`.
- **Errored append chunks are not durable across a save.** A placement whose
  API response errored can still appear in-session — every in-session read
  agrees it's there — and then vanish once the project is saved. Treat the
  save as the real verification boundary: save, re-read the timeline's item
  count from the saved project, and re-append whatever is missing. Never
  report a build as complete on a pre-save read alone.
- **Mixed-fps sources floor to the frame below,** leaving a 1-frame gap
  before the next clip when a clip's native fps differs from the timeline's.
  Plan durations in timeline frames
  (`floor(src_frames * timeline_fps / source_fps)`) and extend by one source
  frame if the floored duration misses the slot. Finish every build with
  `detect_gaps_overlaps` regardless.
- **`ripple_insert` is not an incremental-build primitive** — it shifts
  every track uniformly by the longest clip in the inserted batch, which
  desyncs video/audio when clips are being added as separate calls or
  separate `media_type`s. Its correct use is rebuilding a tail into free
  space after a verified move, not general insertion.
- **`media_type: 1`** on a clip_info places video only (no paired audio) —
  use this plus a separate audio-only entry at the same `record_frame` when
  substituting external mic audio for a camera clip's own embedded sound.
- **Null-id returns.** A returned `TimelineItem` can have an unreadable
  `GetUniqueId` — most often when a `recordFrame` lands inside a span still
  occupied by another item, e.g. a duplicate-then-delete "move" whose offset
  is smaller than the item's own duration. Never trust a non-empty return as
  proof of placement; re-enumerate the track and match on record frame +
  duration before any dependent delete.

## Media pool / discovery

- Newly created timelines and freshly imported media sometimes don't show
  up in `folder.get_clips` for the expected folder even after
  `media_pool.refresh()` — a caching bug in the wrapper, not reality. Use
  `media_pool.probe_media_pool` (full tree dump) or `media_pool.get_selected`
  to find real ids. Imported clips can land in an unexpected "Archive"
  subfolder rather than "Master".
- A timeline's own media-pool-item id (needed to nest it as a clip
  elsewhere) is different from the timeline's own id — get it via
  `timeline.get_media_pool_item` after `timeline.set_current`.
- `media_pool_item.replace_clip(clip_id, path)` hot-swaps a media pool
  item's source file everywhere it's already placed across every timeline —
  useful for retroactively burning captions/credits into an image (or fixing
  any asset) already cut into a timeline, without touching timeline items.

## Titles / text

- **`timeline.insert_title` (Text+) fails silently/opaquely** ("Failed to
  insert title") regardless of parameters tried. Two working alternatives:
  1. **PIL-burned images** (this pipeline's default for quote cards and
     credits) — deterministic, no Resolve title API involved at all.
  2. **The nested-timeline route**, when an actually-editable on-timeline
     title is needed: create the title on its own empty timeline
     (`create_timeline` + `InsertFusionTitleIntoTimeline` — it lands on V1
     there, which doesn't matter), then place *that timeline's* media-pool
     item via `append_to_timeline` with `track_index`/`record_frame`. Text
     stays settable afterward through
     `placedItem.GetMediaPoolItem().GetTimeline()` (Resolve 21.0.4+) then
     `GetFusionCompByIndex(1).FindTool("Template").SetInput("StyledText", ...)`.
     Every placed instance of that timeline shares one media-pool item, so a
     text edit propagates to all placements — use one source timeline per
     distinct card if independent text is needed. Placements still can't
     overlap on a track (see above).
  - **Do not use `Timeline.CreateCompoundClip`** as a substitute for the
    nested-timeline route — it also gets a placeable media-pool item, but it
    severs the Text+ tool entirely (`FusionCompCount` drops to 0), with no
    route back to editable text.
  - **Do not reach for track locking** to steer either insert method onto a
    specific track — locking a track blocks the insert rather than
    redirecting it, both via the API and via the UI padlock.

## Transcription (Resolve's built-in)

- `Timeline.CreateSubtitlesFromAudio` always uses Resolve's own built-in
  speech-recognition engine — there is no API parameter to select Whisper or
  any other provider, and there is no API to import an SRT file
  programmatically (File → Import → Subtitle is UI-only). This pipeline
  doesn't use Resolve's built-in transcription at all — see
  `transcription.md` for the local-Whisper approach instead.

## Bridge stability (free edition)

On the free edition, `resolve_bridge` (Workspace → Scripts → resolve_bridge)
can silently drop mid-session. Symptoms are misleading: frame capture starts
failing with "Resolve refused render format 'jpg'", `render.add_job` fails
with "not answering the scripting API". Before deep-diving a rendering
error, check `resolve_control.runtime_mode` for `database_attached` —
if false/failing, just restart the bridge.

**Reproduced 2026-09-08** while building this pipeline: `runtime_mode`
answered normally (`database_attached: true`) on one call, then the very
next Resolve-touching call (`project_manager.safe_project_create`) timed
out (`bridge_timeout`), and a follow-up `runtime_mode` came back
`database_attached: false` with the tool's own guidance labeling the state
`WEDGED` and explicit that **it does not recover** — Resolve must be quit
and restarted, not just the bridge script. So a passing `runtime_mode`
check moments earlier is not a guarantee the next call will land; if a
build-stage call times out or errors as "not answering the scripting API",
re-check `runtime_mode` immediately rather than retrying the original call,
and if it reports `WEDGED`, stop and ask the user to restart Resolve rather
than retrying in a loop.

## Two cameras recording one synchronous take

When two cameras record the same live take simultaneously (not separate
takes — as with an interview or a solo presenter re-reading lines on
camera), camera-angle choice and best-take choice are independent
decisions: pick the cleanest line reading first (in time, from either
camera's transcript, since spoken content is identical across both), then
assign a camera to that moment separately, for visual variety or blooper
coverage.
