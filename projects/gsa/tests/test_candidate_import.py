import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import candidate_import as ci
import gsa
import pipeline


class CandidateImportTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name).resolve()
        self.home = root / 'home'
        self.downloads = root / 'Downloads'
        self.downloads.mkdir()
        self.db = gsa.connect(self.home)
        self.addCleanup(self.db.close)
        pipeline.migrate(self.db)
        gsa.ingest(self.db, [dict(row_id='1', title='Test Book')], 'test', 'test')
        self.body = b'%PDF-1.7\n' + b'synthetic browser download\n' * 40
        self.md5 = hashlib.md5(self.body).hexdigest()
        self.download = self.downloads / 'Test Book.pdf'
        self.download.write_bytes(self.body)
        self.config = dict(reviewers=['staff'], destination_ids=['folder'],
                           max_file_bytes=10_000, disk_budget_bytes=100_000, reserve_bytes=1)
        self.write_review()
        self.evidence = root / 'source-record.json'
        self.write_evidence()

    def write_review(self, **changes):
        review = dict(reviewer='staff', source_url='https://catalog.example/md5/' + self.md5,
                      matched_work='Test Book (2001)', filename='Test Book.pdf', destination='folder',
                      changelog_text='dated entry', source_md5=self.md5, source_bytes=len(self.body),
                      source_partners=['Slow Partner Server #1'])
        review.update(changes)
        review = {k: v for k, v in review.items() if v is not None}
        path = self.home / 'review.json'
        path.write_text(json.dumps(review))
        pipeline.review(self.db, 1, path, self.config)

    def write_evidence(self, **changes):
        data = dict(schema=ci.SCHEMA, work_id=1, catalog_url='https://catalog.example/md5/' + self.md5,
                    source='Slow Partner Server #1', md5=self.md5, bytes=len(self.body),
                    matched_work='Test Book (2001)', filename='Test Book.pdf', recorded_by='operator',
                    downloaded_at='2026-11-19T20:00:00Z')
        data.update(changes)
        fd = os.open(self.evidence, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f)

    def run_import(self, file=None):
        return ci.import_candidate(self.db, 1, self.home, self.config, file or self.download, self.evidence)

    def record(self):
        return pipeline.get(self.db, 1)[1]

    def assert_nothing_staged(self):
        self.assertEqual(list((self.home / 'candidates').iterdir()), [])
        self.assertEqual(list((self.home / 'incomplete').iterdir()), [])
        self.assertNotIn('candidates', self.record())

    def test_passing_import_registers_immutable_copy(self):
        result = self.run_import()
        self.assertEqual(result['action'], 'imported')
        candidate = Path(result['candidate'])
        self.assertEqual(candidate.parent, self.home / 'candidates')
        self.assertEqual(candidate.read_bytes(), self.body)
        self.assertEqual(stat.S_IMODE(candidate.stat().st_mode), 0o400)
        self.assertEqual(self.download.read_bytes(), self.body)  # original preserved
        record = self.record()
        self.assertEqual(record['candidate'], str(candidate))
        entry = record['candidates'][-1]
        self.assertEqual(entry['origin'], 'browser:https://catalog.example/md5/' + self.md5)
        self.assertEqual(entry['evidence']['sha256'], hashlib.sha256(self.evidence.read_bytes()).hexdigest())
        self.assertNotIn('validation', record)  # validation stays a separate step
        self.assertEqual(list((self.home / 'incomplete').iterdir()), [])

    def test_imported_candidate_flows_into_validation(self):
        self.run_import()
        report = {'automated_verdict': 'pass', 'automated_failures': [], 'automated_checks': {},
                  'sha256': hashlib.sha256(self.body).hexdigest()}
        with patch('pipeline.validation.validate', return_value=report), \
             patch('pipeline.validation.rank', side_effect=lambda r: r):
            best = pipeline.validate_file(self.db, 1, self.config)
        self.assertEqual(best['path'], self.record()['candidate'])

    def test_incomplete_input_is_rejected(self):
        self.download.write_bytes(self.body[:-10])
        with self.assertRaisesRegex(ValueError, 'bytes; the source review expects'):
            self.run_import()
        partial = self.downloads / 'Test Book.pdf.crdownload'
        partial.write_bytes(self.body)
        with self.assertRaisesRegex(ValueError, 'partial'):
            self.run_import(partial)
        self.download.write_bytes(self.body)
        with self.assertRaisesRegex(ValueError, 'in progress'):
            self.run_import()  # Chrome still holds a sibling .crdownload
        self.assert_nothing_staged()

    def test_checksum_mismatch_is_rejected(self):
        self.download.write_bytes(self.body[:-1] + b'?')
        with self.assertRaisesRegex(ValueError, 'MD5 differs'):
            self.run_import()
        self.assert_nothing_staged()

    def test_wrong_file_type_and_unsafe_paths(self):
        self.download.write_bytes(b'<html>' + self.body[6:])
        with self.assertRaisesRegex(ValueError, 'not a PDF'):
            self.run_import()
        self.download.write_bytes(self.body)
        link = self.downloads / 'link.pdf'
        link.symlink_to(self.download)
        with self.assertRaisesRegex(ValueError, 'regular file'):
            self.run_import(link)
        inside = self.home / 'receipts' / 'Test Book.pdf'
        inside.write_bytes(self.body)
        with self.assertRaisesRegex(ValueError, 'outside the worker home'):
            self.run_import(inside)
        self.assert_nothing_staged()

    def test_source_record_cannot_replace_reviewed_identity(self):
        other = hashlib.md5(b'other').hexdigest()
        for change, message in ((dict(md5=other), 'md5 differs'),
                                (dict(matched_work='Another Book'), 'matched_work differs'),
                                (dict(work_id=2), 'another work'),
                                (dict(source='Unlisted mirror'), 'not listed')):
            with self.subTest(change=change):
                self.write_evidence(**change)
                with self.assertRaisesRegex(ValueError, message):
                    self.run_import()
        self.write_evidence()
        os.chmod(self.evidence, 0o644)
        with self.assertRaisesRegex(ValueError, '0600'):
            self.run_import()
        self.assert_nothing_staged()

    def test_review_without_source_checksum_is_refused(self):
        self.write_review(source_md5=None, source_bytes=None)
        with self.assertRaisesRegex(ValueError, 'reviewed source change'):
            self.run_import()
        review = dict(reviewer='staff', source_url='https://catalog.example/x', matched_work='Test Book (2001)',
                      filename='Test Book.pdf', destination='folder', changelog_text='entry', source_md5='BAD')
        path = self.home / 'bad-review.json'
        path.write_text(json.dumps(review))
        with self.assertRaisesRegex(ValueError, 'source_md5'):
            pipeline.review(self.db, 1, path, self.config)

    def test_insufficient_disk_space(self):
        with patch('acquire.shutil.disk_usage') as usage:
            usage.return_value.free = len(self.body)
            self.config['reserve_bytes'] = 100
            with self.assertRaisesRegex(ValueError, 'free_space_reserve'):
                self.run_import()
        self.config.update(reserve_bytes=1, disk_budget_bytes=len(self.body) - 1)
        with self.assertRaisesRegex(ValueError, 'staging_budget_exceeded'):
            self.run_import()
        self.config.update(disk_budget_bytes=100_000, max_file_bytes=10)
        with self.assertRaisesRegex(ValueError, 'file_too_large'):
            self.run_import()
        self.assert_nothing_staged()

    def test_duplicate_import_is_a_no_op(self):
        first = self.run_import()
        events = self.db.execute('SELECT count(*) FROM pipeline_events').fetchone()[0]
        second = self.run_import()
        self.assertEqual(second['action'], 'duplicate')
        self.assertEqual(second['candidate'], first['candidate'])
        self.assertEqual(len(self.record()['candidates']), 1)
        self.assertEqual(self.db.execute('SELECT count(*) FROM pipeline_events').fetchone()[0], events)

    def test_same_bytes_from_another_route_are_not_duplicated(self):
        earlier = self.home / 'candidates' / '1-torrent.pdf'
        earlier.write_bytes(self.body)
        record = self.record()
        record.update(candidate=str(earlier), candidates=[{'path': str(earlier), 'origin': 'torrent:x'}])
        pipeline.save(self.db, 1, record, 'test')
        self.assertEqual(self.run_import()['action'], 'duplicate')
        self.assertEqual(len(self.record()['candidates']), 1)

    def test_interrupted_copy_is_discarded_and_retried(self):
        stale = self.home / 'incomplete' / f'import-1-{self.md5}.part'
        stale.write_bytes(self.body[:20])  # killed process left a partial copy
        with patch('candidate_import.os.fsync', side_effect=OSError('disk error')):
            with self.assertRaises(OSError):
                self.run_import()
        self.assert_nothing_staged()
        self.assertEqual(self.run_import()['action'], 'imported')

    def test_interrupted_registration_is_recovered_once(self):
        with patch('pipeline.save', side_effect=RuntimeError('crash before registration')):
            with self.assertRaises(RuntimeError):
                self.run_import()
        dest = self.home / 'candidates' / f'1-browser-{self.md5}.pdf'
        self.assertTrue(dest.is_file())
        self.assertNotIn('candidates', self.record())  # not registered
        self.assertEqual(self.run_import()['action'], 'recovered')
        self.assertEqual(self.run_import()['action'], 'duplicate')
        self.assertEqual(len(self.record()['candidates']), 1)

    def test_tampered_unregistered_candidate_is_not_registered_or_overwritten(self):
        dest = self.home / 'candidates' / f'1-browser-{self.md5}.pdf'
        dest.write_bytes(self.body[:-1] + b'?')
        with self.assertRaisesRegex(ValueError, 'staff review'):
            self.run_import()
        self.assertEqual(dest.read_bytes(), self.body[:-1] + b'?')
        self.assertNotIn('candidates', self.record())

    def test_concurrent_changes_are_refused(self):
        original = ci.copy_verified

        def change_review(*args):
            original(*args)
            self.write_review(matched_work='Changed during import')
        with patch('candidate_import.copy_verified', side_effect=change_review):
            with self.assertRaisesRegex(ValueError, 'Source review changed'):
                self.run_import()
        self.assert_nothing_staged()
        self.write_review()

        def touch_source(*args):
            original(*args)
            os.utime(self.download, ns=(1, 1))
        with patch('candidate_import.copy_verified', side_effect=touch_source):
            with self.assertRaisesRegex(ValueError, 'changed during import'):
                self.run_import()
        self.assert_nothing_staged()

    def test_approval_cleared_only_when_candidate_changes(self):
        earlier = self.home / 'candidates' / '1-1.pdf'
        earlier.write_bytes(b'%PDF-1.4 earlier candidate')
        approval = {'reviewer': 'staff', 'sha256': 'old'}
        record = self.record()
        record.update(candidate=str(earlier), candidates=[{'path': str(earlier), 'origin': 'direct:x'}],
                      validation={'automated_verdict': 'pass'}, sha256='old', approval=approval,
                      reviewer_checks={'staff': approval})
        pipeline.save(self.db, 1, record, 'test')
        self.db.execute("UPDATE works SET status='awaiting_staff_approval' WHERE id=1")
        self.run_import()
        record = self.record()
        self.assertEqual([c['path'] for c in record['candidates']][0], str(earlier))  # prior kept
        self.assertEqual(len(record['candidates']), 2)
        for key in ('approval', 'reviewer_checks', 'validation'):
            self.assertNotIn(key, record)
        self.assertEqual(pipeline.get(self.db, 1)[0]['status'], 'needs_review')
        # A replay does not change the selected candidate, so it keeps a later approval.
        record.update(approval=approval, validation={'automated_verdict': 'pass'})
        pipeline.save(self.db, 1, record, 'test')
        self.assertEqual(self.run_import()['action'], 'duplicate')
        self.assertEqual(self.record()['approval'], approval)

    def test_upload_in_progress_blocks_import(self):
        record = self.record()
        record['upload_id'] = 'reserved'
        pipeline.save(self.db, 1, record, 'test')
        with self.assertRaisesRegex(ValueError, 'Upload already started'):
            self.run_import()


if __name__ == '__main__':
    unittest.main()
