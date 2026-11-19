# Supervised pipeline implementation

`pipeline.py` extends the existing SQLite queue without replacing the offline rehearsal. It uses the Python standard library. The new code has fixture coverage; it has **not** been validated against live staff Forms, Drive, or Docs resources. Nothing has been scheduled and no GSA files have been published.

## Private configuration

Copy `examples/pipeline-config.json` outside the repository, set mode `0600`, and fill in staff-approved values. Flags start false. The designated reviewer supplies `examples/review.json` and `examples/approval.json` equivalents privately. These are operator attestations, not cryptographically authenticated staff identities; use the dedicated worker account and trusted local operators.

The OAuth Keychain item holds a JSON object containing `client_id`, `client_secret`, and `refresh_token`. OAuth consent/enrollment must be completed separately with staff-approved access. Never put these values in configuration, command arguments, or the repository. The worker refreshes access tokens from this item. Use the Forms read-only response scope for intake (`https://www.googleapis.com/auth/forms.responses.readonly`). Drive access must cover the archive/destinations, and Docs access must cover the changelog; staff must authorize appropriate scopes. `drive.file` alone cannot search arbitrary preexisting archive files.

The archive index is a private JSON array of bibliography records with title, author, ISBN/DOI, edition, year, language, and optional Drive ID. Obtain it from the staff Table of Contents process. A snapshot of the two-column Table of Contents can instead contain name and folder_path fields. Filename hits route to edition review. Exact identifier/edition comparisons and live destination listing complement that export. Filename-only matches are ambiguous. Exact matches block publication. An ambiguous match (for example another edition of the same title) blocks approval until each approving reviewer lists its `key` from the `check` output under `archive_resolution.matches` with a written `reason` in the approval file; the fresh duplicate check at publication honours the same resolution. Index freshness and coverage remain operator responsibilities.

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
- Direct acquisition checks the declared size and each streamed block against the worker disk budgets. For an operator-added, single-file torrent, supply the reviewed infohash in the review packet and run `torrent-loop --work ID --file SOURCE.torrent --evidence EVIDENCE.json` with the usual config/home options. It refuses unless `torrent_acquisition_approved` is true in the private config. Each iteration runs the rollout guard first. The loop checks whole-payload permissions, metadata and staging, monitors progress, and may reannounce, recheck or stop the job. The operator handles missing or paused transfers. A completed file under `incomplete/` passes to the normal validation command.
- Validation checks PDF/MP3/MP4 signatures, runs the configured scanner and `pdfinfo`/`ffprobe`, and binds approval to SHA-256. Every acquired file (each direct download and a completed torrent) is kept as a numbered candidate, and `validate` checks all of them. A file that fails the malware scan moves to `quarantine/` (read-only) and stays out of the candidate list; a scanner *error* fails closed without quarantining. Passing reports are ranked with real scans and original PDFs above ebook conversions, and the best becomes the current candidate; `rank --work ID` prints the ranking. To approve a different passing candidate, a reviewer runs `select --work ID --file CHOICE.json` with `reviewer`, `sha256` and, for a lower-ranked or ebook-converted file, a written `reason`. Only the current candidate is eligible for approval. For Homebrew ClamAV, point the private scanner command at the maintained worker database with `--database=PATH`. Install and maintain a malware scanner and PDF tooling before use. Scanner freshness is an operator responsibility: with `scanner_max_db_age_hours` set, validation fails once the signatures are older than that, so refresh the worker database first with `freshclam --config-file="$WORKER/clamav/freshclam.conf"`. Parser success does not establish completeness: staff must review bibliography, first/last pages and body, or the corresponding media content.
- Publication rechecks duplicates, reserves and persists a Drive file ID, uploads files up to 5 MiB by multipart request and larger files in resumable 4 MiB chunks, verifies metadata and full streamed readback, and persists the receipt before the changelog. A lost upload response is reconciled by ID. Large uploads retain their private session URL and query Drive for the acknowledged byte offset on retry. Expired sessions restart with the same reserved file ID.
- Changelog text is inserted at the configured unique dated anchor with revision concurrency control. The visible `[GSA:FILE_ID]` marker enables retry detection. Staff must approve that marker convention. The anchor must occur in one text run in the configured tab (or default body if no tab ID is set). No notifications or response deletion occur.

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

Run `python3 -m unittest discover -s tests -v` and then `python3 -m unittest discover -s tests -p test_session4.py -v`. For a fuller end-to-end trial, `python3 sandbox_trial.py --home <new folder whose name contains "sandbox"> [--config <private config, read only>]` runs the whole pipeline on synthetic data with in-memory Google and qBittorrent (`tests/fakes.py`) and the real ClamAV, poppler and qpdf, and writes `trial-report.json` (mode 0600) into that folder. The session 4 rehearsal uses a temporary worker home, synthetic PDF, deterministic scanner exit codes and local service doubles. It checks free-text triage, edition ambiguity, failed validation, and recovery of one upload and one dated entry after lost responses. The full suite separately exercises ClamAV with EICAR when its database is available.

### Unattended intake rehearsal

Run `python3 -m unittest discover -s tests -p test_intake_startup.py -v` in the worktree. The tests invoke the poll command with a temporary private config and queue. They check token refresh after HTTP 401, restart while offline, interruption between pages, recovery on the next poll, and exclusion of a second worker. The tests simulate Keychain and Google. A supervised read-only poll under the intended Mac account is still needed to verify actual credential access and reconciliation before enabling scheduling.

### Website review

The private review queue is at `https://samuelbaird.com/gsa`. Reviewers sign in through the site's Google SSO. Samuel and David each inspect the linked reviewer PDF and record their own checks or a change request. A change request requires a note. Decisions are final for that revision. For a correction, update the private review packet and increment its version to request fresh decisions. Republishing the same packet preserves existing decisions.

On the worker Mac, use `review_portal.py queue --home WORKER_QUEUE --packet PRIVATE_SETTINGS.json` after validation and a clean archive check. The settings specify a stable URL-safe id, work ID, version, review_file (the private source review JSON), folder display name, reviewer-copy PDF URL and rights/attribution text. Keep the operator credential in the private worker home as `review-portal.key`; its SHA-256 verifier is configured in the site worker. The queue contains bibliographic and review metadata. Files stay in the separately shared Drive folder.

After both approvals, run the same command with `collect` instead of `queue`. Collection verifies the local candidate hash and exact packet and imports the decisions using the pipeline's review and approval gates. The portal handles direct-download candidates. Publication is still an explicit worker command, with a fresh destination duplicate check.

Reviewers can edit the title, citation, filename, destination folder, rights evidence and changelog entry on the review page. Each box saves about half a second after typing stops (or when it loses focus) and shows a green "Changes saved" check; rejected values (empty, a `/` or `\` in a filename, a changed extension; colons are allowed, as in `Lastname, Title: Subtitle.pdf`) show the reason instead. Every edit changes the review version, so recorded decisions reset and both reviewers approve the edited text. The page keeps who changed what in a history.

The destination is chosen with a folder explorer. The site has no Drive access, so push the archive's folder tree from the worker Mac first, and again whenever shelves change: `review_portal.py folders --home WORKER_QUEUE --config PRIVATE_CONFIG.json`. It uses a live Drive listing under `archive_root_id` when the config's Google access allows; otherwise (today: the intake credential has no Drive scope) it reads the staff Table of Contents, whose Folder Path cells link to each folder, so every folder that holds files gets its real Drive ID. Folders that only hold other folders (such as year/month folders) get `toc-` placeholders: reviewers can open them but must choose a folder inside. The archive root itself can't be chosen. Pass the same `--config` to `collect`: a chosen folder outside `destination_ids` is accepted when the Table of Contents lists it (or Drive confirms it is under the archive root) and both reviewers approved that exact version.

The worker home keeps its config as `pipeline-config.json`, so pass `--config` for `folders` and `remove` (a sandbox home with its own `config.json` doesn't need it). `review_portal.py remove --home HOME --config CONFIG --id REVIEW_ID` takes a queued packet off the site, with its edits, history and decisions (sandbox clean-up or a withdrawn work).

`collect` applies the edits to the source review (citation → matched work, entry → changelog text, filename, destination; title → the work's metadata; rights → the permission basis) and re-runs the duplicate check for the edited title and folder before importing approvals. A folder chosen on the site that is not in `destination_ids` is accepted only if Drive confirms it is a live folder inside `archive_root_id`; both assigned reviewers approving that exact folder stands in for the allowlist entry.
