"""Offline integration rehearsal with synthetic Forms, HTTPS, Drive and Docs."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gsa
import pipeline as p
from pdf_fixtures import text_pdf


class Services:
    def __init__(self, pdf):
        self.pdf = pdf
        self.uploads = self.edits = 0
        self.content = 'Today'

    def files(self, query):
        return []

    def call(self, method, url, params=None, body=None, **kwargs):
        if url.endswith('/responses'):
            return {'responses': [{'responseId': 'request', 'answers': {'q0': {
                'textAnswers': {'answers': [{'value': 'Can you find Book?'}]}}}}]}
        if url.endswith('/generateIds'):
            return {'ids': ['reserved']}
        if method == 'POST' and '/upload/' in url:
            assert self.pdf in body
            self.uploads += 1
            raise ConnectionError('upload interrupted after remote commit')
        if url == p.DRIVE + '/reserved':
            if not self.uploads:
                raise HTTPError(url, 404, 'missing', {}, None)
            if params.get('alt') == 'media':
                assert kwargs.get('stream_hash')
                return p.hashlib.sha256(self.pdf).hexdigest()
            return dict(id='reserved', name='Book.pdf', parents=['folder'], size=len(self.pdf),
                        md5Checksum=p.hashlib.md5(self.pdf).hexdigest())
        if url == p.DOCS + 'log':
            assert params == {'includeTabsContent': 'true'}
            body = {'content': [{'paragraph': {'elements': [
                {'startIndex': 1, 'textRun': {'content': self.content}}]}}]}
            return {'tabs': [{'tabProperties': {'tabId': 'updates'}, 'documentTab': {'body': body}}],
                    'revisionId': '1'}
        if url == p.DOCS + 'log:batchUpdate':
            assert body['requests'][0]['insertText']['location']['tabId'] == 'updates'
            self.content += body['requests'][0]['insertText']['text']
            self.edits += 1
            raise ConnectionError('lost changelog response')
        raise AssertionError(url)


class Sandbox(unittest.TestCase):
    def test_torrent_guard_precedes_client_and_work_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / 'evidence'
            evidence.write_text('{}')
            with patch.object(p.rollout, 'guard', return_value=['unsigned']), patch.object(p.rollout, 'Client') as client:
                with self.assertRaisesRegex(ValueError, 'unsigned'):
                    p.torrent_loop(None, 1, Path(tmp), {'torrent_acquisition_approved': True}, evidence, None)
                client.assert_not_called()
            with patch.object(p.rollout, 'guard') as guard:
                with self.assertRaisesRegex(ValueError, 'not approved torrent acquisition'):
                    p.torrent_loop(None, 1, Path(tmp), {}, evidence, None)
                guard.assert_not_called()

    def test_full_rehearsal(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            db = gsa.connect(home)
            self.addCleanup(db.close)
            p.migrate(db)
            api = Services(text_pdf())
            index = home / 'index'
            index.write_text('[{"title":"Book","edition":"1"}]')
            config = dict(intake_approved=True, form_id='sandbox', reviewers=['staff'],
                          form_question_ids={k: f'q{i}' for i, k in enumerate(
                              ('materials','topics','quality_of_life','bugs'))},
                          destination_ids=['folder'], archive_index=str(index),
                          source_hosts=['publisher.example'], max_file_bytes=100000,
                          disk_budget_bytes=200000, reserve_bytes=1, scanner_command=['/usr/bin/false'],
                          publication_approved=True, changelog_document_id='log', changelog_anchor='Today', changelog_tab_id='updates')
            file = home / 'packet'
            self.assertEqual(p.poll(db, api, config), 1)
            self.assertEqual(db.execute('SELECT count(*) FROM works').fetchone()[0], 0)
            file.write_text(json.dumps(dict(response_id='request', reviewer='staff',
                                works=[dict(row_id='1', title='Book', edition='2')])))
            p.triage(db, config, file)
            review = json.loads((Path(p.__file__).parent/'examples/review.json').read_text())
            review.update(reviewer='staff', filename='Book.pdf', destination='folder')
            for entry in review['permissions'].values():
                entry.update(status='granted', recorded_by='staff', recorded_at=p.stamp(),
                             basis='synthetic license', source='fixture')
            file.write_text(json.dumps(review))
            p.review(db, 1, file, config)
            response = io.BytesIO(api.pdf)
            response.headers = {'Content-Length': str(len(api.pdf))}
            with patch('pipeline.urllib.request.build_opener', return_value=Mock(open=Mock(return_value=response))):
                p.acquire(db, 1, home, config)
            with self.assertRaisesRegex(ValueError, 'malware_scan'):
                p.validate_file(db, 1, config)
            record = p.get(db, 1)[1]
            self.assertTrue(Path(record['candidates'][0]['quarantined_to']).exists())
            self.assertEqual(list((home / 'candidates').iterdir()), [])
            with self.assertRaisesRegex(ValueError, 'No candidate'):
                p.validate_file(db, 1, config)
            config['scanner_command'] = ['/usr/bin/true']
            response = io.BytesIO(api.pdf)
            response.headers = {'Content-Length': str(len(api.pdf))}
            with patch('pipeline.urllib.request.build_opener', return_value=Mock(open=Mock(return_value=response))):
                p.acquire(db, 1, home, config)
            report = p.validate_file(db, 1, config)
            approval = dict(reviewer='staff', destination='folder', sha256=report['sha256'])
            approval.update({k: True for k, _ in p.validation.STAFF_JUDGMENT})
            file.write_text(json.dumps(approval))
            self.assertEqual(p.archive_check(db, 1, api, config, 'folder')[0]['match'], 'ambiguous')
            with self.assertRaisesRegex(ValueError, 'Archive matches'):
                p.approve(db, 1, file, config)
            index.write_text('[]')  # Reviewer reconciled the synthetic index.
            p.archive_check(db, 1, api, config, 'folder')
            p.approve(db, 1, file, config)
            config['reviewers'].append('second')
            config['required_publication_reviewers'] = ['staff', 'second']
            p.archive_check(db, 1, api, config, 'folder')
            p.approve(db, 1, file, config)
            self.assertNotIn('approval', p.get(db, 1)[1])
            approval['reviewer'] = 'second'
            file.write_text(json.dumps(approval))
            p.approve(db, 1, file, config)
            for error in ('upload interrupted', 'lost changelog'):
                with self.assertRaisesRegex(ConnectionError, error):
                    p.publish(db, 1, api, config)
            p.publish(db, 1, api, config)
            self.assertEqual((api.uploads, api.edits), (1, 1))
            self.assertEqual(p.get(db, 1)[0]['status'], 'complete')


class Reconciled(unittest.TestCase):
    """Session 4 additions ported onto the merged pipeline: ranking, selection, edition resolution."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.db = gsa.connect(self.home)
        p.migrate(self.db)
        self.index = self.home / 'index'
        self.index.write_text('[{"title":"Book","author":"Smith","edition":"1"}]')
        self.config = dict(reviewers=['staff'], destination_ids=['folder'], archive_index=str(self.index),
                           source_hosts=['publisher.example'], max_file_bytes=10 ** 7, disk_budget_bytes=10 ** 8,
                           reserve_bytes=1, scanner_command=['/usr/bin/true'])
        gsa.ingest(self.db, [{'row_id': '1', 'title': 'Book', 'author': 'Smith', 'edition': '2'}], 'csv:t', 't')
        review = json.loads((Path(p.__file__).parent / 'examples/review.json').read_text())
        review.update(reviewer='staff', filename='Book.pdf', destination='folder')
        for entry in review['permissions'].values():
            entry.update(status='granted', recorded_by='staff', recorded_at=p.stamp(), basis='synthetic', source='fixture')
        self.file = self.home / 'packet'
        self.file.write_text(json.dumps(review))
        p.review(self.db, 1, self.file, self.config)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def acquire(self, data):
        response = io.BytesIO(data)
        response.headers = {'Content-Length': str(len(data))}
        with patch('pipeline.urllib.request.build_opener', return_value=Mock(open=Mock(return_value=response))):
            p.acquire(self.db, 1, self.home, self.config)

    def write(self, data):
        self.file.write_text(json.dumps(data))
        return self.file

    @unittest.skipUnless(all(p.shutil.which(t) for t in ('pdfinfo', 'pdffonts', 'pdfimages', 'qpdf')), 'poppler and qpdf required')
    def test_scan_outranks_ebook_conversion_and_selection_needs_reason(self):
        from pdf_fixtures import calibre_pdf, scan_pdf
        self.acquire(calibre_pdf())
        self.acquire(scan_pdf(pages=2, ppi=300))
        best = p.validate_file(self.db, 1, self.config)
        record = p.get(self.db, 1)[1]
        self.assertEqual([r['pdf']['classification']['class'] for r in record['candidate_reports']], ['scan', 'likely_ebook_conversion'])
        self.assertEqual(record['candidate'], best['path'])
        conversion = record['candidate_reports'][1]['sha256']
        with self.assertRaisesRegex(ValueError, 'reason'):
            p.select_candidate(self.db, 1, self.write({'reviewer': 'staff', 'sha256': conversion}), self.config)
        p.select_candidate(self.db, 1, self.write({'reviewer': 'staff', 'sha256': conversion, 'reason': 'Scan is missing pages'}), self.config)
        self.assertEqual(p.get(self.db, 1)[1]['sha256'], conversion)

    def test_ambiguous_edition_needs_named_resolution_from_each_reviewer(self):
        from pdf_fixtures import text_pdf
        self.acquire(text_pdf())
        with patch('validate.pdf_checks', return_value=({}, None)):
            report = p.validate_file(self.db, 1, self.config)
        api = Mock(files=Mock(return_value=[]))
        matches = p.archive_check(self.db, 1, api, self.config, 'folder')
        self.assertEqual([m['match'] for m in matches], ['ambiguous'])
        approval = dict(reviewer='staff', destination='folder', sha256=report['sha256'])
        approval.update({k: True for k, _ in p.validation.STAFF_JUDGMENT})
        with self.assertRaisesRegex(ValueError, 'Archive matches'):
            p.approve(self.db, 1, self.write(approval), self.config)
        with self.assertRaisesRegex(ValueError, 'Archive matches'):
            p.approve(self.db, 1, self.write(dict(approval, archive_resolution={'matches': [matches[0]['key']], 'reason': ' '})), self.config)
        p.approve(self.db, 1, self.write(dict(approval, archive_resolution={'matches': [matches[0]['key']], 'reason': 'Archive has the 1st edition'})), self.config)
        self.assertIn('approval', p.get(self.db, 1)[1])
