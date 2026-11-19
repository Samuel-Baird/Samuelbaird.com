#!/usr/bin/env python3
"""Private, offline GSA intake and supervised-pilot rehearsal. Standard library only."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata
from datetime import datetime, timezone

DEFAULT_HOME = Path.home() / 'Library/Application Support/GSA Worker'
FIELDS = 'row_id,title,author,year,edition,isbn,doi,language,suggested_shelf,source_url'.split(',')

def normalized(value):
    return ' '.join(re.sub(r'[^\w\s]', ' ', unicodedata.normalize('NFKC', value).casefold()).split())

def identity(row):
    # Include edition metadata even for identifiers: conflicting records need review.
    return hashlib.sha256(json.dumps([normalized(row.get(k, '')) for k in
        ('title', 'author', 'year', 'edition', 'isbn', 'doi', 'language')]).encode()).hexdigest()

def validate(row):
    row = {k: str(row.get(k) or '').strip() for k in FIELDS}
    if not any(row[k] for k in ('title', 'doi', 'isbn')):
        raise ValueError('Each row requires title, DOI, or ISBN')
    if row['isbn']:
        isbn = re.sub(r'[\s-]', '', row['isbn']).upper()
        if len(isbn) == 13 and isbn.isdigit():
            valid = sum(int(v) * (1 if i % 2 == 0 else 3) for i, v in enumerate(isbn)) % 10 == 0
        elif re.fullmatch(r'\d{9}[\dX]', isbn):
            valid = sum((10-i) * (10 if v == 'X' else int(v)) for i, v in enumerate(isbn)) % 11 == 0
        else:
            valid = False
        if not valid:
            raise ValueError('Invalid ISBN checksum or format')
        row['isbn'] = isbn
    if row['doi']:
        doi = re.sub(r'^https?://(?:dx\.)?doi.org/', '', row['doi'], flags=re.I).lower()
        if not re.fullmatch(r'10\.\d{4,9}/\S+', doi):
            raise ValueError('Invalid DOI')
        row['doi'] = doi
    return row

def connect(home):
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(home, 0o700)
    for name in ('incomplete', 'candidates', 'receipts'):
        (home / name).mkdir(mode=0o700, exist_ok=True)
    db = sqlite3.connect(home / 'queue.sqlite3')
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
      CREATE TABLE IF NOT EXISTS works (
        id INTEGER PRIMARY KEY, fingerprint TEXT NOT NULL UNIQUE, metadata TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'needs_review', reason TEXT NOT NULL,
        matched_work TEXT, proposed_filename TEXT, destination TEXT,
        source TEXT, permission TEXT NOT NULL DEFAULT 'unverified', estimated_bytes INTEGER,
        sha256 TEXT, upload_receipt TEXT, changelog_receipt TEXT);
      CREATE TABLE IF NOT EXISTS submissions (
        source TEXT NOT NULL, submission_id TEXT NOT NULL, work_id INTEGER NOT NULL REFERENCES works(id),
        batch_id TEXT NOT NULL, original TEXT NOT NULL, PRIMARY KEY(source, submission_id));
      CREATE TABLE IF NOT EXISTS checkpoints (source TEXT PRIMARY KEY, value TEXT NOT NULL);
    ''')
    os.chmod(home / 'queue.sqlite3', 0o600)
    return db

def ingest(db, rows, source, batch, checkpoint=None):
    with db:
        return ingest_rows(db, rows, source, batch, checkpoint)


def ingest_rows(db, rows, source, batch, checkpoint=None):
    # Validate the complete batch before any mutation. Submission and checkpoint commit together.
    prepared = []
    seen = set()
    for raw in rows:
        row = validate(raw)
        sid = row['row_id']
        if not sid or sid in seen:
            raise ValueError('Each batch requires unique nonempty row_id values')
        seen.add(sid)
        prepared.append((sid, row))
    added = 0
    for sid, row in prepared:
        existing = db.execute('SELECT original FROM submissions WHERE source=? AND submission_id=?', (source, sid)).fetchone()
        if existing:
            if json.loads(existing['original']) != row:
                raise ValueError(f'Submission {sid} changed; use a new row_id to retain its previous outcome')
            continue
        key = identity(row)
        reason = 'Edition, archive duplicate check, source, permission, and destination require review'
        db.execute('INSERT OR IGNORE INTO works(fingerprint,metadata,reason,source) VALUES(?,?,?,?)',
                   (key, json.dumps(row), reason, row['source_url']))
        wid = db.execute('SELECT id FROM works WHERE fingerprint=?', (key,)).fetchone()['id']
        db.execute('INSERT INTO submissions VALUES(?,?,?,?,?)', (source, sid, wid, batch, json.dumps(row)))
        added += 1
    if checkpoint is not None:
        db.execute('INSERT INTO checkpoints VALUES(?,?) ON CONFLICT(source) DO UPDATE SET value=excluded.value', (source, checkpoint))
    return added

def manifest(db, output):
    columns = ['batch_id', 'submission_id', 'work_id', *FIELDS[1:], 'matched_work', 'status', 'reason',
               'permission', 'estimated_bytes', 'proposed_filename', 'destination', 'sha256', 'verified_drive_link']
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exports contain request details: keep them private even outside the worker directory.
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.chmod(output, 0o600)
    with os.fdopen(fd, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for record in db.execute('SELECT s.*,w.*,w.id AS work_id FROM submissions s JOIN works w ON s.work_id=w.id ORDER BY s.rowid'):
            row = dict(record)
            result = {k: row.get(k) or '' for k in columns}
            result.update(json.loads(row['original']))
            result.pop('row_id', None)
            receipt = json.loads(row['upload_receipt'] or '{}')
            result['verified_drive_link'] = receipt.get('verified_drive_link', '')
            writer.writerow(result)

def sandbox_upload(db, wid, fault=False):
    """Rehearse the post-upload crash window. Never calls Drive or writes a live changelog."""
    row = db.execute('SELECT * FROM works WHERE id=?', (wid,)).fetchone()
    if row is None:
        raise ValueError('Unknown work ID')
    with db:
        if not row['upload_receipt']:
            db.execute('UPDATE works SET upload_receipt=?, status=? WHERE id=?',
                       (json.dumps({'sandbox_file_id': f'mock-{wid}', 'mode': 'sandbox'}), 'sandbox_uploaded', wid))
    if fault:
        raise ValueError('Simulated interruption after upload receipt; rerun to finish sandbox changelog')
    with db:
        db.execute("UPDATE works SET changelog_receipt=COALESCE(changelog_receipt,?), status='sandbox_complete', reason='Simulated upload and changelog only; no live writes' WHERE id=?",
                   (json.dumps({'target': 'sandbox', 'entry_id': f'mock-entry-{wid}', 'date': datetime.now(timezone.utc).date().isoformat()}), wid))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=DEFAULT_HOME)
    sub = parser.add_subparsers(dest='cmd', required=True)
    sub.add_parser('init')
    p = sub.add_parser('import-csv'); p.add_argument('file', type=Path); p.add_argument('--batch', required=True)
    p = sub.add_parser('import-mock-forms'); p.add_argument('file', type=Path); p.add_argument('--form', default='mock-requests')
    p = sub.add_parser('manifest'); p.add_argument('output', type=Path)
    p = sub.add_parser('sandbox-upload'); p.add_argument('work_id', type=int); p.add_argument('--interrupt-after-upload', action='store_true')
    sub.add_parser('status')
    args = parser.parse_args()
    os.umask(0o077)
    db = connect(args.home.expanduser().resolve())
    try:
        if args.cmd == 'init':
            print(f'Initialized paused offline worker at {args.home}')
        elif args.cmd == 'import-csv':
            with args.file.open(newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames or 'row_id' not in reader.fieldnames:
                    raise ValueError('CSV requires row_id header')
                print(f'Imported {ingest(db, list(reader), "csv:" + args.batch, args.batch)} submissions; review required')
        elif args.cmd == 'import-mock-forms':
            payload = json.loads(args.file.read_text())
            # Adapter fixture: responseId, submittedAt, and mapped request fields.
            # Live Forms OAuth, field mapping, pagination and overlap polling are not enabled.
            rows = [dict(r['fields'], row_id=r['responseId']) for r in payload['responses']]
            print(f'Imported {ingest(db, rows, "mock-form:" + args.form, "mock-forms", payload["checkpoint"])} mock submissions')
        elif args.cmd == 'manifest':
            manifest(db, args.output); print(f'Wrote {args.output}')
        elif args.cmd == 'sandbox-upload':
            sandbox_upload(db, args.work_id, args.interrupt_after_upload); print('Sandbox publication complete')
        else:
            print(json.dumps({'mode': 'offline; torrent worker paused; live intake and publication disabled',
                'submissions': db.execute('SELECT COUNT(*) FROM submissions').fetchone()[0],
                'works': [dict(r) for r in db.execute('SELECT status,COUNT(*) AS count FROM works GROUP BY status')]}, indent=2))
    finally:
        db.close()

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, sqlite3.Error) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
