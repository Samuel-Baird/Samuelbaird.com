"""Queue coordinator tests. Temporary worker homes and service doubles only."""
from contextlib import closing
import fcntl
import io
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
import unittest
import urllib.error
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gsa
import gsa_runner as r
import pipeline as p
from fakes import FakeGoogle
from pdf_fixtures import text_pdf

T0 = 1_800_000_000.0


class Clock:
    def __init__(self):
        self.now = T0

    def __call__(self):
        return self.now


class RunnerBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / 'sandbox-runner'
        self.db = gsa.connect(self.home)
        p.migrate(self.db)
        self.index = self.home / 'index.json'
        self.index.write_text('[]')
        self.config = dict(reviewers=['staff'], destination_ids=['folder'], archive_index=str(self.index),
                           source_hosts=['publisher.example'], max_file_bytes=10 ** 7, disk_budget_bytes=10 ** 8,
                           reserve_bytes=1, scanner_command=['/usr/bin/true'], publication_approved=False,
                           changelog_document_id='changelog', changelog_anchor='Today')
        self.google = FakeGoogle(folders=['folder'], changelog='Today\n')
        self.clock = Clock()
        self.downloads = 0
        self.pdf = text_pdf()
        patcher = patch('validate.pdf_checks', return_value=({}, None))
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    # -- fixtures ---------------------------------------------------------
    def add_work(self, row_id='1', title='Book'):
        gsa.ingest(self.db, [{'row_id': row_id, 'title': title, 'author': 'Smith', 'edition': '2'}], 'csv:t', 't')
        return self.db.execute('SELECT max(id) FROM works').fetchone()[0]

    def review(self, wid, **extra):
        data = dict(reviewer='staff', source_url='https://publisher.example/book.pdf', matched_work='Book 2nd ed.',
                    filename='Book.pdf', destination='folder', changelog_text='Added Book')
        data.update(extra)
        path = self.home / f'review-{wid}.json'
        path.write_text(json.dumps(data))
        p.review(self.db, wid, path, self.config)

    def approve(self, wid, reviewer='staff', **extra):
        record = p.get(self.db, wid)[1]
        data = dict(reviewer=reviewer, destination='folder', sha256=record['sha256'], **extra)
        data.update({k: True for k, _ in p.validation.STAFF_JUDGMENT})
        path = self.home / 'approval.json'
        path.write_text(json.dumps(data))
        p.approve(self.db, wid, path, self.config)

    def opener(self, *failures):
        """Fake HTTPS opener: raise each queued failure once, then serve the PDF."""
        queue = list(failures)

        def build(*args, **kwargs):
            def open_url(url, timeout=None):
                self.downloads += 1
                if queue:
                    raise queue.pop(0)
                response = io.BytesIO(self.pdf)
                response.headers = {'Content-Length': str(len(self.pdf))}
                return response
            return Mock(open=open_url)
        return patch('pipeline.urllib.request.build_opener', side_effect=build)

    def run_runner(self, **kwargs):
        kwargs.setdefault('api_factory', lambda config: self.google)
        kwargs.setdefault('clock', self.clock)
        return r.run(self.home, self.config, **kwargs)

    def plan(self, wid=None):
        with closing(sqlite3.connect(self.home / 'queue.sqlite3')) as db:
            db.row_factory = sqlite3.Row
            items = r.plan(db, self.config, self.home, self.clock())
        return [i for i in items if wid is None or i['work_id'] == wid]

    def step(self, wid):
        return self.plan(wid)[0]

    def ops(self, wid=None):
        return r.history(self.home, wid)


class ActionSelection(RunnerBase):
    def test_stages_derived_from_records(self):
        self.db.execute('CREATE TABLE form_requests (form_id TEXT, response_id TEXT, answers TEXT NOT NULL, '
                        'status TEXT NOT NULL DEFAULT "needs_review", PRIMARY KEY(form_id,response_id))')
        self.db.execute("INSERT INTO form_requests(form_id,response_id,answers) VALUES('f','resp','{}')")
        self.db.commit()
        unreviewed = self.add_work('1', 'Unreviewed')
        direct = self.add_work('2', 'Direct')
        self.review(direct)
        browser = self.add_work('3', 'Browser')
        self.review(browser, source_url='https://catalog.example/md5/abc')
        items = {i['item']: i for i in self.plan()}
        self.assertEqual(items['form:resp']['stage'], 'untriaged')
        self.assertNotIn('answers', json.dumps(items['form:resp']))
        self.assertEqual((items[f'work:{unreviewed}']['stage'], items[f'work:{unreviewed}']['actor']), ('source_review', 'agent'))
        self.assertEqual((items[f'work:{direct}']['stage'], items[f'work:{direct}']['action']), ('acquisition', 'acquire'))
        self.assertEqual((items[f'work:{browser}']['stage'], items[f'work:{browser}']['actor']), ('browser_import', 'operator'))
        self.assertFalse(items[f'work:{browser}']['eligible'])

    def test_full_supervised_path_to_publication_ready(self):
        wid = self.add_work()
        self.review(wid)
        with self.opener():
            result = self.run_runner(execute=True, max_actions=5)
        self.assertEqual([o['action'] for o in result['operations']], ['acquire', 'validate', 'check'])
        self.assertTrue(all(o['status'] == 'succeeded' for o in result['operations']))
        step = self.step(wid)
        self.assertEqual((step['stage'], step['actor']), ('staff_approval', 'reviewer'))
        self.approve(wid)
        step = self.step(wid)
        self.assertEqual((step['stage'], step['actor'], step['eligible']), ('publication_ready', 'staff', False))
        self.config['publication_approved'] = True
        step = self.step(wid)
        self.assertEqual((step['stage'], step['action']), ('publication_ready', 'publish'))
        # Publication is never selected without --allow-publish and the named work.
        self.assertEqual(self.run_runner(execute=True)['operations'], [])
        with self.assertRaisesRegex(ValueError, 'requires --work'):
            self.run_runner(execute=True, allow_publish=True)

    def test_bounded_run_and_action_filter(self):
        for n in ('1', '2'):
            self.review(self.add_work(n, 'Book ' + n))
        with self.opener():
            result = self.run_runner(execute=True, max_actions=1)
            self.assertEqual(len(result['operations']), 1)
            result = self.run_runner(execute=True, max_actions=5, actions=('validate',))
        self.assertEqual([o['action'] for o in result['operations']], ['validate'])
        self.assertEqual(self.downloads, 1)
        with self.assertRaisesRegex(ValueError, 'max-actions'):
            self.run_runner(execute=True, max_actions=0)

    def test_dry_run_writes_nothing_and_calls_nothing(self):
        wid = self.add_work()
        self.review(wid)
        self.db.close()
        before = (self.home / 'queue.sqlite3').read_bytes()
        factory = Mock()
        with self.opener():
            result = self.run_runner(api_factory=factory)
        self.assertEqual(result['mode'], 'dry-run')
        self.assertEqual([i['action'] for i in result['would_run']], ['acquire'])
        self.assertEqual(self.downloads, 0)
        factory.assert_not_called()
        self.assertEqual((self.home / 'queue.sqlite3').read_bytes(), before)
        self.assertFalse((self.home / 'pipeline.lock').exists())
        self.db = gsa.connect(self.home)


class Restart(RunnerBase):
    def test_interrupted_acquisition_is_not_repeated(self):
        wid = self.add_work()
        self.review(wid)
        # A runner recorded the start, the download completed, then the process stopped.
        r.migrate(self.db)
        key = self.step(wid)['fingerprint']
        with self.db:
            self.db.execute("INSERT INTO runner_operations(work_id,action,fingerprint,attempt,status,started_at) "
                            "VALUES(?,?,?,1,'started',?)", (wid, 'acquire', key, T0))
        self.assertIn('no result', self.step(wid)['reason'])
        with self.opener():
            p.acquire(self.db, wid, self.home, self.config)
            result = self.run_runner(execute=True, max_actions=5)
        self.assertEqual(result['reconciled_interrupted'], 1)
        self.assertEqual(self.downloads, 1)
        self.assertEqual([o['action'] for o in result['operations']], ['validate', 'check'])
        self.assertEqual(self.ops(wid)[0]['status'], 'interrupted')
        self.assertEqual(len(p.get(self.db, wid)[1]['candidates']), 1)

    def test_state_survives_new_connection_and_runner_state_persists(self):
        wid = self.add_work()
        self.review(wid)
        with self.opener():
            self.run_runner(execute=True, max_actions=1)
        self.db.close()
        self.db = gsa.connect(self.home)
        state = dict(self.db.execute('SELECT stage, actor, action FROM runner_state WHERE item=?', (f'work:{wid}',)).fetchone())
        self.assertEqual(state, {'stage': 'validation', 'actor': 'runner', 'action': 'validate'})
        with self.opener():
            result = self.run_runner(execute=True, max_actions=5)
        self.assertEqual([o['action'] for o in result['operations']], ['validate', 'check'])
        self.assertEqual(self.downloads, 1)

    def test_retained_partial_torrent_data_and_stall_policy(self):
        wid = self.add_work()
        infohash = 'a' * 40
        self.review(wid, infohash=infohash, torrent_member='coll/1.pdf', member_md5='b' * 32)
        partial = self.home / 'incomplete' / infohash / 'coll'
        partial.mkdir(parents=True)
        (partial / '1.pdf').write_bytes(b'x' * 327680)
        step = self.step(wid)
        self.assertEqual((step['stage'], step['actor']), ('acquisition', 'staff'))
        self.config['torrent_acquisition_approved'] = True
        self.assertIn('prepare-member', self.step(wid)['next_action'])
        record = p.get(self.db, wid)[1]
        job = p.acquisition.new_job(infohash, T0 - 600, 1000)
        job['last_progress_at'] = T0 - 300  # five idle minutes: well inside the 30 minute stall limit
        job['history'] = [{'at': T0 - 15, 'action': 'wait', 'reason': 'idle 4 min'}]
        record['torrent_job'] = job
        p.save(self.db, wid, record, 'torrent_wait')
        step = self.step(wid)
        self.assertEqual((step['stage'], step['actor'], step['eligible']), ('acquisition', 'wait', False))
        self.assertIn('idle 4 of 30 min', step['reason'])
        self.assertIn('327680 bytes', step['reason'])
        self.clock.now += 3600  # no torrent-loop observations for an hour
        step = self.step(wid)
        self.assertEqual(step['actor'], 'operator')
        self.assertIn('not source failure', step['reason'])
        job.update(status='review', retries=1)
        job['history'].append({'at': T0, 'action': 'route_to_review', 'reason': 'torrent paused outside the worker'})
        p.save(self.db, wid, record, 'torrent_route_to_review')
        step = self.step(wid)
        self.assertEqual(step['stage'], 'acquisition')
        self.assertIn('not proven unavailable', step['reason'])
        job['retries'] = p.acquisition.DEFAULT_POLICY['max_retries']
        p.save(self.db, wid, record, 'torrent_route_to_review')
        step = self.step(wid)
        self.assertEqual((step['stage'], step['eligible']), ('browser_import', False))
        self.assertIn('not proven unavailable', step['reason'])
        # The runner has no torrent operation and leaves the partial data alone.
        with self.opener():
            self.assertEqual(self.run_runner(execute=True)['operations'], [])
        self.assertEqual((partial / '1.pdf').stat().st_size, 327680)


class LockContention(RunnerBase):
    def test_execute_refuses_while_pipeline_lock_held(self):
        wid = self.add_work()
        self.review(wid)
        with (self.home / 'pipeline.lock').open('a') as other:
            fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.opener():
                with self.assertRaises(r.LockBusy):
                    self.run_runner(execute=True)
                # Plan and dry run stay available for review.
                self.assertEqual(self.run_runner()['would_run'][0]['action'], 'acquire')
        self.assertEqual(self.downloads, 0)
        self.assertEqual(self.ops(), [])
        with self.opener():
            self.assertEqual(len(self.run_runner(execute=True, max_actions=1)['operations']), 1)


class Retries(RunnerBase):
    def test_transient_failure_backs_off_and_is_bounded(self):
        wid = self.add_work()
        self.review(wid)
        offline = [urllib.error.URLError('offline') for _ in range(5)]
        with self.opener(*offline):
            first = self.run_runner(execute=True, max_actions=5)
            self.assertEqual([o['status'] for o in first['operations']], ['transient_failure'])
            step = self.step(wid)
            self.assertEqual((step['actor'], step['eligible']), ('wait', False))
            self.assertIn('Retry 2/3', step['reason'])
            self.assertEqual(self.run_runner(execute=True)['operations'], [])
            self.clock.now += 10 * 60 + 1
            self.assertEqual(self.run_runner(execute=True)['operations'][0]['attempt'], 2)
            self.clock.now += 10 * 60 + 1
            self.assertEqual(self.run_runner(execute=True)['operations'], [])  # second backoff is 20 minutes
            self.clock.now += 10 * 60
            self.assertEqual(self.run_runner(execute=True)['operations'][0]['attempt'], 3)
            self.clock.now += 10 ** 6
            self.assertEqual(self.run_runner(execute=True)['operations'], [])
        self.assertEqual(self.downloads, 3)
        step = self.step(wid)
        self.assertEqual((step['stage'], step['actor']), ('acquisition', 'operator'))
        self.assertIn('reached the limit', step['reason'])
        self.assertNotIn('candidates', p.get(self.db, wid)[1])

    def test_refused_gate_is_not_repeated_until_inputs_change(self):
        wid = self.add_work()
        self.review(wid)
        self.config['max_file_bytes'] = 10  # disk and size limits refuse the download
        with self.opener():
            result = self.run_runner(execute=True, max_actions=5)
            self.assertEqual([o['status'] for o in result['operations']], ['blocked'])
            self.assertIn('ValueError', result['operations'][0]['outcome'])
            self.clock.now += 10 ** 6
            self.assertEqual(self.run_runner(execute=True)['operations'], [])
            self.assertIn('refused', self.step(wid)['reason'])
            # A revised source review is new input.
            self.config['max_file_bytes'] = 10 ** 7
            self.review(wid, source_url='https://publisher.example/book-v2.pdf')
            result = self.run_runner(execute=True, max_actions=1)
        self.assertEqual(result['operations'][0]['status'], 'succeeded')
        self.assertEqual(self.downloads, 2)


class ReviewChanges(RunnerBase):
    def prepared(self):
        wid = self.add_work()
        self.review(wid)
        with self.opener():
            self.run_runner(execute=True, max_actions=3)
        return wid

    def test_changed_candidate_invalidates_approval(self):
        wid = self.prepared()
        self.approve(wid)
        self.assertEqual(self.step(wid)['stage'], 'publication_ready')
        record = p.get(self.db, wid)[1]
        record['approval']['sha256'] = '0' * 64
        p.save(self.db, wid, record, 'test_tamper')
        step = self.step(wid)
        self.assertEqual(step['stage'], 'staff_approval')
        self.assertIn('different file', step['reason'])

    def test_revised_source_review_returns_to_acquisition(self):
        wid = self.prepared()
        self.approve(wid)
        self.review(wid, source_url='https://publisher.example/other.pdf')
        step = self.step(wid)
        self.assertEqual((step['stage'], step['action']), ('acquisition', 'acquire'))

    def test_requested_changes_and_partial_reviewers(self):
        wid = self.prepared()
        self.config['reviewers'] = ['staff', 'second']
        self.config['required_publication_reviewers'] = ['staff', 'second']
        self.approve(wid)
        step = self.step(wid)
        self.assertEqual((step['stage'], step['actor']), ('staff_approval', 'reviewer'))
        self.assertIn('Approved so far by staff', step['reason'])
        record = p.get(self.db, wid)[1]
        record['web_review'] = {'decisions': {'second': {'decision': 'Changes requested', 'note': 'Wrong edition'}}}
        p.save(self.db, wid, record, 'test_web_review')
        step = self.step(wid)
        self.assertEqual((step['stage'], step['actor']), ('staff_approval', 'operator'))
        self.assertIn('Changes requested by second', step['reason'])

    def test_revoked_reviewer_blocks_publication_ready(self):
        wid = self.prepared()
        self.approve(wid)
        self.config['reviewers'] = ['someone-else']
        self.assertEqual(self.step(wid)['stage'], 'staff_approval')

    def test_rerun_validation_when_candidate_added(self):
        wid = self.prepared()
        self.approve(wid)
        with self.opener():
            p.acquire(self.db, wid, self.home, self.config)
        step = self.step(wid)
        self.assertEqual((step['stage'], step['action']), ('validation', 'validate'))


class Duplicates(RunnerBase):
    def prepared(self, index):
        self.index.write_text(json.dumps(index))
        wid = self.add_work()
        self.review(wid)
        with self.opener():
            self.run_runner(execute=True, max_actions=3)
        return wid

    def test_exact_archive_match_blocks(self):
        wid = self.prepared([{'title': 'Book', 'author': 'Smith', 'edition': '2'}])
        step = self.step(wid)
        self.assertEqual((step['stage'], step['actor']), ('duplicate_review', 'staff'))

    def test_ambiguous_match_needs_reviewer_resolution(self):
        wid = self.prepared([{'title': 'Book', 'author': 'Smith', 'edition': '1'}])
        step = self.step(wid)
        self.assertEqual((step['stage'], step['actor']), ('duplicate_review', 'reviewer'))
        key = p.get(self.db, wid)[1]['archive_check']['matches'][0]['key']
        self.approve(wid, archive_resolution={'matches': [key], 'reason': 'Archive holds the 1st edition'})
        self.assertEqual(self.step(wid)['stage'], 'publication_ready')

    def test_publication_resumes_without_duplicate_upload(self):
        wid = self.prepared([])
        self.approve(wid)
        self.config['publication_approved'] = True
        self.google.faults['upload_response'] = 'lost'
        first = self.run_runner(execute=True, allow_publish=True, work=wid)
        self.assertEqual([o['status'] for o in first['operations']], ['transient_failure'])
        self.assertEqual(self.step(wid)['stage'], 'publishing')
        self.assertEqual(self.run_runner(execute=True, allow_publish=True, work=wid)['operations'], [])
        self.clock.now += 10 * 60 + 1
        second = self.run_runner(execute=True, allow_publish=True, work=wid)
        self.assertEqual([o['status'] for o in second['operations']], ['succeeded'])
        self.assertEqual(len(self.google.blobs), 1)
        self.assertEqual(self.google.doc_text.count('[GSA:'), 1)
        self.assertEqual(self.step(wid)['stage'], 'complete')
        calls = len(self.google.calls)
        self.clock.now += 10 ** 6
        self.assertEqual(self.run_runner(execute=True, allow_publish=True, work=wid)['operations'], [])
        self.assertEqual(len(self.google.calls), calls)

    def test_unapproved_or_missing_destination_blocks_check(self):
        wid = self.add_work()
        self.review(wid)
        with self.opener():
            self.run_runner(execute=True, max_actions=2)
        self.config['destination_ids'] = ['other']
        step = self.step(wid)
        self.assertEqual((step['stage'], step['actor'], step['eligible']), ('duplicate_check', 'operator', False))
        self.assertIn('not in the configured destination_ids', step['reason'])
        record = p.get(self.db, wid)[1]
        del record['review']['destination']
        p.save(self.db, wid, record, 'test_no_destination')
        self.assertIn('no destination', self.step(wid)['reason'])
        self.assertEqual(self.run_runner(execute=True)['operations'], [])
        self.assertEqual(self.google.calls, [])

    def test_status_complete_without_receipts_is_not_complete(self):
        wid = self.add_work()
        self.review(wid)
        with self.db:
            self.db.execute("UPDATE works SET status='complete' WHERE id=?", (wid,))
        step = self.step(wid)
        self.assertEqual((step['stage'], step['actor']), ('publishing', 'operator'))


class CommandLine(RunnerBase):
    def test_cli_plan_and_dry_run(self):
        wid = self.add_work()
        self.review(wid)
        config = self.home / 'config.json'
        config.write_text(json.dumps(self.config))
        os.chmod(config, 0o600)
        out = io.StringIO()
        r.main(['--home', str(self.home), '--config', str(config), 'plan'], out=out)
        self.assertIn('acquisition', out.getvalue())
        out = io.StringIO()
        r.main(['--home', str(self.home), '--config', str(config), 'run'], out=out)
        self.assertIn('Dry run', out.getvalue())
        self.assertIn('would run: acquire on work 1', out.getvalue())
        with self.assertRaisesRegex(ValueError, 'acquire, validate, check'):
            r.main(['--home', str(self.home), '--config', str(config), 'run', '--actions', 'publish'], out=out)
        os.chmod(config, 0o644)
        with self.assertRaisesRegex(ValueError, '0600'):
            r.main(['--home', str(self.home), '--config', str(config), 'plan'], out=out)


if __name__ == '__main__':
    unittest.main()
