"""
色谱寻诗 - 选色工具
从中国色全量数据中筛选新颜色，←拒绝 →录用
"""
import http.server
import json
import os
import sys
import webbrowser
import threading

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8768


def gen_pinyin(name):
    """尝试用 pypinyin，失败则用简单方案"""
    try:
        from pypinyin import pinyin, Style
        parts = pinyin(name, style=Style.NORMAL)
        return "".join(p[0] for p in parts)
    except ImportError:
        pass
    # fallback: simple mapping
    return "c" + hex(abs(hash(name)) % 100000)[2:]


def flatten_all():
    full = json.loads(open(os.path.join(ROOT, "data", "zhongguose_full.json"), encoding="utf-8").read())
    result = []
    seen = set()
    for group in full:
        for c in group.get("colors", []):
            name = c.get("name", "").strip()
            hex_val = c.get("hex", "").strip()
            if name and hex_val and len(name) <= 6 and hex_val not in seen:
                seen.add(hex_val)
                result.append({"name": name, "hex": hex_val})
    return result


def find_new_colors():
    all_colors = flatten_all()
    existing_colors = json.loads(open(os.path.join(ROOT, "data", "colors.json"), encoding="utf-8").read())
    existing_pinyin = {c["pinyin"] for c in existing_colors}
    existing_hex = {c["hex"].lower() for c in existing_colors}
    existing_names = {c["name"] for c in existing_colors}

    new_colors = []
    used_pinyin = set(existing_pinyin)
    for c in all_colors:
        if c["hex"].lower() in existing_hex:
            continue
        if c["name"] in existing_names:
            continue
        p = gen_pinyin(c["name"])
        # deduplicate pinyin
        orig = p
        n = 1
        while p in used_pinyin:
            p = f"{orig}{n}"
            n += 1
        used_pinyin.add(p)
        new_colors.append({"name": c["name"], "hex": c["hex"], "pinyin": p})

    return new_colors


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = self.path.split("?")[0]
        if parsed in ("/", "/index.html"):
            html = open(os.path.join(ROOT, "_screen_color.html"), encoding="utf-8").read()
            self._ok("text/html", html.encode("utf-8"))
        elif parsed == "/data":
            self._ok("application/json", json.dumps(NEW_COLORS, ensure_ascii=False).encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/save":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            accepted = body.get("accepted", [])

            cs = json.loads(open(os.path.join(ROOT, "data", "colors.json"), encoding="utf-8").read())

            for item in accepted:
                name = item["name"]
                hex_val = item["hex"]
                pinyin = item["pinyin"]
                h = hex_val.lstrip("#")
                r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                c_val = m_val = y_val = k_val = 0
                if max(r, g, b) > 0:
                    rp, gp, bp = r / 255, g / 255, b / 255
                    k_val = round((1 - max(rp, gp, bp)) * 100)
                    if k_val < 100:
                        c_val = max(0, round((1 - rp - k_val / 100) / (1 - k_val / 100) * 100))
                        m_val = max(0, round((1 - gp - k_val / 100) / (1 - k_val / 100) * 100))
                        y_val = max(0, round((1 - bp - k_val / 100) / (1 - k_val / 100) * 100))
                cs.append({
                    "name": name, "pinyin": pinyin, "hex": hex_val,
                    "RGB": [r, g, b], "CMYK": [c_val, m_val, y_val, k_val],
                })

            cs.sort(key=lambda x: x["name"])
            json.dump(cs, open(os.path.join(ROOT, "data", "colors.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)

            self._ok("application/json", json.dumps({
                "ok": True, "accepted": len(accepted), "total": len(cs),
            }, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def _ok(self, ct, body):
        self.send_response(200)
        self.send_header("Content-type", f"{ct}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    sys.stdout.write("Loading full Chinese color database...\n")
    sys.stdout.flush()
    try:
        import pypinyin
        sys.stdout.write("pypinyin OK\n")
    except ImportError:
        sys.stdout.write("pypinyin not installed, using fallback pinyin\n")
    NEW_COLORS = find_new_colors()
    sys.stdout.write(f"Found {len(NEW_COLORS)} new colors\n")
    sys.stdout.write(f"Opening http://127.0.0.1:{PORT}/\n")
    sys.stdout.write("-> accept  <- reject\n")
    sys.stdout.flush()

    threading.Timer(0.5, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}/")).start()

    server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    sys.stdout.write(f"Server on port {PORT}\n")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\nStopped.\n")
        sys.stdout.flush()
        server.shutdown()
