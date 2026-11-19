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

- Polling maps question IDs, pages responses, overlaps five minutes, deduplicates response IDs, and commits the checkpoint with the complete batch. Changed responses fail without advancing the checkpoint, preserving prior outcomes for manual reconciliation. One process lock prevents concurrent workers. Read requests have bounded transient retries; failed writes reconcile on the next invocation.
- Source review records the exact work, provenance, separate download/upload permission, destination, filename, and staff-written dated changelog text. Direct downloads require approved HTTPS hosts, including redirects, and enforce per-file and total staging budgets. There is no automatic rights inference or source discovery.
- Acquisition currently supports authorized direct downloads. Automated torrent acquisition, payload review, stalled-torrent handling, and format conversion remain unimplemented. Do not enable GSA torrents based on this build.
- Validation checks PDF/MP3/MP4 signatures, runs the configured scanner and `pdfinfo`/`ffprobe`, and binds approval to SHA-256. Install and maintain a malware scanner and PDF tooling before use. Scanner freshness is an operator responsibility. Parser success does not establish completeness: staff must review bibliography, first/last pages and body, or the corresponding media content.
- Publication rechecks duplicates, reserves and persists a Drive file ID, uploads through resumable chunks, verifies metadata and full streamed readback, and persists the receipt before the changelog. A lost upload response is reconciled by ID. An interrupted partial upload starts a fresh session with the same reserved ID; partial session byte offsets are not persisted.
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

Actual deliberate disconnect/reconnect, VPN-down startup, reboot, and network-change tests remain pending. The existing Debian transfer is complete and stopped. A fresh private network observation was collected during this implementation; it is not a passed leak test.

## Verification and remaining rollout work

```sh
python3 -m unittest discover -s tests -v
```

Sixteen tests cover intake atomicity/replay, edition ambiguity, permission gates, validation failures, changed candidate approval, publication receipt/changelog crash recovery, and rollout gates. They do not replace Google integration tests, external-tool validation or packet captures.

Still needed: staff resource IDs and approval, OAuth enrollment, a current archive export, reviewer and source allowlists, scanner/PDF tools, a real supervised end-to-end pilot, torrent integration, and actual network/startup validation. No live rollout gate is marked passed by these tests.

API references: [Forms responses.list](https://developers.google.com/workspace/forms/api/reference/rest/v1/forms.responses/list), [Drive uploads](https://developers.google.com/workspace/drive/api/guides/manage-uploads), [Drive generated IDs](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/generateIds), [Docs batchUpdate concurrency](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/batchUpdate).
