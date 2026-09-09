# Saint Capybara

A separate branch from `docs/pipeline.md`'s response/interview/solo-history
flow — its own pre-production gate, its own render pipeline (DaVinci
Resolve, but built differently than the other three types — see
`docs/saint-capybara/hybrid-resolve-pipeline.md`), no shared visual
identity with the other three types. Read `docs/saint-capybara/brand.md`
first; it is the source of truth for tone, visual design, and the
anonymity rules that make this type work at all. Read
`docs/saint-capybara/apologetics-playbook.md` alongside it before writing
any response-video script — it's the argument-craft companion to
`brand.md` sec 2's tone (six-step structure, audience-specific
playbooks, overclaiming discipline, the pre-publish two-question test).

**Uses DaVinci Resolve, but not the other types' Build stage.** Saint
Capybara videos ARE edited and rendered in Resolve (via the
davinci-resolve MCP) — the old "ffmpeg-only, no Resolve at all" plan is
retired. What's different from response/interview/solo-history is *how*
the Resolve timeline gets built: each beat is pre-composited into one
self-contained clip (chrome + captions + audio baked in with ffmpeg, see
`docs/saint-capybara/hybrid-resolve-pipeline.md`) before Resolve ever
imports it, rather than cutting raw camera footage directly. Don't follow
`docs/pipeline.md` §3's build mechanics for this type; follow the
Resolve build checklist in `hybrid-resolve-pipeline.md` instead.

## What this type does NOT use

- No `docs/script-doc-format.md` `.docx` script — Saint Capybara's script
  artifact is `script/beats.yaml` (source of truth) and `script/script.md`
  (rendered for review).
- No `docs/style-guide.md` visual system (charcoal quote cards, cream
  serif, bottom-left credit chip, music). Saint Capybara has its own
  palette/fonts/layout in `assets/saint-capybara/theme.yaml`.
- No camera footage, no creator voice — TTS narration (Kokoro) and
  pixel-art sprites only. (The source clip being reacted to is real
  footage, same as a response video — it's the *host* that's synthetic.)
- No reuse of any of the creator's other identity: filenames, phrasing,
  usernames, thumbnails. See `docs/saint-capybara/brand.md` sec 9-10
  before doing anything else with this type.

## Source intake

Videos awaiting a reaction (before a project folder exists for them) are
dropped in `D:\saint-capybara-videos-needing-reactions\` — a local-file
staging folder, separate from any `D:\Videos\<slug>\` project. That folder
also holds `need reaction.xlsx`, a running queue with columns `Link to
original` / `Path` / `Video Generated` / `Notes` — check it before assuming
you know the full backlog, and update its `Video Generated` column (mark
`x`) once a project reaches Gate A or ships. Some queue rows are just a URL
(no local file yet — ingest via `capy_ingest.py URL --project ...`, letting
yt_dlp download it) rather than a path into this folder.

## Project layout

```
D:\Videos\<slug>\
  source\       video:   source.mp4 + source_info.json (kind: video)
                article: source.md (numbered ¶ paragraphs, sha256-pinned) +
                         source_info.json (kind: article, url, archive_url, text_sha256)
  transcripts\  source.json/.srt/.txt/.meta.json (tools/transcribe.py, unchanged; video only)
  research\     claims.md, sources.yaml, ESCALATION.md (only when open; renamed
                ESCALATION-resolved.md once the user has signed off)
  images\       cropped evidence PNGs referenced by beats.yaml
  script\       beats.yaml, script.md, pronunciations.yaml
  audio\        <beat_id>.wav / .norm.wav, <beat_id>.timing.json (post-Gate-A)
  captions\     <beat_id>_<n>.png, manifest.json (post-Gate-A)
  frames\       plate_<beat_id>.png, plates_manifest.json,
                beat_<beat_id>.mp4, beat_clips_manifest.json (post-Gate-A)
  exports\      <slug>-resolve.mp4 (Resolve's own render output),
                <slug>.mp4 (final, after the metadata-strip remux pass)
```

Create with `tools/new_project.ps1 -Slug <slug> -Type saint-capybara
[-SourceKind video|article]` — this also copies the beats (`beats.yaml`,
or `beats.article.yaml` for an article source) / sources / claims /
pronunciations templates from `assets/saint-capybara/templates/` with the
slug substituted.

## Pre-production (ends at Gate A — a hard stop)

1. **Ingest.** `tools/capy_ingest.py`, by source kind:
   - **Video:** a URL (yt_dlp download), an existing local file
     (`--file`), or both (local file + `--url` for metadata only). Always
     try to pull title/uploader/canonical-url metadata when a URL is
     available, even if the media itself came from a local file. **Ask the
     user whether the source video already has captions burned in** before
     running this (standing rule, 2026-09-09) and pass
     `--captions-in-source yes|no|unknown` — see `script-format.md`'s
     caption rule for why this matters (short version: clip beats never
     get generated captions either way). Writes `source/source.mp4` +
     `source_info.json` (`kind: video`).
   - **Article:** fetch the page with the agent's own WebFetch (or take
     the user's paste, for paywalled pieces) into a cleaned,
     blank-line-separated text file, then `--article-file cleaned.md
     --article-url URL [--publication --byline --date --paywalled]
     [--archive auto|fresh|skip | --archive-url …]`. Writes
     `source/source.md` (one `¶n` paragraph per block) and
     `source_info.json` (`kind: article`, url, archive receipt,
     `text_sha256` pin). `--article URL --fetch` self-fetches with
     requests + trafilatura and is opt-in (home IP). No media, no Whisper.
2. **Transcribe.** Video only — calls `tools/transcribe.py` unchanged.
   Article projects skip this; `source.md`'s paragraph numbers are the
   anchors.
3. **Triage.** List every discrete claim in `research/claims.md`
   (`docs/saint-capybara/research-protocol.md` sec 1) — anchored by
   timestamp (video) or paragraph number (article); respond / concede /
   skip, with a reason. Not every claim in a source needs (or should get)
   an on-screen response. On an article project the source's own words
   reach the screen as `excerpt` beats (verbatim, `para`-anchored, read by
   the quote voice, ≤30% of runtime together with any clips).
4. **Research.** Pulpit / Gospel Scholar Archive / Latter-day Stats MCP
   tools, per `docs/saint-capybara/research-protocol.md`. Verify every
   quotation before treating it as attributable. Grade every claim
   fact/inference/disputed/speculation. Never fabricate a source, page
   number, or quote.
5. **Escalation check.** Any of the 7 triggers in
   `research-protocol.md` sec 12 → write `research/ESCALATION.md` and
   treat that claim/beat as blocked pending the user's input.
6. **Write `script/beats.yaml`.** Hand-authored per
   `docs/saint-capybara/script-format.md`. **The closing beat must end on
   "...God bless."** (brand.md sec 5a) — `capy_check_sources.py`
   hard-errors if it doesn't.
7. **Lint.** `tools/capy_check_sources.py` and `tools/capy_check_brand.py`
   must both pass (0 errors) before moving on.
8. **Script doc.** `tools/capy_storyboard.py` renders `script/script.md`
   for human review. (Its `--with-captions` libass font-discovery check is
   vestigial from the retired all-ffmpeg pipeline — the current pipeline
   doesn't burn captions via libass at all, see
   `docs/saint-capybara/hybrid-resolve-pipeline.md` — skip that flag.)
9. **Part A review** (`docs/saint-capybara/review-checklist.md`) — all 12
   items — before presenting anything.
10. **Wait — Gate A.** Send the exact message in
    `docs/saint-capybara/script-format.md` ("Gate A — the fixed wording").
    **No TTS, no clip cutting, no rendering happens before the user
    approves.** If they return edits (directly, or via `DROP`/`SPLIT`/
    `MOVE AFTER Bxx` directives on `script.md`), apply them to
    `beats.yaml`, re-lint, re-storyboard, and send Gate A again.

## Build (post-approval — official pipeline, see `docs/saint-capybara/hybrid-resolve-pipeline.md`)

1. `tools/capy_tts.py --project <dir>` renders real narration for every
   beat (voice locked in `brand.md` sec 6).
2. `tools/capy_beat_plates.py --project <dir>` renders one chrome plate
   per beat.
3. `tools/capy_caption_cards.py --project <dir>` renders timed caption
   phrase stills.
4. `tools/capy_render_beat_clips.py --project <dir>` composites each
   beat (plate + captions + audio, and the real source clip for `clip`
   beats) into one self-contained `frames/beat_<id>.mp4`.
5. Import the beat clips into a DaVinci Resolve project (one per beat,
   one MCP call each — Resolve groups sequentially-named siblings into
   an image/clip *sequence* otherwise), assemble them end-to-end on one
   timeline, verify (`detect_gaps_overlaps`, duration check), and render
   — follow the Resolve build checklist in
   `docs/saint-capybara/hybrid-resolve-pipeline.md` step by step, it
   documents the gotchas that actually bit building the first two
   videos this way.
6. Metadata-strip remux (`ffmpeg -c copy -map_metadata -1 -fflags
   +bitexact`) to produce the final `exports/<slug>.mp4`, then
   `tools/capy_check_brand.py --project <dir> --mp4 <final path>`.
7. `tools/capy_description.py` (not yet built) would produce the export
   description package — for now, write `exports/<slug>-description.txt`
   by hand per the description content described in the original pipeline
   plan (hook, summary, sources grouped by tier, source-video credit,
   fair-use line, disclaimer, tags) and run the brand lint on it too.

## QC

Part B of `docs/saint-capybara/review-checklist.md` — TTS listen-through,
caption sync, phone legibility, evidence hold, metadata clean, muted pass,
anonymity pass. The agent reports "ready for review," never "done" or
"published" — the user's own watch-through (Gate B) always comes last,
same principle as `docs/pipeline.md` sec 4.4 for the other three types.
