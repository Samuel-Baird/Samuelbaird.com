# Presentation (multicam talk + slides) → long-form, highlight shorts, thumbnails, copy

A presenter at a desk talking through slides (charts, survey results, a summary card), recorded
on **two cameras** (front + side) with an **external mic**, slides **not** shown on screen during
recording. Optionally the same session also has **stand-alone segments** (a separately read
story) that become their own vertical shorts. First done for *State of Theology* + *The Latin
Mass in the St. George Tabernacle* (2026-10-30 session, edited 2026-11-01/02); the worked
config is [`assets/presentation/state-of-theology.project.json`](../../assets/presentation/state-of-theology.project.json)
and the publishing copy is under `reviews/state-of-theology/` and `reviews/st-george-latin-mass/`.

**Rendered with ffmpeg, not DaVinci Resolve.** Every step below is a script in
`tools/presentation/` driven by one `project.json`, so a change (a cut, a slide cue, a caption
spelling) is an edit to that file and a re-run, and only the affected pieces re-render.

**No pre-production gate** (unlike solo-history's `.docx` or clips' written approval): build
everything, then the user reviews the renders. Standard brand only — never Saint Capybara.

## Deliverables (all of them, every time)

| What | Spec | Where |
|---|---|---|
| Long-form | 1920×1080, 23.976, H.264 CRF 17, AAC 320k, −16 LUFS | `exports/<slug>.mp4` |
| 2-3 highlight shorts from the long-form | 1080×1920, burned captions, −14 LUFS, 40-80 s | `exports/shorts/<title>.mp4` |
| A short per stand-alone segment | same, with sourced historical photos | `exports/shorts/<title>.mp4` |
| YouTube thumbnails for the long-form | 1280×720, at least 3 options (one per title idea the user gives) | `exports/thumbnails/` |
| Instagram cover per short | 1080×1920, headline inside the 4:5 grid crop | `exports/thumbnails/` |
| Titles + descriptions + IG captions for every video | `reviews/<slug>/publishing.md` (pushed) and `exports/publishing.md` | |
| Photo credits (if any CC BY-SA image is used) | `exports/shorts/<short> photo credits.txt` + in the description | |

Look and type for all of it: [`docs/style-guide.md`](../style-guide.md) "Brand kit".

## 0. Setup (once per machine)

- ffmpeg (full build, has libass for captions): `winget install --id Gyan.FFmpeg -e`. The tools
  find it on PATH or in the winget folder.
- `pip install faster-whisper numpy Pillow` (see `tools/requirements.txt`). CPU only here: the
  `medium.en` model transcribes at roughly real time.
- Segoe UI Black / Bold ship with Windows (`C:\Windows\Fonts\seguibl.ttf`, `segoeuib.ttf`).
- A camera card on an exFAT/external drive makes git and some tools complain about ownership;
  keep the repo on C:, and use `git -c safe.directory=<path>` rather than changing global config.

## 1. Intake

Ask only what the files can't tell you:

1. Slug, and where the card dumps are (camera folders, recorder folder, slide images).
2. Which recording is the main talk if there are several takes, and what any other take is.
   (Usually answerable from the transcript; ask only if it isn't.)
3. Stats graphics for the shorts: the user may point at a page of social graphics (e.g.
   `latterdaystats.samuelbaird.com/data-explorer/<study>/social/post2`). Download every PNG on it
   into `graphics/` (they are the user's own; the page lists them as `/social-graphics/...png`).
4. Any titles/thumbnail ideas they already have.

Then `python tools/presentation/new.py <slug>` and copy the card folders in. Fill in
`project.json` → `takes`: one entry per recorder take, each with its mic file (`*_Tr1.WAV`, the
isolated mic track — not the `TrL_R` stereo mix) and the camera clip that covers it on each
camera. Match takes by duration and file times (`ffprobe`): a Sony camera splits a long take at
~4 GB, but here each camera clip lined up 1:1 with a recorder take.

## 2. Sync

`python tools/presentation/sync.py D:\Videos\<slug>` writes each camera's offset. Expect peak
ratios > 4 and start/end drift ≤ 2 ms (State of Theology: offsets +5.30 s / +5.33 s, drift 1 ms
over 15 min). The mic is the only audio used anywhere.

## 3. Transcribe and read

`python tools/presentation/transcribe.py D:\Videos\<slug>` → `work/transcripts/take<k>.txt|.json`
(clean) and `take<k>.fillers.json` (ums written out; see "Shorts"). **Read the whole transcript**
before planning. Things it shows:

- sound check / small talk to skip at the start; "thanks for watching" at the end;
- retakes in a read segment ("restart", "go back", the same sentence twice): use the last clean
  attempt of each sentence;
- asides the user may want gone. If something undercuts the video (State of Theology had "I
  made some random numbers up for this"), **don't cut it silently — flag it** in the hand-off
  and cut on request (`longform.cuts`).

## 4. Slides: rename by content

Make a labelled contact sheet of `images/` and look at every slide. Rename to
`NN[a-d]_<kind>_<topic>_<stance>.png`, keeping the deck order in the number — e.g.
`03_pct_trinity_agree.png`, `14_count_trinity_disagree.png`, `12b_summary_doctrine_vs_culture_war.png`,
`12c_method_how_raw_numbers_estimated.png`. Keep a `rename_map.txt` (old|new) in `work/`. Not
every slide gets used (a deck may have agree *and* disagree versions; show the one the speaker
talks about).

## 5. Plan the long-form (`project.json` → `longform`)

- `start` just before the first real sentence, `end` ~1 s after the sign-off.
- `plan`: `[mic_time, "cam"]` or `[mic_time, "slide", "<slide stem>"]`; each runs until the next
  entry. Put a slide at the first word of the sentence that introduces it ("The next question…",
  "So we can actually estimate this"), and go back to `"cam"` when the speaker moves into
  commentary rather than leaving a slide up for minutes. Find times with word timestamps, then
  sanity-check against the silences: Whisper's word *start* can sit up to ~1 s early (it
  swallows the preceding pause), so a slide landing in the pause before the sentence is right.
- Open on the front camera (the first `"cam"` entry runs to the first slide; it fades in from black).
- `cuts`: `[{start, end, why}]` mic-time spans to remove, end on a silence. The cut is hidden by a
  10-frame dissolve of the slide/camera window.
- Camera faces: `takes.<k>.cameras.<X>.face` = face centre as fractions of the 4K frame (grab a
  gridded frame from a few points in the take to check the speaker doesn't drift).

`python tools/presentation/longform.py D:\Videos\<slug> --plan` prints every unit; then run it
without `--plan` (≈10-25 min on this laptop). What it does, so it isn't reinvented:

- **Slides:** split layout — slide card (1400×788) on a dark gradient backdrop with the live front
  camera in a 392×788 rounded window beside it, so the speaker never disappears for minutes.
  Slides and layout changes crossfade over 10 frames.
- **Camera:** 9-19 s shots cut at sentence starts, cycling front/side and wide/medium/close
  framings, each with a slow push or pull. Zooms are **sub-pixel perspective warps**, not
  `zoompan` (zoompan rounds the crop to whole pixels and slow zooms visibly judder — the user
  noticed; measured 0.3 px → 0.03 px frame-to-frame wobble after the switch).
- **Grade:** light contrast/saturation lift + soft vignette.
- **Audio:** mic only, voice chain (high-pass 80 Hz, −1.5 dB @ 250 Hz, +1.5 dB @ 4.5 kHz, 2.5:1
  compression) and two-pass loudnorm to −16 LUFS / −1.5 dBTP. Mono is duplicated to stereo, which
  reads +3 LU, so the mono target is −19. Pauses are left natural (style guide: only > 1.5 s).

QC: frame count = audio length exactly (2002 samples/frame at 48 kHz), `ffmpeg -v error -f null`
decodes clean, frame-grab a slide, a camera shot and the cut, and transcribe the seconds around
any cut to confirm the line is gone.

## 6. Highlight shorts (2-3 per long-form, no approval gate)

Pick the 2-3 strongest self-contained stretches (State of Theology made five; three is plenty):

- **one number with a payoff**, ideally the speaker's own comparison ("19× more Arians than
  Latter-day Saints", "more Christians reject the Trinity than there are Latter-day Saints");
- hook in the first 3 s, ends on a finished thought, 40-80 s after trims;
- skip stretches that need the earlier setup to make sense.

For each: `shorts.<name>` with `take`, `title`, `hook` (two short lines, shown 0-3 s over the
opening camera shot), `ranges` (can join two stretches of the talk), and `graphics` (the matching
stats graphics, full screen, timed from the statement being read through the numbers). Then
`shorts.py <slug> <name> --plan` (shot list + caption text) → build → `verify.py`.

The editing rules (`tools/presentation/shorts.py` header), all from user feedback:

- **Silences and ums are trimmed.** Pauses > 0.3 s → ~0.2 s. Ums come from a second Whisper pass
  prompted with disfluent text (Whisper normally omits them); each candidate is only cut if the
  audio shows it as its own burst between the neighbouring words' sounds — the prompted pass
  sometimes invents an "uh" and gives it the next word's timing (it once deleted a real "with").
- **Angles hold.** An angle stays 3.6-8 s with a slow zoom; never alternate on every cut ("some of
  the jumps are really fast"). A trim on camera becomes an angle change only once the angle has
  held 3.6 s; otherwise ums and long pauses are still cut behind a 6-frame same-angle dissolve.
- **Graphics full screen.** Stats graphics fill the frame (their paper colour extended to 9:16)
  with a slow push-in; trims underneath are invisible, so put the dense trimming there.
  Camera slivers under 3 s between graphics are absorbed into the graphic.
- **Captions:** brand style (uppercase, 2-3 words, spoken word yellow), placed per layout; fix
  mis-heard names in `caption_fixes` (they're checked against the source, e.g. Commons/biographies).
- **Audio** −14 LUFS stereo. `fade_out` for an ending that should fade to black.

`verify.py` re-transcribes every built short and diffs it against the source words: read every
reported gap — almost all are the checker mis-hearing ("U S", "1870s"), but a real one means a
trim clipped a word.

## 7. Stand-alone segments (story shorts)

Same `shorts` entry, but:

- `ranges` = the last clean attempt of each sentence group (restarts dropped). Use
  `[from, to, "exact_end"]` to stop before a closing line the user doesn't want (St. George: end on
  "…due consideration and respect.", drop "Amen, Father"), with `fade_out: 0.6`.
- **Historical photos** at the moment each person/place/event is named, roughly every 5-15 s:
  search Wikimedia Commons via its API (`action=query&generator=search&gsrnamespace=6` and
  `generator=categorymembers` on the subject's category; send a User-Agent, pause ~3 s between
  calls — it rate-limits with HTTP 429). Prefer public domain (HABS surveys, pre-1929 portraits,
  period engravings); record every file's licence/author/page (`imageinfo&iiprop=extmetadata`)
  in `graphics/credits.json`; download the `thumburl` at ≤ 2000 px (note: Commons serves those as
  JPEG even for PNG originals). Never generate or guess an image. CC BY-SA images are fine but
  their credit goes in every post's description.
- Photo plates: rounded photo over a blurred, darkened copy of itself, label chip underneath
  ("Fr. Lawrence Scanlan", "Camp Floyd, c. 1858"); two portraits side by side with `image: [a, b]`;
  `crop` trims scan borders.

## 8. Thumbnails and covers

Specs in `project.json` → `thumbnails`, rendered by `thumbs.py` (see its header for the element
types). For the long-form make one thumbnail per title idea (the user gave eight; make them all);
for each short one Instagram cover. Rules that came from review:

- a frame with **eye contact** (pull 10-15 candidates across the take, pick from a contact sheet;
  avoid downward glances at the laptop);
- big orange number/key phrase, white supporting line, red for the negative word, a red tag or
  chip for scope — **say it's U.S. data** ("IN THE USA", "AMERICAN CHRISTIANS", "U.S. Christians");
- text on the dark side, never over the face; a chart card or simple diagram only if it reads at
  phone size;
- covers: headline between y≈420-1500 so both the 4:5 profile grid and the old 1:1 crop keep
  it (`thumbs.py` writes a `_check.jpg` showing both crops);
- if a number comes from a different survey wave than the rest, the label says so.

## 9. Titles, descriptions, captions

Write `reviews/<slug>/publishing.md` (template: `reviews/state-of-theology/publishing.md`) with:

- **Long-form:** the title options (pair each with its thumbnail), a description that states the
  claim, the "not calling anyone a heretic / tell me if I got the data wrong" framing the speaker
  uses, **chapters** (from the plan: `Edit.fr(mic_time)` → output time; first at 0:00, each ≥ 10 s),
  and the data sources with years.
- **Each short:** YouTube title (≤ 70 chars, U.S. qualifier where it applies) and a 1-2 sentence
  description with the number and source; Instagram caption kept **short**: one-line hook, "Full
  video on YouTube now, link in bio!" (only when a long-form exists), one data line, 4-5 hashtags,
  and photo credits when required.

Push `publishing.md` and give the user the branch link (pipeline §1 step 4a).

## 10. Hand-off

Report **ready for review**, not done (pipeline §4.4). List: what was cut and why, anything
flagged but left in, which images need credits, and the paths. Expect a round of notes; every
note so far became a rule above.
