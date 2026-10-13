# content_creation

Reusable video-editing pipeline for DaVinci Resolve, built around the
[davinci-resolve MCP server](https://github.com/) and local Whisper
transcription. All five video types render through Resolve; the
anonymous **Saint Capybara** brand builds its Resolve timeline
differently from the other three (each beat pre-composited into one clip
with ffmpeg before Resolve imports it — see
[`docs/saint-capybara/hybrid-resolve-pipeline.md`](docs/saint-capybara/hybrid-resolve-pipeline.md)).
One playbook, five video types (Saint Capybara in short or, on explicit
request, Instagram long form; memes/edits for either brand).

Start here: [`docs/pipeline.md`](docs/pipeline.md) — the master workflow and
the table that routes a new project to its type-specific branch. Saint
Capybara is different enough (its own gates, its own Resolve build stage,
an anonymity system) that it gets its own standalone doc instead: see
[`docs/types/saint-capybara.md`](docs/types/saint-capybara.md).

To kick off a new video in a fresh Claude Code session, paste
[`prompts/kickoff.md`](prompts/kickoff.md)
(response/interview/solo-history/meme-edit) or
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
- `docs/types/` — per-type branches: `response.md`, `interview.md`, `solo-history.md`, `meme-edit.md`, `saint-capybara.md`.
- `docs/script-doc-format.md` — the exact Word-doc spec for the pre-production script (response/interview/solo-history).
- `docs/style-guide.md` — quote-card template, image-credit placement, music rules (NOT used by Saint Capybara — see its own `docs/saint-capybara/brand.md`).
- `docs/transcription.md` — Whisper invocation, model choice, chunking notes.
- `docs/resolve-mcp-gotchas.md` — API traps and the workarounds that avoid them.
- `docs/saint-capybara/` — brand bible, research protocol, script format, review checklist, pronunciation dictionary (Saint Capybara only).
- `tools/` — the scripts the pipeline calls at each stage (see each file's docstring); `tools/capy/` and `tools/capy_*.py` are Saint-Capybara-only.

## Video types

| Type | Source material | On-screen treatment | Pre-production script? |
|---|---|---|---|
| Response/reaction | Downloaded source clip + your recorded reaction | Cuts only, no overlays | Yes |
| Interview/podcast | Multicam simultaneous recording | Camera cuts only, no image overlays | No |
| Solo/history | Single presenter, single or dual camera | Images + quote cards at topic beats | Yes |
| Meme/edit | A base video + short insert clips (either brand — ask) | Meme text overlays, synthetic TTS voice lines, SFX, cut-aways | Yes — `script/edit-plan.md` cue sheet |
| Saint Capybara | Downloaded source clip + a pixel-art capybara host (no camera) | Vertical 9:16, TTS narration, burned-in captions, evidence cards/charts, edited in Resolve from pre-composited per-beat clips. 60-180s short by default; up to 20 min Instagram long form only when explicitly requested | Yes — `script/beats.yaml`/`script.md`, Gate A |

Response/interview/solo-history projects live on `D:\Videos\<slug>\` with
the layout in `docs/pipeline.md` §0. Saint Capybara projects live in the
same root but with a different subfolder set (`research\`, `audio\`,
`captions\`, `frames\` — no `cards\`; its Resolve project is created at
build time, not at intake); see `docs/types/saint-capybara.md` and
`tools/new_project.ps1 -Type saint-capybara`.
