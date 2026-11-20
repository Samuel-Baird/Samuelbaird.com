#!/usr/bin/env python3
"""Resumable, supervised GSA queue coordinator. Standard library only.

The coordinator derives the next step for each request from the existing queue
records (works, pipeline_records, pipeline_events, form_requests). It adds its
own records (runner_runs, runner_operations, runner_state) and never replaces
the queue or publication records.

- `plan` opens the queue read-only. It writes nothing and takes no lock.
- `run` without `--execute` is a dry run. It shows the actions that a run would
  do. It writes nothing and calls no service.
- `run --execute` holds the worker lock (`pipeline.lock`), the same lock that
  pipeline.py uses. It does a bounded number of eligible operations through the
  existing pipeline functions and records each attempt before it starts.

The runner never starts, stops, or retries a torrent, never uses a browser,
never triages, reviews, or approves, and never publishes unless the operator
names one work with `--allow-publish`. No schedule is added or loaded.
"""
import argparse
from contextlib import closing
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.parse

import acquire as acquisition
import gsa
import pipeline as p

STAGES = ('untriaged', 'source_review', 'acquisition', 'browser_import', 'validation',
          'duplicate_check', 'duplicate_review', 'staff_approval', 'publication_ready',
          'publishing', 'complete')
RUNNER_ACTIONS = ('acquire', 'validate', 'check', 'publish')
DEFAULT_ACTIONS = ('acquire', 'validate', 'check')
DEFAULT_RETRY = {'max_attempts': 3, 'backoff_minutes': 10, 'max_backoff_minutes': 240}
MAX_ACTIONS_LIMIT = 20
TRANSIENT_HTTP = (408, 429, 500, 502, 503, 504)
# A torrent-loop poll is every 15 s. No observation for this long means no loop runs.
LOOP_SILENCE_SECONDS = 15 * 60

SCHEMA = '''
CREATE TABLE IF NOT EXISTS runner_runs (
  id INTEGER PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT, mode TEXT NOT NULL,
  max_actions INTEGER NOT NULL, outcome TEXT);
CREATE TABLE IF NOT EXISTS runner_operations (
  id INTEGER PRIMARY KEY, run_id INTEGER REFERENCES runner_runs(id), work_id INTEGER NOT NULL,
  action TEXT NOT NULL, fingerprint TEXT NOT NULL, attempt INTEGER NOT NULL, status TEXT NOT NULL,
  started_at REAL NOT NULL, finished_at REAL, next_retry_at REAL, outcome TEXT);
CREATE INDEX IF NOT EXISTS runner_operations_key ON runner_operations(work_id, action, fingerprint);
CREATE TABLE IF NOT EXISTS runner_state (
  item TEXT PRIMARY KEY, work_id INTEGER, stage TEXT NOT NULL, actor TEXT NOT NULL, action TEXT,
  next_action TEXT NOT NULL, reason TEXT NOT NULL, updated_at TEXT NOT NULL);
'''


class LockBusy(RuntimeError):
    pass


def migrate(db):
    db.executescript(SCHEMA)


def fingerprint(*parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:24]


def iso(epoch):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(epoch))


def retry_policy(config):
    policy = dict(DEFAULT_RETRY, **(config.get('runner_retry') or {}))
    p.require(all(isinstance(v, (int, float)) and v > 0 for v in policy.values()), 'Invalid runner_retry')
    return policy


def open_readonly(home):
    path = home / 'queue.sqlite3'
    p.require(path.is_file(), f'No queue at {path}')
    db = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    return db


def tables(db):
    return {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}


# ------------------------------------------------------------------ state derivation

def item(work_id, stage, actor, next_action, reason, action=None, inputs=None, title=''):
    """actor: runner (eligible runner action), agent, operator, reviewer, staff, wait, none."""
    return {'item': f'work:{work_id}', 'work_id': work_id, 'title': title, 'stage': stage, 'actor': actor,
            'action': action, 'fingerprint': fingerprint(action, inputs) if action else None,
            'next_action': next_action, 'reason': reason, 'eligible': action is not None}


def command(wid, text):
    return f'python3 pipeline.py --config CONFIG --home HOME {text} --work {wid}'


def partial_bytes(home, infohash, member):
    """Size of retained torrent data. Read only; the runner never deletes it."""
    root = home / 'incomplete' / infohash
    target = root / member if member else root
    try:
        if target.is_file():
            return target.stat().st_size
        if target.is_dir():
            return sum(f.stat().st_size for f in target.rglob('*') if f.is_file())
    except OSError:
        pass
    return 0


def torrent_step(wid, review, record, config, home, now, title):
    policy = acquisition.DEFAULT_POLICY  # torrent_loop applies this same policy
    key = review['infohash'].lower()
    member = review.get('torrent_member')
    partial = partial_bytes(home, key, member)
    kept = f' Partial data retained: {partial} bytes in incomplete/{key}.' if partial else ''
    browser = ('Open the reviewed catalog record in Chrome, download a listed partner file completely, '
               'then register it with the supported browser-file import command. '
               'Then run: python3 gsa_runner.py plan')
    if config.get('torrent_acquisition_approved') is not True:
        return item(wid, 'acquisition', 'staff', browser,
                    'Torrent acquisition is not approved in the private configuration.' + kept, title=title)
    job = record.get('torrent_job')
    if not job:
        return item(wid, 'acquisition', 'operator',
                    f'Add the collection stopped with save path incomplete/{key}, then run: '
                    + command(wid, 'prepare-member --file COLLECTION.torrent --evidence NETWORK.json')
                    + ' ; start the job ; then run torrent-loop with the same arguments',
                    'The source review names a torrent. The runner does not control torrents.' + kept, title=title)
    history = job.get('history') or []
    last = history[-1] if history else {}
    status = job.get('status')
    retries, limit = job.get('retries', 0), policy['max_retries']
    if status == 'active':
        observed = last.get('at', job.get('started_at', now))
        idle = max(0, observed - job.get('last_progress_at', observed))
        stall = policy['stall_minutes'] * 60
        if now - observed > LOOP_SILENCE_SECONDS:
            return item(wid, 'acquisition', 'operator',
                        'Check the client and guard, then run: '
                        + command(wid, 'torrent-loop --file COLLECTION.torrent --evidence NETWORK.json'),
                        f'No torrent-loop observation since {iso(observed)}. Idle time is not source failure.'
                        + kept, title=title)
        state = (f'idle {int(idle // 60)} of {policy["stall_minutes"]} min stall limit' if idle <= stall
                 else f'stall limit passed; torrent-loop applies retry {retries}/{limit} with backoff')
        return item(wid, 'acquisition', 'wait', 'Wait. torrent-loop supervises this transfer.',
                    f'Transfer active ({state}). Last decision: {last.get("reason", "none")}.' + kept, title=title)
    if status == 'review' and retries < limit:
        return item(wid, 'acquisition', 'operator',
                    'Check the client, guard, and partial data. Then do one of these: resume with '
                    + command(wid, 'torrent-loop --file COLLECTION.torrent --evidence NETWORK.json')
                    + ' ; or use the browser fallback.',
                    f'Torrent attempt paused for review (retries {retries}/{limit}): {last.get("reason", "no reason recorded")}. '
                    'The source is not proven unavailable.' + kept, title=title)
    if status == 'review':
        return item(wid, 'browser_import', 'operator', browser,
                    f'Torrent retries reached the limit ({retries}/{limit}). The source is not proven unavailable.'
                    + kept, title=title)
    return item(wid, 'acquisition', 'operator',
                'Run torrent-loop once to stage the completed member: '
                + command(wid, 'torrent-loop --file COLLECTION.torrent --evidence NETWORK.json'),
                f'Torrent job status {status!r} but no staged candidate.' + kept, title=title)


def acquisition_step(wid, review, record, config, home, now, title):
    if review.get('infohash'):
        return torrent_step(wid, review, record, config, home, now, title)
    url = urllib.parse.urlparse(review.get('source_url', ''))
    if url.scheme == 'https' and url.hostname in (config.get('source_hosts') or []):
        return item(wid, 'acquisition', 'runner', command(wid, 'acquire'),
                    f'Reviewed HTTPS source on an approved host ({url.hostname}).',
                    action='acquire', inputs=review, title=title)
    return item(wid, 'browser_import', 'operator',
                'Open the reviewed catalog record in Chrome, download a listed partner file completely, '
                'then register it with the supported browser-file import command. Then run: python3 gsa_runner.py plan',
                'The reviewed source is not a direct download from an approved host.', title=title)


def approval_state(record, config):
    """Mirror pipeline.publish checks without hashing the file. Returns (valid, reason)."""
    approval = record.get('approval')
    if not approval:
        checks = record.get('reviewer_checks') or {}
        if checks:
            return False, 'Approved so far by ' + ', '.join(sorted(checks)) + '; more assigned reviewer approval required.'
        return False, 'No staff approval is recorded for the current candidate.'
    sha = record.get('sha256')
    if not (approval.get('sha256') == sha == (record.get('validation') or {}).get('sha256')):
        return False, 'The approval binds to a different file. A reviewer must approve the current candidate.'
    if approval.get('destination') != record['review'].get('destination'):
        return False, 'The approval names a different destination than the source review.'
    if approval.get('reviewer') not in config.get('reviewers', []):
        return False, 'The approving reviewer is no longer in the configured reviewers.'
    STAFF_JUDGMENT = p.validation.STAFF_JUDGMENT
    if not all(approval.get(k) is True for k, _ in STAFF_JUDGMENT):
        return False, 'A staff judgment check is missing from the approval.'
    required = config.get('required_publication_reviewers', [])
    if required:
        checks = approval.get('reviewer_checks', {})
        valid = [r for r in required if r in config.get('reviewers', [])
                 and checks.get(r, {}).get('sha256') == sha
                 and checks.get(r, {}).get('destination') == record['review'].get('destination')
                 and all(checks.get(r, {}).get(k) is True for k, _ in STAFF_JUDGMENT)]
        if len(valid) < p.approvals_needed(config):
            return False, 'Assigned reviewer approval is missing or revoked.'
    return True, 'Approved by ' + ', '.join(sorted(approval.get('reviewer_checks') or [approval['reviewer']])) + '.'


def derive_work(work, record, events, config, home, now):
    """Next step for one work from its actual records. Never invents completed work."""
    wid = work['id']
    title = (json.loads(work['metadata']).get('title') or '')[:80]
    if work['upload_receipt'] and work['changelog_receipt']:
        return item(wid, 'complete', 'none', 'None.', 'Upload and changelog receipts are recorded.', title=title)
    if work['status'] in ('complete', 'sandbox_complete'):
        return item(wid, 'publishing', 'operator', 'Reconcile the receipts before any other step.',
                    f'Status {work["status"]!r} without both receipts.', title=title)
    review = record.get('review')
    if not review:
        return item(wid, 'source_review', 'agent',
                    'Search for a source, decide the edition, write a source review packet, then run: '
                    + command(wid, 'review --file REVIEW.json'),
                    'No source review is recorded.', title=title)
    if record.get('upload_id') or work['upload_receipt']:
        return item(wid, 'publishing', 'operator', command(wid, 'publish'),
                    'Publication started (reserved Drive ID). Rerun publish to reconcile; it reuses the same ID.',
                    action='publish', inputs=[record.get('sha256'), review.get('destination')], title=title)
    candidates = record.get('candidates') or ([{'path': record['candidate'], 'origin': 'current'}]
                                              if record.get('candidate') else [])
    live = [c for c in candidates if not c.get('quarantined_to')]
    missing = [c['path'] for c in live if not Path(c['path']).is_file()]
    if missing:
        return item(wid, 'validation', 'operator', 'Restore or withdraw the missing candidate files.',
                    f'{len(missing)} registered candidate file(s) are missing on disk.', title=title)
    if not live:
        step = acquisition_step(wid, review, record, config, home, now, title)
        if candidates:
            step['reason'] += f' {len(candidates)} earlier candidate(s) were quarantined.'
        return step
    reports = record.get('candidate_reports') or []
    validated = {r.get('path') for r in reports}
    if not record.get('validation') or {c['path'] for c in live} - validated:
        inputs = sorted((c['path'], Path(c['path']).stat().st_size) for c in live)
        return item(wid, 'validation', 'runner', command(wid, 'validate'),
                    f'{len(live)} candidate(s); new or unvalidated candidate present.',
                    action='validate', inputs=inputs, title=title)
    best = record['validation']
    if best.get('automated_verdict') != 'pass':
        return item(wid, 'validation', 'operator',
                    'Inspect the validation report (' + command(wid, 'rank') + '). Acquire or import another '
                    'candidate, or revise the source review.',
                    'Validation failed: ' + ', '.join(best.get('automated_failures') or ['unknown']), title=title)
    destination = review.get('destination')
    check = record.get('archive_check')
    newest_input = max(events.get(a, 0) for a in ('validated', 'candidate_selected', 'source_review'))
    if not check or check.get('destination') != destination or events.get('archive_check', 0) < newest_input:
        if not destination:
            # pipeline.py review replaces the record; the portal collect keeps the validated candidates.
            return item(wid, 'duplicate_check', 'operator',
                        'Choose the destination on the review site: review_portal.py queue, then collect.',
                        'The source review has no destination.', title=title)
        if destination not in (config.get('destination_ids') or []):
            return item(wid, 'duplicate_check', 'operator',
                        'Collect the review-site decision (review_portal.py collect), which checks the chosen folder.',
                        'The destination is not in the configured destination_ids.', title=title)
        return item(wid, 'duplicate_check', 'runner', command(wid, 'check'),
                    'No current archive duplicate check for this file and destination.',
                    action='check', inputs=[record.get('sha256'), destination, newest_input], title=title)
    approval = record.get('approval') or {}
    matches = check.get('matches') or []
    open_matches = p.unresolved_matches(matches, approval.get('archive_resolution'))
    if any(m['match'] == 'exact' for m in open_matches):
        return item(wid, 'duplicate_review', 'staff', 'Staff decide whether to withdraw the request.',
                    'An exact archive match exists: ' + ', '.join(m['key'] for m in open_matches if m['match'] == 'exact'),
                    title=title)
    if open_matches:
        return item(wid, 'duplicate_review', 'reviewer',
                    'Each approving reviewer lists the match keys under archive_resolution.matches with a written '
                    'reason in the approval file, then runs: ' + command(wid, 'approve --file APPROVAL.json'),
                    'Ambiguous archive matches: ' + ', '.join(m['key'] for m in open_matches), title=title)
    decisions = (record.get('web_review') or {}).get('decisions') or {}
    held = sorted(name for name, d in decisions.items() if (d or {}).get('decision') == 'Changes requested')
    if held:
        return item(wid, 'staff_approval', 'operator',
                    'Correct the private review packet, increase its version, and queue it again.',
                    'Changes requested by ' + ', '.join(held) + '.', title=title)
    valid, reason = approval_state(record, config)
    if not valid:
        return item(wid, 'staff_approval', 'reviewer',
                    'Queue the review page (review_portal.py queue) or record an approval: '
                    + command(wid, 'approve --file APPROVAL.json'), reason, title=title)
    if config.get('publication_approved') is not True:
        return item(wid, 'publication_ready', 'staff', 'Staff must enable publication before any publish.',
                    reason + ' Live publication is not enabled (publication_approved is not true).', title=title)
    return item(wid, 'publication_ready', 'operator',
                command(wid, 'publish') + '  (or: python3 gsa_runner.py run --execute --allow-publish --work '
                + f'{wid})', reason + ' Publication is a supervised operator step.',
                action='publish', inputs=[record.get('sha256'), destination], title=title)


def operations(db, wid, action, key):
    if 'runner_operations' not in tables(db):
        return []
    return [dict(r) for r in db.execute(
        'SELECT * FROM runner_operations WHERE work_id=? AND action=? AND fingerprint=? ORDER BY id',
        (wid, action, key))]


def overlay(db, step, config, now):
    """Apply recorded runner attempts to an eligible step: dedupe, refusals and retry timing."""
    if not step['action']:
        return step
    ops = operations(db, step['work_id'], step['action'], step['fingerprint'])
    if not ops:
        return step
    policy = retry_policy(config)
    last = ops[-1]
    failures = sum(op['status'] in ('transient_failure', 'interrupted') for op in ops)
    hold = None
    if last['status'] == 'started':
        hold = ('wait', 'An attempt started at ' + iso(last['started_at']) + ' has no result. The next '
                'executing run reconciles it from the records before any retry.')
    elif last['status'] == 'succeeded':
        hold = ('operator', f'The {step["action"]} operation already succeeded for these inputs, but the records '
                'did not advance (for example, the file was quarantined). The runner does not repeat it. '
                'Revise the source review or import another file.')
    elif last['status'] == 'blocked':
        hold = ('operator', f'The last {step["action"]} attempt was refused: {last["outcome"]}. The runner does '
                'not repeat a refused operation with the same inputs. Fix the cause or change the inputs.')
    elif failures >= policy['max_attempts']:
        hold = ('operator', f'{failures} transient failures reached the limit of {int(policy["max_attempts"])}. '
                f'Last: {last["outcome"]}. Check the service, then retry with pipeline.py.')
    elif last['next_retry_at'] and last['next_retry_at'] > now:
        hold = ('wait', f'Retry {failures + 1}/{int(policy["max_attempts"])} after {iso(last["next_retry_at"])}. '
                f'Last: {last["outcome"]}.')
    if hold:
        step = dict(step, actor=hold[0], eligible=False, reason=step['reason'] + ' ' + hold[1])
    return step


def plan(db, config, home, now=None):
    now = time.time() if now is None else now
    names = tables(db)
    items = []
    if 'form_requests' in names:
        for row in db.execute("SELECT form_id, response_id FROM form_requests WHERE status='needs_review' ORDER BY rowid"):
            items.append({'item': f'form:{row[1]}', 'work_id': None, 'title': '', 'stage': 'untriaged',
                          'actor': 'agent', 'action': None, 'fingerprint': None, 'eligible': False,
                          'next_action': 'Read the request privately, write a triage packet, then run: python3 '
                                         'pipeline.py --config CONFIG --home HOME triage --file PACKET.json',
                          'reason': 'Free-text request is not triaged into works.'})
    has_records = 'pipeline_records' in names
    has_events = 'pipeline_events' in names
    for work in db.execute('SELECT * FROM works ORDER BY id'):
        work = dict(work)
        record, events = {}, {}
        if has_records:
            row = db.execute('SELECT record FROM pipeline_records WHERE work_id=?', (work['id'],)).fetchone()
            record = json.loads(row[0]) if row else {}
        if has_events:
            events = {r[0]: r[1] for r in db.execute(
                'SELECT action, MAX(id) FROM pipeline_events WHERE work_id=? GROUP BY action', (work['id'],))}
        try:
            step = derive_work(work, record, events, config, home, now)
        except (KeyError, TypeError, ValueError, OSError) as exc:
            step = item(work['id'], 'source_review', 'operator', 'Inspect the work record.',
                        f'The record cannot be interpreted ({type(exc).__name__}: {exc}).')
        items.append(overlay(db, step, config, now))
    return items


# ------------------------------------------------------------------ execution

def classify(exc):
    """transient: retry with backoff. blocked: a gate refused; do not repeat with the same inputs."""
    if isinstance(exc, urllib.error.HTTPError):
        return 'transient_failure' if exc.code in TRANSIENT_HTTP else 'blocked'
    if isinstance(exc, (urllib.error.URLError, TimeoutError, ConnectionError)):
        return 'transient_failure'
    if isinstance(exc, (FileNotFoundError, PermissionError, subprocess.CalledProcessError)):
        return 'blocked'
    if isinstance(exc, OSError):
        return 'transient_failure'
    return 'blocked'


def perform(db, step, home, config, api_factory):
    wid, action = step['work_id'], step['action']
    if action == 'acquire':
        p.acquire(db, wid, home, config)
    elif action == 'validate':
        p.validate_file(db, wid, config)
    elif action == 'check':
        _, record = p.get(db, wid)
        p.archive_check(db, wid, api_factory(config), config, record['review']['destination'])
    elif action == 'publish':
        work, _ = p.get(db, wid)
        p.require(not (work['upload_receipt'] and work['changelog_receipt']), 'Already published')
        p.publish(db, wid, api_factory(config), config)
    else:
        raise ValueError('Unknown runner action ' + action)


def reconcile(db, now):
    """Under the worker lock, an unfinished attempt belongs to a process that stopped."""
    with db:
        return db.execute("UPDATE runner_operations SET status='interrupted', finished_at=?, next_retry_at=?, "
                          "outcome='Process stopped before a result was recorded; state rederived from records' "
                          "WHERE status='started'", (now, now)).rowcount


def save_states(db, items):
    with db:
        db.execute('DELETE FROM runner_state')
        db.executemany('INSERT INTO runner_state VALUES(?,?,?,?,?,?,?,?)',
                       [(i['item'], i['work_id'], i['stage'], i['actor'], i['action'] if i['eligible'] else None,
                         i['next_action'], i['reason'], p.stamp()) for i in items])


def selectable(step, actions, work, allow_publish):
    if not step['eligible'] or step['action'] not in actions:
        return False
    if work is not None and step['work_id'] != work:
        return False
    return step['action'] != 'publish' or (allow_publish and work == step['work_id'])


def run(home, config, *, execute=False, actions=DEFAULT_ACTIONS, max_actions=3, work=None,
        allow_publish=False, api_factory=None, clock=time.time):
    p.require(1 <= max_actions <= MAX_ACTIONS_LIMIT, f'--max-actions must be 1-{MAX_ACTIONS_LIMIT}')
    p.require(set(actions) <= set(RUNNER_ACTIONS), 'Unknown action')
    p.require(not allow_publish or work is not None, '--allow-publish requires --work')
    if allow_publish:
        actions = tuple(actions) + ('publish',)
    api_factory = api_factory or p.Google
    if not execute:
        with closing(open_readonly(home)) as db:
            items = plan(db, config, home, clock())
        chosen = [i for i in items if selectable(i, actions, work, allow_publish)][:max_actions]
        return {'mode': 'dry-run', 'would_run': chosen, 'plan': items}
    lock_path = home / 'pipeline.lock'
    with lock_path.open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise LockBusy('Another pipeline.py or runner process holds the worker lock; nothing was run') from None
        with closing(gsa.connect(home)) as db:
            p.migrate(db)
            migrate(db)
            with db:
                run_id = db.execute('INSERT INTO runner_runs(started_at,mode,max_actions) VALUES(?,?,?)',
                                    (p.stamp(), 'execute', max_actions)).lastrowid
            interrupted = reconcile(db, clock())
            results = []
            policy = retry_policy(config)
            for _ in range(max_actions):
                items = plan(db, config, home, clock())
                save_states(db, items)
                step = next((i for i in items if selectable(i, actions, work, allow_publish)), None)
                if step is None:
                    break
                ops = operations(db, step['work_id'], step['action'], step['fingerprint'])
                attempt = len(ops) + 1
                with db:
                    op_id = db.execute(
                        'INSERT INTO runner_operations(run_id,work_id,action,fingerprint,attempt,status,started_at) '
                        "VALUES(?,?,?,?,?,'started',?)",
                        (run_id, step['work_id'], step['action'], step['fingerprint'], attempt, clock())).lastrowid
                try:
                    perform(db, step, home, config, api_factory)
                    status, outcome, retry_at = 'succeeded', 'ok', None
                except Exception as exc:  # noqa: BLE001 - every failure is recorded, then the run continues
                    status = classify(exc)
                    outcome = f'{type(exc).__name__}: {exc}'[:500]
                    failures = 1 + sum(o['status'] in ('transient_failure', 'interrupted') for o in ops)
                    delay = min(policy['backoff_minutes'] * 2 ** (failures - 1), policy['max_backoff_minutes']) * 60
                    retry_at = clock() + delay if status == 'transient_failure' else None
                with db:
                    db.execute('UPDATE runner_operations SET status=?,finished_at=?,next_retry_at=?,outcome=? WHERE id=?',
                               (status, clock(), retry_at, outcome, op_id))
                results.append({'work_id': step['work_id'], 'action': step['action'], 'attempt': attempt,
                                'status': status, 'outcome': outcome})
            items = plan(db, config, home, clock())
            save_states(db, items)
            with db:
                db.execute('UPDATE runner_runs SET finished_at=?, outcome=? WHERE id=?',
                           (p.stamp(), json.dumps({'operations': len(results), 'interrupted': interrupted}), run_id))
            return {'mode': 'execute', 'run_id': run_id, 'reconciled_interrupted': interrupted,
                    'operations': results, 'plan': items}


def history(home, work=None):
    with closing(open_readonly(home)) as db:
        if 'runner_operations' not in tables(db):
            return []
        query = 'SELECT * FROM runner_operations' + (' WHERE work_id=?' if work is not None else '') + ' ORDER BY id'
        return [dict(r) for r in db.execute(query, (work,) if work is not None else ())]


# ------------------------------------------------------------------ CLI

def render(items, out):
    for i in items:
        flag = 'RUN ' if i['eligible'] else ''
        out.write(f"{i['item']:<14} {i['stage']:<18} {i['actor']:<9} {flag}{i['title']}\n")
        out.write(f"    why:  {i['reason']}\n    next: {i['next_action']}\n")
    counts = {}
    for i in items:
        counts[i['stage']] = counts.get(i['stage'], 0) + 1
    out.write('summary: ' + (', '.join(f'{s} {counts[s]}' for s in STAGES if s in counts) or 'no requests') + '\n')


def main(argv=None, out=sys.stdout):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--home', type=Path, default=gsa.DEFAULT_HOME)
    parser.add_argument('--config', type=Path, required=True)
    sub = parser.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('plan', help='Show the next action and wait reason for each request (read only)')
    s.add_argument('--work', type=int)
    s.add_argument('--json', action='store_true')
    s = sub.add_parser('run', help='Advance eligible operations (dry run unless --execute)')
    s.add_argument('--execute', action='store_true', help='Do the operations; without it nothing is written')
    s.add_argument('--max-actions', type=int, default=3)
    s.add_argument('--work', type=int)
    s.add_argument('--actions', default=','.join(DEFAULT_ACTIONS),
                   help='Comma list from acquire,validate,check (default: all three)')
    s.add_argument('--allow-publish', action='store_true', help='Also publish the one work named by --work')
    s.add_argument('--json', action='store_true')
    s = sub.add_parser('history', help='Show recorded runner operations (read only)')
    s.add_argument('--work', type=int)
    args = parser.parse_args(argv)
    os.umask(0o077)
    p.require(args.config.stat().st_mode & 0o077 == 0, 'Private configuration must have mode 0600')
    config = json.loads(args.config.read_text())
    home = args.home.expanduser().resolve()
    if args.cmd == 'plan':
        with closing(open_readonly(home)) as db:
            items = [i for i in plan(db, config, home) if args.work is None or i['work_id'] == args.work]
        out.write(json.dumps(items, indent=2) + '\n') if args.json else render(items, out)
    elif args.cmd == 'history':
        out.write(json.dumps(history(home, args.work), indent=2) + '\n')
    else:
        actions = tuple(a for a in args.actions.split(',') if a)
        p.require(set(actions) <= set(DEFAULT_ACTIONS), '--actions accepts acquire, validate, check')
        result = run(home, config, execute=args.execute, actions=actions, max_actions=args.max_actions,
                     work=args.work, allow_publish=args.allow_publish)
        if args.json:
            out.write(json.dumps(result, indent=2) + '\n')
        elif result['mode'] == 'dry-run':
            out.write('Dry run: nothing was written and no service was called.\n')
            for i in result['would_run']:
                out.write(f"would run: {i['action']} on work {i['work_id']}  ({i['reason']})\n")
            if not result['would_run']:
                out.write('No eligible runner operation.\n')
            out.write('Use --execute to do these operations.\n')
        else:
            out.write(f"Run {result['run_id']}: {len(result['operations'])} operation(s); "
                      f"{result['reconciled_interrupted']} interrupted attempt(s) reconciled.\n")
            for r in result['operations']:
                out.write(f"  work {r['work_id']} {r['action']} attempt {r['attempt']}: {r['status']} ({r['outcome']})\n")
            render(result['plan'], out)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except LockBusy as exc:
        print(f'Runner stopped: {exc}', file=sys.stderr)
        sys.exit(75)
    except Exception as exc:  # noqa: BLE001 - never print HTTP bodies or credentials
        print(f'Runner stopped: {type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(1)
