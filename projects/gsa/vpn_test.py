#!/usr/bin/env python3
"""VPN disconnect/reconnect test helpers: sample qBittorrent + routing, mark phases, analyze a pcap.

The capture itself is taken separately with tcpdump on the physical interface (needs root).
This tool attributes captured packets to qBittorrent by its local ports and remote peers and
reports them per phase. It records observations; a human reviewer decides whether a scenario
passed. It never starts, resumes or reconfigures torrents.
"""
import argparse
from datetime import datetime, timezone
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

QBT_PROCESS = 'qbittorrent'
LINE = re.compile(r'^(\d+\.\d+) (IP6?) (\S+) > (\S+): (.*)$')


def now():
    return datetime.now(timezone.utc).isoformat()


def split_endpoint(token, family):
    """'10.0.0.1.443' -> ('10.0.0.1', 443); IPv6 'a:b::1.443' -> ('a:b::1', 443); no port -> (addr, None)."""
    head, _, tail = token.rpartition('.')
    if family == 'IP':
        if token.count('.') == 4 and tail.isdigit():
            return head, int(tail)
        return token, None
    if head and ':' in head and tail.isdigit():
        return head, int(tail)
    return token, None


def parse_line(line):
    m = LINE.match(line.strip())
    if not m:
        return None
    ts, family, src, dst, rest = m.groups()
    s_addr, s_port = split_endpoint(src, family)
    d_addr, d_port = split_endpoint(dst, family)
    if 'ESP(' in rest and 'UDP-encap' not in rest:
        proto = 'esp'
    elif rest.startswith('Flags') or ' tcp ' in rest:
        proto = 'tcp'
    elif 'UDP' in rest or rest.startswith('[udp') or 'NONESP-encap' in rest or 'isakmp' in rest.lower() or re.match(r'^(\[\w+\] )?\d+\+?', rest) or 'quic' in rest.lower():
        proto = 'udp'
    elif 'ICMP' in rest:
        proto = 'icmp'
    else:
        proto = 'other'
    return {'t': float(ts), 'family': 'ipv6' if family == 'IP6' else 'ipv4', 'proto': proto,
            'src': s_addr, 'sport': s_port, 'dst': d_addr, 'dport': d_port, 'info': rest[:80]}


def is_local_noise(addr):
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return False
    return ip.is_multicast or ip.is_link_local or addr.endswith('.255') or str(ip) == '255.255.255.255'


def vpn_transport(pkt, gateways):
    if pkt['proto'] == 'esp':
        return True
    remote = pkt['dst'] if pkt['src'] not in gateways else pkt['src']
    if pkt['proto'] == 'udp' and (pkt['sport'] in (500, 4500) or pkt['dport'] in (500, 4500)):
        return True
    return remote in gateways


def phase_of(t, phases):
    label = 'before-first-mark'
    for p in phases:
        if t >= p['t']:
            label = p['label']
    return label


def classify(packets, qbt_ports, qbt_remotes, gateways, phases):
    report = {}
    for pkt in packets:
        phase = phase_of(pkt['t'], phases)
        r = report.setdefault(phase, {'packets': 0, 'vpn_transport': 0, 'local_noise': 0, 'other_apps': 0,
                                      'qbittorrent': {'ipv4_tcp': 0, 'ipv4_udp': 0, 'ipv6_tcp': 0, 'ipv6_udp': 0, 'other': 0},
                                      'qbittorrent_examples': []})
        r['packets'] += 1
        if vpn_transport(pkt, gateways):
            r['vpn_transport'] += 1
            continue
        if is_local_noise(pkt['src']) or is_local_noise(pkt['dst']):
            r['local_noise'] += 1
            continue
        ours = (pkt['sport'] in qbt_ports or pkt['dport'] in qbt_ports
                or pkt['src'] in qbt_remotes or pkt['dst'] in qbt_remotes)
        if not ours:
            r['other_apps'] += 1
            continue
        key = f"{pkt['family']}_{pkt['proto']}" if pkt['proto'] in ('tcp', 'udp') else 'other'
        r['qbittorrent'][key] += 1
        if len(r['qbittorrent_examples']) < 10:
            r['qbittorrent_examples'].append(pkt)
    for r in report.values():
        r['qbittorrent_total'] = sum(r['qbittorrent'].values())
    return report


# --- live sampling -------------------------------------------------------------------------

def qbt_pid():
    out = subprocess.run(['pgrep', '-f', 'qBittorrent.app/Contents/MacOS/qbittorrent'], capture_output=True, text=True).stdout.split()
    return int(out[0]) if out else None


def sockets(pid):
    if not pid:
        return []
    out = subprocess.run(['/usr/sbin/lsof', '-nP', '-a', '-p', str(pid), '-i'], capture_output=True, text=True, timeout=10).stdout
    rows = []
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 9:
            rows.append({'type': parts[4], 'proto': parts[7], 'name': ' '.join(parts[8:])})
    return rows


def route_interface():
    out = subprocess.run(['/sbin/route', '-n', 'get', '1.1.1.1'], capture_output=True, text=True, timeout=10).stdout
    for line in out.splitlines():
        if line.strip().startswith('interface:'):
            return line.split(':', 1)[1].strip()
    return None


def interface_up(name):
    return subprocess.run(['/sbin/ifconfig', name], capture_output=True).returncode == 0


def sample(folder, seconds, interface):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from qbt_control import Client
    folder.mkdir(parents=True, exist_ok=True)
    stop = folder / 'stop'
    client, deadline, n = None, time.time() + seconds, 0
    with (folder / 'samples.jsonl').open('a') as out:
        while time.time() < deadline and not stop.exists():
            row = {'at': now(), 't': time.time(), 'route': route_interface(), f'{interface}_present': interface_up(interface)}
            pid = qbt_pid()
            row['qbt_pid'] = pid
            row['sockets'] = sockets(pid)
            try:
                client = client or Client()
                row['binding'] = client.call('app/preferences').get('current_network_interface')
                row['torrents'] = [{k: t.get(k) for k in ('hash', 'state', 'downloaded', 'uploaded', 'dlspeed', 'upspeed', 'num_seeds', 'num_leechs')}
                                   for t in client.call('torrents/info')]
                if n % 5 == 0:
                    peers = {}
                    for t in row['torrents']:
                        data = client.call('sync/torrentPeers?hash=' + t['hash'])
                        peers[t['hash'][:8]] = sorted((data.get('peers') or {}).keys()) if isinstance(data, dict) else []
                    row['peers'] = peers
            except Exception as exc:  # Web UI down (e.g. app restarting): record and keep sampling
                client = None
                row['qbt_error'] = type(exc).__name__
            out.write(json.dumps(row) + '\n')
            out.flush()
            n += 1
            time.sleep(1)


def mark(folder, label):
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / 'phases.jsonl').open('a') as f:
        f.write(json.dumps({'label': label, 't': time.time(), 'at': now()}) + '\n')


def endpoint_host(name):
    """lsof NAME like '10.0.1.113:53514->1.2.3.4:6881 (ESTABLISHED)' or '[2601::1]:53514'."""
    hosts, ports = [], []
    for part in name.split(' ')[0].split('->'):
        m = re.match(r'^\[?([^\]]*?)\]?:(\d+|\*)$', part)
        if m:
            hosts.append(m.group(1))
            ports.append(int(m.group(2)) if m.group(2).isdigit() else None)
    return hosts, ports


def analyze(folder, pcap, gateways, listen_port):
    samples = [json.loads(l) for l in (folder / 'samples.jsonl').read_text().splitlines() if l.strip()]
    phases = [json.loads(l) for l in (folder / 'phases.jsonl').read_text().splitlines() if l.strip()]
    ports, remotes = {listen_port}, set()
    for s in samples:
        for sock in s.get('sockets', []):
            hosts, sock_ports = endpoint_host(sock['name'])
            if sock_ports and sock_ports[0] and sock_ports[0] not in (18765,):
                ports.add(sock_ports[0])
            if len(hosts) > 1:
                remotes.add(hosts[1])
        for addrs in (s.get('peers') or {}).values():
            for a in addrs:
                remotes.add(a.rsplit(':', 1)[0].strip('[]'))
    ports.discard(None)
    text = subprocess.run(['/usr/sbin/tcpdump', '-nn', '-tt', '-r', str(pcap)], capture_output=True, text=True).stdout
    packets = [p for p in (parse_line(l) for l in text.splitlines()) if p]
    report = classify(packets, ports, remotes, set(gateways), phases)
    counters = {}
    for s in samples:
        for t in s.get('torrents') or []:
            label = phase_of(s['t'], phases)
            c = counters.setdefault(label, {'first_downloaded': t['downloaded'], 'first_uploaded': t['uploaded'], 'routes': set(), 'bindings': set()})
            c['last_downloaded'], c['last_uploaded'] = t['downloaded'], t['uploaded']
            c['routes'].add(s.get('route'))
            c['bindings'].add(s.get('binding'))
    for c in counters.values():
        c['routes'], c['bindings'] = sorted(map(str, c['routes'])), sorted(map(str, c['bindings']))
    return {'analyzed_at': now(), 'pcap': str(pcap), 'packets_parsed': len(packets),
            'qbt_ports': sorted(ports), 'qbt_remote_count': len(remotes), 'vpn_gateways': sorted(gateways),
            'phases': report, 'counters': counters,
            'note': 'Observations only. A reviewer decides pass/fail; attribution uses qBittorrent sockets and peer lists sampled once per second.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('sample'); s.add_argument('folder', type=Path); s.add_argument('--seconds', type=int, default=1800); s.add_argument('--interface', default='ipsec0')
    m = sub.add_parser('mark'); m.add_argument('folder', type=Path); m.add_argument('label')
    a = sub.add_parser('analyze'); a.add_argument('folder', type=Path); a.add_argument('pcap', type=Path)
    a.add_argument('--gateway', action='append', default=[]); a.add_argument('--listen-port', type=int, required=True)
    args = ap.parse_args()
    os.umask(0o077)
    if args.cmd == 'sample':
        sample(args.folder, args.seconds, args.interface)
    elif args.cmd == 'mark':
        mark(args.folder, args.label)
    else:
        print(json.dumps(analyze(args.folder, args.pcap, args.gateway, args.listen_port), indent=2))


if __name__ == '__main__':
    main()
