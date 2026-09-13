"""Loopback-only form for saving explicitly supplied public browser captures."""
import argparse
import base64
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
from urllib.parse import urlparse
from collect_source_originals import now, read_jsonl, save_object


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    targets = json.loads((root / 'data/source-recovery-targets.json').read_text(encoding='utf-8'))['targets']
    allowed = {row['canonical_url']: row['prior'] for row in targets}
    token = secrets.token_urlsafe(32)
    endpoint = '/capture/' + token
    log = root / 'source-originals/recovery-inapp.jsonl'

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            if self.path != endpoint:
                self.send_error(404)
                return
            page = '''<!doctype html><meta charset="utf-8"><title>Local Source Archive</title>
<label for="capture">Capture JSON</label><textarea id="capture" style="display:block;width:95%;height:300px"></textarea>
<button id="save">Archive capture</button><pre id="result"></pre>
<script>document.querySelector('#save').onclick=async()=>{
const r=await fetch(location.pathname,{method:'POST',headers:{'Content-Type':'application/json'},body:document.querySelector('#capture').value});
document.querySelector('#result').textContent=await r.text();};</script>'''
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(page.encode())

        def do_POST(self):
            origin = f'http://127.0.0.1:{self.server.server_port}'
            if self.path != endpoint or self.headers.get('Origin') != origin:
                self.send_error(403)
                return
            length = int(self.headers.get('Content-Length', '0'))
            if not 1 <= length <= 60_000_000:
                self.send_error(413)
                return
            try:
                payload = json.loads(self.rfile.read(length))
                url = payload['canonical_url']
                if url not in allowed:
                    raise ValueError('Source URL is not in the explicitly authorised recovery cohort')
                if urlparse(payload['response_url']).scheme != 'https':
                    raise ValueError('The captured source must be HTTPS')
                text = payload['text']
                if not isinstance(text, str) or len(text) < 40:
                    raise ValueError('Empty or implausibly short source text')
                if re_error_page(payload.get('title', ''), text):
                    raise ValueError('Access/error page is not source evidence')
                representation = payload.get('representation', 'browser-rendered-html-and-text')
                snapshot = payload.get('html') or text
                source_path, source_hash = save_object(root, snapshot.encode('utf-8'), '.html' if payload.get('html') else '.txt')
                units = payload.get('units') or [{'locator': 'browser:' + payload.get('selector', 'document'), 'text': text}]
                text_path, text_hash = save_object(root, (json.dumps(units, ensure_ascii=True, indent=2) + '\n').encode(), '.json')
                prior = allowed[url]
                row = {key: prior[key] for key in ('canonical_url', 'references', 'source_family_ids', 'discovery_depth', 'discovered_from')}
                row.update({'capture_status': 'browser-text-preserved', 'recovery_status': 'captured',
                            'acquisition_method': 'inapp-browser-rendered-text', 'representation': representation,
                            'retrieved_at': payload['captured_at'], 'imported_at': now(),
                            'response_url': payload['response_url'], 'title': payload.get('title', ''),
                            'snapshot_path': source_path, 'sha256': source_hash,
                            'text_path': text_path, 'text_sha256': text_hash, 'text_character_count': len(text),
                            'content_type': 'text/html' if payload.get('html') else 'text/plain',
                            'extraction_status': 'extracted-unreviewed', 'content_class': 'browser-rendering-completeness-unreviewed',
                            'legal_review_status': 'not-reviewed', 'current_law_release': False,
                            'redistribution_status': 'not-cleared', 'links': payload.get('links', []),
                            'browser_capture_provenance': {'selector': payload.get('selector'), 'observed_characters': len(text),
                                                           'source_url': payload['response_url']}})
                if payload.get('screenshot_base64'):
                    image = base64.b64decode(payload['screenshot_base64'], validate=True)
                    suffix = '.png' if image.startswith(b'\x89PNG\r\n\x1a\n') else '.jpg' if image.startswith(b'\xff\xd8\xff') else None
                    if not suffix:
                        raise ValueError('Screenshot must be an unmodified PNG or JPEG')
                    row['screenshot_path'], row['screenshot_sha256'] = save_object(root, image, suffix)
                if payload.get('source_relation'):
                    row['source_relation'] = payload['source_relation']
                with log.open('a', encoding='utf-8', newline='\n') as handle:
                    handle.write(json.dumps(row, ensure_ascii=True) + '\n')
                result = {'saved': True, 'url': url, 'characters': len(text), 'sha256': source_hash}
                self.send_response(200)
            except Exception as exc:
                result = {'saved': False, 'error': f'{type(exc).__name__}: {exc}'}
                self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            print(json.dumps(result), flush=True)

    server = HTTPServer(('127.0.0.1', 0), Handler)
    print(json.dumps({'local_capture_url': f'http://127.0.0.1:{server.server_port}{endpoint}'}), flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def re_error_page(title, text):
    import re
    return bool(re.search(r'just a moment|access denied|page not found|^404\b|request rejected', title, re.I))


if __name__ == '__main__':
    main()
