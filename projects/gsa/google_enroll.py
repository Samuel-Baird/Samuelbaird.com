"""Enroll a Desktop OAuth client using a private secret file and native Keychain."""
import argparse
import base64
import ctypes
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
import subprocess
import time
import urllib.parse
import urllib.request
import webbrowser

SCOPES = ' '.join('https://www.googleapis.com/auth/' + s for s in (
    'forms.body.readonly', 'forms.responses.readonly', 'spreadsheets.readonly', 'documents.readonly'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-id')
    parser.add_argument('--client-secret-file', type=Path)
    parser.add_argument('--test-client-from', type=Path, help='Reuse an intake desktop client for a separate drive.file test credential')
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    scopes = SCOPES
    if args.test_client_from:
        source = json.loads(args.test_client_from.read_text())
        if source['keychain_service'] == config['keychain_service']:
            parser.error('Use a separate publication-test Keychain service')
        saved = subprocess.run(['security', 'find-generic-password', '-s', source['keychain_service'],
                                '-a', source['keychain_account'], '-w'], capture_output=True, check=True)
        client = json.loads(saved.stdout)
        args.client_id, client_secret = client['client_id'], client['client_secret']
        scopes = 'https://www.googleapis.com/auth/drive.file'
    elif args.client_id and args.client_secret_file:
        client_secret = args.client_secret_file.read_text().strip()
    else:
        parser.error('Supply the desktop client or --test-client-from')
    if not args.client_id.endswith('.apps.googleusercontent.com'):
        raise SystemExit('Expected a Google OAuth client ID.')
    state, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(64)
    result = {}

    class Callback(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            values = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if values.get('state') != [state]:
                self.send_error(400)
                return
            result.update(values)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Authorization response received. Return to T3 Code.')

    with HTTPServer(('127.0.0.1', 0), Callback) as server:
        server.timeout = 1
        redirect = f'http://127.0.0.1:{server.server_port}/'
        params = dict(client_id=args.client_id, redirect_uri=redirect, response_type='code',
                      scope=scopes, access_type='offline', prompt='consent', state=state,
                      code_challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('='),
                      code_challenge_method='S256')
        webbrowser.open('https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params))
        print('Waiting for Google consent in the browser.', flush=True)
        deadline = time.monotonic() + 600
        while not result and time.monotonic() < deadline:
            server.handle_request()
    if 'code' not in result:
        raise SystemExit('Consent incomplete; credentials were not stored.')
    payload = urllib.parse.urlencode(dict(client_id=args.client_id, client_secret=client_secret,
        code=result['code'][0], code_verifier=verifier, redirect_uri=redirect, grant_type='authorization_code')).encode()
    with urllib.request.urlopen('https://oauth2.googleapis.com/token', data=payload, timeout=30) as response:
        token = json.load(response)
    if not token.get('refresh_token'):
        raise SystemExit('No refresh token received; credentials were not stored.')
    if not set(scopes.split()).issubset(set(token.get('scope', '').split())):
        raise SystemExit('Required scopes were not all granted; credentials were not stored.')
    raw = json.dumps(dict(client_id=args.client_id, client_secret=client_secret, refresh_token=token['refresh_token'])).encode()
    security = ctypes.CDLL('/System/Library/Frameworks/Security.framework/Security')
    add = security.SecKeychainAddGenericPassword
    add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
    add.restype = ctypes.c_int32
    service, account = config['keychain_service'].encode(), config['keychain_account'].encode()
    status = add(None, len(service), service, len(account), account, len(raw), raw, None)
    if status:
        raise SystemExit(f'Keychain storage failed ({status}); existing items were preserved.')
    print('Worker OAuth credentials saved in Keychain.')

if __name__ == '__main__':
    main()
