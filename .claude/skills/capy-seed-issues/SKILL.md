---
name: capy-seed-issues
description: Mines FAIR / Scripture Central / Evidence Central leads for one or more common-issues topics, traces each argument upstream to a primary/scholarly source, and writes proposals/<topic>.md files for the user to review and approve before anything is added to the actual topic file. Never edits a common-issues topic file directly.
---

# /capy-seed-issues — seed common-issues from FAIR / Scripture Central leads

Read `docs/saint-capybara/common-issues/README.md` and `research-protocol.md` sec 2
first if this is the first run in a session — the standing rule this whole skill
exists to honor is: sources found independently (not handed to the agent by the
user) get **proposed**, never added silently.

Usage: `/capy-seed-issues <topic-slug> [<topic-slug> ...]` or `/capy-seed-issues --batch N`
(`N` = a batch number from `docs/saint-capybara/common-issues/README.md`'s batch
order; the seeding plan's original batches: 1 = joseph-smith-s-polygamy,
teenage-plural-wives, seer-stone-hat-translation-method, book-of-abraham-translation,
egyptian-papyri-and-facsimiles; later batches as documented there).

## Procedure

1. **Resolve topics.** For each requested topic slug, confirm
   `docs/saint-capybara/common-issues/<slug>.md` exists and
   `docs/saint-capybara/common-issues/leads.yaml` has an entry (or a close-enough
   one) — if a slug has no leads entry, either skip it and say so, or add a
   reasonable entry to `leads.yaml` yourself (a FAIR/KnoWhy search) before
   launching a miner for it.

2. **Launch one `capy-lead-miner` per topic, in parallel** (Agent tool,
   `run_in_background: true`, single message, max 5 at once — this session's
   default workflow-size guideline applies here too even though this isn't a
   Workflow tool call). Each miner reads its own topic file and leads; you don't
   need to feed it content beyond the topic slug.

3. When all miners report back, run:
   ```
   python tools/capy_seed_issues.py lint
   ```
   Fix anything it flags — a miner's own item that failed validation was still
   written with `accept: false`, so a lint failure here usually means a
   structural problem (missing field, malformed YAML), not a grading dispute.

4. **Commit the proposal files to a branch and push** (same rule as
   `script-format.md`'s Gate A branch-push: give the user the **branch URL**, not
   a commit SHA, so they can edit `accept:` flags directly on GitHub). Branch
   name: `seed/<short-batch-name>` (e.g. `seed/batch-1-polygamy-translation`).

5. **Tell the user**, per topic: how many items proposed, the grade breakdown
   (e.g. "3 fact, 1 disputed, 1 apologetic-claim-unverified"), and the single
   strongest item's one-line rewrite as a preview. Point at the branch URL and
   say how to approve: flip `accept: false` → `true` on the file (in chat, or by
   editing the file on GitHub and pushing back to the branch — same round-trip
   `[[feedback_script_review_via_github]]` already established for `script.md`
   edits).

## Applying an approval

Once the user has approved specific items (in chat: "approve seer-stone A1"; or
by editing the branch and telling you to pull it):

```
python tools/capy_seed_issues.py apply --topic <slug> --items A1,A3
# or: --all
```

This is the **only** thing that ever writes to a `common-issues/<slug>.md` file
from this workflow. It never writes the FAIR/KnoWhy URL into the topic file —
only the upstream primary/scholarly link. Re-run `capy_check_brand.py` over
`docs/saint-capybara/common-issues/` after applying (anonymity lint covers this
directory like any other repo doc) and push the updated topic file + proposal
file on the same branch.

## What this skill does NOT do

- It does not decide what's true — `grade: apologetic-claim-unverified` items are
  presented to the user as unresolved, not silently dropped or silently upgraded.
- It does not touch a topic file until the user has actually flipped `accept`.
- It is not a substitute for `/capy-research`'s per-video claim research — this
  skill builds the standing `common-issues/` reference library; `/capy-research`
  researches one video's specific claims.
