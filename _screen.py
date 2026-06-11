"""
色谱寻诗 - 快速筛选工具
启动后浏览器打开，→ 接受  ← 拒绝
"""
import http.server
import json
import os
import subprocess
import sys
import webbrowser
import threading

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8767

def load_data():
    colors = json.loads(open(os.path.join(ROOT, 'data', 'colors.json'), encoding='utf-8').read())
    poetry_dir = os.path.join(ROOT, 'data', 'poetry')
    items = []
    colors = sorted(colors, key=lambda c: c['name'])
    for c in colors:
        fp = os.path.join(poetry_dir, c['pinyin'] + '.json')
        if os.path.exists(fp):
            pdata = json.loads(open(fp, encoding='utf-8').read())
            entries = pdata.get('entries', [])
            items.append({
                'name': c['name'],
                'pinyin': c['pinyin'],
                'hex': c['hex'],
                'rgb': c['RGB'],
                'poems': [{'line': e['line'], 'title': e.get('title',''), 'author': e.get('author','')} for e in entries]
            })
    return items

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = self.path.split('?')[0]
        if parsed == '/' or parsed == '/index.html':
            html = open(os.path.join(ROOT, '_screen.html'), encoding='utf-8').read()
            self._ok('text/html', html.encode('utf-8'))
        elif parsed == '/data':
            self._ok('application/json', json.dumps(DATA, ensure_ascii=False).encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/save':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length).decode('utf-8'))
            kept = body.get('kept', [])       # [{pinyin,line,title,author}, ...]
            removed = body.get('removed', []) # [{pinyin,line,title,author}, ...]

            poetry_dir = os.path.join(ROOT, 'data', 'poetry')

            # Group kept poems by pinyin
            by_pinyin = {}
            for p in kept:
                by_pinyin.setdefault(p['pinyin'], []).append({
                    'line': p['line'], 'title': p['title'], 'author': p['author'],
                    'type': '诗', 'matchTier': 1, 'verified': True,
                    'source': p.get('source', ''),
                    '_color': p.get('name', ''), '_hex': p.get('hex', '')
                })

            # Read original entries to preserve metadata where possible
            for pinyin, entries in by_pinyin.items():
                fp = os.path.join(poetry_dir, pinyin + '.json')
                if os.path.exists(fp):
                    orig = json.loads(open(fp, encoding='utf-8').read())
                    orig_entries = orig.get('entries', [])
                    # Try to preserve original metadata by line matching
                    enriched = []
                    for e in entries:
                        match = next((oe for oe in orig_entries if oe.get('line') == e['line']), None)
                        if match:
                            enriched.append(match)
                        else:
                            enriched.append(e)
                    orig['entries'] = enriched
                    n = len(enriched)
                    orig['coverage'] = f"{min(n, 5)}/5"
                else:
                    orig = {'entries': entries}
                    n = len(entries)
                    orig['coverage'] = f"{min(n, 5)}/5"
                json.dump(orig, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

            # Delete poems that were removed (remove from file; 色名保留在 colors.json)
            rby_pinyin = {}
            for p in removed:
                rby_pinyin.setdefault(p['pinyin'], []).append(p['line'])

            for pinyin, lines in rby_pinyin.items():
                fp = os.path.join(poetry_dir, pinyin + '.json')
                if os.path.exists(fp):
                    orig = json.loads(open(fp, encoding='utf-8').read())
                    orig['entries'] = [e for e in orig.get('entries', []) if e['line'] not in lines]
                    n = len(orig['entries'])
                    if n:
                        orig['coverage'] = f"{min(n, 5)}/5"
                        json.dump(orig, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
                    else:
                        os.remove(fp)

            colors = json.loads(open(os.path.join(ROOT, 'data', 'colors.json'), encoding='utf-8').read())
            with_poems = 0
            for c in colors:
                fp = os.path.join(poetry_dir, c['pinyin'] + '.json')
                if os.path.exists(fp):
                    pdata = json.loads(open(fp, encoding='utf-8').read())
                    if pdata.get('entries'):
                        with_poems += 1

            subprocess.run(
                [sys.executable, os.path.join(ROOT, 'scripts', 'regen_frontend.py')],
                cwd=ROOT,
                check=False,
            )

            self._ok('application/json', json.dumps({
                'ok': True,
                'poems_kept': len(kept),
                'poems_removed': len(removed),
                'colors': len(colors),
                'colors_with_poems': with_poems,
            }, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def _ok(self, ct, body):
        self.send_response(200)
        self.send_header('Content-type', f'{ct}; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass

if __name__ == '__main__':
    import sys as _sys
    _sys.stdout.write('Loading data...\n'); _sys.stdout.flush()
    DATA = load_data()
    _sys.stdout.write(f'Loaded {len(DATA)} colors\n')
    _sys.stdout.write(f'Opening http://127.0.0.1:{PORT}/\n')
    _sys.stdout.write('-> accept  <- reject\n')
    _sys.stdout.flush()

    threading.Timer(0.5, lambda: webbrowser.open(f'http://127.0.0.1:{PORT}/')).start()

    server = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
    _sys.stdout.write(f'Server started on port {PORT}\n')
    _sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        _sys.stdout.write('\nStopped.\n'); _sys.stdout.flush()
        server.shutdown()
