#!/usr/bin/env python3
"""Save private macOS interface/routing evidence; does not certify VPN protection."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

COMMANDS = {
    'interfaces': ['/sbin/ifconfig', '-a'],
    'ipv4_routes': ['/usr/sbin/netstat', '-rn', '-f', 'inet'],
    'ipv6_routes': ['/usr/sbin/netstat', '-rn', '-f', 'inet6'],
    'network_state': ['/usr/sbin/scutil', '--nwi'],
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('label', choices=['vpn-off', 'vpn-on', 'vpn-reconnected'])
    parser.add_argument('--home', type=Path, default=Path.home() / 'Library/Application Support/GSA Worker')
    args = parser.parse_args()
    os.umask(0o077)
    folder = args.home / 'network-checks'
    folder.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(folder, 0o700)
    evidence = {'label': args.label, 'captured_at': datetime.now(timezone.utc).isoformat(),
                'vpn_provider': 'McAfee', 'verified': False, 'commands': {}}
    for name, command in COMMANDS.items():
        result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
        evidence['commands'][name] = {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    # Retain each observation rather than replacing earlier evidence.
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    target = folder / f'{args.label}-{stamp}.json'
    with target.open('x') as f:
        json.dump(evidence, f, indent=2)
    print(f'Saved private observation: {target}')
    print('Interface presence and routes alone do not verify a VPN or kill switch.')

if __name__ == '__main__':
    main()
