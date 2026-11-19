#!/usr/bin/env python3
"""Fail-closed torrent guard and generation of an inactive intake launchd job."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import gsa
from qbt_control import Client

SCENARIOS = ['connected', 'disconnected', 'reconnected', 'vpn-down-startup', 'reboot', 'network-change']

def problems(config, evidence, preferences, route, now=None):
    now = now or datetime.now(timezone.utc)
    issues = []
    expected = config.get('vpn_interface')
    if not expected or preferences.get('current_network_interface') != expected:
        issues.append('qBittorrent binding mismatch')
    if not expected or not any(line.strip() == 'interface: ' + expected for line in route.splitlines()):
        issues.append('IPv4 route is not through approved tunnel')
    if evidence.get('interface') != expected:
        issues.append('Evidence belongs to a different tunnel')
    try:
        expired = datetime.fromisoformat(evidence['expires_at'].replace('Z', '+00:00')) <= now
    except (KeyError, ValueError, TypeError):
        expired = True
    if expired:
        issues.append('Validation evidence is missing or expired')
    for scenario in SCENARIOS:
        test = evidence.get('scenarios', {}).get(scenario, {})
        if not (test.get('passed') is True and test.get('tcp_checked') is True and test.get('udp_checked') is True and test.get('ipv6') in ('checked', 'unavailable') and test.get('evidence_path')):
            issues.append('Unverified scenario: ' + scenario)
    if evidence.get('reviewer') not in config.get('reviewers', []):
        issues.append('Evidence lacks designated reviewer')
    return issues

def guard(config, evidence):
    client = Client()
    try:
        prefs = client.call('app/preferences')
        route = subprocess.run(['/sbin/route', '-n', 'get', '1.1.1.1'], capture_output=True, text=True, check=True, timeout=15).stdout
        issues = problems(config, evidence, prefs, route)
        if issues:
            client.call('torrents/stop', {'hashes': 'all'})
        return issues
    except Exception:
        client.call('torrents/stop', {'hashes': 'all'})
        raise

def launchd(config_path, home, output, config):
    if not config.get('intake_approved') or not config.get('unattended_intake_validated'):
        raise ValueError('Intake approval and unattended intake validation are required')
    data = {
        'Label': 'org.gsa.intake',
        'ProgramArguments': [sys.executable, str(Path(__file__).with_name('pipeline.py').resolve()), '--home', str(home.resolve()), '--config', str(config_path.resolve()), 'poll'],
        'StartInterval': 300, 'RunAtLoad': True, 'ProcessType': 'Background',
        'StandardOutPath': str(home / 'intake.log'), 'StandardErrorPath': str(home / 'intake-error.log'),
        'Umask': 63,
    }
    with output.open('xb') as f:
        plistlib.dump(data, f)
    os.chmod(output, 0o600)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--home', type=Path, default=gsa.DEFAULT_HOME)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('guard'); p.add_argument('evidence', type=Path)
    p = sub.add_parser('launchd'); p.add_argument('output', type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    config = json.loads(args.config.read_text())
    if args.command == 'guard':
        issues = guard(config, json.loads(args.evidence.read_text()))
        print(json.dumps({'issues': issues, 'action': 'stopped' if issues else 'unchanged; no automatic resume'}, indent=2))
        return bool(issues)
    launchd(args.config, args.home, args.output, config)
    print('Wrote inactive plist. No launchd job installed or started.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
