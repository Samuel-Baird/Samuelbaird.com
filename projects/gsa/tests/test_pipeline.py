import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gsa
import pipeline as p

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.db = gsa.connect(self.home)
        p.migrate(self.db)
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def test_poll_pages_and_overlap_replay(self):
        class API:
            def __init__(self): self.calls = []
            def call(self, method, url, params):
                self.calls.append(dict(params))
                sid = 'b' if params.get('pageToken') else 'a'
                return dict(responses=[{'responseId': sid, 'answers': {'q': {'textAnswers': {'answers': [{'value': 'Book'}]}}}}], **({} if sid == 'b' else {'nextPageToken': 'next'}))
        api = API()
        config = dict(intake_approved=True, form_id='form', question_map={'title': 'q'})
        self.assertEqual(p.poll(self.db, api, config), 2)
        self.assertEqual(p.poll(self.db, api, config), 0)
        self.assertTrue(api.calls[2]['filter'].startswith('timestamp >= '))
        self.assertEqual(self.db.execute('SELECT count(*) FROM works').fetchone()[0], 1)
    def test_failed_second_page_keeps_checkpoint(self):
        class API:
            def call(self, method, url, params):
                if params.get('pageToken'): raise OSError('offline')
                return {'responses': [], 'nextPageToken': 'next'}
        with self.assertRaises(OSError):
            p.poll(self.db, API(), dict(intake_approved=True, form_id='f', question_map={'title':'q'}))
        self.assertEqual(self.db.execute('SELECT count(*) FROM checkpoints').fetchone()[0], 0)
    def test_edition_conflicts_and_missing_evidence(self):
        requested = dict(title='A Book', author='Smith', edition='2', isbn='123')
        self.assertEqual(p.compare(requested, dict(requested)), 'exact')
        self.assertEqual(p.compare(requested, dict(requested, edition='1')), 'ambiguous')
        self.assertEqual(p.compare(requested, {'title':'A Book'}), 'ambiguous')
        self.assertEqual(p.compare(requested, {'title':'Another'}), 'unrelated')
    def seed(self):
        gsa.ingest(self.db, [{'row_id':'1', 'title':'Book'}], 'csv:test', 'test')
    def test_review_requires_both_permissions(self):
        self.seed()
        path = self.home / 'review.json'
        path.write_text(json.dumps(dict(reviewer='staff', source_url='https://example.com/book', permission_evidence='license', matched_work='Book', filename='Book.pdf', destination='folder', changelog_text='dated entry', download_permitted=True)))
        with self.assertRaisesRegex(ValueError, 'Separate'):
            p.review(self.db, 1, path, {'reviewers':['staff'], 'destination_ids':['folder']})
    def test_scanner_failure_never_validates(self):
        self.seed()
        path = self.home / 'candidates' / '1.pdf'
        path.write_bytes(b'%PDF-1.7\n')
        p.save(self.db, 1, {'candidate':str(path)}, 'test')
        with patch('pipeline.subprocess.run', side_effect=FileNotFoundError('scanner')):
            with self.assertRaises(FileNotFoundError):
                p.validate_file(self.db, 1, {'scanner_command':['missing-scanner'], 'max_file_bytes':1024})
        self.assertNotIn('validation', p.get(self.db, 1)[1])
    def test_publish_requires_approval_before_network(self):
        self.seed()
        with self.assertRaisesRegex(ValueError, 'Staff approval required'):
            p.publish(self.db, 1, None, {'publication_approved':True})
    def test_approval_rejects_changed_file(self):
        self.seed()
        candidate = self.home / 'candidates' / '1.pdf'
        candidate.write_bytes(b'changed')
        p.save(self.db, 1, {'candidate':str(candidate), 'sha256':'old', 'validation':{'sha256':'old'}}, 'test')
        approval = self.home / 'approval.json'
        approval.write_text(json.dumps({'reviewer':'staff','sha256':'old'}))
        with self.assertRaisesRegex(ValueError, 'validated file hash'):
            p.approve(self.db, 1, approval, {'reviewers':['staff']})

if __name__ == '__main__': unittest.main()
