# Translation benchmark: Pulpit instructions vs Urim

Same talks, same model (`BENCH_MODEL`, default sonnet), headless Claude Code, one fresh session per talk.

| Arm | Setup | Prompt |
|---|---|---|
| `pulpit` | cwd = `pulpit-vault` (its CLAUDE.md/AGENTS.md and `docs/translation.md` load as in real use), no MCP | `pulpit.prompt.md` |
| `urim` | empty cwd, only the urim MCP, `URIM_HOME=bench/home` (empty translation memory, so the Church's own translation of the test talks cannot come back) | `urim.prompt.md` |

```bash
python bench/run.py --arm pulpit --lang es --talks 2
mcp/.venv/Scripts/python bench/run.py --arm urim --lang es --talks 2
mcp/.venv/Scripts/python bench/run.py --score      # needs the mcp venv: it uses Urim's glossary validator
```

Recorded per run (`runs.csv`): wall time, API time, turns, input/output/cache tokens, cost, tool calls by name, and a
`leak` flag if the agent opened the held-out official translation. Scored (`results.csv`): chrF against the Church's
official translation, glossary problems found by Urim's validator (the official text itself scores about 1 of 10, so
read it as a relative number), and length ratio. Raw transcripts are in `runs/`.

Held-out: the official Spanish/Portuguese text is read only by the scorer. Urim's glossary was mined from the same
corpus (including these talks), so its term counts are slightly favored; for a cleaner test rebuild the glossary without
the test conference.
