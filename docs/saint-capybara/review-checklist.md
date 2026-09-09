# Saint Capybara — review checklist

## Part A — pre-Gate-A (before presenting `script.md` for approval)

Run through all 12 before sending the Gate A message in
`script-format.md`:

1. **Adversarial review** done for every claim responded to (`claims.md`
   has both questions answered — see `research-protocol.md` sec 14).
2. **Tone lint** — no polemics, ad hominem, "destroyed/owned/cope/rekt,"
   sarcasm-as-argument, or treating a critic's honest concern as bad
   faith (see `brand.md` sec 2 "Never" list). Manual read-through plus
   `capy_check_brand.py`'s banned-phrase scan.
3. **Source lint** — `tools/capy_check_sources.py` passes (every factual
   beat cited, all ids resolve and are `inspected: true`, card quotes are
   verbatim substrings of their source's recorded `quote`).
4. **Evidence grading** — every claim in `claims.md` has a
   fact/inference/disputed/speculation grade, and the narration's
   confidence language matches the grade (don't state an inference with
   fact-level confidence).
5. **Doctrine-vs-opinion classification** — every doctrinal claim is
   pinned to one of the six tiers (`research-protocol.md` sec 5), dated,
   never a bare "the Church teaches" for tiers 4-6.
6. **Clip fairness** — critic's own words, hedges kept, one continuous
   span per clip beat, ≤20s continuous, source clip time ≤30% of runtime,
   source title/creator visible on screen.
7. **Duration** — `capy.beats.resolve_durations` + `check_duration_budget`
   report the total inside 60-180s (or a documented, deliberate decision
   to split into two slugs).
8. **Sensitive flag** — `sensitive: true` set if any beat touches a
   sensitive topic (`research-protocol.md` sec 11), and no
   `amused`/`happy` pose anywhere in the video if so.
9. **Escalation** — no unresolved `research/ESCALATION.md` blocking any
   beat in this video.
10. **Brand lint** — `tools/capy_check_brand.py` passes: no banned
    phrases, no home-directory paths, no creator-identifying text in
    beats/description/sources notes.
11. **Sprite map** — every beat's resolved pose exists in
    `assets/saint-capybara/sprites/manifest.json` and isn't
    sensitive-forbidden.
12. **Pronunciations** — every proper noun appearing in narration has an
    entry in `script/pronunciations.yaml` (or an explicit "ok-as-is"
    note) per `docs/saint-capybara/pronunciations.md`.

Only after all 12 pass: render `frames/storyboard.png` + `script/script.md`
and send the Gate A message. **Stop there.**

## Part B — post-approval, before calling a render "ready for review"

(These apply to the render/description steps built in Step 7 of the plan —
not part of this session's Gate-A-only scope, listed here for completeness
and so future sessions on this project use the same checklist.)

1. TTS listen-through of every narration/card/evidence/chart/outro beat —
   pacing, mispronunciations, unnatural emphasis.
2. Caption sync spot-check — a few beats compared by eye against the
   audio.
3. Phone legibility — view `storyboard.png`/a real frame at actual phone
   size, not just on a desktop monitor.
4. Evidence hold — every evidence/card beat held long enough to actually
   read (`capy.beats.estimate_hold_seconds` honored, not undercut by a
   short TTS line).
5. Metadata clean — `ffprobe` tags allow-list only (`title` and required
   container fields), no `encoder` tag, no home-directory paths anywhere.
6. Muted-viewing pass — captions alone convey the argument (many viewers
   watch Shorts muted).
7. Anonymity pass — re-run `capy_check_brand.py --mp4`, re-check
   filenames under `D:\Videos\<slug>\` for anything identifying.
8. **"Ready for review" hand-off** — the agent never says a video is
   "done" or "published"; it reports "ready for review" and waits for the
   user's own watch-through (Gate B, inherits `docs/pipeline.md` sec 4.4).
