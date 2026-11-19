"""Run the intake command against a temporary queue and simulated Google responses."""
import fcntl
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pipeline


class IntakeStartup(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        config = self.home / 'config.json'
        config.write_text(json.dumps(dict(intake_approved=True, form_id='fixture',
            keychain_service='fixture', keychain_account='fixture',
            form_question_ids={k: k for k in ('materials', 'topics', 'quality_of_life', 'bugs')})))
        config.chmod(0o600)
        self.start_patch(patch.object(sys, 'argv', ['pipeline.py', '--home', str(self.home),
                                                          '--config', str(config), 'poll']))
        credentials = self.start_patch(patch('pipeline.subprocess.run'))
        credentials.return_value.stdout = '{"refresh_token":"fixture"}'
        self.http = self.start_patch(patch('pipeline.urllib.request.urlopen'))
        self.start_patch(patch('pipeline.time.sleep'))

    def start_patch(self, context):
        value = context.start()
        self.addCleanup(context.stop)
        return value

    def assert_queue(self, requests, checkpoints):
        db = sqlite3.connect(self.home / 'queue.sqlite3')
        try:
            self.assertEqual(db.execute('SELECT count(*) FROM form_requests').fetchone()[0], requests)
            self.assertEqual(db.execute('SELECT count(*) FROM checkpoints').fetchone()[0], checkpoints)
        finally:
            db.close()

    def test_offline_start_and_interrupted_batch_recover_on_next_poll(self):
        token = b'{"access_token":"fixture","expires_in":3600}'
        first = b'{"responses":[{"responseId":"one"}],"nextPageToken":"next"}'
        self.http.side_effect = [URLError('offline'), io.BytesIO(token), io.BytesIO(first),
                                 URLError('interrupted'), io.BytesIO(token), io.BytesIO(first),
                                 io.BytesIO(b'{"responses":[{"responseId":"two"}]}')]
        for failure in ('offline', 'interrupted'):
            with self.assertRaisesRegex(URLError, failure):
                pipeline.main()
            self.assert_queue(0, 0)
        pipeline.main()
        self.assert_queue(2, 1)

    def test_expired_token_refresh(self):
        self.http.side_effect = [io.BytesIO(b'{"access_token":"old","expires_in":3600}'),
                                 HTTPError('fixture', 401, 'expired', {}, io.BytesIO()),
                                 io.BytesIO(b'{"access_token":"new","expires_in":3600}'),
                                 io.BytesIO(b'{"responses":[]}')]
        pipeline.main()
        self.assert_queue(0, 1)
        self.assertEqual(self.http.call_args.args[0].get_header('Authorization'), 'Bearer new')

    def test_overlapping_invocation_stops_before_google(self):
        with (self.home / 'pipeline.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            with self.assertRaises(BlockingIOError):
                pipeline.main()
        self.http.assert_not_called()
