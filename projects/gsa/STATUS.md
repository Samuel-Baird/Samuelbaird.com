# GSA pipeline status

Updated after the three-book test on 19 November 2026 (Mac local date).
This is the current status. Earlier session notes in `SETUP.md` are historical.
Private configuration, credentials, requests, and receipts stay under
`~/Library/Application Support/GSA Worker`.

## Completed work

- Live read-only Forms intake passed. A replay added no duplicate submissions.
- The dedicated qBittorrent profile, VPN binding, disk limits, and scanner are installed.
- The Debian transfer and checksum test passed.
- Approved fixed Wi-Fi evidence includes the cold-start test. It expires at `2026-11-27T00:24:33.069268+00:00`.
- Volf downloaded through BitTorrent as one numeric member. All other members had zero priority.
- Zizioulas and Moltmann downloaded through Chrome from Anna's Archive Slow Partner Server #1.
- All three books passed checksum, PDF signature, scanner, format, and completeness checks. All three copies in the existing AI testing folder passed full checksum readback.
- The review site and sandbox publication have live evidence. One work in `sandbox-divination-portal` has status `complete` with both upload and changelog receipts.
- The acquisition change passed 110 tests and four session checks. These results do not establish unattended production readiness.

## Three-book result

| Book | Successful route | PDF bytes | Verified MD5 | Completeness |
| --- | --- | ---: | --- | --- |
| After Our Likeness | BitTorrent member `7465862` | 12,816,080 | `350df8c1dff62445ee01a634884050ce` | 1998 Eerdmans; bibliography 283-306; index 307-314; final numbered page 314 |
| Being as Communion | Chrome, Slow Partner Server #1 | 12,636,743 | `633a155e02e4f94056d6b7715c75bcfb` | Title page 1997; third printing 2000; List of Sources 261; index 263-269; final numbered page 269 |
| The Trinity and the Kingdom | Chrome, Slow Partner Server #1 | 14,339,309 | `74d82bdbf98a644c529599ddd83e353e` | First Fortress Press edition, 1993; notes and references 224-253; index 253-256; final numbered page 256 |

The Volf infohash is `c7b43de887da2c0e6108cb59461272b78b0d1ca4`.
The selected member is `pilimi-zlib-7230000-9459999/7465862`.
qBittorrent recorded 16,777,216 downloaded bytes, including boundary pieces.
The excluded Volf MD5 `c7a2ee6d53dc11b6727896c7466f4f11` remains unsuitable.

The full attempt history and delivery links are in
`three-books-sandbox-ut0jwodl/acquisition-test-report.json` under the worker
home. The `volf-delivery-receipt.json`, `zizioulas-browser-receipt.json`, and
`moltmann-browser-receipt.json` files record the passing readback checks.
The three-book deliveries used connected Drive tools. They did not exercise
the production worker's publication and changelog commands.

## Acquisition procedure

1. Check the requested edition against the archive.
2. Identify a matching source file.
3. Record the catalog URL and expected MD5.
4. Inspect the torrent member list.
5. Verify any numeric member mapping in the catalog.
6. Run the network guard.
7. Prepare only the selected member while the torrent is stopped.
8. Start the selected transfer.
9. Monitor the transfer with the configured stall and retry limits.
10. Try another verified member if the first torrent attempt does not complete.
11. Open the catalog in Chrome if the torrent route does not complete.
12. Select a listed partner download.
13. Wait for the complete browser download.
14. Verify the expected MD5 and PDF signature before staging.
15. Run the configured scanner and PDF checks.
16. Check the title page, edition, body samples, final numbered page, bibliography, and index.
17. Deliver the passing file to the reviewed destination.
18. Verify the delivered copy.

Keep partial torrent data for a later retry. Do not download a large TAR
collection in full to obtain one book. A TAR member route requires a verified
member mapping and a maximum transfer size before use.

The first failed torrent attempts ran for about 20-96 active seconds. They
did not establish permanent unavailability. A longer Zizioulas retry received
393,216 bytes. The earlier 327,680-byte stop was not a proven fixed limit.
The cause of the stalls was not established. A tracker seed count does not
prove that a seed is connected or will supply the selected pieces.

The browser fallback uses HTTPS independently of torrent peers. Partner
speed varies. Partner links expire. Respect the partner's concurrent transfer
limit. This test completed all three books through available routes. It does
not establish a universal success rate. A catalog entry alone does not
establish that a complete file can be retrieved.

## Remaining work

### 1. Add supported browser-candidate import

The CLI has no candidate import command. The live browser test used supervised
Python calls to stage and register the files. Add a command that accepts a
complete local file, binds it to the reviewed work and expected checksum,
enforces disk limits, preserves source evidence, and uses normal validation
and review. Test incomplete files, wrong checksums, restart, and duplicate import.

### 2. Connect the queue steps

Free-text triage, source search, edition matching, member review, source fallback,
and completeness review still need agent or operator work. The commands do not
form one automatic request-to-publication runner. Add persistent step records
and bounded retries so a restart can resume work. Keep browser interaction and
content review supervised where necessary. A browser host was unavailable in
this test; native Chrome control provided the fallback.

### 3. Complete production publication configuration

The production configuration currently has:

- `publication_approved: false`
- Empty `destination_ids`
- Empty `source_hosts`
- A placeholder `changelog_anchor`
- `unattended_intake_validated: false`

The recorded worker credential has read access to Forms, Docs, and Sheets.
Production Drive access and Docs write access remain to be established under
the worker credential. Connected chat tools do not supply credentials to the
scheduled worker. Confirm the allowed sources, production destinations, and
dated changelog procedure before enabling production writes.

The current production threshold permits one assigned reviewer to approve.
A change request still holds publication. Do not reset this threshold as part
of the remaining work.

### 4. Prove one supervised production request

Use the intended worker credential for the full path. Check archive duplicates,
review approval, upload receipt, readback, and one dated changelog entry.
Confirm that a retry creates neither a duplicate file nor a duplicate entry.
The sandbox result and AI testing deliveries do not replace this test.

### 5. Validate unattended startup

No dedicated GSA account was found. Confirm the intended runtime account or
create the planned account. Check Keychain access, offline startup, recovery,
concurrent-run exclusion, and overlap replay under that account.
The current `unattended_intake_validated` setting is false.

### 6. Enable the intake schedule

No GSA job was found in the current user's LaunchAgents folder. Generate and
install the five-minute intake job after unattended validation. The existing
job polls intake only. It does not acquire or publish. Define and authorize
any separate acquisition or publication schedule before enabling it.

### 7. Set the operating procedure

Define who handles exceptions, how to pause the worker, how long to retain
private requests and partial files, and whether requester notifications are
required. Maintain scanner signatures. Renew network evidence before expiry.
Add a visible record of failed jobs and the last successful poll.

The next implementation task is the browser-candidate import command.
The next full-system proof is one supervised production request with the
intended credential, production destination, and changelog.
