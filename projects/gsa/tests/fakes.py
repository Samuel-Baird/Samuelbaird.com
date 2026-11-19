"""In-memory stand-ins for Google (Forms, Drive, Docs) and the qBittorrent Web API.

Used by tests and sandbox_trial.py. Nothing here touches the network. Faults are
injected by name so trials can lose a response after the server applied a write.
"""
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import urllib.error
import urllib.parse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import acquire as acq
import pipeline as p


def http_error(url, code):
    return urllib.error.HTTPError(url, code, 'fake', {}, None)


class FakeGoogle:
    def __init__(self, form_pages=None, folders=None, changelog=''):
        self.form_pages = form_pages or [{'responses': []}]
        self.folders = {f: {} for f in (folders or [])}   # folder -> {file_id: meta}
        self.blobs = {}                                   # file_id -> bytes
        self.doc_text = changelog
        self.tab_id = None   # set to model a multi-tab changelog; the changelog lives in this tab
        self.revision = 1
        self.faults = {}   # 'upload': 'before'|'after', 'changelog': 'after'
        self.calls = []
        self.next_id = 0

    # pipeline.Google.files equivalent
    def files(self, query):
        folder = query.split("'")[1]
        return [dict(meta) for meta in self.folders.get(folder, {}).values()]

    def _document(self):
        content, index = [], 1
        for line in self.doc_text.splitlines(keepends=True):
            content.append({'startIndex': index, 'paragraph': {'elements': [{'startIndex': index, 'textRun': {'content': line}}]}})
            index += len(line)
        body = {'content': content}
        if self.tab_id:
            decoy = {'content': [{'startIndex': 1, 'paragraph': {'elements': [{'startIndex': 1, 'textRun': {'content': 'Welcome tab\n'}}]}}]}
            return {'documentId': 'changelog', 'revisionId': str(self.revision),
                    'body': decoy, 'tabs': [{'tabProperties': {'tabId': 'welcome'}, 'documentTab': {'body': decoy}},
                                            {'tabProperties': {'tabId': self.tab_id}, 'documentTab': {'body': body}}]}
        return {'documentId': 'changelog', 'revisionId': str(self.revision), 'body': body}

    def call(self, method, url, body=None, params=None, headers=None, raw=False, stream_hash=False):
        params = params or {}
        self.calls.append((method, url.split('?')[0], dict(params)))
        if url.startswith(p.FORMS) and url.endswith('/responses'):
            index = int(params.get('pageToken', '0'))
            page = dict(self.form_pages[index])
            if index + 1 < len(self.form_pages):
                page['nextPageToken'] = str(index + 1)
            return page
        if url == p.DRIVE + '/generateIds':
            self.next_id += 1
            return {'ids': [f'fake-drive-{self.next_id}']}
        if url.startswith('https://www.googleapis.com/upload/drive/v3/files'):
            if self.faults.pop('upload', None) == 'before':
                raise ConnectionResetError('simulated upload interruption (server stored nothing)')
            boundary = headers['Content-Type'].split('boundary=')[1].encode()
            parts = body.split(b'--' + boundary)
            meta = json.loads(parts[1].split(b'\r\n\r\n', 1)[1].rsplit(b'\r\n', 1)[0])
            data = parts[2].split(b'\r\n\r\n', 1)[1][:-2]
            self.blobs[meta['id']] = data
            self.folders.setdefault(meta['parents'][0], {})[meta['id']] = {
                'id': meta['id'], 'name': meta['name'], 'parents': meta['parents'], 'size': str(len(data)),
                'md5Checksum': hashlib.md5(data).hexdigest(), 'appProperties': meta.get('appProperties', {}),
                'webViewLink': f'https://drive.example/{meta["id"]}'}
            if self.faults.pop('upload_response', None) == 'lost':
                raise TimeoutError('simulated lost upload response (server stored the file)')
            return {'id': meta['id']}
        if url.startswith(p.DRIVE + '/'):
            file_id = url[len(p.DRIVE) + 1:]
            for folder in self.folders.values():
                if file_id in folder:
                    if params.get('alt') == 'media':
                        blob = self.blobs[file_id]
                        return hashlib.sha256(blob).hexdigest() if stream_hash else blob
                    return dict(folder[file_id])
            raise http_error(url, 404)
        if url.startswith(p.DOCS):
            if url.endswith(':batchUpdate'):
                if body['writeControl']['requiredRevisionId'] != str(self.revision):
                    raise http_error(url, 400)
                request = body['requests'][0]['insertText']
                if request['location'].get('tabId') != self.tab_id:
                    raise http_error(url, 400)
                i = request['location']['index'] - 1
                self.doc_text = self.doc_text[:i] + request['text'] + self.doc_text[i:]
                self.revision += 1
                if self.faults.pop('changelog', None) == 'after':
                    raise TimeoutError('simulated lost changelog response (insert applied)')
                return {}
            return self._document()
        raise AssertionError('unexpected call ' + url)


class FakeQbt:
    """Minimal qBittorrent: torrents are added, started, stopped and 'downloaded'
    by the trial writing payload bytes into the save path."""
    def __init__(self):
        self.torrents = {}
        self.calls = []

    def add_torrent(self, data, save_path, stopped=True):
        parsed = acq.parse_torrent(data)
        h = parsed['infohash_v1']
        self.calls.append(('add', h, stopped))
        self.torrents[h] = {'hash': h, 'state': 'stoppedDL' if stopped else 'downloading', 'progress': 0.0,
                            'downloaded': 0, 'completed': 0, 'total_size': parsed['total_bytes'], 'save_path': save_path,
                            'files': parsed['files'], 'added_on': 0, 'num_seeds': 1, 'availability': 1}
        return 'Ok.'

    def call(self, endpoint, data=None):
        data = dict(data or {})
        if '?' in endpoint:
            endpoint, query = endpoint.split('?', 1)
            data.update(urllib.parse.parse_qsl(query))
        self.calls.append((endpoint, dict(data)))
        hashes = [h for h in data.get('hashes', '').split('|') if h]
        targets = list(self.torrents) if data.get('hashes') == 'all' else [h for h in hashes if h in self.torrents]
        if endpoint == 'torrents/info':
            return [dict(self.torrents[h], content_path=str(Path(self.torrents[h]['save_path'], self.torrents[h]['files'][0]['path'].split('/')[0])))
                    for h in hashes if h in self.torrents]
        for h in targets:
            t = self.torrents[h]
            if endpoint == 'torrents/start':
                t['state'] = 'uploading' if t['progress'] >= 1 else 'downloading'
            elif endpoint == 'torrents/stop':
                t['state'] = 'stoppedUP' if t['progress'] >= 1 else 'stoppedDL'
            elif endpoint == 'torrents/recheck':
                t['state'] = 'checkingDL'
            elif endpoint == 'torrents/reannounce':
                t['reannounced'] = t.get('reannounced', 0) + 1
            elif endpoint == 'torrents/delete':
                del self.torrents[h]
                if data.get('deleteFiles') == 'true':
                    shutil.rmtree(t['save_path'], ignore_errors=True)
        return ''

    # trial helpers ---------------------------------------------------------
    def write_payload(self, h, contents, fraction=1.0):
        t = self.torrents[h]
        done = 0
        for f in t['files']:
            if f['padding']:
                continue
            target = Path(t['save_path'], *f['path'].split('/'))
            target.parent.mkdir(parents=True, exist_ok=True)
            blob = contents[f['path']]
            part = blob[:int(len(blob) * fraction)]
            target.write_bytes(part)
            done += len(part)
        t['downloaded'] = t['completed'] = done
        t['progress'] = done / t['total_size']
        if t['progress'] >= 1 and t['state'] == 'downloading':
            t['state'] = 'uploading'

    def restart_losing(self, h):
        """Client restarted and lost the torrent; files stay on disk."""
        del self.torrents[h]


def make_torrent(files, name):
    """files: {path inside the torrent folder: bytes}. Returns .torrent bytes, infohash
    and the payload keyed by the paths parse_torrent reports (folder name included)."""
    info = {'name': name, 'piece length': 16384, 'pieces': b'\0' * 20,
            'files': [{'length': len(data), 'path': path.split('/')} for path, data in files.items()]}
    raw = acq.bencode({'announce': 'https://tracker.example/announce', 'info': info})
    return raw, acq.parse_torrent(raw)['infohash_v1'], {f'{name}/{k}': v for k, v in files.items()}


def single_file_torrent(name, data):
    """A one-file torrent, the only kind the operator loop accepts without staff payload review."""
    raw = acq.bencode({'announce': 'https://tracker.example/announce',
                       'info': {'name': name, 'length': len(data), 'piece length': 16384, 'pieces': b'\0' * 20}})
    return raw, acq.parse_torrent(raw)['infohash_v1'], {name: data}


def granted(reviewer, basis='Publisher license (synthetic)'):
    entry = acq.permission_entry('granted', basis, 'https://publisher.example/terms', reviewer, '2026-11-19T00:00:00Z')
    return {k: dict(entry) for k in acq.PERMISSION_FIELDS}
