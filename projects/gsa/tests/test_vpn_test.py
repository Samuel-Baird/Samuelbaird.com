import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import vpn_test as v  # noqa: E402

LINES = [
    '100.000001 IP 10.0.0.134.4500 > 198.51.100.7.4500: UDP-encap: ESP(spi=0x1,seq=0x2), length 120',
    '100.000002 IP 10.0.0.134 > 198.51.100.7: ESP(spi=0x1,seq=0x3), length 120',
    '101.000000 IP 10.0.0.134.53514 > 203.0.113.9.6881: Flags [S], seq 1, win 65535, length 0',
    '101.500000 IP6 2601:681:c00:3bc::aa33.53514 > 2001:db8::9.6881: Flags [S], seq 1, length 0',
    '102.000000 IP 10.0.0.134.61000 > 203.0.113.9.6881: UDP, length 30',
    '102.100000 IP 10.0.0.134.50000 > 192.0.2.50.443: Flags [P.], seq 1:10, length 9',
    '102.200000 IP 10.0.0.134.5353 > 224.0.0.251.5353: 0 PTR (QM)? _x._tcp.local. (30)',
    '102.300000 IP6 fe80::1.546 > ff02::1:2.547: dhcp6 solicit',
    '102.400000 ARP, Request who-has 10.0.0.1 tell 10.0.0.134, length 28',
]
PHASES = [{'label': 'connected', 't': 100.0}, {'label': 'disconnected', 't': 102.0}]


class Parse(unittest.TestCase):
    def test_endpoints(self):
        p = v.parse_line(LINES[2])
        self.assertEqual((p['src'], p['sport'], p['dst'], p['dport'], p['proto']), ('10.0.0.134', 53514, '203.0.113.9', 6881, 'tcp'))
        p6 = v.parse_line(LINES[3])
        self.assertEqual((p6['family'], p6['src'], p6['sport']), ('ipv6', '2601:681:c00:3bc::aa33', 53514))
        esp = v.parse_line(LINES[1])
        self.assertEqual((esp['proto'], esp['sport']), ('esp', None))
        self.assertIsNone(v.parse_line(LINES[8]))

    def test_lsof_names(self):
        self.assertEqual(v.endpoint_host('10.0.1.113:53514->203.0.113.9:6881 (ESTABLISHED)'), (['10.0.1.113', '203.0.113.9'], [53514, 6881]))
        self.assertEqual(v.endpoint_host('[2601::1]:53514'), (['2601::1'], [53514]))
        self.assertEqual(v.endpoint_host('*:53514'), (['*'], [53514]))


class Classify(unittest.TestCase):
    def test_attribution_by_phase(self):
        packets = [p for p in map(v.parse_line, LINES) if p]
        r = v.classify(packets, {53514}, {'203.0.113.9'}, {'198.51.100.7'}, PHASES)
        c, d = r['connected'], r['disconnected']
        self.assertEqual(c['vpn_transport'], 2)
        self.assertEqual(c['qbittorrent'], {'ipv4_tcp': 1, 'ipv4_udp': 0, 'ipv6_tcp': 1, 'ipv6_udp': 0, 'other': 0})
        self.assertEqual(d['qbittorrent']['ipv4_udp'], 1)   # remote peer match, ephemeral port
        self.assertEqual(d['other_apps'], 1)                # unrelated HTTPS
        self.assertEqual(d['local_noise'], 2)               # mDNS + DHCPv6
        self.assertEqual(d['qbittorrent_total'], 1)


if __name__ == '__main__':
    unittest.main()
