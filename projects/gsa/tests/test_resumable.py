import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pipeline as p
from pdf_fixtures import scan_pdf


class LargeUpload(unittest.TestCase):
    def test_interrupted_scan_resumes_at_server_offset(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'scan.pdf'
            pdf = scan_pdf()
            # A PDF comment before the EOF marker keeps the generated scan valid.
            data = pdf.replace(b'%%EOF', b'%' + b'x' * (6 * 1024 * 1024) + b'\n%%EOF')
            path.write_bytes(data)
            queue = Path(directory) / 'queue'
            db = sqlite3.connect(queue)
            p.migrate(db)
            stored = bytearray()
            sessions = []
            def drive(api, method, url, body, headers):
                if method == 'POST':
                    sessions.append(url)
                    return 200, {'Location': 'https://www.googleapis.com/session'}
                if not body:
                    return 308, {'Range': f'bytes=0-{len(stored)-1}'}
                end = len(stored) + len(body)
                self.assertEqual(headers['Content-Range'], f'bytes {len(stored)}-{end-1}/{len(data)}')
                if not stored:
                    stored.extend(body[:1024 * 1024])
                    raise ConnectionError('partial chunk')
                stored.extend(body)
                return (201, {}) if end == len(data) else (308, {'Range': f'bytes=0-{end-1}'})
            with patch.object(p, 'upload_request', side_effect=drive):
                with self.assertRaises(ConnectionError):
                    p.resumable_upload(db, None, path, {'id': 'reserved'})
                db.close()
                db = sqlite3.connect(queue)
                try:
                    p.resumable_upload(db, None, path, {'id': 'reserved'})
                finally:
                    db.close()
            self.assertEqual(len(sessions), 1)
            self.assertEqual(data, stored)
