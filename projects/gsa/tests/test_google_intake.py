import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import google_intake as intake

class IntakeReadinessTests(unittest.TestCase):
    def test_mapping_checks_actual_question_ids(self):
        schema = {'items': [{'title': 'Title', 'questionItem': {'question': {'questionId': 'q', 'textQuestion': {}}}}]}
        intake.validate_mapping(schema, {'title': 'q'})
        with self.assertRaises(ValueError):
            intake.validate_mapping(schema, {'title': 'missing'})
        with self.assertRaises(ValueError):
            intake.validate_mapping(schema, {'author': 'q'})

    def test_access_failure_does_not_authorize_or_skip_other_checks(self):
        class API:
            def __init__(self): self.calls = []
            def call(self, method, url, **kwargs):
                self.calls.append(method)
                raise PermissionError('private detail')
        api = API()
        config = dict(form_id='f', toc_spreadsheet_id='s', changelog_document_id='d')
        report = intake.readiness(api, config)
        self.assertEqual(api.calls, ['GET'] * 3)
        self.assertFalse(report['intake_approved'])
        self.assertNotIn('private detail', str(report))
        self.assertNotIn('intake_approved', config)

    def test_changelog_selects_nested_configured_tab(self):
        body = {'content': []}
        doc = {'tabs': [{'tabProperties': {'tabId': 'other'}, 'childTabs': [
            {'tabProperties': {'tabId': 'wanted'}, 'documentTab': {'body': body}}]}]}
        self.assertIs(intake.document_body(doc, 'wanted'), body)
        with self.assertRaisesRegex(ValueError, 'not found'):
            intake.document_body(doc, 'missing')

    def test_freeform_poll_replay_and_failed_page_are_atomic(self):
        import tempfile
        import gsa
        import json
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as folder:
            db = gsa.connect(Path(folder))
            config = {'intake_approved': True, 'form_id': 'synthetic', 'form_question_ids':
                      {'materials': 'm', 'topics': 't', 'quality_of_life': 'q', 'bugs': 'b'}}
            page = {'responses': [{'responseId': 'r', 'answers': {'b': {'textAnswers': {'answers': [{'value': 'Broken link'}]}}}}]}
            api = Mock()
            api.call.return_value = page
            self.assertEqual(intake.poll_freeform(db, api, config), 1)
            self.assertEqual(intake.poll_freeform(db, api, config), 0)
            self.assertEqual(db.execute('SELECT count(*) FROM works').fetchone()[0], 0)
            row = db.execute('SELECT answers,status FROM form_requests').fetchone()
            self.assertEqual(json.loads(row[0])['bugs'], 'Broken link')
            self.assertEqual(row[1], 'needs_review')
            before = db.execute('SELECT value FROM checkpoints').fetchone()[0]
            api.call.side_effect = [{'responses': [], 'nextPageToken': 'next'}, OSError('offline')]
            with self.assertRaises(OSError): intake.poll_freeform(db, api, config)
            self.assertEqual(db.execute('SELECT value FROM checkpoints').fetchone()[0], before)
            api.call.side_effect = None
            api.call.return_value = {'responses': [{'responseId': 'r', 'answers': {}}]}
            with self.assertRaisesRegex(ValueError, 'Changed response'): intake.poll_freeform(db, api, config)
            self.assertEqual(db.execute('SELECT value FROM checkpoints').fetchone()[0], before)
            db.close()
