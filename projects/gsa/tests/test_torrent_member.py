import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import acquire
import gsa
import pipeline
from test_acquire import torrent


class Client:
    def __init__(self, row, files):
        self.row, self.files = row, files
        self.calls = []

    def call(self, endpoint, data=None):
        self.calls.append((endpoint, data))
        if endpoint.startswith('torrents/info?'):
            return [self.row] if self.row else []
        if endpoint.startswith('torrents/files?'):
            return self.files
        if endpoint == 'torrents/filePrio':
            ids = {int(i) for i in data['id'].split('|')}
            for file in self.files:
                if file['index'] in ids:
                    file['priority'] = data['priority']
        elif endpoint != 'torrents/stop':
            raise AssertionError(endpoint)


class SelectedMemberTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name).resolve()
        self.db = gsa.connect(self.home)
        self.addCleanup(self.db.close)
        pipeline.migrate(self.db)
        gsa.ingest(self.db, [dict(row_id='1', title='Test')], 'test', 'test')
        self.body = b'%PDF-1.7\nsmall test file'
        self.md5 = hashlib.md5(self.body).hexdigest()
        data, _ = torrent([(self.md5, len(self.body)), ('other.pdf', 10**9)], name='collection')
        self.file = self.home / 'collection.torrent'
        self.file.write_bytes(data)
        self.key = acquire.parse_torrent(data)['infohash_v1']
        root = self.home / 'incomplete' / self.key
        member = 'collection/' + self.md5
        self.path = root / member
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(self.body)
        self.review = dict(infohash=self.key, torrent_member=member, member_md5=self.md5, filename='Test.pdf')
        pipeline.save(self.db, 1, {'review': self.review}, 'source_review')
        self.config = dict(torrent_acquisition_approved=True, max_file_bytes=1000, disk_budget_bytes=1<<17, reserve_bytes=1)
        self.evidence = self.home / 'evidence.json'
        self.evidence.write_text('{}')
        row = dict(hash=self.key, state='stoppedDL', save_path=str(root), total_size=10**9 + len(self.body))
        self.client = Client(row, [dict(index=5, name=member, size=len(self.body), priority=0, progress=1),
                                   dict(index=8, name='collection/other.pdf', size=10**9, priority=1, progress=0)])

    def run_loop(self, prepare=False):
        with patch('pipeline.rollout.guard', return_value=[]), patch('pipeline.rollout.Client', return_value=self.client):
            return pipeline.torrent_loop(self.db, 1, self.home, self.config, self.evidence, self.file, prepare)

    def test_prepare_and_stage_only_the_selected_file(self):
        self.assertEqual(self.run_loop(True)['action'], 'prepared')
        self.assertEqual([f['priority'] for f in self.client.files], [1, 0])
        self.client.row['state'] = 'stalledUP'
        self.assertEqual(self.run_loop()['action'], 'complete')
        candidate = Path(pipeline.get(self.db, 1)[1]['candidate'])
        self.assertEqual(candidate.parent, self.home / 'candidates')
        self.assertEqual(candidate.read_bytes(), self.body)
        self.assertEqual(candidate.suffix, '.pdf')

    def test_numeric_member_requires_bound_mapping(self):
        import torrent_member
        data, _ = torrent([('7465862', len(self.body))], name='collection')
        meta = acquire.parse_torrent(data)
        review = dict(infohash=meta['infohash_v1'], torrent_member='collection/7465862',
                      member_md5=self.md5, filename='Test.pdf', source_url='https://catalog.example/book')
        with self.assertRaises(ValueError):
            torrent_member.inspect(meta, review)
        review['member_mapping'] = dict(torrent_member=review['torrent_member'], member_md5=self.md5,
                                       catalog_url=review['source_url'], evidence='Catalog server path')
        self.assertIn(review['torrent_member'], torrent_member.inspect(meta, review)[0])
        review['member_mapping']['member_md5'] = '0' * 32
        with self.assertRaises(ValueError):
            torrent_member.inspect(meta, review)

    def test_prepare_requires_collection_in_client(self):
        self.client.row = None
        with self.assertRaisesRegex(ValueError, 'Add the reviewed collection'):
            self.run_loop(True)
        self.assertNotIn('torrent_job', pipeline.get(self.db, 1)[1])

    def test_active_or_drifted_selection_is_stopped(self):
        self.client.row['state'] = 'downloading'
        with self.assertRaisesRegex(ValueError, 'Stop the collection'):
            self.run_loop(True)
        with self.assertRaisesRegex(ValueError, 'only the reviewed'):
            self.run_loop()
        self.assertEqual(self.client.calls[-1][0], 'torrents/stop')
        self.assertFalse(any(c[0]=='torrents/filePrio' for c in self.client.calls))

    def test_checksum_mismatch_cannot_stage(self):
        self.run_loop(True)
        self.path.write_bytes(self.body[:-1] + b'?')
        self.client.row['state'] = 'stalledUP'
        with self.assertRaisesRegex(ValueError, 'MD5'):
            self.run_loop()
        self.assertEqual(list((self.home / 'candidates').iterdir()), [])

    def test_boundary_pieces_must_fit(self):
        self.config['disk_budget_bytes'] = 2000
        with self.assertRaisesRegex(ValueError, 'staging budget'):
            self.run_loop(True)

    def test_refuses_renamed_paths_and_external_temp_directory(self):
        self.client.files[0]['name'] = 'renamed.pdf'
        with self.assertRaisesRegex(ValueError, 'file list differs'):
            self.run_loop(True)
        self.client.row['download_path'] = '/tmp'
        with self.assertRaisesRegex(ValueError, 'Temporary download path'):
            self.run_loop(True)
