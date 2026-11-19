import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import acquire as a

CONFIG = {'max_file_bytes': 1000, 'disk_budget_bytes': 5000, 'reserve_bytes': 2000}


def torrent(files=None, name='Lastname, Title', **meta):
    info = {'name': name, 'piece length': 16384, 'pieces': b'\0' * 20}
    if files is None:
        info['name'] = name + '.pdf'
        info['length'] = 500
    else:
        info['files'] = [dict({'length': n, 'path': p.split('/')}, **extra) for p, n, *rest in files
                         for extra in [rest[0] if rest else {}]]
    data = dict({'announce': 'https://tracker.example/announce', 'info': info}, **meta)
    return a.bencode(data), info


class BencodeTests(unittest.TestCase):
    def test_roundtrip_and_strictness(self):
        value = {'a': [1, -2, b'x'], 'b': {'c': 0}}
        self.assertEqual(a.bdecode(a.bencode(value)), {b'a': [1, -2, b'x'], b'b': {b'c': 0}})
        for bad in (b'i01e', b'i-0e', b'ie', b'03:abc', b'5:abc', b'd1:bi1e1:ai2ee', b'i1ei2e', b'l', b'x', b'd1:ai1e1:ai2ee'):
            with self.subTest(bad=bad), self.assertRaises(a.BencodeError):
                a.bdecode(bad)

    def test_infohash_is_sha1_of_raw_info(self):
        data, info = torrent()
        parsed = a.parse_torrent(data)
        self.assertEqual(parsed['infohash_v1'], hashlib.sha1(a.bencode(info)).hexdigest())
        self.assertEqual(parsed['files'], [{'path': 'Lastname, Title.pdf', 'length': 500, 'padding': False}])
        self.assertEqual(parsed['trackers'], ['https://tracker.example/announce'])

    def test_multifile_padding_and_v2(self):
        data, _ = torrent([('book.pdf', 400), ('.pad/0', 100, {'attr': 'p'})])
        parsed = a.parse_torrent(data)
        self.assertEqual(parsed['total_bytes'], 400)
        self.assertEqual(parsed['files'][0]['path'], 'Lastname, Title/book.pdf')
        v2 = a.bencode({'info': {'name': 'x', 'meta version': 2, 'piece length': 16384,
                                 'file tree': {'x.pdf': {'': {'length': 9, 'pieces root': b'\0' * 32}}}}})
        parsed = a.parse_torrent(v2)
        self.assertIsNone(parsed['infohash_v1'])
        self.assertEqual(len(parsed['infohash_v2']), 64)
        self.assertEqual(parsed['files'][0]['path'], 'x.pdf')

    def test_rejects_missing_info(self):
        with self.assertRaises(a.BencodeError):
            a.parse_torrent(a.bencode({'announce': 'x'}))


class PayloadTests(unittest.TestCase):
    def review(self, files, **kw):
        data, _ = torrent(files)
        return a.review_payload(a.parse_torrent(data), CONFIG, **kw)

    def test_single_pdf_goes_to_permission_check_not_approval(self):
        data, _ = torrent()
        result = a.review_payload(a.parse_torrent(data), CONFIG)
        self.assertEqual(result['route'], 'permission_check')
        self.assertEqual(result['flags'], [])

    def test_mixed_bundle_and_multi_work_route_to_staff(self):
        result = self.review([('a.pdf', 10), ('b.pdf', 10), ('talk.mp3', 10)])
        self.assertEqual(result['route'], 'staff_review')
        self.assertTrue(any(f.startswith('mixed_bundle') for f in result['flags']))
        self.assertTrue(any(f.startswith('multi_work_payload') for f in result['flags']))

    def test_unexpected_sidecar_and_ebook_types_flagged(self):
        result = self.review([('a.pdf', 10), ('cover.jpg', 10), ('a.epub', 10), ('notes.xyz', 10)])
        self.assertEqual(result['route'], 'staff_review')
        joined = ' '.join(result['flags'])
        for word in ('sidecar_file_would_be_shared', 'non_pdf_ebook', 'unexpected_file_type'):
            self.assertIn(word, joined)

    def test_executables_unsafe_paths_and_oversize_block(self):
        self.assertEqual(self.review([('a.pdf', 10), ('setup.exe', 10)])['route'], 'blocked')
        self.assertEqual(self.review([('../evil.pdf', 10)])['route'], 'blocked')
        self.assertEqual(self.review([('a.pdf', 1001)])['route'], 'blocked')
        self.assertEqual(self.review([('notes.txt', 10)])['route'], 'blocked')  # no content file

    def test_infohash_must_match_reviewed_record(self):
        result = self.review([('a.pdf', 10)], expected_infohash='0' * 40)
        self.assertEqual(result['route'], 'blocked')

    def test_cli_inspects_local_file_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'x.torrent'
            path.write_bytes(torrent()[0])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = a.main(['inspect-torrent', str(path)])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out.getvalue())['route'], 'permission_check')


def granted(**kw):
    return a.permission_entry('granted', kw.get('basis', 'CC BY 4.0 notice on publisher page'),
                              'https://publisher.example/terms', 'staff-a', '2026-11-19T00:00:00Z')


class PermissionTests(unittest.TestCase):
    def test_all_three_required_and_separate(self):
        record = {f: granted() for f in a.PERMISSION_FIELDS}
        result = a.evaluate_permissions(record, reviewers=['staff-a'])
        self.assertTrue(result['may_download_torrent'] and result['may_upload_to_gsa'])
        del record['peer_sharing']
        result = a.evaluate_permissions(record)
        self.assertTrue(result['may_download_direct'])
        self.assertFalse(result['may_download_torrent'])
        self.assertFalse(result['may_seed_after_completion'])
        self.assertTrue(result['may_upload_to_gsa'])

    def test_unknown_truthy_and_missing_provenance_block(self):
        for bad in ({'status': 'unknown'}, {'status': True}, {'status': 'yes'},
                    dict(granted(), basis=''), dict(granted(), recorded_by=None), None):
            with self.subTest(bad=bad):
                record = {f: granted() for f in a.PERMISSION_FIELDS}
                record['gsa_upload'] = bad
                result = a.evaluate_permissions(record)
                self.assertFalse(result['may_upload_to_gsa'])
                self.assertTrue(result['may_download_torrent'])

    def test_unapproved_recorder_blocks(self):
        record = {f: granted() for f in a.PERMISSION_FIELDS}
        self.assertFalse(a.evaluate_permissions(record, reviewers=['other'])['may_download_direct'])

    def test_empty_record_blocks_everything(self):
        result = a.evaluate_permissions({})
        self.assertFalse(any(v for k, v in result.items() if k.startswith('may_')))


class DiskTests(unittest.TestCase):
    def test_limits(self):
        self.assertTrue(a.check_disk([500], staged=0, free=10_000, config=CONFIG)['ok'])
        self.assertIn('file_too_large', a.check_disk([1001], 0, 10_000, CONFIG)['problems'][0])
        self.assertIn('staging_budget', a.check_disk([900], 4500, 10_000, CONFIG)['problems'][0])
        self.assertIn('free_space_reserve', a.check_disk([900], 0, 2500, CONFIG)['problems'][0])
        # A resumed partial already on disk is not counted twice.
        self.assertTrue(a.check_disk([900], 4500, 10_000, CONFIG, already_present=600)['ok'])

    def test_staged_bytes_counts_worker_folders(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            for folder in ('incomplete', 'candidates', 'receipts'):
                (home / folder).mkdir()
                (home / folder / 'f').write_bytes(b'x' * 10)
            self.assertEqual(a.staged_bytes(home), 20)
            self.assertTrue(a.disk_check(home, [1], dict(CONFIG, reserve_bytes=0))['ok'])


HASH = 'ab' * 20
MIN = 60


def snap(state='downloading', downloaded=0, size=1000, progress=None, **kw):
    return dict(hash=HASH, state=state, downloaded=downloaded, completed=downloaded, total_size=size,
                progress=progress if progress is not None else downloaded / size, num_seeds=0,
                availability=0.5, added_on=0, **kw)


class StallTests(unittest.TestCase):
    def setUp(self):
        self.job = a.new_job(HASH, now=0, expected_bytes=1000)
        self.policy = {'stall_minutes': 30, 'metadata_minutes': 15, 'max_retries': 2, 'retry_backoff_minutes': 10}

    def step(self, snapshot, minute):
        return a.assess(self.job, snapshot, minute * MIN, self.policy, CONFIG)['action']

    def test_progress_resets_stall_clock(self):
        self.assertEqual(self.step(snap(downloaded=100), 20), 'wait')
        self.assertEqual(self.step(snap(downloaded=200), 45), 'wait')
        self.assertEqual(self.step(snap(downloaded=200), 70), 'wait')
        self.assertEqual(self.step(snap('stalledDL', downloaded=200), 76), 'retry')

    def test_bounded_retries_then_pause_and_review(self):
        self.assertEqual(self.step(snap(downloaded=10), 0), 'wait')
        self.assertEqual(self.step(snap(downloaded=10), 31), 'retry')
        self.assertEqual(self.step(snap(downloaded=10), 62), 'retry')
        self.assertEqual(self.step(snap(downloaded=10), 93), 'pause_and_review')
        self.assertEqual(self.job['status'], 'review')
        # Once in review, later snapshots never restart it.
        self.assertEqual(self.step(snap(downloaded=900), 200), 'route_to_review')

    def test_metadata_never_arrives(self):
        meta = snap('metaDL', size=0, progress=0)
        self.assertEqual(self.step(meta, 10), 'wait')
        self.assertEqual(self.step(meta, 16), 'retry')
        self.assertEqual(self.step(meta, 20), 'wait')       # within new window
        self.assertEqual(self.step(meta, 32), 'retry')
        self.assertEqual(self.step(meta, 48), 'pause_and_review')

    def test_error_state_retries_with_backoff(self):
        self.assertEqual(self.step(snap('error'), 1), 'retry')
        self.assertEqual(self.step(snap('error'), 5), 'wait')  # backoff
        self.assertEqual(self.step(snap('error'), 12), 'retry')
        self.assertEqual(self.step(snap('error'), 30), 'pause_and_review')

    def test_complete_and_guard_paused(self):
        self.assertEqual(self.step(snap('stalledUP', downloaded=1000, progress=1), 5), 'complete')
        job = a.new_job(HASH, 0, 1000)
        self.assertEqual(a.assess(job, snap('stoppedDL', downloaded=5), 60)['action'], 'route_to_review')

    def test_payload_or_hash_change_routes_to_review(self):
        self.assertEqual(self.step(snap(size=2000), 1), 'pause_and_review')
        job = a.new_job('cd' * 20, 0)
        self.assertEqual(a.assess(job, snap(), 60)['action'], 'pause_and_review')

    def test_oversize_against_budget(self):
        job = a.new_job(HASH, 0)
        self.assertEqual(a.assess(job, snap(size=9999), 60, config=CONFIG)['action'], 'pause_and_review')

    def test_checking_waits_and_unknown_state_reviews(self):
        self.assertEqual(self.step(snap('checkingResumeData'), 1), 'wait')
        self.assertEqual(self.step(snap('somethingNew'), 2), 'pause_and_review')


class RecoveryTests(unittest.TestCase):
    def test_missing_torrent_with_partial_file_readds_paused(self):
        job = a.new_job(HASH, 0, 1000)
        job['best_downloaded'] = 700
        decision = a.recover(job, None, partial_bytes=600, now=100)
        self.assertEqual(decision['action'], 'readd_paused')
        self.assertIn('600 bytes', decision['reason'])
        self.assertEqual(job['best_downloaded'], 600)

    def test_missing_files_with_partial_rechecks(self):
        job = a.new_job(HASH, 0, 1000)
        self.assertEqual(a.recover(job, snap('missingFiles'), 300, 100)['action'], 'recheck')

    def test_regressed_progress_after_restart_is_not_a_stall(self):
        job = a.new_job(HASH, 0, 1000)
        a.assess(job, snap(downloaded=800), 60)
        decision = a.recover(job, snap(downloaded=500), 500, now=60 * MIN)
        self.assertEqual(decision['action'], 'wait')
        self.assertEqual(job['best_downloaded'], 500)

    def test_recovery_retries_are_bounded(self):
        job = a.new_job(HASH, 0, 1000)
        policy = {'max_retries': 1}
        self.assertEqual(a.recover(job, None, 0, 10, policy)['action'], 'readd_paused')
        self.assertEqual(a.recover(job, None, 0, 20, policy)['action'], 'route_to_review')

    def test_completed_job_stays_complete(self):
        job = a.new_job(HASH, 0, 1000)
        a.assess(job, snap('uploading', downloaded=1000, progress=1), 60)
        self.assertEqual(a.recover(job, None, 1000, 120)['action'], 'complete')


if __name__ == '__main__':
    unittest.main()
