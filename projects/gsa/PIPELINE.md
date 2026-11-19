# Supervised pipeline implementation

`pipeline.py` extends the existing SQLite queue without replacing the offline rehearsal. It uses the Python standard library. The new code has fixture coverage; it has **not** been validated against live staff Forms, Drive, or Docs resources. Nothing has been scheduled and no GSA files have been published.

## Private configuration

Copy `examples/pipeline-config.json` outside the repository, set mode `0600`, and fill in staff-approved values. Flags start false. The designated reviewer supplies `examples/review.json` and `examples/approval.json` equivalents privately. These are operator attestations, not cryptographically authenticated staff identities; use the dedicated worker account and trusted local operators.

The OAuth Keychain item holds a JSON object containing `client_id`, `client_secret`, and `refresh_token`. OAuth consent/enrollment must be completed separately with staff-approved access. Never put these values in configuration, command arguments, or the repository. The worker refreshes access tokens from this item. Use the Forms read-only response scope for intake (`https://www.googleapis.com/auth/forms.responses.readonly`). Drive access must cover the archive/destinations, and Docs access must cover the changelog; staff must authorize appropriate scopes. `drive.file` alone cannot search arbitrary preexisting archive files.

The archive index is a private JSON array of bibliography records with title, author, ISBN/DOI, edition, year, language, and optional Drive ID. Obtain it from the staff Table of Contents process. Automatic extraction from the existing Table of Contents is not implemented because its schema and location are unknown. Exact identifier/edition comparisons and live destination listing complement that export. Filename-only matches are ambiguous. Conflicting records block publication; staff must reconcile the index/metadata before rerunning. Index freshness and coverage remain operator responsibilities.

## Commands

Run from this directory, substituting the private configuration and review paths:

```sh
python3 pipeline.py --config /private/config.json poll
python3 pipeline.py --config /private/config.json review --work 1 --file /private/review.json
python3 pipeline.py --config /private/config.json acquire --work 1
python3 pipeline.py --config /private/config.json validate --work 1
python3 pipeline.py --config /private/config.json check --work 1
python3 pipeline.py --config /private/config.json approve --work 1 --file /private/approval.json
python3 pipeline.py --config /private/config.json publish --work 1
```

Use `--home /private/sandbox` for isolated trials. Do not use real submissions in repository fixtures.

- With the four free-text `form_question_ids`, polling stores unparsed answers in `form_requests`. Inspect pending rows privately and run `triage --file PACKET.json` with `reviewer`, `response_id` and a `works` array containing one ordinary intake row per identified work with a unique row_id. Use an empty array for feedback without a work request. Structured polling maps question IDs, pages responses, overlaps five minutes, deduplicates response IDs, and commits the checkpoint with the complete batch. Changed responses fail without advancing the checkpoint, preserving prior outcomes for manual reconciliation. One process lock prevents concurrent workers. Read requests have bounded transient retries; failed writes reconcile on the next invocation.
- Source review records the exact work, provenance, separate download, peer-sharing and GSA upload records, destination, filename, and staff-written dated changelog text. Direct downloads require approved HTTPS hosts, including redirects, and enforce per-file and total staging budgets. There is no automatic rights inference or source discovery.
- Direct acquisition checks the declared size and each streamed block against the worker disk budgets. For an operator-added, single-file torrent, supply the reviewed infohash in the review packet and run `torrent-loop --work ID --file SOURCE.torrent --evidence EVIDENCE.json` with the usual config/home options. Each iteration runs the rollout guard first. The loop checks whole-payload permissions, metadata and staging, monitors progress, and may reannounce, recheck or stop the job. The operator handles missing or paused transfers. A completed file under `incomplete/` passes to the normal validation command.
- Validation checks PDF/MP3/MP4 signatures, runs the configured scanner and `pdfinfo`/`ffprobe`, and binds approval to SHA-256. Use `rank --work ID` to compare historical reports for that work. Only its current candidate is eligible for approval. For Homebrew ClamAV, point the private scanner command at the maintained worker database with `--database=PATH`. Install and maintain a malware scanner and PDF tooling before use. Scanner freshness is an operator responsibility. Parser success does not establish completeness: staff must review bibliography, first/last pages and body, or the corresponding media content.
- Publication rechecks duplicates, reserves and persists a Drive file ID, uploads files up to 5 MiB by multipart request, verifies metadata and full streamed readback, and persists the receipt before the changelog. A lost upload response is reconciled by ID. An interrupted upload retries with the same reserved ID.
- Changelog text is inserted at the configured unique dated anchor with revision concurrency control. The visible `[GSA:FILE_ID]` marker enables retry detection. Staff must approve that marker convention. Only plain text anchors in a single text run and the default document body are supported; complex/multitab changelogs require adaptation to staff formatting. No notifications or response deletion occur.

The original manifest includes verified Drive links once publication succeeds. Private `pipeline_records` and append-only `pipeline_events` retain review and validation details. Retention still requires staff policy.

## VPN and startup validation

`rollout.py guard` stops all torrents in the dedicated profile if the route/binding differs, evidence expires, or a required scenario lacks signoff. It never resumes torrents. This is an operator-invoked supplemental guard, not a continuously running kill switch, and it cannot stop a client whose Web UI is unavailable. Interface/route checks alone do not prove VPN identity or absence of leaks.

Private evidence JSON requires `interface`, `expires_at` (timezone-aware ISO timestamp), `reviewer`, and `scenarios`. Each of `connected`, `disconnected`, `reconnected`, `vpn-down-startup`, `reboot`, and `network-change` requires `passed: true`, `tcp_checked: true`, `udp_checked: true`, `ipv6: "checked"` or `"unavailable"`, and `evidence_path`. These are manual attestations referencing independently inspected packet captures and observations; the guard does not interpret packet captures or certify them.

```sh
python3 rollout.py --config /private/config.json guard /private/network-evidence.json
python3 rollout.py --config /private/config.json launchd /private/org.gsa.intake.plist
```

The launchd command only generates an inactive five-minute intake job after intake approval and unattended-intake validation are recorded. It does not install or load it. Test with a sandbox queue, expired credentials, concurrent invocations, interrupted pagination, and startup while offline. Install into the dedicated account only after those tests and staff access approval. This job polls intake only; it cannot acquire or publish automatically.

Session 3 captured the connected, disconnect/reconnect and VPN-down startup scenarios, including the startup retest. Reviewer signoff, reboot and network-change evidence remain pending. See SETUP.md for observations.

## Sandbox verification

Run `python3 -m unittest discover -s tests -v` and then `python3 -m unittest discover -s tests -p test_session4.py -v`. The session 4 rehearsal uses a temporary worker home, synthetic PDF, deterministic scanner exit codes and local service doubles. It checks free-text triage, edition ambiguity, failed validation, and recovery of one upload and one dated entry after lost responses. The full suite separately exercises ClamAV with EICAR when its database is available.

### Unattended intake rehearsal

Run `python3 -m unittest discover -s tests -p test_intake_startup.py -v` in the worktree. The tests invoke the poll command with a temporary private config and queue. They check token refresh after HTTP 401, restart while offline, interruption between pages, recovery on the next poll, and exclusion of a second worker. The tests simulate Keychain and Google. A supervised read-only poll under the intended Mac account is still needed to verify actual credential access and reconciliation before enabling scheduling.
