#!/usr/bin/env python3
"""Fail-closed torrent guard and generation of an inactive intake launchd job."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import gsa
from qbt_control import Client

SCENARIOS = ['connected', 'disconnected', 'reconnected', 'vpn-down-startup', 'reboot', 'network-change']

def wifi_underlay(tunnel, wifi, hardware, nwi, udp):
    """Verify the only physical IP path and the IPv4 IKEv2 transport socket on macOS."""
    if not isinstance(wifi, str) or not re.fullmatch(r'en[0-9]+', wifi):
        return False
    if (not isinstance(tunnel, str) or tunnel == wifi
            or wifi not in re.findall(r'^Hardware Port: Wi-Fi\nDevice: (\S+)$', hardware, re.M)):
        return False
    active = re.search(r'^Network interfaces: (.+)$', nwi, re.M)
    if not active or set(active[1].split()) != {wifi, tunnel}:
        return False
    # Associate each address and VPN endpoint with its own IPv4 interface stanza.
    ipv4 = nwi.partition('IPv4 network interface information')[2].partition('IPv6 network interface information')[0]
    blocks = re.split(r'^ +([\w.-]+) : flags[^\n]*$', ipv4, flags=re.M)
    interfaces = dict(zip(blocks[1::2], blocks[2::2]))
    peer = re.search(r'^ +VPN server : ([0-9.]+)$', interfaces.get(tunnel, ''), re.M)
    address = re.search(r'^ +address +: ([0-9.]+)$', interfaces.get(wifi, ''), re.M)
    if not peer or not address:
        return False
    # An unscoped route lookup for the VPN server can itself point into ipsec0.
    # Instead verify the kernel's connected outer IKE sockets to the reported peer.
    local_addresses = set()
    for row in udp.splitlines():
        fields = row.split()
        if len(fields) < 6 or fields[0] != 'udp4' or not any(f.startswith('NEIKEv2Provider:') for f in fields[5:]):
            continue
        if fields[4] in (peer[1] + '.4500', peer[1] + '.500'):
            local_addresses.add(fields[3].rpartition('.')[0])
    return local_addresses == {address[1]}


def network_output(*command):
    return subprocess.run(command, capture_output=True, text=True, check=True, timeout=15).stdout


def current_wifi_underlay(config):
    return wifi_underlay(config.get('vpn_interface'), config['fixed_wifi_interface'],
                         network_output('/usr/sbin/networksetup', '-listallhardwareports'),
                         network_output('/usr/sbin/scutil', '--nwi'),
                         network_output('/usr/sbin/netstat', '-anv', '-p', 'udp'))


def problems(config, evidence, preferences, route, now=None, *, wifi_verified=False):
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
    except (KeyError, ValueError, TypeError, AttributeError):
        expired = True
    if expired:
        issues.append('Validation evidence is missing or expired')
    fixed_wifi = 'fixed_wifi_interface' in config
    if fixed_wifi and not wifi_verified:
        issues.append('Fixed Wi-Fi transport could not be verified')
    for scenario in SCENARIOS:
        test = evidence.get('scenarios', {}).get(scenario, {})
        if fixed_wifi and scenario == 'network-change':
            if test.get('status') != 'not_applicable' or test.get('interface') != config['fixed_wifi_interface']:
                issues.append('Fixed Wi-Fi handoff exception missing or for another interface')
            continue
        if not (test.get('passed') is True and test.get('tcp_checked') is True and test.get('udp_checked') is True and test.get('ipv6') in ('checked', 'unavailable') and test.get('evidence_path')):
            issues.append('Unverified scenario: ' + scenario)
    if evidence.get('reviewer') not in config.get('reviewers', []):
        issues.append('Evidence lacks designated reviewer')
    return issues

def guard(config, evidence):
    client = Client()
    try:
        prefs = client.call('app/preferences')
        route = network_output('/sbin/route', '-n', 'get', '1.1.1.1')
        wifi_verified = 'fixed_wifi_interface' in config and current_wifi_underlay(config)
        issues = problems(config, evidence, prefs, route, wifi_verified=wifi_verified)
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
