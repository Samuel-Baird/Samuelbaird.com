"""Select and stage one reviewed PDF from an operator-added, stopped torrent."""
import hashlib
import os
from pathlib import Path
import re
import shutil
import tempfile
import unicodedata

import acquire


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inspect(torrent, review):
    key = review['infohash'].lower()
    require(key in (torrent['infohash_v1'], torrent['infohash_v2']), 'Reviewed infohash mismatch')
    path = review['torrent_member']
    checksum = review.get('member_md5', '')
    require(re.fullmatch('[0-9a-f]{32}', checksum), 'Expected lowercase member_md5')
    require(isinstance(path, str) and not acquire._unsafe(path), 'Invalid selected file path')
    require(Path(review['filename']).suffix.lower() == '.pdf', 'Reviewed destination must be a PDF')
    require(Path(path).suffix.lower() == '.pdf' or Path(path).name == checksum,
            'Choose an individual PDF or its exact MD5 filename')
    names = {}
    folded = set()
    for entry in torrent['files']:
        name = entry['path']
        normalized = unicodedata.normalize('NFD', name).casefold()
        require(not acquire._unsafe(name) and normalized not in folded and entry['length'] >= 0,
                'Unsafe or colliding collection paths')
        folded.add(normalized)
        if not entry['padding']:
            names[name] = entry['length']
    require(names.get(path, 0) > 0, 'Reviewed PDF missing from metainfo')
    piece = torrent['piece_length']
    require(isinstance(piece, int) and piece > 0, 'Invalid piece length')
    return names, piece


def client_selection(client, key, names, path):
    files = client.call('torrents/files?hash=' + key)
    require(len(files) == len(names) and {f['name']: f['size'] for f in files} == names,
            'Client file list differs from reviewed metainfo')
    indexes = {f['index'] for f in files}
    require(len(indexes) == len(files) and all(type(i) is int and i >= 0 for i in indexes),
            'Invalid client file indexes')
    return next(f for f in files if f['name'] == path), [f for f in files if f['name'] != path]


def checked_paths(home, row, key, member):
    root = (home / 'incomplete' / key).absolute()
    require(root.resolve() == root and Path(row['save_path']).resolve() == root,
            'Collection needs its dedicated incomplete/INFOHASH save path')
    if row.get('download_path'):
        require(Path(row['download_path']).resolve() == root, 'Temporary download path differs')
    path = root / member
    require(path.resolve() == path and path.is_relative_to(root), 'Unsafe collection member path')
    return path


def budget(home, config, size, piece, present):
    # Reserve one immutable staged copy plus two boundary pieces. Unselected
    # files can contribute bytes to pieces that straddle the chosen file.
    limits = acquire.check_disk([size], acquire.staged_bytes(home) + size + 2 * piece,
                                shutil.disk_usage(home).free - size - 2 * piece,
                                config, min(present, size))
    require(limits['ok'], 'Selected member exceeds staging budget: ' + ', '.join(limits['problems']))


def check(client, key, names, piece, member, row, home, config, prepare):
    path = checked_paths(home, row, key, member)
    size = names[member]
    budget(home, config, size, piece, path.stat().st_size if path.is_file() else 0)
    selected, others = client_selection(client, key, names, member)
    if prepare:
        require(row['state'] in ('stoppedDL', 'stoppedUP', 'pausedDL', 'pausedUP'),
                'Stop the collection before preparing file priorities')
        ids = [str(f['index']) for f in others if f['priority'] != 0]
        for start in range(0, len(ids), 256):
            client.call('torrents/filePrio', dict(hash=key, id='|'.join(ids[start:start + 256]), priority=0))
        if not selected['priority']:
            client.call('torrents/filePrio', dict(hash=key, id=str(selected['index']), priority=1))
        selected, others = client_selection(client, key, names, member)
    require(selected['priority'] > 0 and all(f['priority'] == 0 for f in others),
            'Client must select only the reviewed file')
    return path, selected


def stage(home, wid, path, review, size):
    """Copy out of libtorrent's mutable data directory, then verify identity."""
    dest = home / 'candidates' / f"{wid}-{review['infohash'].lower()}-{review['member_md5']}.pdf"
    md5 = hashlib.md5()
    with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as out:
        temp = Path(out.name)
    try:
        with path.open('rb') as source, temp.open('wb') as out:
            require(source.read(5) == b'%PDF-', 'Selected member is not a PDF')
            source.seek(0)
            for block in iter(lambda: source.read(1024 * 1024), b''):
                require(out.tell() + len(block) <= size, 'Member grew while staging')
                md5.update(block)
                out.write(block)
            require(out.tell() == size and md5.hexdigest() == review['member_md5'],
                    'Member length or MD5 differs from source review')
        os.replace(temp, dest)
        return dest
    finally:
        temp.unlink(missing_ok=True)
