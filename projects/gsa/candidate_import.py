"""Import one complete browser download as an immutable, reviewed candidate.

The operator downloads the file (for example from a catalog partner server in
Chrome) and writes a private JSON source record. This module binds that record
to the existing source review, copies the file into the worker's candidate
folder, verifies size, PDF signature and MD5, and registers the copy. It does
not validate, rank, approve or publish. Run `validate` after import.

Recovery: the copy goes to a fixed temporary path under `incomplete/`. The
verified copy replaces a content-addressed candidate path atomically. A rerun
removes a stale temporary copy, registers a verified candidate that an earlier
run left unregistered, and does nothing for a candidate already registered.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat

import acquire as acquisition

SCHEMA = 'gsa.browser-candidate.v1'
PARTIAL_SUFFIXES = ('.crdownload', '.part', '.partial', '.download', '.tmp', '.opdownload')
EVIDENCE_FIELDS = ('schema', 'work_id', 'catalog_url', 'source', 'md5', 'bytes',
                   'matched_work', 'filename', 'recorded_by')
MAX_EVIDENCE_BYTES = 64 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_evidence(path):
    """Read the private source record. Only a 0600 regular file is accepted."""
    path = Path(path)
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode), 'Source record must be a regular file')
    require(info.st_mode & 0o077 == 0, 'Source record must have mode 0600')
    require(info.st_size <= MAX_EVIDENCE_BYTES, 'Source record too large')
    raw = path.read_bytes()
    data = json.loads(raw)
    require(isinstance(data, dict), 'Source record must be a JSON object')
    for key in EVIDENCE_FIELDS:
        require(key in data and data[key] not in ('', None), 'Source record missing: ' + key)
    require(data['schema'] == SCHEMA, 'Unsupported source record schema')
    require(type(data['work_id']) is int, 'work_id must be an integer')
    require(re.fullmatch('[0-9a-f]{32}', str(data['md5'])), 'md5 must be 32 lowercase hex digits')
    require(type(data['bytes']) is int and data['bytes'] > 0, 'bytes must be a positive integer')
    require(str(data['catalog_url']).startswith('https://'), 'catalog_url must use HTTPS')
    return data, hashlib.sha256(raw).hexdigest()


def bind_to_review(evidence, review, wid):
    """The source record repeats the reviewed values. It cannot replace them."""
    require(evidence['work_id'] == wid, 'Source record is for another work')
    require(review.get('source_md5') and review.get('source_bytes'),
            'Source review lacks source_md5 and source_bytes; record a reviewed source change first')
    pairs = (('catalog_url', 'source_url'), ('md5', 'source_md5'), ('bytes', 'source_bytes'),
             ('matched_work', 'matched_work'), ('filename', 'filename'))
    for mine, reviewed in pairs:
        require(evidence[mine] == review.get(reviewed),
                f'Source record {mine} differs from the source review; record a reviewed source change first')
    partners = review.get('source_partners')
    if partners is not None:
        require(evidence['source'] in partners, 'Source or partner is not listed in the source review')
    require(Path(review['filename']).suffix.lower() == '.pdf', 'Browser import accepts reviewed PDFs only')


def check_input(path, home, expected_bytes):
    """Reject links, special files, partial browser files and worker-owned paths."""
    path = Path(path).expanduser()
    require(path.is_absolute(), 'Give the downloaded file as an absolute path')
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode), 'Downloaded file must be a regular file, not a link or folder')
    require(path.resolve() == path, 'Downloaded file path must not pass through a link')
    require(not path.is_relative_to(home), 'Downloaded file must be outside the worker home')
    lower = path.name.lower()
    require(not lower.endswith(PARTIAL_SUFFIXES) and not lower.startswith('unconfirmed '),
            'Browser download is still partial')
    for suffix in PARTIAL_SUFFIXES:
        require(not path.with_name(path.name + suffix).exists(), 'Browser download is still in progress')
    require(info.st_size == expected_bytes,
            f'Downloaded file has {info.st_size} bytes; the source review expects {expected_bytes}')
    return path, info


def file_md5(path):
    h = hashlib.md5()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def copy_verified(source, temp, size, md5):
    """Copy and verify in one pass. The temporary copy stays private."""
    h = hashlib.md5()
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with source.open('rb') as src, os.fdopen(fd, 'wb') as out:
        require(src.read(5) == b'%PDF-', 'Downloaded file is not a PDF')
        src.seek(0)
        for block in iter(lambda: src.read(1024 * 1024), b''):
            require(out.tell() + len(block) <= size, 'Downloaded file grew during import')
            h.update(block)
            out.write(block)
        out.flush()
        os.fsync(out.fileno())
        require(out.tell() == size, 'Downloaded file is shorter than the source review')
    require(h.hexdigest() == md5, 'Downloaded file MD5 differs from the source review')


def same_file(before, after):
    return (before.st_ino, before.st_dev, before.st_size, before.st_mtime_ns) == \
           (after.st_ino, after.st_dev, after.st_size, after.st_mtime_ns)


def registered(record, md5, size):
    """A live candidate that already holds these bytes, or None."""
    candidates = record.get('candidates') or (
        [{'path': record['candidate']}] if record.get('candidate') else [])
    for c in candidates:
        p = Path(c['path'])
        if (not c.get('quarantined_to') and p.is_file() and not p.is_symlink()
                and p.stat().st_size == size and file_md5(p) == md5):
            return c
    return None


def import_candidate(db, wid, home, config, file, evidence_path):
    import pipeline
    home = Path(home).resolve()
    evidence, evidence_sha256 = load_evidence(evidence_path)
    _, record = pipeline.get(db, wid)
    require(record.get('review'), 'Source review required before import')
    require(not record.get('upload_id'), 'Upload already started')
    review = record['review']
    review_snapshot = json.dumps(review, sort_keys=True)
    bind_to_review(evidence, review, wid)
    md5, size = review['source_md5'], review['source_bytes']
    source, before = check_input(file, home, size)

    candidates_dir = home / 'candidates'
    dest = candidates_dir / f'{wid}-browser-{md5}.pdf'
    temp = home / 'incomplete' / f'import-{wid}-{md5}.part'
    temp.unlink(missing_ok=True)  # Stale copy from an interrupted run: never registered.

    existing = registered(record, md5, size)
    if existing:
        return {'action': 'duplicate', 'candidate': existing['path'], 'md5': md5}

    if dest.exists():
        # An earlier run verified and placed this copy but stopped before registration.
        require(dest.is_file() and not dest.is_symlink(), 'Candidate path is not a regular file')
        require(dest.stat().st_size == size and file_md5(dest) == md5,
                'Unregistered candidate differs from the source review; staff review required')
        action = 'recovered'
    else:
        limits = acquisition.disk_check(home, [size], config)
        require(limits['ok'], 'Disk limit: ' + ', '.join(limits['problems']))
        try:
            copy_verified(source, temp, size, md5)
            require(same_file(before, source.lstat()), 'Downloaded file changed during import')
            os.chmod(temp, 0o400)
            _, current = pipeline.get(db, wid)
            require(json.dumps(current.get('review'), sort_keys=True) == review_snapshot,
                    'Source review changed during import')
            require(not dest.exists(), 'Candidate path appeared during import')
            os.replace(temp, dest)
        finally:
            temp.unlink(missing_ok=True)
        action = 'imported'

    _, record = pipeline.get(db, wid)
    require(json.dumps(record.get('review'), sort_keys=True) == review_snapshot,
            'Source review changed during import')
    require(not record.get('upload_id'), 'Upload already started')
    candidates = record.get('candidates') or (
        [{'path': record['candidate'], 'origin': 'earlier'}] if record.get('candidate') else [])
    entry = {'path': str(dest), 'origin': 'browser:' + evidence['catalog_url'], 'added_at': pipeline.stamp(),
             'md5': md5, 'bytes': size, 'source': evidence['source'],
             'evidence': dict(evidence, sha256=evidence_sha256, path=str(Path(evidence_path).resolve()),
                              original_file=str(source))}
    record['candidates'] = candidates + [entry]
    record['candidate'] = str(dest)
    # The current candidate changed, so earlier results no longer apply (same rule as acquire).
    for key in ('validation', 'approval', 'reviewer_checks', 'candidate_reports', 'format_choice'):
        record.pop(key, None)
    pipeline.save(db, wid, record, 'candidate_imported')
    with db:
        db.execute("UPDATE works SET status='needs_review' WHERE id=? AND status='awaiting_staff_approval'", (wid,))
    return {'action': action, 'candidate': str(dest), 'md5': md5, 'bytes': size}
