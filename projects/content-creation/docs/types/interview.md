# Interviews / podcasts

Source material: two (or more) cameras recording the same conversation
simultaneously — not separate takes. Content is kept essentially original:
camera cuts between angles for variety and to hide the occasional blooper,
no image overlays, no quote cards, no pre-production script doc (this type
skips `pipeline.md` §1 entirely and goes straight to transcription-for-cut-
decisions plus build).

## Cut logic

1. **Speaker-follow.** Default angle is whoever is currently talking. Use a
   wide/two-shot for crosstalk or back-and-forth exchanges.
2. **Periodic variety.** During a long single-speaker monologue (roughly
   20-40 seconds on one angle), switch to the other angle even without a
   speaker change, so no single shot sits static too long. Don't switch on a
   fixed metronome — pick natural sentence/thought boundaries near that
   window.
3. **Blooper handling.** When a blooper or stumble happens, do not trim it
   out. Instead, cut to the *other* camera angle so the moment is covered
   without an audio jump or a visible jump-cut — the same technique used for
   ordinary angle variety, just triggered by a flub instead of pacing.
   Confirm with `docs/media-analysis` style silence/retake detection which
   camera has the cleaner concurrent audio at that moment (both cameras hear
   the same room, so pick whichever angle reads better on screen, not by
   audio quality — audio comes from whichever mic is authoritative for the
   whole edit).
4. Because both cameras capture the same live take, camera choice and
   best-take choice are independent: first identify the cleanest line
   reading in time (from either camera's transcript, since content is
   identical), then assign a camera to that moment for visual variety.

## Build

- Sync both cameras (and any external mic) once at the top of the timeline;
  reuse that offset for the whole build.
- Build as an alternating sequence of camera-angle segments on one video
  track (not a stacked multicam clip — the Resolve API doesn't expose
  native multicam angle switching, see `../resolve-mcp-gotchas.md`), audio
  from the single authoritative source (external mic if present, otherwise
  the better camera's embedded audio) on its own track throughout.
- No stills, no cards, no music.

## QC

Watch for angle switches that land mid-word or on an eyeline mismatch;
nudge the cut point a few frames rather than re-picking the angle.
