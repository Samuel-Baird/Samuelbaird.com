# Memes / edits

Short comedic edits: take a base video, cut in funny insert clips, and add
on-screen meme text and/or synthetic (TTS) voice lines. Usually 10-60s,
vertical 9:16. Built in DaVinci Resolve like the other types, but the
timeline is assembled from four layers instead of camera cuts:

| Layer | What | Made with |
|---|---|---|
| Base | The video being edited (`source\source.mp4`) | `tools/capy_ingest.py` (URL) or a local file |
| Inserts | Short reaction/punchline clips cut in or overlaid | Trimmed from their own sources, recorded in the plan |
| Text | Meme captions ("when the...", labels, punchlines) | `tools/meme_text.py` → transparent PNGs |
| Voice / SFX | TTS voice lines, sound effects | `tools/capy_tts.py --sample` (Kokoro), licensed SFX |

## Brand — ask first

A meme can be made for **either** identity, and the answer changes almost
every rule below. At intake, ask: **standard** (the creator's own
identity) or **saint-capybara**? Never guess.

- **saint-capybara:** every rule in `docs/saint-capybara/brand.md` applies,
  sec 9-10 anonymity first. Use only that brand's assets: its fonts
  (`meme_text.py --brand saint-capybara`), its sprites (the capybara can be
  an insert — `deadpan`, `surprised`, `confused`, `amused` read well as
  reaction shots), its locked host voice (`am_michael` @ 1.5) when the
  capybara speaks. Tone rules still hold — humor aims at situations,
  arguments, and the capybara himself, never at a real person (sec 2's
  "Never" list: no mocking, no rage-bait words). Any factual claim the
  meme makes still needs a source (`research-protocol.md`). The closing
  "...God bless." rule (sec 5a) applies unless the user waives it for that
  video; on a meme it can be the capybara's last line or end-card text.
  Final export gets the metadata-strip remux and
  `tools/capy_check_brand.py --project <dir> --mp4 <final>`.
- **standard:** never use anything from `assets/saint-capybara/` (sprites,
  pixel fonts, palette) and never use the `am_michael` voice — those are
  Saint Capybara's signature and reusing them links the two identities.
  `meme_text.py` defaults to Impact for this brand.

## AI voices and text — hard limits

- **Never clone or imitate a real, identifiable person's voice**, and never
  put fabricated words in a real person's mouth (TTS, dubbed audio, or
  on-screen text presented as their quote). Generic synthetic voices only
  (Kokoro's stock voices — `tools/capy_voice_audition.py --out <dir>
  --voices <ids>` to preview). `capy_tts.py --sample` defaults to
  `am_michael`, so a standard-brand meme must always pass `--voice`.
- On-screen text must read as the editor's joke, not as a fake caption,
  headline, or quote attributed to someone real.
- Never generate a realistic image or video of a real person.

## Source clips

- Record every insert in the plan's provenance table: what it is, where it
  came from (URL or file), the in/out used. No unlabeled clips.
- Keep inserts short (a beat or two, typically ≤5s) and transformative —
  the edit is the point, not a re-upload of someone else's footage.
- The base video's creator gets credit in the description per the user's
  usual practice (same as `response.md`'s QC note).

## Project layout

```
D:\Videos\<slug>\
  source\     base video (source.mp4 + source_info.json when ingested)
  inserts\    trimmed insert clips, one file per cue (i01.mp4, i02.mp4, ...)
  overlays\   meme_text.py PNGs (t01.png, ...)
  audio\      TTS voice lines (v01.wav, ...), SFX (sfx01.wav, ...)
  script\     edit-plan.md
  exports\    final render
```

Create with `tools/new_project.ps1 -Slug <slug> -Type meme-edit -Brand
standard|saint-capybara` — copies `assets/meme-edit/edit-plan.md` into
`script\` with the slug and brand filled in.

## Pre-production — the edit plan (a gate)

1. **Ingest + transcribe** the base video (`tools/transcribe.py`) so cues
   can be anchored to exact words.
2. **Write `script\edit-plan.md`** — the cue sheet: one row per cue with
   base-video timestamp, cue type (`insert` / `text` / `voice` / `sfx` /
   `cut` / `freeze` / `zoom`), content, and duration. Plus the provenance
   table and the voice list. Keep it to the jokes that land; a meme with
   three good beats beats one with ten.
3. **Push for review** — copy to `reviews/<slug>/edit-plan.md`, commit,
   push, and send the branch link (`docs/pipeline.md` §1 step 4a).
4. **Wait.** No TTS, no overlays, no timeline until the user approves the
   plan. Memes are cheap to build, but a joke that misses is cheaper to
   kill on paper.

## Build

1. **Assets:** `meme_text.py` per text cue → `overlays\`;
   `capy_tts.py --sample "<line>" --out audio\vNN.wav --voice <voice>
   --speed <speed>` per voice cue; trim inserts to `inserts\`.
2. **Timeline** (shared mechanics in `docs/pipeline.md` §3 and
   `docs/resolve-mcp-gotchas.md`):
   - V1: base video, cut per the plan (`cut` cues remove spans; a
     cut-away `insert` replaces base picture for its duration).
   - V2: overlaid inserts (picture-in-picture / green-screen reactions).
   - V3: text PNGs as stills — cap each still's duration at the next
     placement on that track (overlaps silently drop the later clip).
   - A1: base audio (duck under voice lines); A2: voice lines; A3: SFX.
3. Render to `exports\<slug>.mp4`. Saint Capybara memes then get the
   metadata-strip remux + brand lint (see Brand above).

## QC

- Watch it at phone size with sound **and** muted — every text cue must
  be readable in the time it's on screen (≈3s + 0.15s/word).
- Text sits inside the safe zone (not under platform UI) — `meme_text.py`
  positions handle this; check any manual placement.
- Voice lines aren't clipped and don't step on base dialogue the joke
  depends on.
- Provenance table is complete; base-video credit is in the description.
- Report "ready for review", never "done" — the user's watch-through comes
  last (`docs/pipeline.md` §4.4).
