import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gsa

class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.db = gsa.connect(self.home)
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def row(self, sid='1', **changes):
        return dict(row_id=sid, title='Example', author='Author', edition='2nd', **changes)
    def test_cross_source_duplicates_preserve_submissions_and_editions(self):
        gsa.ingest(self.db, [self.row()], 'csv:a', 'a')
        gsa.ingest(self.db, [self.row('r1')], 'mock-form:f', 'forms', 'checkpoint')
        row = self.row('2'); row['edition'] = '1st'
        gsa.ingest(self.db, [row], 'csv:a', 'a')
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM submissions').fetchone()[0], 3)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM works').fetchone()[0], 2)
    def test_replay_keeps_outcome_and_changed_response_rolls_back_checkpoint(self):
        gsa.ingest(self.db, [self.row()], 'f', 'b', 'old')
        gsa.sandbox_upload(self.db, 1)
        self.assertEqual(gsa.ingest(self.db, [self.row()], 'f', 'b', 'old'), 0)
        changed = self.row(); changed['title'] = 'Changed'
        with self.assertRaises(ValueError):
            gsa.ingest(self.db, [self.row('2'), changed], 'f', 'b', 'new')
        self.assertEqual(self.db.execute('SELECT value FROM checkpoints').fetchone()[0], 'old')
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM submissions').fetchone()[0], 1)
        self.assertEqual(self.db.execute('SELECT status FROM works').fetchone()[0], 'sandbox_complete')
    def test_invalid_batch_does_not_advance_checkpoint(self):
        with self.assertRaises(ValueError):
            gsa.ingest(self.db, [self.row(), {'row_id': '2', 'isbn': '123'}], 'f', 'b', 'new')
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM submissions').fetchone()[0], 0)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM checkpoints').fetchone()[0], 0)
    def test_crash_recovery_keeps_upload_receipt_and_changelog_idempotent(self):
        gsa.ingest(self.db, [self.row()], 'f', 'b')
        with self.assertRaises(ValueError):
            gsa.sandbox_upload(self.db, 1, True)
        first = self.db.execute('SELECT * FROM works').fetchone()
        self.assertIsNotNone(first['upload_receipt'])
        self.assertIsNone(first['changelog_receipt'])
        gsa.sandbox_upload(self.db, 1)
        completed = dict(self.db.execute('SELECT * FROM works').fetchone())
        gsa.sandbox_upload(self.db, 1)
        self.assertEqual(dict(self.db.execute('SELECT * FROM works').fetchone()), completed)
        self.assertEqual(completed['upload_receipt'], first['upload_receipt'])
    def test_manifest_does_not_invent_matches_or_verified_links(self):
        gsa.ingest(self.db, [self.row()], 'f', 'b')
        gsa.sandbox_upload(self.db, 1)
        out = self.home / 'manifest.csv'
        gsa.manifest(self.db, out)
        with out.open() as f:
            row = next(csv.DictReader(f))
        self.assertNotIn('permission', row)
        self.assertEqual(row['verified_drive_link'], '')
        self.assertEqual(row['matched_work'], '')
        self.assertEqual(out.stat().st_mode & 0o777, 0o600)
    def test_identifiers(self):
        self.assertEqual(gsa.validate({'isbn':'978-0-306-40615-7'})['isbn'], '9780306406157')
        self.assertEqual(gsa.validate({'doi':'https://doi.org/10.1234/EXAMPLE'})['doi'], '10.1234/example')
        with self.assertRaises(ValueError):
            gsa.validate({'isbn':'9780306406158'})

if __name__ == '__main__':
    unittest.main()
