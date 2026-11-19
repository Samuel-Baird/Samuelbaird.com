"""Send a validated work to the private review website or import both decisions."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import tempfile
import urllib.request

import pipeline as p


def make_packet(work, record, draft, settings):
    report = record['validation']
    p.require(report['automated_verdict'] == 'pass' and
              p.digest(record['candidate']) == record['sha256'] == report['sha256'],
              'A passing validation of the current candidate is required')
    checks = record.get('archive_check', {})
    p.require(checks.get('matches') == [] and checks.get('destination') == draft['destination'],
              'Run the duplicate check for this destination first')
    return dict(title=json.loads(work['metadata'])['title'], citation=draft['matched_work'],
                pdf=settings['pdf'], source=draft['source_url'], folder=settings['folder'],
                destination=draft['destination'], filename=draft['filename'], entry=draft['changelog_text'],
                rights=settings['rights'], sha256=record['sha256'], validation='Passed',
                version=settings['version'], validation_at=report['checked_at'])


def run(args):
    home = args.home.resolve()
    config = json.loads((home / 'config.json').read_text())
    settings = json.loads(args.packet.read_text())
    draft = json.loads(Path(settings['review_file']).read_text())
    key = (p.gsa.DEFAULT_HOME / 'review-portal.key').read_text().strip()
    with (home / 'pipeline.lock').open('a') as lock, p.closing(p.gsa.connect(home)) as db:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        p.migrate(db)
        wid = settings['work']
        work, record = p.get(db, wid)
        p.require(not record.get('upload_id'), 'Publication already started')
        p.require(draft['destination'] in config['destination_ids'], 'Destination approval revoked')
        packet = make_packet(work, record, draft, settings)
        request = {'id': settings['id'], 'action': 'put' if args.command == 'queue' else 'get'}
        if args.command == 'queue':
            request['packet'] = packet
        req = urllib.request.Request('https://samuelbaird.com/gsa/operator', data=json.dumps(request).encode(),
                                     headers={'Authorization':'Bearer ' + key, 'Content-Type':'application/json',
                                              'User-Agent':'GSA-Review-Worker/1.0'})
        with urllib.request.urlopen(req, timeout=45) as response:
            result = json.load(response)
        if args.command == 'queue':
            print('Queued', settings['id'], result['revision'])
            return
        p.require(result and result['packet'] == packet, 'Web review differs from current work')
        decisions = result['decisions']
        reviewers = {'Samuel':'b13llama@gmail.com', 'David':'davidjasonharper@gmail.com'}
        p.require(set(config.get('required_publication_reviewers', [])) == set(reviewers.values()),
                  'Configure both assigned reviewers')
        for name in reviewers:
            check = decisions.get(name, {})
            p.require(check.get('decision') == 'Approved' and
                      all(check['checks'].get(k) is True for k, _ in p.validation.STAFF_JUDGMENT),
                      'Awaiting approval from ' + name)
        # Portal approval covers the displayed direct-download rights and exact destination.
        # Preserve the validated bytes while adding the source review for a browser-acquired PDF.
        p.require(not draft.get('infohash'), 'Portal supports direct downloads')
        staff = reviewers['Samuel']
        data = dict(draft, reviewer=staff, permissions={})
        for kind in p.acquisition.PERMISSION_FIELDS:
            data['permissions'][kind] = dict(status='unknown' if kind=='peer_sharing' else 'granted',
                basis=packet['rights'], source=packet['source'], recorded_by=staff, recorded_at=decisions['Samuel']['at'])
        with tempfile.TemporaryDirectory(dir=home) as folder:
            file = Path(folder) / 'packet.json'
            file.write_text(json.dumps(data))
            # Use normal source review and approval gates. Roll back all changes on failure.
            db.isolation_level = None
            db.execute('SAVEPOINT portal_import')
            class Transaction:
                def __enter__(self): return self
                def __exit__(self, *exc): return False
                def __getattr__(self, name): return getattr(db, name)
            tx = Transaction()
            try:
                p.review(tx, wid, file, config)
                _, updated = p.get(tx, wid)
                for field in ('candidate','sha256','validation','archive_check'):
                    updated[field] = record[field]
                updated['web_review'] = {'revision':result['revision'], 'decisions':decisions}
                p.save(tx, wid, updated, 'web_review_received')
                for name, email in reviewers.items():
                    file.write_text(json.dumps(dict(decisions[name]['checks'], reviewer=email,
                                        sha256=packet['sha256'], destination=packet['destination'])))
                    p.approve(tx, wid, file, config)
                db.execute('RELEASE portal_import')
            except BaseException:
                db.execute('ROLLBACK TO portal_import')
                db.execute('RELEASE portal_import')
                raise
        print('Both decisions imported. Publication remains a separate operator command.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['queue','collect'])
    parser.add_argument('--home', required=True, type=Path)
    parser.add_argument('--packet', required=True, type=Path)
    os.umask(0o077)
    run(parser.parse_args())
