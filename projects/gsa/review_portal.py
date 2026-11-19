"""Send a validated work to the private review website or import both decisions."""
import argparse
import fcntl
import hashlib
import json
import os
import re
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


FOLDER_LINK = re.compile(r'https://drive\.google\.com/drive/(?:u/\d+/)?folders/([\w-]{10,})')


def toc_rows(api, config):
    """Name / Folder Path rows from the staff Table of Contents (refreshed daily by staff).
    Each Folder Path cell links to its Drive folder, which gives the folder's real ID."""
    import urllib.parse
    base = 'https://sheets.googleapis.com/v4/spreadsheets/' + config['toc_spreadsheet_id']
    tab = "'" + config['toc_sheet_name'].replace("'", "''") + "'!A:B"
    result = api.call('GET', base, params={'ranges': tab, 'includeGridData': 'true',
                                           'fields': 'sheets.data.rowData.values(formattedValue,hyperlink)'})
    rows = [[v for v in row.get('values', [])] for row in result['sheets'][0]['data'][0].get('rowData', [])]
    p.require(rows and [v.get('formattedValue') for v in rows[0][:2]] == ['Name', 'Folder Path'], 'Table of Contents headers changed')
    out = []
    for row in rows[1:]:
        if len(row) > 1 and str(row[1].get('formattedValue') or '').strip():
            link = FOLDER_LINK.match(row[1].get('hyperlink') or '')
            out.append({'name': row[0].get('formattedValue', ''), 'folder_path': row[1]['formattedValue'],
                        'folder_id': link.group(1) if link else None})
    return out


def toc_folder_id(segments):
    """Stable placeholder for a folder known only by its path; resolved to a Drive ID at collect."""
    return 'toc-' + hashlib.sha256(json.dumps(segments, ensure_ascii=False).encode()).hexdigest()[:24]


def toc_snapshot(rows, config):
    """Folder tree from Table of Contents paths ("Archive / Read📚 / Shelf"). Top-level shelves
    use their known Drive IDs; deeper folders get toc- placeholders."""
    known = {r['name'].strip(): r['id'] for r in config.get('discovered_archive_resources', [])
             if r.get('type') == FOLDER}
    root = {'id': config['archive_root_id'], 'name': None}
    linked = {}  # path below the root -> real Drive ID from the row's folder link
    for row in rows:
        segments = [part.strip() for part in row['folder_path'].split('/') if part.strip()]
        if row.get('folder_id') and len(segments) > 1:
            linked[tuple(segments[1:])] = row['folder_id']
    ids, out = {}, []
    for row in rows:
        segments = [part.strip() for part in row['folder_path'].split('/') if part.strip()]
        if not segments:
            continue
        root['name'] = root['name'] or segments[0]
        if segments[0] != root['name']:
            continue
        for depth in range(1, len(segments)):
            key = tuple(segments[1:depth + 1])
            if key in ids:
                continue
            ids[key] = linked.get(key) or (known.get(key[0]) if depth == 1 else None) or toc_folder_id(list(key))
            parent = ids[key[:-1]] if depth > 1 else root['id']
            out.append({'id': ids[key], 'name': key[-1], 'parent': parent, 'path': list(key)})
    p.require(root['name'], 'Table of Contents lists no folders')
    return {'root': root, 'folders': [{k: f[k] for k in ('id', 'name', 'parent')} for f in out], 'source': 'Table of Contents'}


def resolve_toc_folder(api, config, path_names):
    """Walk Drive from archive_root_id by folder name to the real ID of a toc- placeholder."""
    parent = config['archive_root_id']
    for name in path_names:
        hits = [f for f in api.files(f"'{p.quote(parent)}' in parents and mimeType='{FOLDER}' and trashed=false")
                if f['name'].strip() == name]
        p.require(len(hits) == 1, f'Cannot find the Drive folder "{name}" with the worker\'s current Google access. '
                  'Matching a folder chosen from the Table of Contents needs Drive read access to the archive.')
        parent = hits[0]['id']
    return parent


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


def archive_folder(api, config, index_config_path, folder_id):
    """True when folder_id is a real folder inside the archive: listed (with its own Drive link) in
    the staff Table of Contents, or, failing that, found under archive_root_id in Drive."""
    if folder_id.startswith('toc-') or not config.get('archive_root_id'):
        return False
    if index_config_path:
        source = json.loads(Path(index_config_path).read_text())
        if source.get('toc_spreadsheet_id'):
            snapshot = toc_snapshot(toc_rows(p.Google(source), source), dict(source, archive_root_id=config['archive_root_id']))
            if any(f['id'] == folder_id for f in snapshot['folders']):
                return True
    try:
        return under_archive(api, config, folder_id)
    except Exception:  # noqa: BLE001 - no Drive access to the archive counts as "not shown"
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
    home = args.home.expanduser().resolve()
    # A sandbox home carries its own config.json; the worker home keeps pipeline-config.json,
    # passed with --config.
    config_path = home / 'config.json' if (home / 'config.json').exists() else args.config
    p.require(config_path is not None, f'No config.json in {home}; pass --config')
    config = json.loads(config_path.read_text())
    key = (p.gsa.DEFAULT_HOME / 'review-portal.key').read_text().strip()
    if args.command == 'remove':
        p.require(args.id, '--id is required for remove')
        result = send({'id': args.id, 'action': 'delete'}, key)
        print('Removed' if result.get('deleted') else 'Nothing queued under', args.id)
        return
    if args.command == 'folders':
        # Prefer a live Drive listing; fall back to the Table of Contents when the worker's
        # Google access can't list the archive (e.g. a drive.file-only credential).
        source = json.loads(args.config.read_text()) if args.config else config
        api = p.Google(source)
        snapshot = None
        try:
            drive = folder_snapshot(api, source)
            if drive['folders']:
                snapshot = dict(drive, source='Drive')
        except Exception as exc:  # noqa: BLE001 - access errors fall through to the index
            print('Drive listing unavailable:', type(exc).__name__)
        if snapshot is None:
            p.require(source.get('toc_spreadsheet_id'), 'No Drive access and no Table of Contents configured; pass --config')
            snapshot = toc_snapshot(toc_rows(api, source), source)
        result = send(dict(snapshot, action='folders', at=p.stamp()), key)
        print('Sent', result['folders'], 'archive folders from the', snapshot['source'], 'to the review site')
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
        if packet['destination'].startswith('toc-'):
            # Chosen from the Table of Contents tree: find the real Drive folder by its path.
            names = [n.strip() for n in packet['folder'].split(' / ')][1:]
            packet['destination'] = draft['destination'] = resolve_toc_folder(api, config, names)
        if packet['destination'] not in config['destination_ids']:
            p.require(archive_folder(api, config, args.config, packet['destination']),
                      'Edited destination is not a folder inside the archive (checked the Table of Contents and Drive)')
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
    parser.add_argument('command', choices=['queue','collect','folders','remove'])
    parser.add_argument('--home', required=True, type=Path)
    parser.add_argument('--packet', type=Path, help='Private packet settings (queue and collect)')
    parser.add_argument('--id', help='remove: review id to take off the site')
    parser.add_argument('--config', type=Path, help='folders and collect: private config whose Google access and Table of Contents to use (read only)')
    os.umask(0o077)
    args = parser.parse_args()
    if args.command in ('queue', 'collect') and not args.packet:
        parser.error('--packet is required for queue and collect')
    run(args)
