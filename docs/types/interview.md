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

## ffmpeg route (no Resolve on the machine) — `tools/interview/build.py`

First used for the Carl Youngblood / Transfigurism interview (2026-11-04): three Sony
PXW-Z200s (A = host close, B = wide two-shot, C = guest close) and a Zoom F6 (`Tr2` host
lav/dynamic, `Tr3` guest, `TrL_R` the F6's mono mix). Same `project.json`, `sync.py` and
transcript as the presentation pipeline (`docs/types/presentation.md` §1-3), plus:

- `takes.<k>.iso: [host_mic, guest_mic]`, `interview.cams` (`host`/`guest`/`wide` → camera
  letter) and `interview.wide_faces` (each face in the wide frame). `mic` stays the F6 mix —
  sync and Whisper use it.
- **Speaker-follow from the iso mics, not the transcript.** 100 ms RMS per mic; the louder one
  (−3 dB margin for bleed, both quiet below 52 dB = nobody) is the talker. Turns < 1.5 s are
  backchannels and are absorbed; exchanges < 3.5 s hold the wide.
- **Angle variety inside a turn** (cut logic §2): talker's close-up first, then a fixed cycle of
  wide / tight / side (a 1.7× crop of the wide on the talker) / listener reaction (3.5-9 s,
  only in turns ≥ 15 s) / close, every 10-26 s, each cut placed in a breath pause (both mics
  < 45 dB for ≥ 0.3 s; the quietest 100 ms if there's none). The cycle restarts per turn so
  a later edit only re-renders nearby units.
- **Websites / images**: `longform.web: [[from, to, stem]]` puts an image in the brand split
  layout with the *talker's* close camera in the window; `scroll:<stem>` slowly scrolls a
  full-page capture through the card. Capture pages with Playwright (`channel='chrome'`,
  1400×788 viewport, device scale 2) and frame them with `tools/interview/browser_frame.py`
  (dark browser bar + URL, so viewers can read the address). Cue each at the first word of
  the sentence that mentions the site.
- **Audio**: auto-mix of the iso mics (idle mic ducked 10 dB to kill the bleed comb, talkers
  levelled to the same speech median), then the presentation voice chain and −16 LUFS.
- Pauses where both mics are quiet > 1.5 s are trimmed to 0.6 s and always land on an angle
  change (style guide pacing; none occurred in the first interview).

`--plan` prints the shot list (output time, mic time, shot) — read it before rendering; `--only
a-b` renders a range of units for a check.
