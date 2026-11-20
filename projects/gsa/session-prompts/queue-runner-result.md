# Queue runner result

Date: 19 November 2026.
Files added: `gsa_runner.py`, `tests/test_gsa_runner.py`, and this file.
No other file was changed. The runner did not change `pipeline.py`, the private configuration, qBittorrent, the VPN, live queues, Drive, the review site, or schedules.

## Summary

`gsa_runner.py` is a separate entry point. It finds the next action for each request from the existing queue records. It records its own attempts in new tables. It does eligible operations only through the existing `pipeline.py` functions.

- `plan` is read-only. It does not take the worker lock. You can use it while torrent retries or other pipeline commands run.
- `run` is a dry run by default. A dry run writes nothing and calls no service.
- `run --execute` holds `pipeline.lock`, which is the lock that `pipeline.py` uses. It does a maximum of `--max-actions` operations (default 3, limit 20).
- The runner can do only these operations: `acquire` (reviewed HTTPS download from an approved host), `validate`, and `check` (archive duplicate check, which reads Drive).
- The runner does `publish` only when the operator gives `--execute --allow-publish --work ID`. The existing `publication_approved` setting, approval checks, and the fresh duplicate check in `pipeline.publish` still apply.
- The runner does not start, stop, reannounce, or recheck torrents. It does not use a browser. It does not triage, write source reviews, approve, or collect review-site decisions. For these steps it shows a concrete next action for the agent, operator, reviewer, or staff.

## Usage

Run these commands from `projects/gsa`. Replace `CONFIG` with the private configuration (mode 0600). Replace `HOME` with the worker home or a sandbox home.

1. Show the next action for each request:

   ```sh
   python3 gsa_runner.py --config CONFIG --home HOME plan
   python3 gsa_runner.py --config CONFIG --home HOME plan --work 3 --json
   ```

2. Show the operations that a run would do. This step writes nothing:

   ```sh
   python3 gsa_runner.py --config CONFIG --home HOME run
   ```

3. Do the eligible operations:

   ```sh
   python3 gsa_runner.py --config CONFIG --home HOME run --execute --max-actions 3
   python3 gsa_runner.py --config CONFIG --home HOME run --execute --actions validate,check --work 3
   ```

4. Publish one approved work under supervision:

   ```sh
   python3 gsa_runner.py --config CONFIG --home HOME run --execute --allow-publish --work 3 --max-actions 1
   ```

5. Show the recorded runner attempts:

   ```sh
   python3 gsa_runner.py --config CONFIG --home HOME history --work 3
   ```

Exit status 75 means that another `pipeline.py` or runner process holds the worker lock. The runner did nothing in this case.

## Stages

The plan gives each request one stage, one actor, the reason, and the next action. The stage comes only from recorded data. The runner never marks work as complete, approved, or failed by inference.

| Stage | Record condition | Actor | Next action |
| --- | --- | --- | --- |
| `untriaged` | `form_requests` row with status `needs_review` | agent | Write a triage packet. Run `pipeline.py triage`. The plan does not show request text. |
| `source_review` | Work with no `review` in `pipeline_records` | agent | Find the source and decide the edition. Run `pipeline.py review`. |
| `acquisition` | Review, no live candidate, approved HTTPS host | runner | `acquire` |
| `acquisition` | Review names a torrent | operator, staff, or wait | `prepare-member` or `torrent-loop`, or wait. See "Torrent stall policy". |
| `browser_import` | Catalog source that is not a direct download, or torrent retries at the limit | operator | Download the file in Chrome. Register it with the browser-file import command. |
| `validation` | Live candidate without a report, or a new candidate | runner | `validate` |
| `validation` | Best report failed | operator | Inspect `rank`. Get another candidate or revise the review. |
| `duplicate_check` | No archive check, or the check is older than the last `validated`, `candidate_selected`, or `source_review` event, or a different destination | runner | `check` |
| `duplicate_check` | No destination, or destination not in `destination_ids` | operator | Use the review site (`review_portal.py queue`, then `collect`). |
| `duplicate_review` | Exact archive match | staff | Decide whether to withdraw the request. |
| `duplicate_review` | Ambiguous match without `archive_resolution` | reviewer | Add the match keys and a reason to the approval file. |
| `staff_approval` | No approval, partial reviewer approval, approval for a different SHA-256 or destination, revoked reviewer, or "Changes requested" in `web_review` | reviewer or operator | Queue the review page or record an approval. |
| `publication_ready` | Valid approval, `publication_approved` is not true | staff | Staff enable publication. |
| `publication_ready` | Valid approval, publication enabled | operator | `pipeline.py publish`, or the runner with `--allow-publish --work`. |
| `publishing` | `upload_id` reserved, or status `complete` without both receipts | operator | Run `publish` again. It reuses the reserved Drive ID. |
| `complete` | Upload receipt and changelog receipt recorded | none | None. |

The approval check in the plan copies the checks in `pipeline.publish`, without the file hash. `pipeline.approve` and `pipeline.publish` still hash the file.

## Coordinator records

`gsa_runner.py` adds three tables to `queue.sqlite3`. It creates them only during `run --execute`. It does not change `works`, `pipeline_records`, `pipeline_events`, `upload_sessions`, or `form_requests`.

- `runner_runs`: one row for each executing run, with start time, end time, limit, and result counts.
- `runner_operations`: one row for each attempt. Columns: work ID, action, input fingerprint, attempt number, status, start time, end time, next retry time, and outcome text. Status is `started`, `succeeded`, `transient_failure`, `blocked`, or `interrupted`.
- `runner_state`: the last plan for each request (stage, actor, eligible action, next action, reason). It contains no request text.

The input fingerprint is a hash of the inputs of the operation:

- `acquire`: the complete source review.
- `validate`: the live candidate paths and sizes.
- `check`: the SHA-256, the destination, and the newest input event ID.
- `publish`: the SHA-256 and the destination.

A change to the inputs gives a new fingerprint and a new retry budget.

## Restart and retry behavior

1. The runner writes the `started` row and commits it before each operation.
2. A new executing run holds the lock. It changes each remaining `started` row to `interrupted`. Then it finds the state again from the queue records. If an interrupted download completed, the work already has a candidate. The next step is `validate`, so the runner does not download again.
3. A refused gate (`ValueError`, HTTP 4xx, missing file, Keychain error) gives `blocked`. The runner does not do the same operation with the same inputs again. The plan shows the refusal text.
4. A network failure (URL error, time-out, connection error, HTTP 408, 429, or 5xx, other `OSError`) gives `transient_failure`. The next attempt waits 10, then 20 minutes (doubled each time, limit 240 minutes). After 3 transient failures or interruptions the operator must look at it. The private configuration can override these values with `runner_retry` (`max_attempts`, `backoff_minutes`, `max_backoff_minutes`). The current configuration does not set it.
5. A `succeeded` operation is never done again with the same inputs. Example: a download that succeeded, but validation quarantined the file. The plan then asks the operator to revise the source review or import another file.
6. Publication uses the existing reserved Drive ID and the `[GSA:FILE_ID]` changelog marker. A lost upload response gives a retry after the backoff. The retry finds the stored file and does not upload it again. A run after completion makes no service call.

## Torrent stall policy

The runner reads `torrent_job` from the record. It uses `acquire.DEFAULT_POLICY`, which is the same policy that `torrent-loop` uses (30 minute stall, 3 retries, 10 minute backoff). It never changes the job.

- Active job, last observation in the past 15 minutes: the actor is `wait`. The reason shows the idle minutes and the stall limit.
- Active job, no observation for more than 15 minutes: the operator checks the client and the guard, then runs `torrent-loop` again. The reason says that idle time is not source failure.
- Job in review with retries below the limit: the operator chooses a guarded `torrent-loop` retry or the browser fallback. The reason says that the source is not proven unavailable.
- Job in review with retries at the limit: the stage is `browser_import`. The reason says that the source is not proven unavailable.
- In all cases the plan shows the bytes of partial data in `incomplete/INFOHASH`. The runner never deletes them.

## Test results

Focused tests:

```sh
python3 -W error::ResourceWarning -m unittest discover -s tests -p test_gsa_runner.py
```

Result: 21 tests, OK.

Full suite (includes the new browser-import tests of the other session):

```sh
python3 -m unittest discover -s tests
```

Result: 147 tests, OK.

The tests use temporary homes whose names contain `sandbox`, `tests/fakes.FakeGoogle`, a fake HTTPS opener, and `/usr/bin/true` as the scanner. They cover:

- Action selection: all stages, dry run without writes or service calls, the `--max-actions` limit, the `--actions` filter, and the publish flags.
- Restart: an interrupted download is not repeated, an interrupted attempt is reconciled, and `runner_state` remains after a new connection.
- Lock contention: `run --execute` stops while another process holds `pipeline.lock`. `plan` and the dry run continue to work.
- Blocked prerequisites: torrent acquisition not approved, publication not enabled, no destination, and a destination that is not approved.
- Bounded retry: 10 and 20 minute backoff, limit of 3 attempts, and a refused gate that is not repeated until the source review changes.
- Rejected or changed review: changed approval hash, revised source review, partial reviewer approval, "Changes requested", revoked reviewer, and an added candidate.
- Duplicate prevention: exact match, ambiguous match with resolution, publication after a lost upload response (one file, one changelog entry), and a status of `complete` without receipts.
- Stall policy: a 5 minute idle period gives `wait`, partial data is retained, and the retry limit sends the work to `browser_import` without a failure state.

Read-only check of real records (no lock, no writes; the file times did not change):

- `three-books-sandbox-ut0jwodl`: 3 works at `duplicate_check`, actor operator, reason "The source review has no destination." This is correct. Those three deliveries used connected Drive tools, not the worker publication path, so the queue has no receipts.
- Worker home queue: no requests.

## Remaining integration needs

1. Browser-file import: the other session added `pipeline.py import-candidate` and `candidate_import.py`. That command adds the file to `record['candidates']`. The runner then shows `validate` for that work with no runner change. After that work merges, change the `browser_import` next-action text to the exact command: `python3 pipeline.py --config CONFIG --home HOME import-candidate --work ID --file FILE --evidence SOURCE.json`. Add one test that imports a file and checks that the next stage is `validation`.
2. Review-site decisions: the runner does not read the review site. A "Changes requested" decision shows only after `web_review` is in the record. Add a read-only `review_portal.py status` command if the plan must show site decisions before `collect`.
3. Torrent supervision: `torrent-loop` keeps the job in the record, but it does not record each operator start or stop. If the plan must tell "loop stopped by the operator" from "loop crashed", `torrent-loop` must write a stop event. This is a change to `pipeline.py`. This session did not make it.
4. A source review with no destination: `pipeline.py review` replaces the whole record and removes the candidates. For the three-book sandbox works, use the review site to set the destination. `collect` keeps the validated candidates.
5. Configuration: the runner reads only the existing keys and the optional `runner_retry` key. No configuration change is necessary.
6. Schedules: the runner adds no schedule. Do not run `run --execute` from launchd until staff authorize an acquisition schedule. Never add `--allow-publish` to a schedule.
