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


PORTAL = 'https://samuelbaird.com/gsa/operator'
FOLDER = 'application/vnd.google-apps.folder'
# Packet fields reviewers may edit on the site, and where each lands in the source review.
EDIT_TARGETS = {'filename': 'filename', 'citation': 'matched_work', 'entry': 'changelog_text', 'destination': 'destination'}


def send(request, key):
    req = urllib.request.Request(PORTAL, data=json.dumps(request).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json',
                                          'User-Agent': 'GSA-Review-Worker/1.0'})
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.load(response)


def folder_snapshot(api, config):
    """Every Drive folder below archive_root_id, as {id, name, parent}. Shortcuts are skipped."""
    root = config['archive_root_id']
    children = {}
    for f in api.files(f"mimeType='{FOLDER}' and trashed=false"):
        for parent in f.get('parents', []):
            children.setdefault(parent, []).append(f)
    out, queue, seen = [], [root], {root}
    while queue:
        parent = queue.pop()
        for f in children.get(parent, []):
            if f['id'] not in seen:
                seen.add(f['id'])
                out.append({'id': f['id'], 'name': f['name'], 'parent': parent})
                queue.append(f['id'])
    name = api.call('GET', p.DRIVE + '/' + root, params={'fields': 'name', 'supportsAllDrives': 'true'})['name']
    return {'root': {'id': root, 'name': name}, 'folders': out}


def under_archive(api, config, folder_id, depth=40):
    """True when folder_id is a folder inside archive_root_id (walks Drive parents)."""
    current = folder_id
    for _ in range(depth):
        meta = api.call('GET', p.DRIVE + '/' + current, params={'fields': 'id,mimeType,parents,trashed', 'supportsAllDrives': 'true'})
        if current == folder_id and (meta.get('mimeType') != FOLDER or meta.get('trashed')):
            return False
        parents = meta.get('parents') or []
        if config['archive_root_id'] in parents:
            return True
        if not parents:
            return False
        current = parents[0]
    return False


def apply_edits(draft, packet, edits):
    """Return the source review and packet with the reviewers' web edits applied."""
    draft, packet = dict(draft), dict(packet)
    for field, edit in edits.items():
        packet[field] = edit['value']
        if field in EDIT_TARGETS:
            draft[EDIT_TARGETS[field]] = edit['value']
    return draft, packet


def run(args):
    home = args.home.resolve()
    config = json.loads((home / 'config.json').read_text())
    key = (p.gsa.DEFAULT_HOME / 'review-portal.key').read_text().strip()
    if args.command == 'folders':
        snapshot = folder_snapshot(p.Google(config), config)
        result = send(dict(snapshot, action='folders', at=p.stamp()), key)
        print('Sent', result['folders'], 'archive folders to the review site')
        return
    settings = json.loads(args.packet.read_text())
    draft = json.loads(Path(settings['review_file']).read_text())
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
        result = send(request, key)
        if args.command == 'queue':
            print('Queued', settings['id'], result['revision'])
            return
        p.require(result and result['packet'] == packet, 'Web review differs from current work')
        decisions = result['decisions']
        # Reviewers' edits on the site (title, citation, filename, folder, rights, changelog entry).
        # Both approvals below cover the edited version, because any edit resets decisions.
        draft, packet = apply_edits(draft, packet, result.get('edits') or {})
        api = p.Google(config)
        if packet['destination'] not in config['destination_ids']:
            p.require(config.get('archive_root_id') and under_archive(api, config, packet['destination']),
                      'Edited destination is not a folder inside the archive')
            # Both assigned reviewers approved this exact folder, which stands in for the allowlist.
            config = dict(config, destination_ids=[*config['destination_ids'], packet['destination']])
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
                if packet['title'] != json.loads(work['metadata'])['title']:
                    metadata = dict(json.loads(work['metadata']), title=packet['title'])
                    db.execute('UPDATE works SET metadata=? WHERE id=?', (json.dumps(metadata), wid))
                p.review(tx, wid, file, config)
                _, updated = p.get(tx, wid)
                for field in ('candidate','sha256','validation','candidates','candidate_reports','format_choice'):
                    if field in record:
                        updated[field] = record[field]
                updated['web_review'] = {'revision':result['revision'], 'decisions':decisions,
                                         'edits':result.get('edits') or {}, 'history':result.get('history') or []}
                p.save(tx, wid, updated, 'web_review_received')
                # The edited title or folder needs a fresh duplicate check before approval.
                matches = p.archive_check(tx, wid, api, config, packet['destination'])
                p.require(not matches, 'Archive matches for the edited title or folder; resolve before collecting')
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
    parser.add_argument('command', choices=['queue','collect','folders'])
    parser.add_argument('--home', required=True, type=Path)
    parser.add_argument('--packet', type=Path, help='Private packet settings (queue and collect)')
    os.umask(0o077)
    args = parser.parse_args()
    if args.command != 'folders' and not args.packet:
        parser.error('--packet is required for queue and collect')
    run(args)
