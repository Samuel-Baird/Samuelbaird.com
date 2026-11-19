import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rollout  # noqa: E402

NOW = datetime(2026, 11, 19, tzinfo=timezone.utc)
ROUTE_VPN = '   route to: 1.1.1.1\n  interface: ipsec0\n'
ROUTE_WIFI = '   route to: 1.1.1.1\n    gateway: 10.0.0.1\n  interface: en1\n'


def scenario(**over):
    s = {'passed': True, 'tcp_checked': True, 'udp_checked': True, 'ipv6': 'checked', 'evidence_path': '/private/x.pcap'}
    s.update(over)
    return s


def evidence(**over):
    e = {'interface': 'ipsec0', 'expires_at': (NOW + timedelta(days=7)).isoformat(), 'reviewer': 'staff',
         'scenarios': {name: scenario() for name in rollout.SCENARIOS}}
    e.update(over)
    return e


CONFIG = {'vpn_interface': 'ipsec0', 'reviewers': ['staff']}
PREFS = {'current_network_interface': 'ipsec0'}


class Problems(unittest.TestCase):
    def test_all_gates_pass(self):
        self.assertEqual(rollout.problems(CONFIG, evidence(), PREFS, ROUTE_VPN, NOW), [])

    def test_binding_mismatch(self):
        issues = rollout.problems(CONFIG, evidence(), {'current_network_interface': ''}, ROUTE_VPN, NOW)
        self.assertIn('qBittorrent binding mismatch', issues)

    def test_route_on_wifi(self):
        self.assertIn('IPv4 route is not through approved tunnel', rollout.problems(CONFIG, evidence(), PREFS, ROUTE_WIFI, NOW))

    def test_missing_interface_config_fails_closed(self):
        issues = rollout.problems({'reviewers': ['staff']}, evidence(), PREFS, ROUTE_VPN, NOW)
        self.assertIn('qBittorrent binding mismatch', issues)
        self.assertIn('IPv4 route is not through approved tunnel', issues)

    def test_expired_or_bad_timestamp(self):
        for value in [(NOW - timedelta(seconds=1)).isoformat(), 'not a date', None, '2027-01-01T00:00:00']:  # last: no timezone
            issues = rollout.problems(CONFIG, evidence(expires_at=value), PREFS, ROUTE_VPN, NOW)
            self.assertIn('Validation evidence is missing or expired', issues)

    def test_each_scenario_field_required(self):
        for bad in [{'passed': False}, {'tcp_checked': False}, {'udp_checked': False}, {'ipv6': 'skipped'}, {'evidence_path': ''}]:
            ev = evidence()
            ev['scenarios']['reboot'] = scenario(**bad)
            self.assertIn('Unverified scenario: reboot', rollout.problems(CONFIG, ev, PREFS, ROUTE_VPN, NOW), bad)

    def test_missing_scenario(self):
        ev = evidence()
        del ev['scenarios']['network-change']
        self.assertIn('Unverified scenario: network-change', rollout.problems(CONFIG, ev, PREFS, ROUTE_VPN, NOW))

    def test_reviewer_must_be_designated(self):
        self.assertIn('Evidence lacks designated reviewer', rollout.problems({**CONFIG, 'reviewers': []}, evidence(), PREFS, ROUTE_VPN, NOW))


class Guard(unittest.TestCase):
    def _client(self, prefs):
        client = mock.Mock()
        client.call.side_effect = lambda endpoint, data=None: prefs if endpoint == 'app/preferences' else ''
        return client

    def test_stops_all_on_problem_and_never_resumes(self):
        client = self._client({'current_network_interface': 'en1'})
        with mock.patch.object(rollout, 'Client', return_value=client), \
             mock.patch.object(rollout.subprocess, 'run', return_value=mock.Mock(stdout=ROUTE_VPN)):
            issues = rollout.guard(CONFIG, evidence())
        self.assertTrue(issues)
        endpoints = [c.args[0] for c in client.call.call_args_list]
        self.assertIn('torrents/stop', endpoints)
        self.assertNotIn('torrents/start', endpoints)

    def test_stops_when_route_check_errors(self):
        client = self._client(PREFS)
        with mock.patch.object(rollout, 'Client', return_value=client), \
             mock.patch.object(rollout.subprocess, 'run', side_effect=OSError('route failed')):
            with self.assertRaises(OSError):
                rollout.guard(CONFIG, evidence())
        self.assertIn('torrents/stop', [c.args[0] for c in client.call.call_args_list])


class Launchd(unittest.TestCase):
    def test_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as d:
            for cfg in [{}, {'intake_approved': True}, {'unattended_intake_validated': True}]:
                with self.assertRaises(ValueError):
                    rollout.launchd(Path(d) / 'c.json', Path(d), Path(d) / 'job.plist', cfg)
            self.assertFalse((Path(d) / 'job.plist').exists())

    def test_writes_inactive_private_plist_once(self):
        import plistlib
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'job.plist'
            cfg = {'intake_approved': True, 'unattended_intake_validated': True}
            rollout.launchd(Path(d) / 'c.json', Path(d), out, cfg)
            data = plistlib.loads(out.read_bytes())
            self.assertEqual(data['StartInterval'], 300)
            self.assertEqual(data['ProgramArguments'][-1], 'poll')
            self.assertEqual(out.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                rollout.launchd(Path(d) / 'c.json', Path(d), out, cfg)


if __name__ == '__main__':
    unittest.main()
