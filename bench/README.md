# Translation benchmark: Pulpit instructions vs Urim (local route and agent pipeline)

Same six April 2026 talks, es and pt, one fresh headless agent session per talk. Raw run fields: `runs.csv`.

| Arm | Agent | Setup | Prompt | What it could see |
|---|---|---|---|---|
| `pulpit` | Claude Code (`sonnet`, or `-claude-<model>`) | cwd = `pulpit-vault` (its CLAUDE.md/AGENTS.md and `docs/translation.md` load as in real use), no MCP | `pulpit.prompt.md` | The whole vault: glossary files, `npm run quote`, the parallel corpus **including the held-out talks** (the `leak` column counts runs that opened the held-out official text) |
| `urim` | Claude Code `sonnet` | empty cwd, urim MCP only, `URIM_HOME=bench/home` (empty translation memory), `translate_file` on local Ollama | `urim.prompt.md` | Urim glossary built from the **full** corpus, so it includes the test talks (slightly favoured); no TM; Church scripture only as book names |
| `pipeline-claude-haiku` | Claude Code `haiku` | empty cwd, urim MCP only, pipeline tools | `pipeline.prompt.md` | Glossary and TM **without 2026-04** (`heldout.py`), Church scripture text, nothing else |
| `pipeline-codex` | OpenAI Codex CLI (account default model, reasoning effort low) | same MCP server and prompt | `pipeline.prompt.md` | same as the Haiku pipeline arm |

```bash
mcp/.venv/Scripts/python bench/heldout.py                  # once: held-out glossary + TM (no 2026-04), about 10 minutes
python bench/run.py --arm pulpit --lang es --talks 6 --model haiku
mcp/.venv/Scripts/python bench/run.py --arm urim --lang es --talks 2          # needs `python -m urim_translate setup` first (Ollama)
python bench/run.py --arm pipeline --agent claude --model haiku --lang es --talks 6
python bench/run.py --arm pipeline --agent codex --lang es --talks 2
mcp/.venv/Scripts/python bench/run.py --score             # needs the mcp venv: it uses Urim's glossary validator
```

Recorded per run (`runs.csv`): wall time, API time, turns, input/output/cache tokens, cost, tool calls by name, `leak`.
Codex reports tokens but neither dollars (it runs on a ChatGPT subscription) nor API time, so those cells are `n/a`.
Scored (`results.csv`, `results.md`): chrF against the Church's official translation, glossary problems found by Urim's validator
(the official text itself scores about 1 of 10, so read it as a relative number; the same full glossary judges every arm, whatever
the arm could see) and length ratio. Raw transcripts are in `runs/`.

## Held-out data

The pipeline arm must not see the Church's translation of the test talks. `heldout.py` rebuilds the glossary evidence
(`URIM_EXCLUDE=2026-04 URIM_DATA=bench/heldout/data python -m pipeline.attest`) and seeds the translation memory with
`seed-tm --exclude=2026-04`. The glossary hardly moves without that conference (403/345 entries kept, 1 confidence level changed,
no preferred rendering changed), so the old arms' glossary advantage is small. A few generic paragraphs (closing testimony lines)
repeat across talks and come back from the TM; that is what the TM is for, not a leak. The Pulpit glossary hints behind the concept files
and the scripture text are not talk-specific and are visible to the pipeline arm.

The Pulpit arm's agent could in principle read the held-out talks; the `leak` column shows whether it did, but it also had the
parallel corpus (which holds the other 2026 talks and every earlier talk) and the translation-packet script, so its chrF is
not directly comparable with the pipeline arm's.

Before the `urim` arm, run `mcp/.venv/Scripts/python -m urim_translate setup` once so Argos and Ollama are installed; otherwise
that arm measures only the glossary tools. The pipeline arm needs no local models.

## Results (6 April 2026 talks per language unless n says otherwise)

| arm | lang | n | wall s | API s | turns | tool calls | output tok | cost | chrF | glossary problems / terms | length ratio | leaks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pipeline-claude-haiku | es | 6 | 67 | 62 | 14.5 | 13.5 | 14098 | $0.017 | 84.3 | 1.7 / 13 | 1.00 | 0 |
| pipeline-claude-haiku | pt | 6 | 67 | 62 | 14.8 | 13.8 | 13472 | $0.017 | 85.4 | 1.5 / 12 | 1.00 | 0 |
| pipeline-codex | es | 3 | 78 | n/a | 13.0 | 10.0 | 3788 | n/a | 86.1 | 1.3 / 11 | 0.99 | 0 |
| pipeline-codex | pt | 3 | 71 | n/a | 13.7 | 10.3 | 3318 | n/a | 86.2 | 1.7 / 11 | 1.00 | 0 |
| pulpit | es | 6 | 111 | 66 | 7.8 | 6.8 | 9020 | $0.349 | 88.1 | 2.2 / 13 | 1.01 | 0 |
| pulpit | pt | 6 | 155 | 74 | 9.0 | 8.0 | 10840 | $0.398 | 88.7 | 1.8 / 12 | 1.00 | 0 |
| pulpit-claude-haiku | es | 5 | 140 | 123 | 14.0 | 13.0 | 26579 | $0.093 | 84.6 | 3.2 / 13 | 1.00 | 0 |
| pulpit-claude-haiku | pt | 2 | 127 | 106 | 14.0 | 13.0 | 24518 | $0.119 | 86.1 | 2.0 / 12 | 1.00 | 0 |
| urim | es | 6 | 346 | 8 | 3.0 | 2.0 | 497 | $0.053 | 78.9 | 1.5 / 13 | 1.00 | 0 |
| urim | pt | 6 | 332 | 10 | 3.0 | 2.0 | 488 | $0.053 | 79.5 | 1.8 / 12 | 1.00 | 0 |

`n` counts runs that produced a file. Averages are over those runs only. Cost is what the agent's own session cost (Claude Code's
reported `total_cost_usd`); Codex runs on a ChatGPT subscription and reports tokens only. Rows `pulpit` and `urim` are the earlier
runs with `claude-sonnet-5-5`; every other row was run in one clean sequence on 3 November 2026.

How to read it:

- **Pipeline vs Pulpit, same model (Haiku):** about 67 s vs 140 s and about $0.017 vs $0.09-0.12 per talk, with chrF 84-85 vs 85-86.
  Pulpit-with-Haiku also had 5 of 12 runs that wrote no file (Haiku declined to translate a conference talk on copyright
  grounds), which the averages do not show. The pipeline arm completed 12 of 12.
- **Pipeline vs the earlier Sonnet runs:** the Pulpit arm with Sonnet scores chrF 88 at $0.35-0.40 and 111-155 s. The pipeline gives
  up about 3 chrF points to Sonnet+Pulpit for about 20 times lower cost. Part of that gap is the model (Haiku vs Sonnet) and part
  is what each arm could see (below), so do not read it as the pipeline's own deficit.
- **Local route (`urim`, Ollama qwen3.5:4b on CPU):** chrF 79, about 340 s, nearly no agent tokens. The pipeline beats it on quality and speed;
  it stays as the zero-cost fallback.
- **Agent-agnostic:** the same server, tools and prompt were driven by Claude Haiku and by OpenAI's Codex CLI (its account default
  model, reasoning effort set to low); both completed every run (6 of 6 and 6 of 6) and scored alike (chrF 85 vs 86). Codex was only run on
  3 talks per language. No third agent or open-weight model was run; agnosticism is shown for two vendors, not for any MCP client.
- Glossary problems are 1.3-1.7 of 11-13 terms for the pipeline arms against 1.5-3.2 for the others. The official text itself scores about 1, so these are close to the floor and
  the differences are within noise at this sample size.

What each arm could still see:

- `pulpit` / `pulpit-claude-haiku`: the whole Pulpit vault, including its parallel corpus (which contains the held-out talks' official translations) and
  translation-packet script. The `leak` column was 0 in the final scoring (no run opened the official file), but corpus examples could still have
  surfaced held-out text through the tools, so its chrF may be flattered.
- `urim` (local route): empty TM, but the glossary was mined from the full corpus, including the test talks.
- `pipeline-*`: TM and glossary evidence rebuilt **without 2026-04**; Church scripture text (not talk-specific); the Pulpit glossary hints the concept files were seeded
  from. This is the cleanest arm.
- Scoring uses the full Church glossary for every arm.

Not covered: only 6 talks per language and one run each (no variance estimate); chrF against one official text rewards imitating Church
phrasing and does not measure doctrinal accuracy or style; Argos could not run on this machine (Smart App Control), so the local route
was Ollama only.
