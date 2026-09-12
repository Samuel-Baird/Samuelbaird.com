---
name: capy-research
description: Multi-angle research fan-out for a Saint Capybara project. Launches 2-4 expert-angle subagents (historian, scripture-theologian, doctrine-scholar, philosopher, data-analyst — chosen by claim category) plus a red-team subagent for every chosen claim in research/claims.md, in parallel, then merges their briefs into sources.yaml and claims.md. Use after triage (claims.md's Chosen? column is filled) and before writing beats.yaml.
---

# /capy-research — multi-angle research fan-out

Read `docs/saint-capybara/research-protocol.md` §15 "Multi-angle research" for the
full roster, category→roster mapping table, and the brief/merge contract before
running this the first time in a session.

## Precondition

`research/claims.md`'s triage table is complete: every row has `Chosen?` filled, and
(new column) `Audience` set to one of `catholic | protestant | exmo | atheist |
media | general`. If `Audience` is missing, infer it from the source and note the
inference in the table rather than blocking.

## Procedure

1. **For each row with `Chosen?: yes`**, look up its `Category` in the roster table
   (`research-protocol.md` §15) to get 2-3 researcher roles, and always add
   `capy-red-team`. Hard cap: 3 researchers + red-team per claim. Concede/skip rows
   get nothing.

2. **Launch every researcher for every chosen claim in one parallel batch** — a
   single message with multiple `Agent` tool calls (`run_in_background: true`), not
   claim-by-claim. Give each agent, in its prompt: the absolute project directory,
   the claim number, its verbatim text, its anchor and anchor context, the triage
   decision, and the audience. Do not read any brief file yourself yet.

3. When all agents report back, run:
   ```
   python tools/capy_merge_briefs.py --project <absolute project dir>
   ```
   This parses every `research/briefs/claim*.md`, validates tool-verified provenance
   (rejects/downgrades anything not backed by a real tool call), dedupes by id then
   locator, and **appends** (never prepends — `sources.yaml`'s `find_critic_article_entry`
   takes the first `type: critic` match) to `research/sources.yaml`. Read its printed
   report, not the raw briefs, to see what happened.

4. For each chosen claim, fill in `research/claims.md`'s per-claim section:
   - **Research**: synthesize the researchers' "Finding" sections (read the brief
     files now, one claim's worth at a time, not all at once).
   - **Grading**: the most cautious grade among the briefs if they disagree; note the
     disagreement explicitly rather than silently picking one.
   - **Doctrine tier**: from the doctrine-scholar brief (or scripture-theologian, if
     doctrine-scholar wasn't dispatched).
   - **Adversarial Q1/Q2**: paste directly from the red-team brief's "Strongest
     objection after the response" and "Omitted from the clip" sections — this is
     research-protocol.md §14, now seeded by an independent agent instead of
     self-assessed.
   - **Briefs**: list the brief file paths used.

5. **Escalate, don't silently resolve**: an unresolvable grade disagreement between
   briefs is §12 trigger 1 — write `research/ESCALATION.md`. Any brief with
   `status: blocked` also escalates. A researcher reporting an escalation trigger in
   its own brief does not write `ESCALATION.md` itself — only the orchestrator does,
   after seeing it here.

6. Run `python tools/capy_check_sources.py --project <dir>` on the merged
   `sources.yaml` before writing `script/beats.yaml`. Fix anything it flags before
   moving on — a brief that failed provenance validation was imported with
   `inspected: false` specifically so this lint catches it.

7. **Common-issues**: if a brief surfaces a source, argument, or approach relevant to
   one of the topics in `docs/saint-capybara/common-issues/*.md`, ask the user before
   adding it there — don't add silently (standing rule).

## What this skill does NOT do

It does not write `beats.yaml` or narration — that is the next step in
`docs/types/saint-capybara.md`'s pre-production stage, done by the main session using
the merged `claims.md`/`sources.yaml`, not by a subagent.
