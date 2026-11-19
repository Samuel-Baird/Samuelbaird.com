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


class CommandTests(unittest.TestCase):
    def test_remove_uses_config_flag_when_home_has_no_config_json(self):
        import json, tempfile, types
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / 'review-portal.key').write_text('k')
            (home / 'pipeline-config.json').write_text(json.dumps({'archive_root_id': 'root'}))
            args = types.SimpleNamespace(command='remove', home=home, config=home / 'pipeline-config.json', id='sandbox-x', packet=None)
            with patch.object(rp.p.gsa, 'DEFAULT_HOME', home), patch.object(rp, 'send', return_value={'deleted': True}) as send:
                rp.run(args)
            send.assert_called_once_with({'id': 'sandbox-x', 'action': 'delete'}, 'k')
            with self.assertRaises(Exception):
                rp.run(types.SimpleNamespace(args.__dict__ | {'config': None}))


class ReviewerRuleTests(unittest.TestCase):
    BOTH = ['b13llama@gmail.com', 'davidjasonharper@gmail.com']

    def test_production_needs_both_reviewers(self):
        self.assertEqual(set(rp.required_reviewers({'required_publication_reviewers': self.BOTH}, '/w/GSA Worker')), {'Samuel', 'David'})
        with self.assertRaises(Exception):
            rp.required_reviewers({'required_publication_reviewers': self.BOTH[:1]}, '/w/GSA Worker')

    def test_single_reviewer_only_in_a_marked_sandbox_home(self):
        one = {'required_publication_reviewers': self.BOTH[:1], 'sandbox': True}
        self.assertEqual(rp.required_reviewers(one, '/w/sandbox-x'), {'Samuel': self.BOTH[0]})
        with self.assertRaises(Exception):
            rp.required_reviewers(one, '/w/production')  # flag alone isn't enough
        with self.assertRaises(Exception):
            rp.required_reviewers(dict(one, sandbox=False), '/w/sandbox-x')
        with self.assertRaises(Exception):
            rp.required_reviewers(dict(one, required_publication_reviewers=['stranger@example.org']), '/w/sandbox-x')


if __name__ == '__main__':
    unittest.main()


class TocTests(unittest.TestCase):
    CONFIG = {'archive_root_id': 'root', 'discovered_archive_resources': [
        {'id': 'READ', 'name': 'Read📚', 'type': FOLDER}, {'id': 'doc', 'name': 'Table of Contents', 'type': 'application/vnd.google-apps.spreadsheet'}]}
    ROWS = [{'name': 'a.pdf', 'folder_path': 'Gospel Scholar Archives™️ / Read📚 / Bible / Old Testament', 'folder_id': 'OTREAL123456'},
            {'name': 'b.pdf', 'folder_path': 'Gospel Scholar Archives™️ /  Read📚  / Bible'},
            {'name': 'c.mp3', 'folder_path': 'Gospel Scholar Archives™️ / Listen🎧 '},
            {'name': 'TOC', 'folder_path': 'Gospel Scholar Archives™️'},
            {'name': 'x', 'folder_path': 'Someone Else / Stuff'}]

    def test_toc_paths_become_a_tree_with_known_and_placeholder_ids(self):
        snap = rp.toc_snapshot(self.ROWS, self.CONFIG)
        self.assertEqual(snap['root'], {'id': 'root', 'name': 'Gospel Scholar Archives™️'})
        tree = {f['name']: f for f in snap['folders']}
        self.assertEqual(set(tree), {'Read📚', 'Bible', 'Old Testament', 'Listen🎧'})
        self.assertEqual(tree['Read📚']['id'], 'READ')
        self.assertEqual(tree['Bible']['parent'], 'READ')
        self.assertEqual(tree['Old Testament']['parent'], tree['Bible']['id'])
        self.assertEqual(tree['Old Testament']['id'], 'OTREAL123456')  # real ID from the row's folder link
        self.assertTrue(tree['Listen🎧']['id'].startswith('toc-'))
        self.assertTrue(rp.FOLDER_LINK.match('https://drive.google.com/drive/folders/1JOPXajLJWGP0Ym4_vORK001ksMV-jYjD').group(1).startswith('1JOP'))
        self.assertEqual(rp.toc_snapshot(self.ROWS, self.CONFIG), snap)  # stable IDs between pushes

    def test_placeholder_resolves_by_walking_drive_names(self):
        drive = DriveStub([
            {'id': 'root', 'name': 'Archive', 'mimeType': FOLDER, 'parents': []},
            {'id': 'READ', 'name': 'Read📚 ', 'mimeType': FOLDER, 'parents': ['root']},
            {'id': 'BIB', 'name': 'Bible', 'mimeType': FOLDER, 'parents': ['READ']}])
        drive.files = lambda q: [f for f in drive.byid.values() if f"'{q.split(chr(39))[1]}' in parents" in q and q.split("'")[1] in f['parents']]
        self.assertEqual(rp.resolve_toc_folder(drive, self.CONFIG, ['Read📚', 'Bible']), 'BIB')
        with self.assertRaisesRegex(ValueError, 'Drive read access'):
            rp.resolve_toc_folder(drive, self.CONFIG, ['Read📚', 'Missing'])


class ArchiveFolderTests(unittest.TestCase):
    def test_table_of_contents_vouches_for_a_folder_without_drive_access(self):
        import json, tempfile
        from unittest.mock import patch
        rows = [{'name': 'a.pdf', 'folder_path': 'Archive / Read📚 / Bible', 'folder_id': 'BIBLEREAL123'}]
        class NoDrive:
            def call(self, *a, **k): raise PermissionError('drive.file only')
            def files(self, q): return []
        with tempfile.NamedTemporaryFile('w', suffix='.json') as f:
            json.dump({'toc_spreadsheet_id': 'sheet', 'toc_sheet_name': 'Table of Contents'}, f); f.flush()
            with patch.object(rp, 'toc_rows', return_value=rows), patch.object(rp.p, 'Google'):
                self.assertTrue(rp.archive_folder(NoDrive(), {'archive_root_id': 'root'}, f.name, 'BIBLEREAL123'))
                self.assertFalse(rp.archive_folder(NoDrive(), {'archive_root_id': 'root'}, f.name, 'ELSEWHERE123'))
                self.assertFalse(rp.archive_folder(NoDrive(), {'archive_root_id': 'root'}, f.name, 'toc-abc'))
        self.assertFalse(rp.archive_folder(NoDrive(), {'archive_root_id': 'root'}, None, 'BIBLEREAL123'))
