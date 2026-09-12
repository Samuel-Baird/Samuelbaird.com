# Saint Capybara — review checklist

## Part A — pre-Gate-A (before presenting `script.md` for approval)

Run through all 15 before sending the Gate A message in
`script-format.md`:

1. **Adversarial review** done for every claim responded to (`claims.md`
   has both questions answered — see `research-protocol.md` sec 14).
2. **Tone lint** — no polemics, ad hominem, "destroyed/owned/cope/rekt,"
   sarcasm-as-argument, or treating a critic's honest concern as bad
   faith (see `brand.md` sec 2 "Never" list). Manual read-through plus
   `capy_check_brand.py`'s banned-phrase scan.
3. **Source lint** — `tools/capy_check_sources.py` passes (every factual
   beat cited, all ids resolve and are `inspected: true`, card quotes are
   verbatim substrings of their source's recorded `quote`; on an article
   project, every `excerpt` beat is a verbatim, in-order match of its
   anchored paragraph(s) in `source/source.md`, whose sha256 still equals
   the `text_sha256` pinned at ingest, and the article's `critic` entry
   has `url` + `archive_url`).
4. **Evidence grading** — every claim in `claims.md` has a
   fact/inference/disputed/speculation grade, and the narration's
   confidence language matches the grade (don't state an inference with
   fact-level confidence).
5. **Doctrine-vs-opinion classification** — every doctrinal claim is
   pinned to one of the six tiers (`research-protocol.md` sec 5), dated,
   never a bare "the Church teaches" for tiers 4-6.
6. **Clip/excerpt fairness** — the source's own words, hedges kept.
   Clips: one continuous span per beat, ≤20s. Excerpts: one anchored
   span (`para: N` or one paragraph boundary), ≤60 words, `[...]` marks
   every cut and never sits at the edges, the neighbours were read
   ("Anchor context" in `claims.md`), and the excerpt precedes the
   response to it exactly as a clip would. Source time (clips +
   excerpts) ≤30% of runtime — `capy_check_sources.py` now errors on
   this. The source is credited in the description (title, creator or
   publication, URL, archive URL for articles).
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
13. **Clip-beat pose variety** — `clip` beats react to what the source is
    saying (see `brand.md`), not blanket `pose: listening`. Flag if most
    or all `clip` beats in the video share the same pose.
14. **Response-to-clip alignment** — every beat group's response text is
    actually about the claim in its immediately preceding clip/excerpt
    beat, not a claim that only exists in the fuller source transcript or
    article (see `script-format.md`'s "Response-to-clip alignment"
    standing rule).
15. **Critique** — `/capy-critique` (`research-protocol.md` sec 15;
    `.claude/skills/capy-critique/`) has been run against the rendered
    `script.md`; `research/critique.md` exists with no open BLOCKER
    finding, and any MAJOR/MINOR findings are summarized in the Gate A
    message for the user's review.

Only after all 15 pass: render `frames/storyboard.png` + `script/script.md`
and send the Gate A message. **Stop there.**

## Part B — post-approval, before calling a render "ready for review"

(These apply to the render/description steps built in Step 7 of the plan —
not part of this session's Gate-A-only scope, listed here for completeness
and so future sessions on this project use the same checklist.)

1. TTS listen-through of every narration/card/evidence/chart beat —
   pacing, mispronunciations, unnatural emphasis. Confirm the closing beat
   actually lands on "...God bless." on screen and in audio.
   1b. **Quote-voice listen-through** of every `excerpt` beat — the second
   voice reads the source's words verbatim, its sex matches the person
   quoted (`voice: quote_male | quote_female`), the `[...]` pause lands
   where the cut is, and the contrast with the host voice is audible
   (compare `audio/x01.norm.wav` against a neighbouring narration beat).
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
