# Benchmark: the Urim agent pipeline

Six April 2026 talks, es and pt, one fresh headless agent session per talk, scored against the Church's official translation.

| Arm | Agent | What it could see |
|---|---|---|
| `pipeline-claude-haiku` | Claude Code `haiku` | Glossary and translation memory **without 2026-04**, the Church's scripture text, nothing else |
| `pipeline-claude-sonnet` | Claude Code `sonnet` | same |
| `pipeline-codex` | OpenAI Codex CLI (account default model, reasoning effort low), 3 talks per language | same |

The agent runs in an empty folder with only the urim MCP and the prompt in `pipeline.prompt.md`; it gets no other instructions than the server's own.

```bash
mcp/.venv/Scripts/python bench/heldout.py                  # once: held-out glossary + TM (no 2026-04), about 10 minutes
python bench/run.py --arm pipeline --agent claude --model haiku --lang es --talks 6
python bench/run.py --arm pipeline --agent codex --lang es --talks 2
mcp/.venv/Scripts/python bench/run.py --score             # needs the mcp venv: it uses Urim's glossary validator
```

Recorded per run (`runs.csv`): wall time, API time, turns, input/output/cache tokens, cost, tool calls by name, `leak` (the agent opened the
held-out official text). Codex reports tokens but neither dollars (ChatGPT subscription) nor API time, so those cells are `n/a`.
Scored (`results.csv`, `results.md`): chrF against the official translation, glossary problems found by Urim's validator (the official text
itself scores about 1 of 10, so read it as a relative number), length ratio, and estimated whole-corpus time and cost for one agent
(26.2M words in the 12,198 English talks, scaled linearly from the 1,300-word test talks).

## Results

See [results.md](results.md). On the final runs, Haiku scores chrF about 85 at about $0.018 and 65-70 s per talk; Sonnet about 86 at about $0.21
and 60-70 s; Codex about 86. Sonnet and Codex rows were run before two later bug fixes (inline-link scripture citations, reference footnotes),
so they are not directly comparable with the Haiku rows. Earlier comparisons with other approaches (Pulpit's own instructions, a local-model
route, Argos drafts) are in the git history before the commit that removed them.

## Held-out data

The Church's translation of the test talks must not be visible. `heldout.py` rebuilds the glossary evidence
(`URIM_EXCLUDE=2026-04 URIM_DATA=bench/heldout/data python -m pipeline.attest`) and seeds the translation memory with
`seed-tm --exclude=2026-04`. The glossary hardly moves without that conference (1 confidence level changed, no preferred rendering changed).
A few generic paragraphs (closing testimony lines) repeat across talks and come back from the TM; that is what the TM is for, not a leak.
The scripture text and the Pulpit glossary hints the concept files were seeded from are not talk-specific and are visible.

## Not covered

Six talks per language and one run each (no variance estimate); chrF against one official text rewards imitating Church phrasing and does not
measure doctrinal accuracy or style; two vendors only (Claude and Codex), no open-weight model through an MCP client.
