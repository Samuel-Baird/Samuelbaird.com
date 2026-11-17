# Clips

Short social clips cut from one long-form video: a solo podcast, a
dialogue, an interview, or a debate. The long-form video is given; the
agent transcribes it, finds the best moments, proposes several numbered
clips in one review document (full transcript at the bottom, like the
Saint Capybara scripts), and — **only after the user approves the clips in
writing** — builds and renders every approved clip in DaVinci Resolve.

| Step | What | Made with |
|---|---|---|
| Ingest | Long-form video into `source\source.mp4` | `tools/capy_ingest.py` (URL) or a local copy |
| Transcribe | Word-timestamped transcript | `tools/transcribe.py` → `transcripts\source.json` |
| Pick | The proposed clips, hand-authored | `script\clips.yaml` (template: `assets/clips/clips.yaml`) |
| Review | Numbered clips + full transcript | `tools/clips_plan.py` → `script\clips.md` |
| **Gate** | User approves in writing | recorded in `clips.yaml` `approval:` |
| Build | One Resolve timeline + render per approved clip | `tools/clips_plan.py --build-plan` → davinci-resolve MCP |

**Not for highlight shorts from a presentation-type video.** Those 2-3
shorts are built straight from the camera originals by
`tools/presentation/shorts.py` with no approval gate (the user reviews the
renders) — see `docs/types/presentation.md`. This type and its written
gate are for clips from someone else's show, a dialogue/interview/debate,
or any long-form that only exists as a finished file.

Look: same brand as every other vertical video — burned captions, hook
card and Reel cover per `docs/style-guide.md` "Brand kit", and the shorts
pacing rule there (tight trims, but angles/framings held 3.6-8 s, never
flipping on every cut).

Standard brand only. Never use anything from `assets/saint-capybara/` on
a clip, and never put a Saint Capybara clip through this type — that brand
has its own pipeline and anonymity rules (`docs/types/saint-capybara.md`).

## Intake — ask

1. The long-form source: URL or local file, and whose it is (the
   creator's own show, or someone else's — credit either way).
2. Kind: **solo / dialogue / interview / debate** (drives reframing and the
   fairness check below).
3. Format: **vertical 9:16** (default — Shorts/Reels/TikTok), landscape
   16:9, or square.
4. Captions: **burned** (default) or none.
5. Roughly how many clips and how long (defaults: as many strong moments
   as the source has, typically 3-10; 15-90s each).

Then `tools/new_project.ps1 -Slug <slug> -Type clips -Kind <kind>`.

## Project layout

```
D:\Videos\<slug>\
  source\       source.mp4 (+ source_info.json when ingested from a URL)
  transcripts\  source.json/.srt/.txt (+ .meta.json)
  script\       clips.yaml, clips.md, clips.build.json (after approval)
  captions\     <id>.srt per approved clip (captions: burned)
  exports\      <slug>-<id>.mp4 per clip
```

## Finding the best moments

Read the whole transcript before choosing anything. A good clip:

- **Hooks in the first ~3 seconds** — a claim, question, story turn, or
  surprising line. Start on it, not on the warm-up before it (trim "so,
  um, yeah, I think..." into a later start, or use a `cuts:` span).
- **Stands alone** — no dangling "like I said earlier", "that", or "he"
  without its referent. If it needs context, start earlier or add an
  on-screen `hook:` line; don't propose it otherwise.
- **Is one idea with a payoff** and **ends on a finished thought** — the
  punchline, conclusion, or strongest line, never mid-sentence.
- **Fits the length target** (15-90s by default; 180s hard cap for
  vertical). Shorter usually wins.
- Prefer variety across the set: different topics, and for multi-person
  sources, different speakers.

**Fairness (dialogue / interview / debate).** A clip must not
misrepresent anyone's position: don't end a speaker's turn before their
qualifier, don't cut a question so the answer reads as something else,
and in a debate don't clip only one side's best moments while framing it
as a win. Fill each clip's `context:` with how it stays fair. `cuts:`
inside a clip are for filler and dead air only, never for joining two
things a person said into a sentence they didn't say.

Rank by strength; propose the set in source order unless an order matters
for posting.

## The review document — the gate

1. Fill `script\clips.yaml` (one entry per clip: id, title, start/end,
   `why`, optional `hook`/`cuts`/`caption`/`speakers`/`context`, and
   `reframe` for non-landscape formats).
2. `python tools/clips_plan.py --project D:\Videos\<slug>` → lints and
   writes `script\clips.md`: a header, then `## 01. <title> (~Ns)` per
   clip (in–out, opening line, why it works, reframe, transcript with any
   cut words struck through, blank **Notes:**), then the **full source
   transcript** with `▶ Clip NN starts` / `■ Clip NN ends` markers, then
   source credit. Clear its errors; read its warnings (mid-word boundary,
   mid-sentence ending, length) and fix or justify each.
3. Push for review — copy `clips.md` to `reviews/<slug>/clips.md`, commit,
   push, send the **branch** link (`docs/pipeline.md` §1 step 4a).
4. Send the gate message (close paraphrase OK, keep every clause):

   > **Clips ready for review.** `script/clips.md` proposes *N* clips
   > (numbered 01-*N*), with the full transcript at the bottom. This is a
   > hard stop: **nothing will be built or rendered in DaVinci Resolve
   > until you approve the clips in writing.** Reply `approved` for all,
   > `approve 1, 3, 4` for a subset, or edit the doc (`DROP`, `TRIM START
   > mm:ss`, `TRIM END mm:ss`, or plain-language notes per clip).

5. **Wait.** Apply any edits, re-run `clips_plan.py`, and re-send if the
   set changed. Approval has to be the user's own written words naming
   the clips (or "all"/"approved") — silence, a thumbs-up on a different
   question, or approval of an earlier version of a changed clip is not
   approval. Record it:

   ```yaml
   approval:
     date: 2026-10-17
     words: "approve 1, 3 and 4"
     clips: [1, 3, 4]
   ```

   `--build-plan` refuses to run without it.

## Build (DaVinci Resolve)

1. `python tools/clips_plan.py --project D:\Videos\<slug> --build-plan
   --fps <source fps> --source-size <WxH>` (both from `ffprobe` on
   `source\source.mp4`) → `script\clips.build.json` and, for burned
   captions, `captions\<id>.srt` (times already rebased to each clip's own
   timeline with cuts closed up). Only approved clips are included.
2. Create one Resolve project named `<slug>`; import `source\source.mp4`
   once.
3. Per clip in `clips.build.json` (shared mechanics in `docs/pipeline.md`
   §3 and `docs/resolve-mcp-gotchas.md`):
   - Create a timeline named by the plan's `timeline` (`<slug>-<id>`) at its
     `canvas` and the source fps. For non-landscape formats use
     timeline-specific settings and set the resolution-mismatch behaviour
     to scale-to-fill ("Scale full frame with crop"); verify with
     `get_setting` — writes can silently revert (gotchas, "Project
     settings").
   - Append each `pieces[]` entry with its `start_frame`/`end_frame` at
     its `record_frame` (V1 + A1). Pieces abut exactly; a clip with no
     cuts or reframe switches is one piece.
   - Set each item's `Pan` to the piece's `pan` (horizontal crop centre).
     **On the first build, grab a frame per reframe position and check the
     speaker is actually centred** — the pan values assume scale-to-fill
     and haven't been calibrated against every Resolve version; adjust the
     speaker `x` in `clips.yaml` and regenerate rather than hand-nudging.
   - Captions: render the clip without captions, then burn them in the
     brand style with ffmpeg + libass — the ASS header and per-word
     highlight logic are in `tools/presentation/brand.py` /
     `tools/presentation/shorts.py` (`write_ass`), fed from
     `captions\<id>.srt`'s word timing. (Resolve's subtitle track can't do
     the per-word highlight; the old "import the .srt onto the subtitle
     track" route is superseded.) Never caption by hand-retyping.
   - Save, re-read the item count, `timeline.detect_gaps_overlaps`.
   - Queue a render job to the plan's `export` path (H.264 MP4).
4. Render the queue; check every file exists and its duration matches
   `total_frames / fps`.

## QC

- Watch each clip at phone size, with sound and muted: hook lands in the
  first ~3s, no mid-word in/out, captions readable and in sync, the
  speaker stays in frame through every reframe switch.
- Spot-check that no clip changed what anyone meant (fairness, above).
- Credit the long-form source in each clip's description.
- Report "ready for review", never "done" — the user's watch-through
  comes last (`docs/pipeline.md` §4.4).
