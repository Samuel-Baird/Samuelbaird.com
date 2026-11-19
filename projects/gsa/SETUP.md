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
