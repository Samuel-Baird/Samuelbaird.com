#!/usr/bin/env python3
"""Control the dedicated localhost qBittorrent profile; credentials stay in Keychain."""
import argparse
import http.cookiejar
import json
import subprocess
import urllib.parse
import urllib.request

class Client:
    def __init__(self):
        self.base = 'http://127.0.0.1:18765/api/v2/'
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        password = subprocess.run(['security', 'find-generic-password', '-a', 'gsa-worker',
            '-s', 'GSA qBittorrent WebUI', '-w'], capture_output=True, text=True, check=True).stdout.strip()
        self.call('auth/login', {'username': 'gsa-worker', 'password': password})
        self.call('app/version')  # Verify authenticated access; login can return an empty body.

    def call(self, endpoint, data=None):
        body = None if data is None else urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(self.base + endpoint, data=body)
        with self.opener.open(req, timeout=20) as response:
            raw = response.read().decode()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    def status(self):
        prefs = self.call('app/preferences')
        keys = ('current_network_interface', 'save_path', 'temp_path', 'temp_path_enabled',
                'add_stopped_enabled', 'max_active_downloads', 'max_active_torrents',
                'web_ui_address', 'web_ui_port', 'bypass_local_auth', 'upnp', 'dht', 'lsd', 'pex')
        return {'preferences': {k: prefs.get(k) for k in keys},
                'transfer': self.call('transfer/info'), 'torrents': self.call('torrents/info')}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'stop-all'])
    args = parser.parse_args()
    client = Client()
    if args.action == 'stop-all':
        client.call('torrents/stop', {'hashes': 'all'})
        print('Stopped all torrents in the GSA profile.')
    else:
        print(json.dumps(client.status(), indent=2))
