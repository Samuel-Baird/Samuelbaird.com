#!/usr/bin/env python3
"""End-to-end sandbox trial of pipeline.py with synthetic data.

Google Forms/Drive/Docs and qBittorrent are in-memory fakes (tests/fakes.py);
ClamAV, poppler and qpdf are the real installed tools. Nothing contacts Google,
qBittorrent or the VPN, and nothing is published. The private config is read
only for reviewer IDs and the scanner command; it is never written.

Covers: free-text intake and triage, an ambiguous
edition resolved by both reviewers, a failed malware scan (real scanner error and
a simulated detection with quarantine), the guarded torrent loop (guard failure
on the real evidence draft, then a stall and completion), ranking a scan above an
ebook conversion, and publication after an interrupted upload, a lost upload
response and a lost changelog response.
"""
import argparse
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent / 'tests'))
import fakes
import gsa
import pdf_fixtures as fx
import pipeline as p
import rollout
import validate as val

EICAR = ('X5O!P%@AP[4\\PZX54(P^)7CC)7}$' + 'EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*').encode()


class Steps:
    def __init__(self):
        self.log = []

    def __call__(self, name, ok, **detail):
        self.log.append(dict(step=name, ok=bool(ok), **detail))
        print(('PASS ' if ok else 'FAIL ') + name + ('  ' + json.dumps(detail, default=str, ensure_ascii=False) if detail else ''))

    def refuses(self, name, pattern, fn):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - the refusal is the result
            self(name, pattern in f'{type(exc).__name__}: {exc}', error=f'{type(exc).__name__}: {exc}'[:220])
            return
        self(name, False, error='no error raised')


class Clock:
    """Stands in for pipeline.time inside the torrent loop; each sleep runs the next trial event."""
    def __init__(self, start, events):
        self.now, self.events = start, list(events)

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds
        if self.events:
            self.events.pop(0)(self)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--home', type=Path, required=True, help='New sandbox directory whose name contains "sandbox"')
    parser.add_argument('--config', type=Path, help='Private pipeline config, read only for reviewers and scanner')
    args = parser.parse_args()
    home = args.home.expanduser().resolve()
    if home == gsa.DEFAULT_HOME.resolve() or 'sandbox' not in home.name or home.exists():
        raise SystemExit('Use a new directory whose name contains "sandbox"')
    private = json.loads(args.config.read_text()) if args.config else {}
    reviewers = private.get('reviewers') or ['reviewer-a', 'reviewer-b']
    first, second = reviewers[0], reviewers[-1]
    db = gsa.connect(home)
    p.migrate(db)
    step = Steps()

    def write(name, data):
        path = home / 'inputs' / name
        path.parent.mkdir(mode=0o700, exist_ok=True)
        path.write_bytes(data) if isinstance(data, bytes) else path.write_text(json.dumps(data, indent=2))
        return path

    folder = 'sandbox-read-folder'
    index = [{'title': 'A Study of Things', 'author': 'Smith', 'edition': '1', 'year': '1970', 'language': 'en'}]
    config = dict(
        intake_approved=True, publication_approved=True, torrent_acquisition_approved=True,
        form_id='synthetic-form', form_question_ids={'materials': 'qm', 'topics': 'qt', 'quality_of_life': 'qq', 'bugs': 'qb'},
        reviewers=reviewers, required_publication_reviewers=sorted(set(reviewers)), destination_ids=[folder],
        source_hosts=['publisher.example'], archive_index=str(write('archive-index.json', index)),
        max_file_bytes=50 * 1024 * 1024, disk_budget_bytes=500 * 1024 * 1024, reserve_bytes=1024 * 1024 * 1024,
        scanner_command=private.get('scanner_command') or ['clamscan', '--infected', '--no-summary'], scanner_max_db_age_hours=72,
        changelog_document_id='sandbox-changelog', changelog_tab_id='sandbox-changelog-tab', changelog_anchor='== 19 November 2026 ==',
        vpn_interface='ipsec0')
    api = fakes.FakeGoogle(folders=[folder], changelog='Requests & Updates\n== 19 November 2026 ==\nEarlier entry\n')
    api.tab_id = 'sandbox-changelog-tab'
    checks = {k: True for k, _ in val.STAFF_JUDGMENT}
    served = {}

    def acquire(wid, url, data):
        response = io.BytesIO(data)
        response.headers = {'Content-Length': str(len(data))}
        served[url] = data
        with patch('pipeline.urllib.request.build_opener', return_value=Mock(open=Mock(return_value=response))):
            p.acquire(db, wid, home, config)

    def review(wid, name, url, filename, **extra):
        doc = dict(reviewer=first, source_url=url, matched_work=name, filename=filename, destination=folder,
                   changelog_text=f'19 November 2026: added {filename} (sandbox)', **extra)
        p.review(db, wid, write(f'review-{wid}.json', doc), config)

    def approve_both(wid, sha, **extra):
        for reviewer in (first, second) if first != second else (first,):
            p.approve(db, wid, write(f'approve-{wid}-{reviewer}.json', dict(checks, reviewer=reviewer, destination=folder, sha256=sha, **extra)), config)

    # 1. Free-text intake and triage ------------------------------------------------------
    answer = lambda v: {'textAnswers': {'answers': [{'value': v}]}}
    api.form_pages = [
        {'responses': [{'responseId': 'resp-1', 'answers': {'qm': answer('A Study of Things by Smith, 2nd edition please, and its companion volume')}}]},
        {'responses': [{'responseId': 'resp-2', 'answers': {'qm': answer('Jones, Collected Lectures (a scan if possible)')}},
                       {'responseId': 'resp-3', 'answers': {'qb': answer('The search box is slow on my phone')}}]}]
    added, replay = p.poll(db, api, config), p.poll(db, api, config)
    step('free-text poll queues 3 responses for review; overlap replay adds none',
         added == 3 and replay == 0 and db.execute('SELECT count(*) FROM works').fetchone()[0] == 0)
    p.triage(db, config, write('triage-1.json', dict(reviewer=first, response_id='resp-1', works=[
        dict(row_id='resp-1:1', title='A Study of Things', author='Smith', edition='2', language='en'),
        dict(row_id='resp-1:2', title='A Study of Things: Companion', author='Smith', language='en')])))
    p.triage(db, config, write('triage-2.json', dict(reviewer=first, response_id='resp-2', works=[
        dict(row_id='resp-2:1', title='Collected Lectures', author='Jones', language='en')])))
    p.triage(db, config, write('triage-3.json', dict(reviewer=second, response_id='resp-3', works=[])))
    study, companion, lectures = 1, 2, 3
    step('reviewers triage free text into 3 works; the bug report creates none',
         db.execute('SELECT count(*) FROM works').fetchone()[0] == 3
         and db.execute("SELECT count(*) FROM form_requests WHERE status='needs_review'").fetchone()[0] == 0)

    # 2. Source review and an ambiguous edition
    review(study, 'Smith, A Study of Things, 2nd ed.', 'https://publisher.example/study.pdf', 'Smith, A Study of Things.pdf')
    acquire(study, 'https://publisher.example/study.pdf', fx.scan_pdf(pages=3, ppi=300, with_ocr_layer=True))
    report = p.validate_file(db, study, config)
    step('real ClamAV, poppler and qpdf pass the synthetic scan', report['automated_verdict'] == 'pass',
         pdf_class=report['pdf']['classification']['class'], score=report['ranking_score'], clamav=report['tool_versions'].get('clamscan'))
    matches = p.archive_check(db, study, api, config, folder)
    step('archive holds the 1st edition, request is the 2nd: routed as ambiguous', [m['match'] for m in matches] == ['ambiguous'], key=matches[0]['key'])
    step.refuses('approval blocked while the edition match is unresolved', 'Archive matches',
                 lambda: approve_both(study, report['sha256']))
    step.refuses('approval blocked when a reviewer check is missing', 'Staff check required: body_spot_check',
                 lambda: p.approve(db, study, write('approve-missing.json', dict(checks, body_spot_check=False, reviewer=first, destination=folder, sha256=report['sha256'])), config))
    p.archive_check(db, study, api, config, folder)
    approve_both(study, report['sha256'], archive_resolution={'matches': [matches[0]['key']], 'reason': 'Archive holds the 1970 1st edition; this is the revised 2nd'})
    step('both reviewers name the match and approve', 'approval' in p.get(db, study)[1])

    # 3. Failed malware scan -------------------------------------------------------------------
    review(companion, 'Smith, Companion', 'https://publisher.example/companion.pdf', 'Smith, Companion.pdf')
    acquire(companion, 'https://publisher.example/companion.pdf', b'%PDF-1.4\n' + EICAR + b'\n%%EOF\n')
    empty = home / 'empty-clamav-db'
    empty.mkdir(mode=0o700)
    broken = dict(config, scanner_command=['clamscan', '--no-summary', f'--database={empty}'], scanner_max_db_age_hours=None)
    step.refuses('real ClamAV with no signatures errors and fails closed', 'malware_scan', lambda: p.validate_file(db, companion, broken))
    detector = write('detect-eicar.sh', b'#!/bin/sh\n# Sandbox stand-in: ClamAV does not flag EICAR inside a PDF wrapper.\n'
                     b'if grep -q "EICAR-STANDARD-ANTIVIRUS-TEST-FILE" "$1"; then echo "$1: Eicar-Test-Signature FOUND"; exit 1; fi\nexit 0\n')
    detector.chmod(0o700)
    step.refuses('simulated detection fails validation', 'malware_scan',
                 lambda: p.validate_file(db, companion, dict(config, scanner_command=[str(detector)], scanner_max_db_age_hours=None)))
    record = p.get(db, companion)[1]
    quarantined = record['candidates'][0].get('quarantined_to')
    step('infected file moved to quarantine, nothing left to approve',
         bool(quarantined) and Path(quarantined).exists() and not Path(record['candidates'][0]['path']).exists(), quarantined_to=quarantined)

    # 4. Torrent loop and ranking ----------------------------------------------------------------
    name = 'Jones, Collected Lectures.pdf'
    raw, infohash, payload = fakes.single_file_torrent(name, fx.scan_pdf(pages=4, ppi=300))
    torrent_file = write('lectures.torrent', raw)
    review(lectures, 'Jones, Collected Lectures', 'https://publisher.example/lectures.pdf', name, infohash=infohash)
    acquire(lectures, 'https://publisher.example/lectures.pdf', fx.calibre_pdf(pages=4))  # publisher's copy is an EPUB conversion
    client = fakes.FakeQbt()
    client.add_torrent(raw, str(home / 'incomplete'), stopped=False)  # the operator adds and starts it
    client.write_payload(infohash, payload, 0.4)
    draft_path = gsa.DEFAULT_HOME / 'network-checks/session3-2026-11-19/network-evidence-draft.json'
    draft = json.loads(draft_path.read_text()) if draft_path.exists() else {}
    evidence = write('evidence.json', draft)
    route = subprocess.run(['/sbin/route', '-n', 'get', '1.1.1.1'], capture_output=True, text=True).stdout
    issues = rollout.problems(config, draft, {'current_network_interface': 'ipsec0'}, route)
    calls_before = len(client.calls)
    with patch.object(p.rollout, 'guard', return_value=issues), patch.object(p.rollout, 'Client', return_value=client):
        step.refuses('guard on the real session 3 evidence draft stops the loop before the client', 'Torrent guard blocked',
                     lambda: p.torrent_loop(db, lectures, home, config, evidence, torrent_file))
    step('no client call was made while the guard failed', len(client.calls) == calls_before, issues=len(issues))
    clock = Clock(datetime(2026, 11, 19, 20, tzinfo=timezone.utc).timestamp(), [
        lambda c: setattr(c, 'now', c.now + 40 * 60),        # 40 minutes with no progress
        lambda c: client.write_payload(infohash, payload, 1.0)])  # transfer finishes after the reannounce
    with patch.object(p.rollout, 'guard', return_value=[]), patch.object(p.rollout, 'Client', return_value=client), patch.object(p, 'time', clock):
        decision = p.torrent_loop(db, lectures, home, config, evidence, torrent_file)
    history = [h['action'] for h in p.get(db, lectures)[1]['torrent_job']['history']]
    step('torrent loop: wait, stall retry (reannounce), complete, stopped',
         history == ['wait', 'retry', 'complete'] and decision['action'] == 'complete'
         and client.torrents[infohash]['state'] == 'stoppedUP', history=history)
    best = p.validate_file(db, lectures, config)
    ranked = p.get(db, lectures)[1]['candidate_reports']
    step('ranking puts the torrent scan above the publisher EPUB conversion',
         [r['pdf']['classification']['class'] for r in ranked] == ['scan', 'likely_ebook_conversion'] and best['origin'].startswith('torrent:'),
         ranking=[(r['origin'].split(':')[0], r['pdf']['classification']['class'], r['ranking_score']) for r in ranked])
    step.refuses('choosing the EPUB conversion needs a written reason', 'reason',
                 lambda: p.select_candidate(db, lectures, write('select.json', dict(reviewer=first, sha256=ranked[1]['sha256'])), config))
    p.archive_check(db, lectures, api, config, folder)
    approve_both(lectures, best['sha256'])

    # 5. Publication with interruptions -------------------------------------------------------
    api.faults['upload'] = 'before'
    step.refuses('interrupted upload (nothing stored) stops after reserving the Drive ID', 'ConnectionResetError', lambda: p.publish(db, study, api, config))
    upload_id = p.get(db, study)[1]['upload_id']
    api.faults['changelog'] = 'after'
    step.refuses('changelog insert applied but its response lost', 'TimeoutError', lambda: p.publish(db, study, api, config))
    step('upload receipt persisted before the changelog', p.get(db, study)[0]['status'] == 'uploaded' and p.get(db, study)[0]['changelog_receipt'] is None)
    p.publish(db, study, api, config)
    p.publish(db, study, api, config)
    step('reruns reconcile: one Drive file, one changelog entry, complete',
         sum(1 for f in api.folders[folder] if f == upload_id) == 1 and api.doc_text.count(f'[GSA:{upload_id}]') == 1
         and p.get(db, study)[0]['status'] == 'complete')
    api.faults['upload_response'] = 'lost'
    step.refuses('upload stored but its response lost', 'TimeoutError', lambda: p.publish(db, lectures, api, config))
    p.publish(db, lectures, api, config)
    posts = sum(1 for c in api.calls if 'upload/drive' in c[1])
    step('lost upload response reconciled by the reserved ID, no second upload',
         posts == 3 and p.get(db, lectures)[0]['status'] == 'complete', upload_posts=posts)

    gsa.manifest(db, home / 'manifest.csv')
    result = {'home': str(home), 'ran_at': datetime.now(timezone.utc).isoformat(), 'passed': all(s['ok'] for s in step.log),
              'steps': step.log, 'works': [dict(r) for r in db.execute('SELECT id,status,reason FROM works ORDER BY id')],
              'changelog_after': api.doc_text}
    out = home / 'trial-report.json'
    out.write_text(json.dumps(result, indent=2, default=str))
    out.chmod(0o600)
    print(f"\n{sum(s['ok'] for s in step.log)}/{len(step.log)} steps passed. Report: {out}")
    db.close()
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
