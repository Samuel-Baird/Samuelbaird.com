# content_creation

Reusable video-editing pipeline for DaVinci Resolve, built around the
[davinci-resolve MCP server](https://github.com/) and local Whisper
transcription. Every video type renders through Resolve except
**presentation**, which is built end to end with ffmpeg from one
`project.json` (`tools/presentation/`, see
[`docs/types/presentation.md`](docs/types/presentation.md)); the three
anonymous **Saint Capybara** types build their Resolve timeline
differently from the rest (each beat pre-composited into one clip
with ffmpeg before Resolve imports it — see
[`docs/saint-capybara/hybrid-resolve-pipeline.md`](docs/saint-capybara/hybrid-resolve-pipeline.md)).
One playbook, nine video types (table below). The standard brand's
fonts, colours, caption and thumbnail look are in
[`docs/style-guide.md`](docs/style-guide.md) "Brand kit".

Start here: [`docs/pipeline.md`](docs/pipeline.md) — the master workflow and
the table that routes a new project to its type-specific branch. Saint
Capybara is different enough (its own gates, its own Resolve build stage,
an anonymity system) that it gets its own standalone doc instead: see
[`docs/types/saint-capybara.md`](docs/types/saint-capybara.md).

To kick off a new video in a fresh Claude Code session, paste
[`prompts/kickoff.md`](prompts/kickoff.md)
(response/interview/solo-history/meme-edit/clips) or
[`prompts/kickoff-saint-capybara.md`](prompts/kickoff-saint-capybara.md)
(Saint Capybara).

**Anonymity warning:** Saint Capybara is a standalone, anonymous brand,
deliberately separated from the creator's other identity (this repo's own
name and history included). Never reuse this repo's other visual style
(`docs/style-guide.md`), phrasing, filenames, or any personal/identifying
detail inside a Saint Capybara project. See
[`docs/saint-capybara/brand.md`](docs/saint-capybara/brand.md) sec 9-10
before touching that type at all.

## Layout

- `docs/pipeline.md` — master workflow for the first three types: intake, pre-production gate, build, QC.
- `docs/types/` — per-type branches: `response.md`, `interview.md`, `solo-history.md`, `meme-edit.md`, `clips.md`, `presentation.md`, `saint-capybara.md`.
- `docs/script-doc-format.md` — the exact Word-doc spec for the pre-production script (response/interview/solo-history).
- `docs/style-guide.md` — quote-card template, image-credit placement, music rules (NOT used by Saint Capybara — see its own `docs/saint-capybara/brand.md`).
- `docs/transcription.md` — Whisper invocation, model choice, chunking notes.
- `docs/resolve-mcp-gotchas.md` — API traps and the workarounds that avoid them.
- `docs/saint-capybara/` — brand bible, research protocol, script format, review checklist, pronunciation dictionary (Saint Capybara only).
- `tools/` — the scripts the pipeline calls at each stage (see each file's docstring); `tools/capy/` and `tools/capy_*.py` are Saint-Capybara-only; `tools/presentation/` is the ffmpeg presentation pipeline (sync, transcribe, long-form, shorts, thumbnails, verify).
- `assets/presentation/` — a complete worked `project.json` (State of Theology + the St. George story short).
- `tools/` — the scripts the pipeline calls at each stage (see each file's docstring); `tools/capy/` and `tools/capy_*.py` are Saint-Capybara-only. `tools/capy_fetch_queue.py` batch-downloads the Saint Capybara reaction queue (`docs/types/saint-capybara.md` "Batch-downloading URL-only queue rows").

## Video types

| Type | Source material | On-screen treatment | Pre-production script? |
|---|---|---|---|
| Response/reaction | Downloaded source clip + your recorded reaction | Cuts only, no overlays | Yes |
| Interview/podcast | Multicam simultaneous recording | Camera cuts only, no image overlays | No |
| Solo/history | Single presenter, single or dual camera | Images + quote cards at topic beats | Yes |
| Meme/edit | A base video + short insert clips (either brand — ask) | Meme text overlays, synthetic TTS voice lines, SFX, cut-aways | Yes — `script/edit-plan.md` cue sheet |
| Presentation | Presenter at a desk, two cameras + external mic, slide images (+ optional separately read story segments) | Long-form 16:9 with slides in a split layout beside the live camera, slow zooms, angle changes; plus 2-3 vertical highlight shorts, a short per story segment (with sourced historical photos), thumbnails, Reel covers, titles/descriptions. ffmpeg, not Resolve | No — built straight through, user reviews the renders |
| Clips | One long-form video (solo podcast, dialogue, interview, debate) | Several standalone clips, vertical 9:16 by default, reframed to the speaker, burned-in captions; one Resolve timeline + render per clip | Yes — numbered `script/clips.md` (full transcript at bottom); built only after written approval |
| Saint Capybara — short form | Downloaded source clip + a pixel-art capybara host (no camera) | Vertical 9:16, 60-180s. TTS narration, burned-in captions, evidence cards/charts, edited in Resolve from pre-composited per-beat clips. The default Saint Capybara type | Yes — `script/beats.yaml`/`script.md`, Gate A |
| Saint Capybara — long form (Instagram) | Same as short form | Vertical 9:16, up to 20 min; Instagram feed video, reaches followers only. Only when explicitly requested | Yes — same, `video_type: long-instagram` |
| Saint Capybara — long form (YouTube) | Same as short form | Widescreen 16:9, no length cap (as long as the reaction needs); the same frame modes re-laid out to use the width. Only when explicitly requested | Yes — same, `video_type: long-youtube` |

Response/interview/solo-history projects live on `D:\Videos\<slug>\` with
the layout in `docs/pipeline.md` §0. Saint Capybara projects live in the
same root but with a different subfolder set (`research\`, `audio\`,
`captions\`, `frames\` — no `cards\`; its Resolve project is created at
build time, not at intake); see `docs/types/saint-capybara.md` and
`tools/new_project.ps1 -Type saint-capybara`.
