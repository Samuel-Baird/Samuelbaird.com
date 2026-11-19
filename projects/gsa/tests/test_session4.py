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
                    p.torrent_loop(None, 1, Path(tmp), {}, evidence, None)
                client.assert_not_called()

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
            config['scanner_command'] = ['/usr/bin/true']
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
            for error in ('upload interrupted', 'lost changelog'):
                with self.assertRaisesRegex(ConnectionError, error):
                    p.publish(db, 1, api, config)
            p.publish(db, 1, api, config)
            self.assertEqual((api.uploads, api.edits), (1, 1))
            self.assertEqual(p.get(db, 1)[0]['status'], 'complete')
