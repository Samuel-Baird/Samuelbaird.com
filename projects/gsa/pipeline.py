#!/usr/bin/env python3
"""Supervised GSA pipeline. Private JSON configuration; no live defaults."""
from contextlib import closing
import argparse
import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
import acquire as acquisition
import validate as validation
import rollout
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
import gsa

FORMS = 'https://forms.googleapis.com/v1/forms/'
DRIVE = 'https://www.googleapis.com/drive/v3/files'
DOCS = 'https://docs.googleapis.com/v1/documents/'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def stamp():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def migrate(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS pipeline_records (
      work_id INTEGER PRIMARY KEY REFERENCES works(id), record TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS upload_sessions (file_id TEXT PRIMARY KEY, url TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS pipeline_events (
      id INTEGER PRIMARY KEY, at TEXT NOT NULL, work_id INTEGER, action TEXT NOT NULL, detail TEXT NOT NULL);
    ''')

def save(db, wid, record, action):
    with db:
        db.execute('INSERT INTO pipeline_records VALUES(?,?) ON CONFLICT(work_id) DO UPDATE SET record=excluded.record', (wid, json.dumps(record)))
        db.execute('INSERT INTO pipeline_events(at,work_id,action,detail) VALUES(?,?,?,?)', (stamp(), wid, action, json.dumps(record)))

def get(db, wid):
    work = db.execute('SELECT * FROM works WHERE id=?', (wid,)).fetchone()
    require(work is not None, 'Unknown work')
    row = db.execute('SELECT record FROM pipeline_records WHERE work_id=?', (wid,)).fetchone()
    return dict(work), json.loads(row[0]) if row else {}

class Google:
    """Refresh credentials stored as one JSON Keychain item; never log tokens."""
    def __init__(self, config):
        self.config = config
        self.token = None
        self.expiry = 0

    def access_token(self):
        if time.time() < self.expiry:
            return self.token
        raw = subprocess.run(['security', 'find-generic-password', '-s', self.config['keychain_service'], '-a', self.config['keychain_account'], '-w'], capture_output=True, text=True, check=True).stdout
        credentials = json.loads(raw)
        data = urllib.parse.urlencode(dict(credentials, grant_type='refresh_token')).encode()
        with urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token', data=data), timeout=30) as response:
            result = json.load(response)
        self.token = result['access_token']
        self.expiry = time.time() + result['expires_in'] - 60
        return self.token

    def call(self, method, url, body=None, params=None, headers=None, raw=False, stream_hash=False):
        if params:
            url += '?' + urllib.parse.urlencode(params)
        payload = json.dumps(body).encode() if isinstance(body, dict) else body
        for attempt in range(4):
            req = urllib.request.Request(url, data=payload, method=method, headers={
                'Authorization': 'Bearer ' + self.access_token(),
                'Content-Type': 'application/json', **(headers or {})})
            try:
                with urllib.request.urlopen(req, timeout=90) as response:
                    if stream_hash:
                        digest_state = hashlib.sha256()
                        for chunk in iter(lambda: response.read(1024 * 1024), b''):
                            digest_state.update(chunk)
                        return digest_state.hexdigest()
                    result = response.read()
                    return result if raw else (json.loads(result) if result else {})
            except urllib.error.HTTPError as exc:
                # Only reads are automatically retried. Mutations reconcile on the next run.
                if method != 'GET' or exc.code not in (401, 429, 500, 502, 503, 504) or attempt == 3:
                    raise
                if exc.code == 401:
                    self.expiry = 0
                time.sleep(2 ** attempt)

    def files(self, query):
        result, token = [], None
        while True:
            params = dict(q=query, fields='nextPageToken,incompleteSearch,files(id,name,parents,mimeType,size,md5Checksum,appProperties,webViewLink)', pageSize=1000, supportsAllDrives='true', includeItemsFromAllDrives='true')
            if token:
                params['pageToken'] = token
            page = self.call('GET', DRIVE, params=params)
            require(not page.get('incompleteSearch'), 'Incomplete Drive search; review required')
            result.extend(page.get('files', []))
            token = page.get('nextPageToken')
            if not token:
                return result

def poll(db, api, config):
    if 'form_question_ids' in config:
        from google_intake import poll_freeform
        return poll_freeform(db, api, config)
    require(config.get('intake_approved') is True, 'Staff intake approval missing')
    form = config['form_id']
    source = 'form:' + form
    cp = db.execute('SELECT value FROM checkpoints WHERE source=?', (source,)).fetchone()
    start = datetime.now(timezone.utc)
    params = {'pageSize': 5000}
    if cp:
        since = datetime.fromisoformat(cp[0].replace('Z', '+00:00')) - timedelta(minutes=5)
        params['filter'] = 'timestamp >= ' + since.isoformat().replace('+00:00', 'Z')
    rows = {}
    mapping = config['question_map']
    require(mapping and set(mapping).issubset(set(gsa.FIELDS) - {'row_id'}), 'Invalid question mapping')
    while True:
        page = api.call('GET', FORMS + form + '/responses', params=params)
        for response in page.get('responses', []):
            row = {'row_id': response['responseId']}
            for field, question in mapping.items():
                answers = response.get('answers', {}).get(question, {}).get('textAnswers', {}).get('answers', [])
                require(len(answers) <= 1, 'Multivalue answer needs staff mapping')
                row[field] = answers[0]['value'] if answers else ''
            require(row['row_id'] not in rows or rows[row['row_id']] == row, 'Response changed during pagination')
            rows[row['row_id']] = row
        if not page.get('nextPageToken'):
            break
        params['pageToken'] = page['nextPageToken']
    return gsa.ingest(db, list(rows.values()), source, 'forms', start.isoformat().replace('+00:00', 'Z'))

def compare(request, candidate):
    """Missing edition evidence never establishes an exact archive match."""
    same_id = any(request.get(k) and request.get(k) == candidate.get(k) for k in ('isbn', 'doi'))
    same_title = bool(request.get('title')) and gsa.normalized(request['title']) == gsa.normalized(candidate.get('title', ''))
    if not (same_id or same_title):
        return 'unrelated'
    for key in ('isbn', 'doi', 'edition', 'year', 'language', 'author'):
        if request.get(key) and gsa.normalized(request[key]) != gsa.normalized(candidate.get(key, '')):
            return 'ambiguous'
    return 'exact' if same_id or (request.get('author') and request.get('edition')) else 'ambiguous'

def quote(value):
    return value.replace('\\', '\\\\').replace("'", "\\'")

def archive_check(db, wid, api, config, destination):
    work, record = get(db, wid)
    request = json.loads(work['metadata'])
    require(destination in config['destination_ids'], 'Destination is not staff approved')
    # Index is a staff-maintained bibliographic JSON export. Always inspect live destination too.
    index = json.loads(Path(config['archive_index']).read_text())
    matches = []
    for item in index:
        match = compare(request, item)
        title = gsa.normalized(request.get('title', ''))
        if match == 'unrelated' and title and title in gsa.normalized(item.get('name', '')):
            match = 'ambiguous'
        matches.append(dict(item, match=match))
    matches = [item for item in matches if item['match'] != 'unrelated']
    files = api.files("'" + quote(destination) + "' in parents and trashed=false")
    for item in files:
        props = item.get('appProperties', {})
        if props.get('gsa_sha256') and props.get('gsa_sha256') == record.get('sha256'):
            matches.append(dict(item, match='exact'))
        elif request.get('title') and gsa.normalized(request['title']) in gsa.normalized(item['name']):
            matches.append(dict(item, match='ambiguous'))
    record['archive_check'] = {'at': stamp(), 'destination': destination, 'matches': matches}
    record.pop('approval', None)
    record.pop('reviewer_checks', None)
    save(db, wid, record, 'archive_check')
    return matches

def triage(db, config, path):
    packet = json.loads(path.read_text())
    require(packet.get('reviewer') in config['reviewers'], 'Unknown reviewer')
    pair = (config['form_id'], packet['response_id'])
    row = db.execute('SELECT status FROM form_requests WHERE form_id=? AND response_id=?', pair).fetchone()
    require(row is not None, 'Unknown form request')
    source = 'triage:' + json.dumps(pair)
    rows = packet['works']
    require(isinstance(rows, list), 'Expected works array')
    if row[0] != 'needs_review':
        raise ValueError('Form request already reviewed')
    with db:
        gsa.ingest_rows(db, rows, source, packet['reviewer'])
        db.execute("UPDATE form_requests SET status='reviewed' WHERE form_id=? AND response_id=?", pair)


def permissions(data, config, torrent=False):
    entries = data.get('permissions', {})
    require(all(isinstance(entries.get(k), dict) for k in acquisition.PERMISSION_FIELDS),
            'Separate download, peer-sharing and upload records required')
    result = acquisition.evaluate_permissions(entries, config['reviewers'])
    require(result['may_download_torrent' if torrent else 'may_download_direct']
            and result['may_upload_to_gsa'], 'Permission evidence incomplete')


def review(db, wid, path, config):
    work, record = get(db, wid)
    require(not record.get('upload_id'), 'Cannot revise an upload in progress')
    data = json.loads(path.read_text())
    require(data.get('reviewer') in config['reviewers'], 'Unknown reviewer')
    for key in ('source_url', 'matched_work', 'filename', 'destination', 'changelog_text'):
        require(bool(data.get(key)), 'Missing review field: ' + key)
    permissions(data, config, bool(data.get('infohash')))
    require(data['destination'] in config['destination_ids'], 'Unapproved destination')
    require(Path(data['filename']).name == data['filename'] and data['filename'] not in ('.', '..'), 'Invalid filename')
    record = {'review': data}
    save(db, wid, record, 'source_review')
    with db:
        db.execute('UPDATE works SET source=?,permission=?,matched_work=?,proposed_filename=?,destination=? WHERE id=?', (data['source_url'], 'staff-reviewed', data['matched_work'], data['filename'], data['destination'], wid))

def acquire(db, wid, home, config):
    _, record = get(db, wid)
    review_data = record['review']
    permissions(review_data, config)
    url = review_data['source_url']
    require(urllib.parse.urlparse(url).scheme == 'https', 'Only authorized HTTPS direct downloads supported; torrents remain supervised')
    require(urllib.parse.urlparse(url).hostname in config['source_hosts'], 'Source host not approved')
    limit = int(config['max_file_bytes'])
    class Redirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            target = urllib.parse.urlparse(newurl)
            require(target.scheme == 'https' and target.hostname in config['source_hosts'], 'Redirect host not approved')
            return super().redirect_request(req, fp, code, msg, headers, newurl)
    target = home / 'incomplete' / f'{wid}.part'
    require(not record.get('upload_id'), 'Upload already started')
    try:
        with urllib.request.build_opener(Redirect()).open(url, timeout=60) as response, target.open('wb') as out:
            length = response.headers.get('Content-Length')
            if length:
                require(acquisition.disk_check(home, [int(length)], config)['ok'], 'Disk budget exhausted')
            size = 0
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                size += len(block)
                require(size <= limit, 'Download exceeds file limit')
                out.flush()
                require(acquisition.disk_check(home, [size], config, out.tell())['ok'], 'Disk budget exhausted')
                out.write(block)
            require(size > 0, 'Empty download')
            if response.headers.get('Content-Length'):
                require(size == int(response.headers['Content-Length']), 'Incomplete download')
        candidate = home / 'candidates' / f'{wid}{Path(review_data["filename"]).suffix.lower()}'
        target.replace(candidate)
        record['candidate'] = str(candidate)
        record.pop('validation', None)
        record.pop('approval', None)
        record.pop('reviewer_checks', None)
        save(db, wid, record, 'acquired')
    finally:
        target.unlink(missing_ok=True)

def validate_file(db, wid, config):
    _, record = get(db, wid)
    require(not record.get('upload_id'), 'Upload already started')
    record.pop('approval', None)
    record.pop('reviewer_checks', None)
    record.pop('validation', None)
    save(db, wid, record, 'validation_started')
    report = validation.validate(Path(record['candidate']), config)
    record['validation'] = report
    record['sha256'] = report['sha256']
    passed = report['automated_verdict'] == 'pass'
    save(db, wid, record, 'validated' if passed else 'validation_failed')
    with db:
        db.execute('UPDATE works SET sha256=?,status=? WHERE id=?',
                   (report['sha256'], 'awaiting_staff_approval' if passed else 'needs_review', wid))
    require(passed, 'Validation failed: ' + ', '.join(report['automated_failures']))
    return report


def approve(db, wid, path, config):
    _, record = get(db, wid)
    approval = json.loads(path.read_text())
    require(approval.get('reviewer') in config['reviewers'], 'Unknown reviewer')
    require(record.get('validation') and approval.get('sha256') == record['sha256'] == digest(record['candidate']), 'Approval must bind to validated file hash')
    permissions(record['review'], config, bool(record['review'].get('infohash')))
    require(record['validation'].get('automated_verdict') == 'pass', 'Passing validation required')
    for key, _ in validation.STAFF_JUDGMENT:
        require(approval.get(key) is True, 'Staff check required: ' + key)
    require(approval.get('destination') == record['review']['destination'], 'Approval destination mismatch')
    require(record.get('archive_check') and not record['archive_check']['matches'], 'Archive matches require resolution before approval')
    required = config.get('required_publication_reviewers', [])
    if required:
        require(approval['reviewer'] in required, 'Reviewer not assigned to this publication')
        checks = record.setdefault('reviewer_checks', {})
        checks[approval['reviewer']] = dict(approval, at=stamp())
        if not all(reviewer in checks for reviewer in required):
            save(db, wid, record, 'awaiting_other_reviewer')
            return
        approval['reviewer_checks'] = dict(checks)
    record['approval'] = dict(approval, at=stamp())
    save(db, wid, record, 'approved')


def upload_request(api, method, url, body, headers):
    parsed = urllib.parse.urlsplit(url)
    require(parsed.scheme == 'https' and parsed.netloc == 'www.googleapis.com',
            'Unexpected Drive upload endpoint')
    request = urllib.request.Request(url, data=body, method=method,
        headers={**headers, 'Authorization': 'Bearer ' + api.access_token()})
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return response.status, response.headers
    except urllib.error.HTTPError as exc:
        with exc:
            if exc.code in (308, 404):
                return exc.code, exc.headers
            raise ValueError(f'Drive upload failed with HTTP {exc.code}') from None


def resumable_upload(db, api, path, metadata):
    size = path.stat().st_size
    file_id = metadata['id']
    row = db.execute('SELECT url FROM upload_sessions WHERE file_id=?', (file_id,)).fetchone()
    offset = 0
    if row:
        url = row[0]
        status, headers = upload_request(api, 'PUT', url, b'', {'Content-Range': f'bytes */{size}'})
        if status in (200, 201):
            return
        require(status in (308, 404), 'Unexpected upload status response')
        if status == 308:
            offset = received_bytes(headers, size)
        else:
            row = None
    if not row:
        status, headers = upload_request(api, 'POST',
            'https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true',
            json.dumps(metadata).encode(), {'Content-Type': 'application/json',
            'X-Upload-Content-Type': 'application/octet-stream', 'X-Upload-Content-Length': str(size)})
        require(status in (200, 201) and headers.get('Location'), 'Could not start upload')
        url = headers['Location']
        with db:
            db.execute('INSERT OR REPLACE INTO upload_sessions VALUES(?,?)', (file_id, url))
    with path.open('rb') as source:
        while offset < size:
            source.seek(offset)
            block = source.read(min(4 * 1024 * 1024, size - offset))
            end = offset + len(block)
            require(block, 'Candidate truncated during upload')
            status, headers = upload_request(api, 'PUT', url, block, {
                'Content-Type': 'application/octet-stream', 'Content-Range': f'bytes {offset}-{end-1}/{size}'})
            if status in (200, 201):
                require(end == size, 'Premature upload completion')
                return
            require(status == 308, 'Upload session interrupted; retry publication')
            next_offset = received_bytes(headers, size)
            require(offset < next_offset <= end, 'Unexpected upload progress')
            offset = next_offset


def received_bytes(headers, size):
    value = headers.get('Range')
    if not value:
        return 0
    match = re.fullmatch(r'bytes=0-(\d+)', value)
    require(match and int(match[1]) + 1 < size, 'Invalid upload acknowledgement')
    return int(match[1]) + 1


def publish(db, wid, api, config):
    require(config.get('publication_approved') is True, 'Live publication not enabled by staff')
    work, record = get(db, wid)
    require(record.get('approval'), 'Staff approval required')
    for reviewer in config.get('required_publication_reviewers', []):
        check = record['approval'].get('reviewer_checks', {}).get(reviewer, {})
        require(reviewer in config['reviewers'] and check.get('sha256') == record['sha256']
                and check.get('destination') == record['review']['destination']
                and all(check.get(k) is True for k, _ in validation.STAFF_JUDGMENT),
                'Assigned reviewer approval missing or revoked')
    permissions(record['review'], config, bool(record['review'].get('infohash')))
    require(record.get('validation', {}).get('automated_verdict') == 'pass'
            and all(record['approval'].get(k) is True for k, _ in validation.STAFF_JUDGMENT),
            'Current validation and staff checks required')
    path = Path(record['candidate'])
    require(digest(path) == record['approval']['sha256'], 'File changed after approval')
    review_data = record['review']
    destination = review_data['destination']
    require(destination in config['destination_ids'], 'Destination approval revoked')
    require(record['approval']['reviewer'] in config['reviewers'], 'Reviewer approval revoked')
    if not record.get('upload_id'):
        # Preserve approval while doing a fresh duplicate check.
        approval = record['approval']
        matches = archive_check(db, wid, api, config, destination)
        require(not matches, 'Duplicate or ambiguous archive match; staff review required')
        _, record = get(db, wid)
        record['approval'] = approval
        record['upload_id'] = api.call('GET', DRIVE + '/generateIds', params={'count': 1, 'space': 'drive'})['ids'][0]
        save(db, wid, record, 'upload_reserved')
    file_id = record['upload_id']
    try:
        remote = api.call('GET', DRIVE + '/' + file_id, params={'fields': 'id,name,parents,size,md5Checksum,webViewLink', 'supportsAllDrives': 'true'})
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        exc.close()
        metadata = {'id': file_id, 'name': review_data['filename'], 'parents': [destination], 'appProperties': {'gsa_sha256': record['sha256']}}
        if path.stat().st_size > 5 * 1024 * 1024:
            resumable_upload(db, api, path, metadata)
        else:
            boundary = 'gsa_' + record['sha256']
            body = (f'--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n' + json.dumps(metadata) + f'\r\n--{boundary}\r\nContent-Type: application/octet-stream\r\n\r\n').encode() + path.read_bytes() + f'\r\n--{boundary}--\r\n'.encode()
            api.call('POST', 'https://www.googleapis.com/upload/drive/v3/files', body=body, params={'uploadType': 'multipart', 'supportsAllDrives': 'true'}, headers={'Content-Type': 'multipart/related; boundary=' + boundary})
        remote = api.call('GET', DRIVE + '/' + file_id, params={'fields': 'id,name,parents,size,md5Checksum,webViewLink', 'supportsAllDrives': 'true'})
    require(remote['name'] == review_data['filename'] and destination in remote.get('parents', []) and int(remote['size']) == path.stat().st_size and remote.get('md5Checksum') == digest(path, 'md5'), 'Uploaded file verification failed')
    # Verify readability, not just metadata.
    readback_hash = api.call('GET', DRIVE + '/' + file_id, params={'alt': 'media', 'supportsAllDrives': 'true'}, stream_hash=True)
    require(readback_hash == record['sha256'], 'Drive readback mismatch')
    with db:
        db.execute('DELETE FROM upload_sessions WHERE file_id=?', (file_id,))
        db.execute('UPDATE works SET upload_receipt=?,status=? WHERE id=?', (json.dumps(dict(remote, verified_drive_link=remote.get('webViewLink', 'https://drive.google.com/file/d/' + file_id + '/view'))), 'uploaded', wid))
    document_id = config['changelog_document_id']
    tab_id = config.get('changelog_tab_id')
    if tab_id:
        from google_intake import document_body
        document = api.call('GET', DOCS + document_id, params={'includeTabsContent': 'true'})
        document['body'] = document_body(document, tab_id)
    else:
        document = api.call('GET', DOCS + document_id)
    marker = '[GSA:' + file_id + ']'
    entry = review_data['changelog_text'] + '\n' + marker + '\n'
    require('body' in document, 'Changelog must expose a document body')
    content = ''.join(el.get('textRun', {}).get('content', '') for item in document['body']['content'] for el in item.get('paragraph', {}).get('elements', []))
    if marker not in content:
        anchor = config['changelog_anchor']
        require(anchor and content.count(anchor) == 1, 'Changelog dated anchor missing or ambiguous')
        # Find the actual Docs UTF-16 index, accounting for structural elements.
        insertion = None
        for item in document['body']['content']:
            for el in item.get('paragraph', {}).get('elements', []):
                text = el.get('textRun', {}).get('content', '')
                if anchor in text:
                    insertion = el['startIndex'] + len(text[:text.index(anchor) + len(anchor)].encode('utf-16-le')) // 2
        require(insertion is not None, 'Anchor spans text runs; staff must choose a plain-text anchor')
        api.call('POST', DOCS + document_id + ':batchUpdate', body={'writeControl': {'requiredRevisionId': document['revisionId']}, 'requests': [{'insertText': {'location': dict(index=insertion, **({'tabId': tab_id} if tab_id else {})), 'text': '\n' + entry}}]})
    with db:
        db.execute('UPDATE works SET changelog_receipt=?,status=?,reason=? WHERE id=?', (json.dumps({'target': document_id, 'marker': marker, 'at': stamp()}), 'complete', 'Verified Drive upload and dated changelog', wid))


def torrent_loop(db, wid, home, config, evidence, metainfo):
    """Supervise one operator-added torrent. The operator alone starts transfers."""
    while True:
        issues = rollout.guard(config, json.loads(evidence.read_text()))
        require(not issues, 'Torrent guard blocked: ' + ', '.join(issues))
        _, record = get(db, wid)
        data = record['review']
        require(not record.get('upload_id'), 'Upload already started')
        permissions(data, config, torrent=True)
        key = data['infohash'].lower()
        require(bool(key), 'Missing reviewed infohash')
        payload = acquisition.review_payload(acquisition.parse_torrent(metainfo.read_bytes()), config, key)
        require(payload['route'] == 'permission_check', 'Payload requires staff review')
        client = rollout.Client()
        rows = client.call('torrents/info?' + urllib.parse.urlencode({'hashes': key}))
        now = time.time()
        job = record.setdefault('torrent_job', acquisition.new_job(key, now, payload['total_bytes']))
        row = rows[0] if len(rows) == 1 else None
        decision = acquisition.assess(job, row, now, config=config)
        if row:
            root = (home / 'incomplete').resolve()
            path = Path(row['content_path']).resolve()
            expected = payload['files'][0]
            safe = path.is_relative_to(root) and path.name == Path(expected['path']).name
            present = path.stat().st_size if safe and path.is_file() else 0
            if not safe or not acquisition.disk_check(home, [expected['bytes']], config, present)['ok']:
                decision = {'action': 'pause_and_review', 'reason': 'Unapproved path or disk budget'}
                job['status'] = 'review'
        action = decision['action']
        if action in ('complete', 'pause_and_review', 'route_to_review') and row:
            client.call('torrents/stop', {'hashes': key})
        if action == 'complete':
            require(path.is_file() and present == expected['bytes'], 'Incomplete payload')
            record['candidate'] = str(path)
            record.pop('approval', None)
            record.pop('reviewer_checks', None)
            record.pop('validation', None)
        if action == 'recheck':
            job['retries'] += 1
        save(db, wid, record, 'torrent_' + action)
        if action not in ('retry', 'recheck', 'wait'):
            return decision
        if action != 'wait':
            client.call('torrents/' + ('reannounce' if action == 'retry' else 'recheck'), {'hashes': key})
        time.sleep(15)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=gsa.DEFAULT_HOME)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('command', choices=['poll', 'triage', 'rank', 'torrent-loop', 'check', 'review', 'acquire', 'validate', 'approve', 'publish'])
    parser.add_argument('--work', type=int)
    parser.add_argument('--file', type=Path)
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    require(args.config.stat().st_mode & 0o077 == 0, 'Private configuration must have mode 0600')
    config = json.loads(args.config.read_text())
    home = args.home.expanduser().resolve()
    with closing(gsa.connect(home)) as db:
        migrate(db)
        # One process covers poll/acquisition/publication; crash releases the lock.
        with (home / 'pipeline.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            api = Google(config)
            if args.command == 'triage':
                require(args.file, '--file required')
                triage(db, config, args.file)
            elif args.command == 'poll':
                print(f'Imported {poll(db, api, config)} submissions')
            else:
                require(args.work is not None, '--work required')
                if args.command in ('review', 'approve'):
                    require(args.file is not None, '--file required')
                    globals()[args.command](db, args.work, args.file, config)
                elif args.command == 'rank':
                    reports = [json.loads(row[0])['validation'] for row in db.execute(
                        "SELECT detail FROM pipeline_events WHERE work_id=? AND action IN ('validated','validation_failed')", (args.work,))
                        if 'automated_verdict' in json.loads(row[0])['validation']]
                    print(json.dumps(validation.rank(reports), indent=2))
                elif args.command == 'torrent-loop':
                    require(args.file and args.evidence, '--file and --evidence required')
                    print(torrent_loop(db, args.work, home, config, args.evidence, args.file))
                elif args.command == 'check':
                    _, record = get(db, args.work)
                    print(json.dumps(archive_check(db, args.work, api, config, record['review']['destination']), indent=2))
                elif args.command == 'acquire':
                    acquire(db, args.work, home, config)
                elif args.command == 'validate':
                    print(validation.render(validate_file(db, args.work, config)))
                else:
                    publish(db, args.work, api, config)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # HTTP bodies and credentials are never printed.
        print(f'Pipeline stopped: {type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(1)
