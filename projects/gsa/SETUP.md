# Local pilot setup

The first build is an **offline intake rehearsal**. It runs on Python 3.10+ with no third-party packages. It does not download, connect to Forms or Drive, search the archive, assess permissions, scan files, or publish. The torrent worker remains paused. Read [the workflow plan](README.md) before configuring live services.

## Installed state

The empty production queue is initialized at `~/Library/Application Support/GSA Worker/queue.sqlite3`. Local incomplete files, candidates and receipts have separate directories alongside it. The directory is mode 0700 and the database is mode 0600. Keep this location outside Drive sync and do not commit private configuration or request data.

A separate `sandbox/` directory at the same location contains the synthetic pilot: five submissions map to three works. The sample has an identical book requested twice in CSV and once through mock Forms, a different edition, and an article. All works require review. `sandbox/manifest.csv` contains the per-submission results; empty matched-work and permission fields indicate checks still to perform, not approval.

## Commands

Run from this directory:

```sh
python3 gsa.py status
python3 gsa.py --home "$HOME/Library/Application Support/GSA Worker/sandbox" import-csv examples/requests.csv --batch synthetic-pilot
python3 gsa.py --home "$HOME/Library/Application Support/GSA Worker/sandbox" import-mock-forms examples/forms.json
python3 gsa.py --home "$HOME/Library/Application Support/GSA Worker/sandbox" manifest "$HOME/Library/Application Support/GSA Worker/sandbox/manifest.csv"
python3 -m unittest discover -s tests -v
```

`import-csv` writes the intake queue only. No import initiates a download. Reuse the batch ID and row IDs when repeating an import: identical submissions are skipped and earlier outcomes survive. Changing a prior row raises an error and rolls back the batch; assign a new ID to record a correction. Different batches retain separate submissions. Exact normalized bibliographic matches share a work; year, language, identifier and edition conflicts stay separate for later review. This is conservative deduplication, not archive matching.

For sandbox crash recovery, use a separate sandbox queue:

```sh
python3 gsa.py --home "$HOME/Library/Application Support/GSA Worker/sandbox" sandbox-upload 1 --interrupt-after-upload
# Expected error: simulated interruption. The mock upload receipt is already committed.
python3 gsa.py --home "$HOME/Library/Application Support/GSA Worker/sandbox" sandbox-upload 1
```

Both commands simulate records in SQLite only. Repeating the second command retains the same upload and changelog receipts. No Drive links are generated. The mock Forms adapter takes mapped fields rather than raw Google API responses, and commits its provided checkpoint in the same transaction as its submissions. Live authentication, question-ID mapping, pagination, overlap polling, retries and scheduling still need implementation after access is approved.

## Next setup steps

1. Confirm the worker Mac and dedicated standard account; select and connect its VPN. qBittorrent was not present when this pilot was initialized. Install it from the [official download page](https://www.qbittorrent.org/download), then identify and bind the actual VPN tunnel. Set local download paths, disk and queue limits. Keep the Web UI disabled until needed; automation must use authenticated localhost access.
2. Complete the Debian transfer and checksum tests in the plan, including VPN disconnect/reconnect, startup with VPN down, reboot and network changes. Record actual TCP, UDP and IPv6 observations. Do not infer a passing kill-switch test merely from a selected interface or speed display.
3. Obtain David's intake approval, request form ID and question mapping, Table of Contents and destination access, and reviewer identity. Keep those details and OAuth tokens outside the repository. Use Keychain for credentials. Request only read-only responses access for intake initially.
4. Implement and compare archive/edition matching with volunteer decisions. Exercise ambiguous editions, unsupported files and stalled-download handling before moving beyond mock intake; the current suite does not implement or test these acquisition stages.
5. After staff approve sources, sharing/upload permission, writable folders and changelog procedure, add acquisition, validation, staff review and live publication adapters. Confirm retention and notifications before implementing them.
6. Install a five-minute launchd intake job only after live reconciliation and unattended-startup tests pass. This build intentionally installs no background job because there is no live intake adapter yet.

No live rollout gates have been marked complete by the mock run.

## Manual disconnect/reconnect observation (2026-11-18)

A fresh official Debian transfer ran through `ipsec0`, McAfee was manually switched off, and then switched back on. During the 44-second interval sampled with the route on Wi-Fi, the download counter increased by 3,112,000 bytes in the first two seconds and then remained unchanged for the remaining samples. Transfer resumed after reconnect. This demonstrates eventual transfer cessation and recovery, but the transition increase cannot be classified as delayed accounting versus traffic without packet capture.

The administrator password prompt timed out, so no TCP/UDP packet capture was collected. IPv6 became available on Wi-Fi while the VPN was off. A disconnected socket inspection showed only qBittorrent's localhost Web UI listener. These observations do **not** certify leak protection or Safe Reconnect behavior during an involuntary failure.

The VPN was restored, the route and qBittorrent binding were verified as `ipsec0`, and the test torrent was stopped. The original completed ISO was preserved and its SHA-256 reverified; the new partial download was retained separately. Private samples and the result are in `network-checks/manual-disconnect/` beneath the worker home. VPN-down startup, reboot, network-change and packet-capture validation remain pending.

## Session 3 analysis (2026-11-19)

- **The counter rise during the 2026-11-18 disconnect** looks like delayed accounting: qBittorrent's `downloaded` counter updates in bursts, it was flat for the two samples before the route moved to Wi-Fi while the speed still read 0.5–1 MB/s, and it caught up by about 11.6 MB in the first two Wi-Fi samples, then stopped. This is an interpretation, not a passed test; it needs a packet capture.
- **IPv6 is now live on Wi-Fi while McAfee is connected** (global addresses and an IPv6 default route on `en1`; `ipsec0` is IPv4 only). Capture IPv6 on `en1` in the connected scenario as well as the disconnected one; don't record IPv6 as "unavailable" on this network.
- Still pending: the packet-captured disconnect/reconnect, VPN-down startup, reboot and network-change scenarios. McAfee has no `scutil --nc` service, so the VPN is toggled by hand in the McAfee app during each test.
- `rollout.py` now fails closed on a null `expires_at` instead of crashing; `tests/test_rollout.py` covers the guard gates, stop-never-resume, and the launchd approval gate.

## Session 3 packet-captured VPN tests (2026-11-19)

Run with `vpn_test.py` (sampler + phase marks + pcap attribution) and a root `tcpdump` on `en1`; 851,704 packets, 0 dropped. Private evidence: `network-checks/session3-2026-11-19/` (pcap, samples, `analysis-final.json`, `network-evidence-draft.json`). Observations only; no scenario is signed off until a designated reviewer inspects the capture.

| Scenario | Observed |
|---|---|
| Connected | No qBittorrent packets on Wi-Fi, IPv4 or IPv6. It listens only on the tunnel's IPv4 address. |
| Disconnected | `ipsec0` disappears, the listener closes, the last tunnel socket dies within ~25 s, the torrent stalls. Zero qBittorrent packets on Wi-Fi; no tracker DNS. The counter rose once (4.2 MB, 3 s after the drop) with no matching traffic on Wi-Fi: delayed accounting. |
| Reconnected | The tunnel returns with a new address; qBittorrent re-binds by itself and resumes through the VPN ~40 s later. |
| VPN-down startup | First run failed: qBittorrent's own HTTPS requests (DB-IP GeoIP download, ~4.2 MB, and the program update check) went out over Wi-Fi on IPv4 and IPv6, though no BitTorrent traffic did. Fixed by setting `Preferences/Advanced/updateCheck=false` and `Preferences/Connection/ResolvePeerCountries=false` in the profile's qBittorrent.ini (backup `.before-session3-fix`). Retest (torrent started with the VPN down): nothing from qBittorrent on Wi-Fi, no related DNS, only the localhost Web UI socket; it re-bound to the tunnel when the VPN returned. |
| Reboot, network change | Not tested. |

Attribution note: `vpn_test.py` matches packets to qBittorrent by its sampled local ports and peer addresses, so an unrelated process reusing a port can be flagged (one Apple DNS query was); check flagged packets by hand.

### Deferred operator work for long-term torrent use

Keep the following items open until a designated reviewer records the evidence. Direct HTTPS intake and publication rehearsals can proceed independently.

- [ ] Review the session 3 connected, disconnected, reconnected and VPN-down startup captures, including the startup retest. Record a separate decision and evidence path for each scenario.
- [ ] **Reboot.** Arrange an uninterrupted maintenance window. Capture from before qBittorrent starts after boot, retain the physical-interface capture and startup timeline, and check the route and binding before starting the official Debian test transfer. A capture started after client launch leaves startup unverified.
- [ ] **Network change.** Arrange a second connection. During the Debian test, capture the old and new physical interfaces through the handoff and tunnel recovery. Record TCP, UDP, IPv4 and IPv6 observations on both connections, including DNS and client background traffic.
- [ ] Save the dated phase marks, samples, captures, attribution analysis and reviewer decisions under the private worker network-checks directory. Record evidence expiration and run the guard before any GSA torrent use.

## Session 4 reconciliation (2026-11-19)

Ported onto the merged pipeline from PR #87: quarantine of files that fail the malware scan, numbered candidates ranked with scans above ebook conversions plus a reviewer `select` command, reviewer resolution of ambiguous archive matches, and the `torrent_acquisition_approved` staff flag on `torrent-loop`. `sandbox_trial.py` passed 22/22 in `sandbox-session4-reconciled/` under the worker home (fake Google and qBittorrent, real ClamAV 1.5.5, poppler and qpdf). The guard step used the real session 3 evidence draft and still fails on 8 issues, so no torrent may run.

## Session 5 (2026-11-19)

- **Review site.**
  - The worker's Google token has Forms, Docs and Sheets read scopes but no Drive scope, so `folders` builds the tree from the Table of Contents (PRs #90 and #91).
  - Run it as `review_portal.py folders --home WORKER_HOME --config WORKER_HOME/pipeline-config.json`.
  - A synthetic sandbox packet (`sandbox-session5`, fake destination) is queued for the browser check. Remove it afterwards with `remove`.
  - The browser check could not be driven from the session (Chrome Profile 1 was signed out of samuelbaird.com, and no browser-control tool was available), so the owner runs it by hand.
- **Read-only pilot.** A supervised `poll` against the real form ran into a separate pilot queue under the worker home; the form currently holds 3 responses. Triage produced 5 works. The index check found no archive copies. The private comparison and the draft staff questions are in that pilot folder.
  - `check` cannot run against live folders until `destination_ids` is set and the worker has Drive read access.
  - Table of Contents matching is filename-only, so it never yields `exact`.
- **Config.** `scanner_max_db_age_hours: 72` and `required_publication_reviewers` (both reviewers) were added with the owner's approval. A backup is at `pipeline-config.before-session5-2026-11-19.json`. Run `freshclam` against the worker database before validating.
- **Changelog format.** Requests & Updates uses plain `MM/DD/YY` lines, newest first. `changelog_anchor` is still a placeholder pending staff approval.
- **Network evidence review.** A private review aid sits next to the session 3 evidence. Two gaps matter:
  - The VPN-down startup retest capture hit its file limit before the VPN returned, and its sampler started after qBittorrent launched.
  - In every "VPN off" window a high-rate UDP flow to the VPN provider's network continued, so "off" may not mean all VPN transport stopped.

  No scenario is signed.
- **Unattended intake.** No dedicated worker account exists yet. A private `unattended-intake-check/check.sh` under the worker home checks five things:
  - Keychain access.
  - Offline start, simulated with an unreachable local proxy.
  - Recovery once back online.
  - A second concurrent run is refused.
  - Overlap replay adds no duplicates.

  It passed as the owner's account as a dry run only. The gate stays open until it is run as the worker account.
