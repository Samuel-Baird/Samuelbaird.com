# GSA intake pilot lessons

For the current result and remaining work, see [STATUS.md](STATUS.md). Earlier sections record the findings available at that stage. All three requested books have now been delivered.

## Find the correct file

The three book searches returned HTTP 403 on the command line. An interactive browser showed the catalog records on the same mirror. An HTTP 403 response gives no information about whether the book exists.

1. Search for the title and author in the browser.
2. Check the language, edition, and file format.
3. Record the catalog URL and the MD5 value for that file.
4. Open the catalog record to find its collection torrent.
5. Inspect the torrent file list before you start a transfer.

The catalog MD5 identifies the book file. The torrent infohash identifies the collection. One value cannot replace the other. The worker can select a book only if the torrent lists the book as a separate file. A torrent can list a single large archive that contains many books.

The Moltmann and Zizioulas torrents that we inspected each listed one TAR file. They contained about 303 GB and 126 GB of data respectively. The Internet Archive copy of Volf also mapped to one TAR file. Another Volf collection listed files by number. The worker requires a PDF file name or a file name that matches the catalog MD5. These four collections had no verified, selectable PDF for this test.

## Test the network

A Debian transfer confirmed that the client could receive data through the VPN. The completed ISO matched its published checksum. This test covered the connected condition only.

After a cold start, the Mac used Wi-Fi while the VPN was down. The first packet capture recorded process names but truncated the packet headers. A second capture included IPv4 and IPv6 headers. Neither capture showed Wi-Fi packets attributed to qBittorrent during the observed startup period.

1. Start the packet capture before you start qBittorrent.
2. Check that the capture includes the required headers.
3. Compare packet observations with the client sockets and transfer counters.
4. Keep the capture times and limitations with the results.

This Mac has one physical network connection. Its guard checks the Wi-Fi interface and the VPN transport. Other installations retain their configured network tests.

## Check the book before delivery

A Volf PDF from a separate source passed the malware scan and PDF checks. Its bibliography stopped at printed page 297. The catalog described 314 pages and an index. The file failed the completeness check. Its MD5 also matched one Anna’s Archive record (c7a2ee6d53dc11b6727896c7466f4f11). A second source with that checksum contains the same incomplete file.

1. Check the file against the selected catalog record.
2. Scan the file for malware.
3. Inspect the title page and edition information.
4. Check the last numbered page, bibliography, and index against the edition description.
5. Put the file in the test folder only after these checks pass.

## Numeric member test on 19 November 2026

The Volf catalog record for MD5 `350df8c1dff62445ee01a634884050ce`
shows server path `g5/zlib1/zlib1/pilimi-zlib-7230000-9459999/7465862`.
The torrent lists `pilimi-zlib-7230000-9459999/7465862` as a separate
12,816,080-byte member. Its infohash is
`c7b43de887da2c0e6108cb59461272b78b0d1ca4`.

The live test selected only this member. qBittorrent recorded 16,777,216
downloaded bytes, which includes boundary pieces. The worker checked the PDF
signature and MD5 before staging. Malware and PDF checks passed. Visual checks
confirmed the 1998 Eerdmans edition, bibliography through page 306, and index
through the final numbered page 314. The delivered copy in AI testing passed
full readback with the same MD5 and SHA-256.

A numeric member requires a recorded catalog mapping in the source review.
The worker checks that the mapping uses the same catalog URL, member path,
and MD5. The operator must verify the evidence in the catalog. These fields
are an operator record, not independent proof from the catalog.

qBittorrent can briefly report a checking state after an add or a stopped
state after a start. Wait for the requested state before the next command.
The prepare command correctly refuses a collection that is still checking.

## Retry and browser fallback correction

The first Moltmann and Zizioulas tests were too short to establish that the
files were unavailable. Saved samples show about 20 to 96 active seconds.
A tracker seed count is a report from the tracker. It does not show that a
seed is connected or will supply the selected pieces. A connected seed can
also stop sending data. The reason for the repeated 327,680-byte stops was
not established. Do not label this value as a server limit.

1. Keep the partial member for a later guarded retry.
2. Record connected seeds, member progress, and time without new data.
3. Use the configured stall and retry limits before declaring the torrent attempt exhausted.
4. Try another verified collection member.
5. Open the catalog in Chrome if the torrent route does not complete.
6. Select a listed partner download.
7. Check the complete browser download with the same MD5, PDF, scanner, and completeness checks.

A catalog listing does not establish that a complete copy is retrievable.
The browser fallback can use an HTTPS server independently of torrent peers.
On this Mac, the browser access host was unavailable. Native Chrome control
opened Slow Partner Server #9 and started both remaining book downloads.
Starting a download is not a passing acquisition result.

The longer Zizioulas torrent retry received 393,216 bytes. This exceeds the
first stop value. Chrome Slow Partner Server #1 then supplied the complete
12,636,743-byte PDF. Its MD5 is `633a155e02e4f94056d6b7715c75bcfb`.
The scanner and PDF checks passed. Visual checks confirmed the title page,
printing statement, List of Sources on page 261, and index through page 269.
The title page says 1997. The copyright page records third printing, 2000.
The delivered AI testing copy passed the full MD5 readback.

Chrome Slow Partner Server #1 also supplied the complete Moltmann PDF. Its MD5 is `74d82bdbf98a644c529599ddd83e353e`. The 1993 Fortress Press edition has notes and references on pages 224-253 and an index through page 256. All checks and the Drive readback passed. All three requested books are now delivered.
