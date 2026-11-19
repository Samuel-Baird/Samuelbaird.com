#!/usr/bin/env python3
"""Supervised GSA pipeline. Private JSON configuration; no live defaults."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
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

    def call(self, method, url, body=None, params=None, headers=None, raw=False):
        if params:
            url += '?' + urllib.parse.urlencode(params)
        payload = json.dumps(body).encode() if isinstance(body, dict) else body
        for attempt in range(4):
            req = urllib.request.Request(url, data=payload, method=method, headers={
                'Authorization': 'Bearer ' + self.access_token(),
                'Content-Type': 'application/json', **(headers or {})})
            try:
                with urllib.request.urlopen(req, timeout=90) as response:
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
    matches = [dict(item, match=compare(request, item)) for item in index]
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
    save(db, wid, record, 'archive_check')
    return matches

def review(db, wid, path, config):
    work, record = get(db, wid)
    require(not record.get('upload_id'), 'Cannot revise an upload in progress')
    data = json.loads(path.read_text())
    require(data.get('reviewer') in config['reviewers'], 'Unknown reviewer')
    for key in ('source_url', 'permission_evidence', 'matched_work', 'filename', 'destination', 'changelog_text'):
        require(bool(data.get(key)), 'Missing review field: ' + key)
    require(data.get('download_permitted') is True and data.get('gsa_upload_permitted') is True, 'Separate download and upload permission required')
    require(data['destination'] in config['destination_ids'], 'Unapproved destination')
    require(Path(data['filename']).name == data['filename'] and data['filename'] not in ('.', '..'), 'Invalid filename')
    record = {'review': data}
    save(db, wid, record, 'source_review')
    with db:
        db.execute('UPDATE works SET source=?,permission=?,matched_work=?,proposed_filename=?,destination=? WHERE id=?', (data['source_url'], 'staff-reviewed', data['matched_work'], data['filename'], data['destination'], wid))

def acquire(db, wid, home, config):
    _, record = get(db, wid)
    review_data = record['review']
    url = review_data['source_url']
    require(urllib.parse.urlparse(url).scheme == 'https', 'Only authorized HTTPS direct downloads supported; torrents remain supervised')
    require(urllib.parse.urlparse(url).hostname in config['source_hosts'], 'Source host not approved')
    limit = int(config['max_file_bytes'])
    used = sum(p.stat().st_size for folder in ('incomplete', 'candidates') for p in (home / folder).rglob('*') if p.is_file())
    require(used + limit <= config['disk_budget_bytes'] and shutil.disk_usage(home).free > limit + config['reserve_bytes'], 'Disk budget exhausted')
    class Redirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            target = urllib.parse.urlparse(newurl)
            require(target.scheme == 'https' and target.hostname in config['source_hosts'], 'Redirect host not approved')
            return super().redirect_request(req, fp, code, msg, headers, newurl)
    target = home / 'incomplete' / f'{wid}.part'
    require(not record.get('upload_id'), 'Upload already started')
    try:
        with urllib.request.build_opener(Redirect()).open(url, timeout=60) as response, target.open('wb') as out:
            size = 0
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                size += len(block)
                require(size <= limit, 'Download exceeds file limit')
                out.write(block)
            require(size > 0, 'Empty download')
            if response.headers.get('Content-Length'):
                require(size == int(response.headers['Content-Length']), 'Incomplete download')
        candidate = home / 'candidates' / f'{wid}{Path(review_data["filename"]).suffix.lower()}'
        target.replace(candidate)
        record['candidate'] = str(candidate)
        record.pop('validation', None)
        record.pop('approval', None)
        save(db, wid, record, 'acquired')
    finally:
        target.unlink(missing_ok=True)

def validate_file(db, wid, config):
    _, record = get(db, wid)
    path = Path(record['candidate'])
    require(path.stat().st_size <= config['max_file_bytes'], 'File exceeds limit')
    with path.open('rb') as f:
        magic = f.read(32)
    ext = path.suffix.lower()
    require((ext == '.pdf' and magic.startswith(b'%PDF-')) or
            (ext == '.mp3' and (magic.startswith(b'ID3') or (len(magic) > 1 and magic[0] == 255 and magic[1] & 224 == 224))) or
            (ext == '.mp4' and magic[4:8] == b'ftyp'), 'Unsupported or mismatched file type')
    # Tool errors and unavailable/stale scanners must never count as clean.
    scanner = config['scanner_command']
    require(isinstance(scanner, list) and scanner, 'Configure a malware scanner command array')
    before = digest(path)
    subprocess.run([*scanner, str(path)], capture_output=True, check=True, timeout=600)
    command = ['pdfinfo', str(path)] if ext == '.pdf' else ['ffprobe', '-v', 'error', '-show_format', '-show_streams', str(path)]
    result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=120)
    require(before == digest(path), 'Candidate changed during validation')
    record['sha256'] = before
    record['validation'] = {'at': stamp(), 'sha256': before, 'tool_output': result.stdout, 'scanner': scanner}
    record.pop('approval', None)
    save(db, wid, record, 'validated')
    with db:
        db.execute('UPDATE works SET sha256=?,status=? WHERE id=?', (record['sha256'], 'awaiting_staff_approval', wid))

def approve(db, wid, path, config):
    _, record = get(db, wid)
    approval = json.loads(path.read_text())
    require(approval.get('reviewer') in config['reviewers'], 'Unknown reviewer')
    require(record.get('validation') and approval.get('sha256') == record['sha256'] == digest(record['candidate']), 'Approval must bind to validated file hash')
    for key in ('bibliography_verified', 'complete', 'first_last_and_body_checked'):
        require(approval.get(key) is True, 'Staff check required: ' + key)
    require(approval.get('destination') == record['review']['destination'], 'Approval destination mismatch')
    require(record.get('archive_check') and not record['archive_check']['matches'], 'Archive matches require resolution before approval')
    record['approval'] = dict(approval, at=stamp())
    save(db, wid, record, 'approved')


def publish(db, wid, api, config):
    require(config.get('publication_approved') is True, 'Live publication not enabled by staff')
    work, record = get(db, wid)
    require(record.get('approval'), 'Staff approval required')
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
        require(path.stat().st_size <= 5 * 1024 * 1024, 'Pilot multipart uploader supports at most 5 MiB; larger files require resumable upload implementation')
        boundary = 'gsa_' + record['sha256']
        metadata = {'id': file_id, 'name': review_data['filename'], 'parents': [destination], 'appProperties': {'gsa_sha256': record['sha256']}}
        body = (f'--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n' + json.dumps(metadata) + f'\r\n--{boundary}\r\nContent-Type: application/octet-stream\r\n\r\n').encode() + path.read_bytes() + f'\r\n--{boundary}--\r\n'.encode()
        api.call('POST', 'https://www.googleapis.com/upload/drive/v3/files', body=body, params={'uploadType': 'multipart', 'supportsAllDrives': 'true'}, headers={'Content-Type': 'multipart/related; boundary=' + boundary})
        remote = api.call('GET', DRIVE + '/' + file_id, params={'fields': 'id,name,parents,size,md5Checksum,webViewLink', 'supportsAllDrives': 'true'})
    require(remote['name'] == review_data['filename'] and destination in remote.get('parents', []) and int(remote['size']) == path.stat().st_size and remote.get('md5Checksum') == digest(path, 'md5'), 'Uploaded file verification failed')
    # Verify readability, not just metadata.
    downloaded = api.call('GET', DRIVE + '/' + file_id, params={'alt': 'media', 'supportsAllDrives': 'true'}, raw=True)
    require(hashlib.sha256(downloaded).hexdigest() == record['sha256'], 'Drive readback mismatch')
    with db:
        db.execute('UPDATE works SET upload_receipt=?,status=? WHERE id=?', (json.dumps(dict(remote, verified_drive_link=remote.get('webViewLink', 'https://drive.google.com/file/d/' + file_id + '/view'))), 'uploaded', wid))
    document_id = config['changelog_document_id']
    document = api.call('GET', DOCS + document_id)
    marker = '[GSA:' + file_id + ']'
    entry = review_data['changelog_text'] + '\n' + marker + '\n'
    # Staff supplies exact dated entry; reject multi-tab docs until a tab is explicitly supported.
    require('body' in document, 'Changelog must expose a document body')
    content = ''.join(el.get('textRun', {}).get('content', '') for item in document['body']['content'] for el in item.get('paragraph', {}).get('elements', []))
    if marker not in content:
        anchor = config['changelog_anchor']
        require(content.count(anchor) == 1, 'Changelog dated anchor missing or ambiguous')
        # Find the actual Docs UTF-16 index, accounting for structural elements.
        insertion = None
        for item in document['body']['content']:
            for el in item.get('paragraph', {}).get('elements', []):
                text = el.get('textRun', {}).get('content', '')
                if anchor in text:
                    insertion = el['startIndex'] + len(text[:text.index(anchor) + len(anchor)].encode('utf-16-le')) // 2
        require(insertion is not None, 'Anchor spans text runs; staff must choose a plain-text anchor')
        api.call('POST', DOCS + document_id + ':batchUpdate', body={'writeControl': {'requiredRevisionId': document['revisionId']}, 'requests': [{'insertText': {'location': {'index': insertion}, 'text': '\n' + entry}}]})
    with db:
        db.execute('UPDATE works SET changelog_receipt=?,status=?,reason=? WHERE id=?', (json.dumps({'target': document_id, 'marker': marker, 'at': stamp()}), 'complete', 'Verified Drive upload and dated changelog', wid))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=gsa.DEFAULT_HOME)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('command', choices=['poll', 'check', 'review', 'acquire', 'validate', 'approve', 'publish'])
    parser.add_argument('--work', type=int)
    parser.add_argument('--file', type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    require(args.config.stat().st_mode & 0o077 == 0, 'Private configuration must have mode 0600')
    config = json.loads(args.config.read_text())
    home = args.home.expanduser().resolve()
    db = gsa.connect(home)
    migrate(db)
    # One process covers poll/acquisition/publication; crash releases the lock.
    with (home / 'pipeline.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        api = Google(config)
        if args.command == 'poll':
            print(f'Imported {poll(db, api, config)} submissions')
        else:
            require(args.work is not None, '--work required')
            if args.command in ('review', 'approve'):
                require(args.file is not None, '--file required')
                globals()[args.command](db, args.work, args.file, config)
            elif args.command == 'check':
                _, record = get(db, args.work)
                print(json.dumps(archive_check(db, args.work, api, config, record['review']['destination']), indent=2))
            elif args.command == 'acquire':
                acquire(db, args.work, home, config)
            elif args.command == 'validate':
                validate_file(db, args.work, config)
            else:
                publish(db, args.work, api, config)
    db.close()

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # HTTP bodies and credentials are never printed.
        print(f'Pipeline stopped: {type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(1)
