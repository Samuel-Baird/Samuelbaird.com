import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import review_portal as rp

FOLDER = rp.FOLDER


class DriveStub:
    def __init__(self, files):
        self.byid = {f['id']: f for f in files}

    def files(self, query):
        assert FOLDER in query
        return [f for f in self.byid.values() if f.get('mimeType') == FOLDER]

    def call(self, method, url, params=None, **kw):
        return dict(self.byid[url.rsplit('/', 1)[1]])


DRIVE = DriveStub([
    {'id': 'root', 'name': 'Archive', 'mimeType': FOLDER, 'parents': []},
    {'id': 'read', 'name': 'Read', 'mimeType': FOLDER, 'parents': ['root']},
    {'id': 'bible', 'name': 'Bible', 'mimeType': FOLDER, 'parents': ['read']},
    {'id': 'other', 'name': 'Personal', 'mimeType': FOLDER, 'parents': ['mydrive']},
    {'id': 'mydrive', 'name': 'My Drive', 'mimeType': FOLDER, 'parents': []},
    {'id': 'pdf', 'name': 'A.pdf', 'mimeType': 'application/pdf', 'parents': ['read']},
    {'id': 'gone', 'name': 'Old', 'mimeType': FOLDER, 'parents': ['read'], 'trashed': True},
])
CONFIG = {'archive_root_id': 'root'}


class ReviewPortalTests(unittest.TestCase):
    def test_folder_snapshot_keeps_only_archive_descendants(self):
        snap = rp.folder_snapshot(DRIVE, CONFIG)
        self.assertEqual(snap['root'], {'id': 'root', 'name': 'Archive'})
        self.assertEqual({f['id']: f['parent'] for f in snap['folders']}, {'read': 'root', 'bible': 'read', 'gone': 'read'})

    def test_edited_destination_must_be_a_live_folder_inside_the_archive(self):
        self.assertTrue(rp.under_archive(DRIVE, CONFIG, 'bible'))
        self.assertTrue(rp.under_archive(DRIVE, CONFIG, 'read'))
        self.assertFalse(rp.under_archive(DRIVE, CONFIG, 'other'))
        self.assertFalse(rp.under_archive(DRIVE, CONFIG, 'pdf'))
        self.assertFalse(rp.under_archive(DRIVE, CONFIG, 'gone'))

    def test_web_edits_map_onto_the_source_review(self):
        draft = {'filename': 'A.pdf', 'matched_work': 'A (1999)', 'changelog_text': 'old', 'destination': 'read', 'source_url': 'https://x'}
        packet = {'title': 'A', 'filename': 'A.pdf', 'citation': 'A (1999)', 'entry': 'old', 'destination': 'read', 'folder': 'Archive / Read', 'rights': 'CC'}
        edits = {k: {'value': v, 'by': 'David', 'at': 'now'} for k, v in
                 {'title': 'A, Revised', 'filename': 'A (2nd ed.).pdf', 'citation': 'A, 2nd ed. (2001)', 'entry': 'new',
                  'destination': 'bible', 'folder': 'Archive / Read / Bible', 'rights': 'CC BY 4.0'}.items()}
        new_draft, new_packet = rp.apply_edits(draft, packet, edits)
        self.assertEqual(new_draft, {'filename': 'A (2nd ed.).pdf', 'matched_work': 'A, 2nd ed. (2001)', 'changelog_text': 'new',
                                     'destination': 'bible', 'source_url': 'https://x'})
        self.assertEqual(new_packet['rights'], 'CC BY 4.0')
        self.assertEqual(new_packet['title'], 'A, Revised')
        self.assertEqual(draft['filename'], 'A.pdf')  # inputs untouched


if __name__ == '__main__':
    unittest.main()
