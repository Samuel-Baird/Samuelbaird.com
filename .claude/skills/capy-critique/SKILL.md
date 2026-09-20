---
name: capy-critique
description: Independent three-lens critique of a finished Saint Capybara script.md before Gate A — does it defend the Church well, is it accurate, and is it compelling. Runs capy-critic-opponent, capy-critic-factcheck, and capy-critic-editor in parallel, merges findings, fixes BLOCKERs, and reports MAJOR/MINOR. Runs automatically before every Gate A message and can be invoked on demand.
---

# /capy-critique — independent script critique before Gate A

Precondition: `script/beats.yaml` exists, `tools/capy_check_sources.py`,
`tools/capy_check_brand.py`, and `tools/capy_check_tone.py` all pass with 0 errors,
and `tools/capy_storyboard.py` has rendered `script/script.md`. (The tone lint
catches mechanical concession/polemic tells so the critics can spend their attention
on the ones a regex can't see — run it first, fix its errors, then launch.)

## Procedure

1. **Launch the three critics in one parallel batch** — `capy-critic-opponent`,
   `capy-critic-factcheck`, `capy-critic-editor` (Agent tool, `run_in_background:
   true`, single message). Each reads the project's own files; you don't need to feed
   them content beyond the absolute project directory.

2. When all three report back, read their three `research/critique-*.md` files and
   merge into `research/critique.md`, severity-ranked (BLOCKER, then MAJOR, then
   MINOR), each line keyed by beat id:
   ```markdown
   # Critique — <slug>

   ## BLOCKER
   - [opponent|factcheck|editor] <beat id> — <finding> (from critique-<lens>.md)
   ## MAJOR
   ...
   ## MINOR
   ...
   ```

3. **Fix every BLOCKER** in `script/beats.yaml`:
   - Never silently rewrite narration text the user themselves wrote in a prior
     Gate A edit round — flag it as a finding instead of overwriting it, same rule as
     `script-format.md`'s edit-directive handling.
   - After fixing, re-run `tools/capy_check_sources.py`,
     `tools/capy_check_brand.py`, and `tools/capy_check_tone.py`, re-run
     `tools/capy_storyboard.py`, and **re-run only
     the critic(s) whose BLOCKER you touched** on the changed beats (not all three
     again) to confirm the fix actually resolves it.
   - Cap at two fix-and-recheck iterations per BLOCKER; if it's still open after two,
     stop and escalate it in the Gate A message rather than looping.

4. Mirror the final `research/critique.md` to `reviews/<slug>/critique.md` in this
   repo (after `capy_check_brand.py` passes on it — it can contain narration excerpts,
   so it goes through the same anonymity lint as `script.md`), on the same branch as
   the Gate A `script.md` push.

5. **Report, don't hide, MAJOR/MINOR.** Prepend a short "Critique summary" block
   *before* the fixed Gate A message from `script-format.md` (that message's wording
   is locked — the summary goes ahead of it, not inside it):
   ```
   Critique before Gate A: <N> BLOCKER(s) found and fixed (beats: ...).
   <M> MAJOR / <K> MINOR left for your review:
   - <beat id>: <finding> — suggested: "<rewrite>"
   ```
   If there were zero findings at any severity, say so plainly rather than omitting
   the block.

## On demand

The user (or a future session) can invoke `/capy-critique` any time after Gate A,
e.g. after applying the user's own edits from a GitHub review round, to re-check
before the next Gate A message. Re-running always regenerates all three
`critique-*.md` files and the merged `critique.md` from scratch — it does not diff
against a prior run.
