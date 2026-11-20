# GSA torrenting plan

Current test results and remaining work: [STATUS.md](STATUS.md).

Code: [SETUP.md](SETUP.md) (local pilot, offline rehearsal and network notes) and [PIPELINE.md](PIPELINE.md) (supervised pipeline, rollout gates). Private config, credentials and request data live in `~/Library/Application Support/GSA Worker`, never in this repo.

Run a volunteer workflow on a dedicated Mac. New form submissions and bulk book or paper lists enter the same queue. The agent checks the archive first, identifies the requested edition, acquires eligible files, and prepares them for staff-approved upload. Start with a dry run and a supervised pilot.

## Where the work happens

| GSA resource | Role in the workflow |
| --- | --- |
| Request form | Source of new submissions. The volunteer manual directs volunteers to the form’s **Responses** tab. |
| Table of Contents | Search by file name and folder path. The manual says the index refreshes daily, so also check the destination folder before upload. |
| Read, Listen, Watch, Visuals, Quick Quotes, Languages, Gospel Scholar Resources, External Drives | Use the existing hierarchy to propose a destination. Books and papers generally start under **Read**. Follow the closest existing shelf or series and route ambiguous placements to staff. Treat shortcuts to external drives as references. |
| Welcome – Archive Master Documents | **Preface** explains collection scope and quality expectations. **Requests & Updates** is the dated record of outcomes and additions. **Revitalizing Your Personal Study** gives collection and bibliography context. |

The volunteer manual calls for PDF, MP3, or MP4, descriptive filenames, and dated entries in **Requests & Updates**. For example, name a single-author book `Lastname, Title.pdf`, a two-author book `Lastname1 & Lastname2, Title.pdf`, and a numbered recording `42 - Episode Title.mp3`. Use the current dated section and staff formatting for requests and additions. Let the existing process refresh the Table of Contents.

## Set up and test the Mac

1. Install [qBittorrent for macOS](https://www.qbittorrent.org/download) and the chosen VPN client. Use a dedicated standard macOS account. Keep incomplete downloads and candidates awaiting review in local folders outside any Drive sync folder. Set queue and disk limits, and store credentials in Keychain.
2. With the VPN connected, identify its tunnel interface by comparing the interface and routing state before and after connection. In qBittorrent’s advanced settings, bind **Network interface** to the confirmed tunnel. Turn on the VPN’s kill switch and turn off split tunneling if those options are available. Record the binding and check it after a VPN reconnect or reboot, since the interface name can change.
3. Start an [official Debian torrent](https://www.debian.org/CD/torrent-cd/) and wait for sustained transfer. Keep qBittorrent running while deliberately disconnecting and reconnecting the VPN. Check both TCP and UDP traffic, including IPv6 if available. Where possible, inspect the underlying network interface for direct peer and tracker traffic during the disconnect. Expect the transfer to stop and resume only after the approved tunnel returns. The speed column can lag. Repeat with the VPN already down at startup, and again after reboot or a network change. Verify the downloaded image against Debian’s published checksums.
4. Keep the torrent worker paused until these tests pass. If the tunnel disappears or the binding no longer matches, pause queued jobs and require a fresh check. Use `launchd` for the intake worker once the unattended startup behavior has been tested. If using qBittorrent’s Web UI for automation, bind it to localhost and require authentication.

## Process new requests

1. **Intake.** Start with a five-minute poll using [Google Forms `responses.list`](https://developers.google.com/workspace/forms/api/reference/rest/v1/forms.responses/list) if David approves API access. Use a read-only responses scope, page through results, and store a checkpoint only after the batch is written to a local SQLite queue. Use a small overlap on polls and deduplicate by form response ID. A staff-owned [installable form-submit trigger](https://developers.google.com/apps-script/guides/triggers/installable) can be added later if faster pickup matters. Authenticate trigger messages and retain polling for reconciliation. Keep the queue on the Mac and store only the request details needed to fulfill the item.
2. **Match and check for duplicates.** Normalize title and author, then check DOI, ISBN, edition, year, language, or volume where available. Search the Table of Contents and the proposed destination. Record an existing match as **Already in GSA**. Send ambiguous editions, conflicting records, or unclear destinations to review. Preserve the original submission ID even when several requests refer to one item.
3. **Find and acquire.** For clear matches, look for publisher or institutional repository copies first. Anna’s Archive can provide a lead for a matching work. Review the complete torrent file list. Route mixed bundles and unsuitable files to review. Capture the source and edition in the private job record.
4. **Validate and stage.** Check the file type, malware scan result, completeness, and bibliography against the request. For scans, confirm the first and last pages and spot-check the body. Keep the approved filename, destination, and SHA-256 in the review record. If a format conversion is needed, review output quality before upload.
5. **Publish and confirm.** During the pilot, staff approve the candidate and destination before any live write. Recheck for a duplicate, upload, then verify the returned Drive file ID, name, folder, and file readability. Only then record the dated outcome in **Requests & Updates** using the existing format. Apply the staff-approved notification procedure if there is one. Queue statuses should track individual submissions while leaving the form response history available. Confirm retention and closure with David before implementing either.
6. **Recover from interruptions.** Persist the upload receipt before updating the changelog. If the process stops between those writes, check Drive for the matching file and retry the missing action. Record the changelog write with its date and target so retries can detect an existing entry. Use bounded retries for temporary errors and send persistent failures or stalled torrents to review.

## Bulk books and papers

Accept a CSV with one work per row. Require a title, DOI, or ISBN. When using title alone, include author and edition details whenever possible. Allow a suggested shelf and a source URL as hints. Use separate ISBN and DOI fields so identifiers are easy to validate.

```csv
row_id,title,author,year,edition,isbn,doi,language,suggested_shelf,source_url
1,Example book,A. Author,2020,2nd,,,en,Read/Bible,
2,Example article,B. Author,2024,,,,en,Read/Articles,
```

Run a dry import before downloading. The manifest should show the matched work and edition, archive duplicates, source, estimated size, proposed filename and destination, and items requiring review. Once approved, pass eligible rows to the same queue with a batch ID. Limit active downloads and total disk use. Deduplicate across the batch and form queue, and reuse any already-staged file with the same hash. Return a CSV with a per-row outcome, reason, and any verified Drive link. Preserve prior outcomes when re-running failed rows. Staff can decide whether bulk additions belong in one dated changelog entry or several.

## Rollout and staff decisions

| Phase | Ready to advance when |
| --- | --- |
| Mac setup | The Debian transfer passes the connected, disconnected, and reconnected checks, including after restart. |
| Mock data | Synthetic form responses and a sample CSV exercise duplicates, ambiguous matches, unsupported files, a stalled download, and an interruption after upload. |
| Read-only pilot | David authorizes intake access and approves a review of a small set of real requests. Compare the agent’s matches and proposed destinations against a volunteer’s decisions. |
| Supervised fulfillment | David confirms the writable folders and changelog access, names the reviewer, and signs off on response retention, notification, and the allowed sources. Staff review the first uploads and their changelog entries. |
| Routine operation | Staff agree on which steps can run unattended, who reviews exceptions, and how to pause the worker. |

The first build can use mock submissions and a sandbox destination while staff access is pending. Keep production IDs, tokens, response data, and staff-only instructions in private configuration outside this repository.
