# Relay GSA log

Short log for the GSA pipeline manager. No request details, tokens or GSA hosts here.

## 2026-11-19 (start)

- Tests: 79 pass (`cd projects/gsa && python3 -m unittest discover -s tests`).
- Open PRs on `gsa/*`: none. #88–#102 merged.
- Worktrees `../gsa-*` and `.claude/worktrees/agent-aaf29f5fae5c69176`: branches all merged into main. Cleanup candidate (check each for uncommitted changes first). `../sbc-gsa-sbx` is a detached HEAD sandbox.
- Rollout gates: none marked passed.
  - Mac setup: blocked. VPN disconnect/reconnect, VPN-down startup, reboot and network-change tests not done. Torrents stay off.
  - Mock data: code and fixtures exist; confirm the sandbox run covers every README case.
  - Read-only pilot and later: waiting on David (intake approval, form ID and question map, ToC export, reviewer, allowed sources).

## 2026-11-19 (daily loop)

- Tests: 147 pass (main now has #102 merged). No open `gsa/*` PRs.
- Mock data gate, coverage check: every README case has a fixture test.
  - Duplicates: `test_cross_source_duplicates_preserve_submissions_and_editions`, `test_duplicate_import_is_a_no_op`.
  - Ambiguous match: `test_ambiguous_match_needs_reviewer_resolution`, `test_ambiguous_edition_needs_named_resolution_from_each_reviewer`.
  - Unsupported file: `test_signatures`, `test_signature_failure_stops_before_tools` (test_validate.py).
  - Stalled download: `test_retained_partial_torrent_data_and_stall_policy`, `test_progress_resets_stall_clock`.
  - Interruption after upload: `test_crash_recovery_keeps_upload_receipt_and_changelog_idempotent`, `test_publication_resumes_without_duplicate_upload`.
  - Left for this gate: one end-to-end sandbox run (`--home`) of a sample CSV plus mock forms, with Samuel's look at the manifest. Then the gate can be marked passed.

## Waiting on staff (David)
- Intake access approval and form question map.
- Archive index export, writable folders, changelog access, `[GSA:FILE_ID]` marker convention.
- Retention, notification and allowed-source policy.

## Waiting on Samuel
- Network/startup leak tests on the worker Mac (manual).
