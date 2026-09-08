# content_creation

Reusable video-editing pipeline for DaVinci Resolve, built around the
[davinci-resolve MCP server](https://github.com/) and local Whisper
transcription. One playbook, three video types, one quote-card style.

Start here: [`docs/pipeline.md`](docs/pipeline.md) — the master workflow and
the table that routes a new project to its type-specific branch.

To kick off a new video in a fresh Claude Code session, paste
[`prompts/kickoff.md`](prompts/kickoff.md).

## Layout

- `docs/pipeline.md` — master workflow: intake, pre-production gate, build, QC.
- `docs/types/` — per-type branches: `response.md`, `interview.md`, `solo-history.md`.
- `docs/script-doc-format.md` — the exact Word-doc spec for the pre-production script.
- `docs/style-guide.md` — quote-card template, image-credit placement, music rules.
- `docs/transcription.md` — Whisper invocation, model choice, chunking notes.
- `docs/resolve-mcp-gotchas.md` — API traps and the workarounds that avoid them.
- `tools/` — the scripts the pipeline calls at each stage (see each file's docstring).

## Video types

| Type | Source material | On-screen treatment | Pre-production script? |
|---|---|---|---|
| Response/reaction | Downloaded source clip + your recorded reaction | Cuts only, no overlays | Yes |
| Interview/podcast | Multicam simultaneous recording | Camera cuts only, no image overlays | No |
| Solo/history | Single presenter, single or dual camera | Images + quote cards at topic beats | Yes |

Projects live on `D:\Videos\<slug>\`. See `docs/pipeline.md` §0 for the exact
subfolder layout and `tools/new_project.ps1` to create it.
