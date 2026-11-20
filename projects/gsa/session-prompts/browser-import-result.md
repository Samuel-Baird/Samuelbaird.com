# Browser candidate import: result

Date: 19 November 2026. Status: implemented and tested with fixture homes only.
No private configuration, queue, qBittorrent, VPN, Drive, or review-site record was changed.

## Changed files

- `candidate_import.py` (new): source record loading, review binding, copy, verification, recovery, and registration.
- `pipeline.py`: new `import-candidate` command. The `review` command now checks the format of the optional `source_md5` and `source_bytes` fields.
- `tests/test_candidate_import.py` (new): 16 regression tests.

## Procedure

1. Record a reviewed source change for the work. The review file must contain these fields in addition to the existing review fields:

   ```json
   {
     "source_url": "https://annas-archive.gl/md5/<md5>",
     "source_md5": "<32 lowercase hex digits>",
     "source_bytes": 14339309,
     "source_partners": ["Slow Partner Server #1"]
   }
   ```

   `source_partners` is optional. If it is present, the source record must name one of these values.

2. Run the review command:

   ```sh
   python3 pipeline.py --config "$CONFIG" review --work <id> --file <review.json>
   ```

3. Download the file in Chrome. Wait until Chrome completes the download. Do not use a file that ends in `.crdownload`.
4. Write the source record (see the schema below) to a private file.
5. Set the source record to mode `0600`:

   ```sh
   chmod 600 <source-record.json>
   ```

6. Import the file:

   ```sh
   python3 pipeline.py --home "$HOME/Library/Application Support/GSA Worker" --config "$CONFIG" \
     import-candidate --work <id> --file "$HOME/Downloads/<file>.pdf" --evidence <source-record.json>
   ```

7. Validate the candidate with the existing command:

   ```sh
   python3 pipeline.py --config "$CONFIG" validate --work <id>
   ```

8. Continue with `check`, `approve`, and `publish` as before.

The command prints JSON. `action` is one of these values:

| Value | Meaning |
| --- | --- |
| `imported` | The command copied, verified, and registered a new candidate. |
| `recovered` | An earlier run placed a verified copy but stopped before registration. The command verified the copy again and registered it. |
| `duplicate` | A live candidate with the same MD5 and size is already registered. The command made no change. |

## Source record schema

```json
{
  "schema": "gsa.browser-candidate.v1",
  "work_id": 3,
  "catalog_url": "https://annas-archive.gl/md5/<md5>",
  "source": "Slow Partner Server #1",
  "md5": "<32 lowercase hex digits>",
  "bytes": 14339309,
  "matched_work": "<same value as the source review>",
  "filename": "<same value as the source review>",
  "recorded_by": "<operator>",
  "downloaded_at": "2026-11-19T20:00:00Z"
}
```

All fields are required except `downloaded_at`. Other fields are kept with the candidate.

Binding rules:

- `work_id` must equal `--work`.
- `catalog_url` must equal the review `source_url`.
- `md5` must equal the review `source_md5`.
- `bytes` must equal the review `source_bytes`.
- `matched_work` and `filename` must equal the review values.
- `source` must be in the review `source_partners` list, if the list is present.
- The review `filename` must end in `.pdf`.

The source record cannot replace a reviewed value. To change the source, MD5, size, or work identity, record a new source review first.

## Checks

The command refuses the import in these conditions:

- The source record is not a regular file with mode `0600`, or a required field is missing or malformed.
- The source review has no `source_md5` or `source_bytes`, or a value differs from the source record.
- `--file` is a symbolic link, is not a regular file, passes through a link, or is inside the worker home.
- The file name ends in `.crdownload`, `.part`, `.partial`, `.download`, `.tmp`, or `.opdownload`, or starts with `Unconfirmed `.
- A sibling partial file (for example `<file>.crdownload`) exists.
- The size differs from the reviewed size.
- The file does not start with `%PDF-`.
- The MD5 differs from the reviewed MD5.
- The disk limits fail (`max_file_bytes`, `disk_budget_bytes`, `reserve_bytes`).
- The downloaded file changes (inode, size, or modification time) during the copy.
- The source review changes during the import.
- An upload has started for the work.

## Storage and registration

- The candidate path is `candidates/<work>-browser-<md5>.pdf`. The candidate has mode `0400`.
- The temporary copy is `incomplete/import-<work>-<md5>.part`. The command deletes it after success or failure.
- The command does not change or move the original download.
- The new candidate entry has origin `browser:<catalog_url>`, the MD5, the size, the source, and a copy of the source record with its SHA-256.
- Prior candidates stay in the `candidates` list.
- The new candidate becomes the current candidate. This follows the existing `acquire` rule. The command removes `validation`, `approval`, `reviewer_checks`, `candidate_reports`, and `format_choice`. If the work status is `awaiting_staff_approval`, the status changes to `needs_review`.
- A `duplicate` result does not change the record. An existing approval stays.
- The command does not run validation, ranking, or approval.
- `main()` holds the existing `pipeline.lock` during the import.

## Recovery

- Interrupted copy: the temporary copy is never registered. The next run deletes it and copies again.
- Interrupted registration: the verified candidate exists but is not registered. The next run checks its size and MD5 again and registers it once (`recovered`).
- Changed unregistered candidate: if the file at the candidate path does not match the review, the command stops. It does not register or overwrite that file. Staff must review it.

## Test results

Focused tests:

```text
python3 -m unittest test_candidate_import   (from tests/)
Ran 16 tests in 0.091s
OK
```

The tests cover a passing import, flow into `validate_file`, incomplete input, partial Chrome files, checksum mismatch, wrong file type, unsafe paths, review binding, a review without a source checksum, insufficient disk space (reserve, budget, and file limit), duplicate import, duplicate bytes from another route, interrupted copy, interrupted registration, a changed unregistered candidate, concurrent review and file changes, approval handling, and an upload in progress.

Full suite:

```text
python3 -m unittest discover -s tests
Ran 126 tests in 15.789s
OK

node --test tests/review-website.test.mjs
tests 12, pass 12, fail 0
```

CLI check in a temporary fixture home: the first `import-candidate` run returned `imported`. The second run returned `duplicate`.

## Limitations

- The source record is an operator attestation. The command does not check the catalog page or the partner server.
- The `review` command still replaces the whole pipeline record. A reviewed source change therefore removes earlier candidates from the record. The files stay on disk. The import command preserves the candidates that exist after the latest review.
- The command accepts PDF files only.
- A path through a symbolic link is refused. On macOS, `/tmp` is a link to `/private/tmp`. Give the resolved path, for example a path in `~/Downloads`.
- The command did not run against the live worker home. The live three-book files were registered earlier by supervised Python calls. They were not imported again.
