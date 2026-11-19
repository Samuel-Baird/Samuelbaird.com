#!/usr/bin/env python3
"""GSA acquisition gates: offline torrent payload review, permission records,
disk limits, and stalled-download decisions. Standard library only.

Nothing here downloads, talks to qBittorrent, or touches the VPN. Functions take
parsed data or status snapshots and return decisions; the caller performs any
action after its own checks (see PIPELINE.md and rollout.py guard).
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import sys

# ---------------------------------------------------------------- bencode


class BencodeError(ValueError):
    pass


def _decode(data, i, spans, depth):
    if depth > 64:
        raise BencodeError('Nesting too deep')
    if i >= len(data):
        raise BencodeError('Unexpected end of data')
    c = data[i:i + 1]
    if c == b'i':
        end = data.index(b'e', i)
        raw = data[i + 1:end]
        if not raw or raw == b'-0' or (raw.lstrip(b'-')[:1] == b'0' and raw.lstrip(b'-') != b'0'):
            raise BencodeError('Invalid integer')
        try:
            return int(raw), end + 1
        except ValueError:
            raise BencodeError('Invalid integer') from None
    if c == b'l':
        i += 1
        out = []
        while data[i:i + 1] != b'e':
            value, i = _decode(data, i, None, depth + 1)
            out.append(value)
        return out, i + 1
    if c == b'd':
        i += 1
        out = {}
        last = None
        while data[i:i + 1] != b'e':
            key, i = _decode(data, i, None, depth + 1)
            if not isinstance(key, bytes):
                raise BencodeError('Dictionary key must be a byte string')
            if last is not None and key <= last:
                raise BencodeError('Dictionary keys unsorted or duplicated')
            start = i
            value, i = _decode(data, i, None, depth + 1)
            if spans is not None and depth == 0 and key == b'info':
                spans['info'] = (start, i)
            out[key] = value
            last = key
        return out, i + 1
    if c.isdigit():
        colon = data.index(b':', i)
        raw = data[i:colon]
        if raw[:1] == b'0' and raw != b'0':
            raise BencodeError('Invalid string length')
        length = int(raw)
        end = colon + 1 + length
        if end > len(data):
            raise BencodeError('String exceeds data')
        return data[colon + 1:end], end
    raise BencodeError(f'Unexpected byte at {i}')


def bdecode(data, spans=None):
    """Strict bencode decoder. `spans` (dict) receives the byte span of the
    top-level 'info' value, needed for the infohash."""
    try:
        value, end = _decode(data, 0, spans, 0)
    except (IndexError, ValueError) as exc:
        if isinstance(exc, BencodeError):
            raise
        raise BencodeError(str(exc)) from None
    if end != len(data):
        raise BencodeError('Trailing data after bencoded value')
    return value


def bencode(value):
    """Encoder used for test fixtures."""
    if isinstance(value, bool):
        raise TypeError('bool not encodable')
    if isinstance(value, int):
        return b'i%de' % value
    if isinstance(value, str):
        value = value.encode()
    if isinstance(value, bytes):
        return b'%d:%s' % (len(value), value)
    if isinstance(value, list):
        return b'l' + b''.join(bencode(v) for v in value) + b'e'
    if isinstance(value, dict):
        items = sorted((k.encode() if isinstance(k, str) else k, v) for k, v in value.items())
        return b'd' + b''.join(bencode(k) + bencode(v) for k, v in items) + b'e'
    raise TypeError(f'Cannot encode {type(value).__name__}')


# ---------------------------------------------------------------- torrent parsing

MAX_TORRENT_BYTES = 16 * 1024 * 1024


def _text(value):
    return value.decode('utf-8', 'replace') if isinstance(value, bytes) else str(value)


def _v2_files(tree, prefix=()):
    for name, node in tree.items():
        if name == b'':
            yield prefix, node
        else:
            yield from _v2_files(node, prefix + (_text(name),))


def parse_torrent(data):
    """Parse .torrent bytes offline. Returns infohash(es), name and file list."""
    if isinstance(data, (str, Path)):
        path = Path(data)
        if path.stat().st_size > MAX_TORRENT_BYTES:
            raise BencodeError('Torrent file too large')
        data = path.read_bytes()
    spans = {}
    meta = bdecode(data, spans)
    if not isinstance(meta, dict) or not isinstance(meta.get(b'info'), dict):
        raise BencodeError('Missing info dictionary')
    info = meta[b'info']
    raw_info = data[spans['info'][0]:spans['info'][1]]
    version = info.get(b'meta version', 1)
    name = _text(info.get(b'name', b''))
    files = []
    if b'file tree' in info and version == 2:
        for parts, node in _v2_files(info[b'file tree']):
            files.append({'path': list(parts), 'length': int(node.get(b'length', 0)), 'padding': False})
    elif b'files' in info:
        for entry in info[b'files']:
            parts = [_text(p) for p in entry.get(b'path.utf-8', entry.get(b'path', []))]
            files.append({'path': [name, *parts], 'length': int(entry[b'length']),
                          'padding': b'p' in entry.get(b'attr', b'')})
    elif b'length' in info:
        files.append({'path': [name], 'length': int(info[b'length']), 'padding': False})
    else:
        raise BencodeError('Info dictionary lists no files')
    trackers = []
    if b'announce' in meta:
        trackers.append(_text(meta[b'announce']))
    for tier in meta.get(b'announce-list', []):
        trackers.extend(_text(t) for t in tier if _text(t) not in trackers)
    hybrid = b'pieces' in info and version == 2
    return {
        'name': name,
        'infohash_v1': hashlib.sha1(raw_info).hexdigest() if (version == 1 or hybrid) else None,
        'infohash_v2': hashlib.sha256(raw_info).hexdigest() if version == 2 else None,
        'meta_version': version,
        'private': info.get(b'private') == 1,
        'piece_length': info.get(b'piece length'),
        'files': [dict(f, path='/'.join(f['path'])) for f in files],
        'total_bytes': sum(f['length'] for f in files if not f['padding']),
        'trackers': trackers,
        'web_seeds': [_text(u) for u in (meta.get(b'url-list') if isinstance(meta.get(b'url-list'), list) else [meta[b'url-list']] if b'url-list' in meta else [])],
        'comment': _text(meta.get(b'comment', b'')),
        'created_by': _text(meta.get(b'created by', b'')),
        'source': _text(info.get(b'source', b'')),
    }


# ---------------------------------------------------------------- payload review

CONTENT_TYPES = {'.pdf': 'document', '.mp3': 'audio', '.mp4': 'video'}
# Harmless sidecars still get shared by the whole torrent; they are flagged, not blocked.
SIDECAR_TYPES = {'.txt', '.nfo', '.md', '.jpg', '.jpeg', '.png', '.sfv', '.md5', '.sha256', '.cue', '.m3u'}
DANGEROUS_TYPES = {'.exe', '.dll', '.bat', '.cmd', '.com', '.scr', '.msi', '.vbs', '.js', '.jar', '.ps1',
                   '.sh', '.app', '.pkg', '.dmg', '.command', '.lnk', '.apk', '.iso', '.bin', '.py'}
ARCHIVE_TYPES = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tgz', '.cbz', '.cbr'}
EBOOK_TYPES = {'.epub', '.mobi', '.azw', '.azw3', '.djvu', '.fb2', '.lit', '.doc', '.docx', '.rtf', '.html', '.htm'}


def _unsafe(path):
    parts = PurePosixPath(path).parts
    return (not path or path.startswith('/') or '\\' in path or any(p in ('', '.', '..') for p in path.split('/'))
            or any(ord(ch) < 32 for ch in path) or parts[:1] == ('~',))


def review_payload(torrent, config=None, expected_infohash=None):
    """Classify a parsed torrent's payload. Any flag routes it to staff review.

    A clean result only means the payload looks like one supported file; it is
    still blocked until all three permission records are granted (see
    evaluate_permissions) and staff confirm provenance and edition.
    """
    config = config or {}
    flags = []
    blocking = []
    files = [f for f in torrent['files'] if not f['padding']]
    content = []
    for f in files:
        ext = PurePosixPath(f['path']).suffix.lower()
        if _unsafe(f['path']):
            blocking.append(f"unsafe_path: {f['path']!r}")
        if ext in CONTENT_TYPES:
            content.append((f, CONTENT_TYPES[ext]))
        elif ext in DANGEROUS_TYPES:
            blocking.append(f"executable_or_disk_image: {f['path']}")
        elif ext in ARCHIVE_TYPES:
            flags.append(f"archive_contents_unknown: {f['path']}")
        elif ext in EBOOK_TYPES:
            flags.append(f"non_pdf_ebook_or_document: {f['path']}")
        elif ext in SIDECAR_TYPES:
            flags.append(f"sidecar_file_would_be_shared: {f['path']}")
        else:
            flags.append(f"unexpected_file_type: {f['path']}")
        if f['length'] == 0:
            flags.append(f"empty_file: {f['path']}")
    kinds = {k for _, k in content}
    if not content:
        blocking.append('no_supported_content_file (PDF, MP3 or MP4)')
    if len(kinds) > 1:
        flags.append('mixed_bundle: ' + ', '.join(sorted(kinds)))
    documents = [f for f, k in content if k == 'document']
    if len(documents) > 1:
        flags.append(f'multi_work_payload: {len(documents)} PDFs (may be several works or volumes)')
    media = [f for f, k in content if k != 'document']
    if len(media) > 1:
        # One audiobook/lecture series can legitimately be many tracks; staff decide.
        flags.append(f'multi_file_media: {len(media)} audio/video files (confirm one work)')
    if len(files) > int(config.get('max_payload_files', 200)):
        blocking.append(f'too_many_files: {len(files)}')
    if expected_infohash and expected_infohash.lower() not in (torrent.get('infohash_v1'), torrent.get('infohash_v2')):
        blocking.append('infohash_mismatch with staff-reviewed record')
    if not torrent.get('trackers') and not torrent.get('web_seeds'):
        flags.append('no_trackers_listed (DHT-only; provenance harder to establish)')
    limits = disk_requirements(torrent, config) if config.get('max_file_bytes') else {'problems': []}
    blocking.extend(limits['problems'])
    route = 'blocked' if blocking else ('staff_review' if flags else 'permission_check')
    return {
        'name': torrent['name'],
        'infohash_v1': torrent.get('infohash_v1'),
        'infohash_v2': torrent.get('infohash_v2'),
        'files': [{'path': f['path'], 'bytes': f['length']} for f in files],
        'total_bytes': torrent['total_bytes'],
        'trackers': torrent.get('trackers', []),
        'blocking': blocking,
        'flags': flags,
        'route': route,
        'note': 'Torrent payload is shared whole while seeding; every listed file needs download and peer-sharing permission.',
    }


# ---------------------------------------------------------------- permissions

PERMISSION_FIELDS = ('download', 'peer_sharing', 'gsa_upload')
GRANTED = 'granted'


def evaluate_permissions(record, reviewers=None):
    """Check the three separate permission records.

    Each field is {status, basis, source, recorded_by, recorded_at}. Only the
    literal status "granted" with all provenance fields counts; missing,
    "unknown", true/yes or anything else blocks. Nothing is inferred, and no
    field implies another.
    """
    record = record or {}
    result = {}
    for field in PERMISSION_FIELDS:
        entry = record.get(field)
        problems = []
        if not isinstance(entry, dict):
            problems.append('missing')
        else:
            status = entry.get('status')
            if status != GRANTED:
                problems.append(f'status is {status!r}, not "granted"')
            for key in ('basis', 'source', 'recorded_by', 'recorded_at'):
                if not str(entry.get(key) or '').strip():
                    problems.append(f'{key} missing')
            if reviewers is not None and entry.get('recorded_by') not in reviewers:
                problems.append('recorded_by is not an approved reviewer')
        result[field] = {'ok': not problems, 'problems': problems}
    ok = {k: v['ok'] for k, v in result.items()}
    return {
        'fields': result,
        # Downloading by BitTorrent uploads pieces to peers, so it needs both.
        'may_download_direct': ok['download'],
        'may_download_torrent': ok['download'] and ok['peer_sharing'],
        'may_seed_after_completion': ok['peer_sharing'],
        'may_upload_to_gsa': ok['gsa_upload'],
    }


def permission_entry(status, basis, source, recorded_by, recorded_at):
    """Helper so callers build records explicitly field by field."""
    return {'status': status, 'basis': basis, 'source': source, 'recorded_by': recorded_by, 'recorded_at': recorded_at}


# ---------------------------------------------------------------- disk limits

def staged_bytes(home):
    """Bytes already held in the worker's incomplete and candidates folders."""
    home = Path(home)
    return sum(p.stat().st_size for folder in ('incomplete', 'candidates')
               for p in (home / folder).rglob('*') if p.is_file() and not p.is_symlink())


def check_disk(file_sizes, staged, free, config, already_present=0):
    """Pure disk-limit check. `already_present` counts bytes of this job that are
    already on disk (resumed partial), so they are not double counted."""
    problems = []
    max_file = int(config['max_file_bytes'])
    for size in file_sizes:
        if size > max_file:
            problems.append(f'file_too_large: {size} > max_file_bytes {max_file}')
    total = sum(file_sizes)
    needed = max(0, total - already_present)
    if staged + needed > int(config['disk_budget_bytes']):
        problems.append(f'staging_budget_exceeded: {staged} staged + {needed} needed > {config["disk_budget_bytes"]}')
    if free - needed < int(config['reserve_bytes']):
        problems.append(f'free_space_reserve: {free} free - {needed} needed < reserve {config["reserve_bytes"]}')
    return {'ok': not problems, 'problems': problems, 'needed_bytes': needed}


def disk_requirements(torrent, config, staged=0, free=None):
    sizes = [f['length'] for f in torrent['files'] if not f['padding']]
    return check_disk(sizes, staged, free if free is not None else float('inf'), config)


def disk_check(home, file_sizes, config, already_present=0):
    home = Path(home)
    return check_disk(file_sizes, staged_bytes(home), shutil.disk_usage(home).free, config, already_present)


# ---------------------------------------------------------------- stalled-download decisions
# Snapshots are rows shaped like qBittorrent /api/v2/torrents/info. Times are
# epoch seconds. Decisions are data; the caller acts on them.

DEFAULT_POLICY = {
    'stall_minutes': 30,          # no byte progress for this long while downloading
    'metadata_minutes': 15,       # magnet metadata never arrived
    'max_retries': 3,
    'retry_backoff_minutes': 10,  # minimum spacing between retries
}
COMPLETE_STATES = {'uploading', 'stalledUP', 'pausedUP', 'stoppedUP', 'queuedUP', 'forcedUP', 'checkingUP'}
CHECKING_STATES = {'checkingDL', 'checkingUP', 'checkingResumeData', 'allocating', 'moving'}
METADATA_STATES = {'metaDL', 'forcedMetaDL'}
ACTIVE_STATES = {'downloading', 'stalledDL', 'forcedDL', 'queuedDL'}
PAUSED_STATES = {'pausedDL', 'stoppedDL'}
ERROR_STATES = {'error', 'missingFiles', 'unknown'}


def new_job(infohash, now, expected_bytes=None):
    return {'infohash': infohash.lower(), 'started_at': now, 'last_progress_at': now,
            'best_downloaded': 0, 'retries': 0, 'last_retry_at': None,
            'expected_bytes': expected_bytes, 'status': 'active', 'history': []}


def _decision(job, action, reason, now):
    job['history'] = (job.get('history') or [])[-19:] + [{'at': now, 'action': action, 'reason': reason}]
    if action in ('pause_and_review', 'route_to_review'):
        job['status'] = 'review'
    elif action == 'complete':
        job['status'] = 'complete'
    return {'action': action, 'reason': reason, 'retries': job['retries']}


def _retry_or_review(job, reason, now, policy):
    if job['retries'] >= policy['max_retries']:
        return _decision(job, 'pause_and_review', f'{reason}; retries exhausted ({job["retries"]})', now)
    last = job.get('last_retry_at')
    if last is not None and now - last < policy['retry_backoff_minutes'] * 60:
        return _decision(job, 'wait', f'{reason}; waiting for retry backoff', now)
    job['retries'] += 1
    job['last_retry_at'] = now
    # Reset the stall clock so the retry gets a full window.
    job['last_progress_at'] = now
    return _decision(job, 'retry', f'{reason}; retry {job["retries"]}/{policy["max_retries"]}', now)


def assess(job, snapshot, now, policy=None, config=None):
    """Decide what to do with one torrent given its latest snapshot.

    Mutates and returns the job's decision. Actions:
      wait             nothing to do yet
      retry            stop and restart (or reannounce) the torrent
      recheck          force a hash recheck against files on disk
      readd_paused     torrent missing from the client; re-add paused at the same save path
      pause_and_review pause it and route to staff review (never auto-resume)
      route_to_review  already stopped; staff review
      complete         payload complete; hand to validation
    """
    policy = dict(DEFAULT_POLICY, **(policy or {}))
    if job.get('status') == 'review':
        return {'action': 'route_to_review', 'reason': 'awaiting staff review', 'retries': job['retries']}
    if snapshot is None:
        return _decision(job, 'route_to_review', 'torrent not present in client; use recover() after restart', now)
    if snapshot.get('hash', '').lower() != job['infohash']:
        return _decision(job, 'pause_and_review', 'snapshot infohash does not match job', now)
    state = snapshot.get('state', 'unknown')
    size = snapshot.get('total_size', snapshot.get('size', 0)) or 0
    if config and config.get('disk_budget_bytes') and size > int(config['disk_budget_bytes']):
        return _decision(job, 'pause_and_review', 'torrent size exceeds staging budget', now)
    if job.get('expected_bytes') and size and state not in METADATA_STATES and size != job['expected_bytes']:
        # Partial file selection would change the shared payload: staff decide.
        return _decision(job, 'pause_and_review', f'selected size {size} differs from reviewed payload {job["expected_bytes"]}', now)
    downloaded = int(snapshot.get('downloaded', 0) or 0)
    completed = int(snapshot.get('completed', downloaded) or 0)
    progress_bytes = max(downloaded, completed)
    if progress_bytes > job['best_downloaded']:
        job['best_downloaded'] = progress_bytes
        job['last_progress_at'] = now

    if snapshot.get('progress', 0) >= 1 and state in COMPLETE_STATES:
        return _decision(job, 'complete', 'download complete; validate before any further step', now)
    if state in ERROR_STATES:
        if state == 'missingFiles':
            return _decision(job, 'recheck', 'client reports missing files; recheck save path', now) \
                if job['retries'] < policy['max_retries'] else _decision(job, 'pause_and_review', 'missing files persist', now)
        return _retry_or_review(job, f'client state {state}', now, policy)
    if state in CHECKING_STATES:
        return _decision(job, 'wait', f'client {state}', now)
    if state in PAUSED_STATES:
        return _decision(job, 'route_to_review', 'torrent paused outside the worker (guard or operator); do not auto-resume', now)
    if state in METADATA_STATES:
        added = snapshot.get('added_on') or job['started_at']
        if now - max(added, job.get('last_retry_at') or 0) > policy['metadata_minutes'] * 60:
            return _retry_or_review(job, 'metadata not received', now, policy)
        return _decision(job, 'wait', 'awaiting metadata', now)
    if state in ACTIVE_STATES:
        idle = now - job['last_progress_at']
        if idle > policy['stall_minutes'] * 60:
            seeds = snapshot.get('num_seeds', 0)
            avail = snapshot.get('availability', -1)
            detail = f'no progress for {int(idle // 60)} min (seeds {seeds}, availability {avail})'
            return _retry_or_review(job, detail, now, policy)
        return _decision(job, 'wait', 'progressing' if idle == 0 else f'idle {int(idle // 60)} min', now)
    return _decision(job, 'pause_and_review', f'unrecognised client state {state!r}', now)


def recover(job, snapshot, partial_bytes, now, policy=None):
    """Decide how to resume after a worker or client restart.

    `partial_bytes` is the size of this job's data found on disk at the
    reviewed save path (0 or None if absent). Recovery never resumes a torrent
    the guard paused; it re-adds paused and lets the operator start it.
    """
    policy = dict(DEFAULT_POLICY, **(policy or {}))
    if job.get('status') in ('review', 'complete'):
        return {'action': 'route_to_review' if job['status'] == 'review' else 'complete',
                'reason': f'job already {job["status"]}', 'retries': job['retries']}
    if snapshot is not None:
        if snapshot.get('state') == 'missingFiles' and partial_bytes:
            return _decision(job, 'recheck', 'partial data present; client lost track; recheck', now)
        # Client still has it: progress may regress after a recheck. Rebase the baseline.
        done = int(snapshot.get('completed', snapshot.get('downloaded', 0)) or 0)
        if done < job['best_downloaded']:
            job['best_downloaded'] = done
        job['last_progress_at'] = now
        return assess(job, snapshot, now, policy)
    if job['retries'] >= policy['max_retries']:
        return _decision(job, 'route_to_review', 'torrent missing from client and retries exhausted', now)
    job['retries'] += 1
    job['last_retry_at'] = now
    job['last_progress_at'] = now
    job['best_downloaded'] = int(partial_bytes or 0)
    if partial_bytes:
        return _decision(job, 'readd_paused', f'torrent missing; {partial_bytes} bytes on disk; re-add paused with recheck', now)
    return _decision(job, 'readd_paused', 'torrent missing and no partial data; re-add paused', now)


# ---------------------------------------------------------------- CLI

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('inspect-torrent', help='Parse a local .torrent offline and review its payload')
    p.add_argument('torrent', type=Path)
    p.add_argument('--config', type=Path, help='Private pipeline config (read only) for disk limits')
    p.add_argument('--expected-infohash')
    p = sub.add_parser('check-permissions', help='Evaluate a permission record JSON file')
    p.add_argument('record', type=Path)
    args = parser.parse_args(argv)
    if args.cmd == 'inspect-torrent':
        config = json.loads(args.config.read_text()) if args.config else {}
        report = review_payload(parse_torrent(args.torrent), config, args.expected_infohash)
        print(json.dumps(report, indent=2))
        return 0 if report['route'] == 'permission_check' else 2
    record = json.loads(args.record.read_text())
    result = evaluate_permissions(record)
    print(json.dumps(result, indent=2))
    return 0 if all(v['ok'] for v in result['fields'].values()) else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
