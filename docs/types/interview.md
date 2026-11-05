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
- **Angle variety inside a turn** (cut logic §2): the talker's camera first, then alternate
  between the wide camera (wide / a 1.7× side crop on the talker) and the talker's camera
  (close / tight) every 20-40 s, each cut in a breath pause (both mics < 45 dB for ≥ 0.3 s;
  the quietest 100 ms if there's none). Exchanges under 5 s hold the wide; turns under 2.5 s
  are backchannels. **Never cut between two framings of one camera** (user feedback
  2026-11-04: a punch-out to the same camera that then pushes in again reads as a jump) — if
  the talker's camera is already up, that shot just continues. First cut ran ~5 cuts/min and
  was "hopping a bit too fast"; ~3/min (median shot 23 s) is the target.
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

### Cold-open teaser, shorts, thumbnails (same session)

- `tools/interview/teaser.py`: 4-6 strong lines (a big question from the host, the guest's most
  surprising lines), each 2-4 s, letterboxed, white-flash cuts with synthesized impacts over a
  building drone/pulse (no library music), then a title card. `--into-longform` prepends it to
  the built long-form by stream copy (set `longform.output` to `work/longform_body.mp4`; the
  final goes to `exports/<slug>.mp4`). Chapter times shift by the teaser length. End each line
  inside the pause before the next word (check the 10 ms envelope) — the first cut ended 0.1 s
  into "Right." and the user heard it.
- `tools/interview/interview_shorts.py`: the presentation shorts engine with speaker-chosen
  cameras (talker's close camera, alternating with the wide camera cropped on them — virtual
  cameras `Bh`/`Bg` in `project.json`). Interview shorts may run **30 s - 3 min** (user,
  2026-11-04): use the whole arc of an answer. Ranges accept `exact_start` to drop a stutter
  with no pause before it. Run the disfluent Whisper pass only over the short ranges.
  **An angle holds at least 15 s** (user, 2026-11-04: 4-7 s angle changes were too busy): one
  slow zoom per hold; trims inside a hold are 6-frame dissolves on the same angle; a change goes
  to whoever holds the floor next (a short question plays over the listener); a talker past
  ~40 s gets their other angle once. Website plates in a short: ~4.5 s each, not 3 s.
- Thumbnails (`tools/presentation/thumbs.py`): intrigue with a kernel of truth (a real quote, the
  site's own art or merch titles); **no text over the face** — measure each line's right edge
  against the face position, then look at the render.
