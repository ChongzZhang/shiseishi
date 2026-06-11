"""
色谱寻诗 - 诗句配色工具
后台：解析诗句，预匹配4个颜色，保存用户选择
"""
import http.server
import json
import os
import re
import subprocess
import sys
import webbrowser
import threading

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8769

# ================= 解析诗句 =================

def parse_poems():
    """从 color_poems.txt 解析所有诗句"""
    text = open(os.path.join(ROOT, "data", "color_poems.txt"), encoding="utf-8").read()
    poems = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        # Poem line: starts with 2 spaces, content, no source pattern
        if raw.startswith("  ") and not raw.startswith("    ——") and line and \
           not line.startswith("━━") and not line.startswith("=") and \
           "色谱" not in line and "来源" not in line and "总计" not in line:
            # Next line should be the source
            if i + 1 < len(lines):
                src = lines[i + 1].strip()
                m = re.match(r"——《(.+?)》\s+(.+)", src)
                if m:
                    poems.append({
                        "line": line,
                        "title": m.group(1).strip(),
                        "author": m.group(2).strip(),
                    })
            i += 2
        else:
            i += 1
    return poems


# ================= 颜色匹配 =================

# 颜色字 → 匹配色名的关键词
COLOR_MAP = {
    "红": ["红"], "朱": ["朱"], "赤": ["赤"], "丹": ["丹"], "绛": ["绛"], "绯": ["绯"],
    "殷": ["殷"], "彤": ["彤"], "赭": ["赭"], "茜": ["茜"], "胭": ["胭脂"],
    "绿": ["绿"], "碧": ["碧"], "翠": ["翠"],
    "青": ["青"], "苍": ["苍"], "葱": ["葱绿", "葱青"],
    "蓝": ["蓝"], "靛": ["靛"], "绀": ["绀"],
    "黄": ["黄"], "缃": ["缃"], "橙": ["橙"], "金": ["金黄", "金"],
    "白": ["白"], "素": ["素"], "皓": ["皓"], "皎": ["皎"], "银": ["银"],
    "黑": ["黑"], "乌": ["乌"], "墨": ["墨"], "皂": ["皂"], "玄": ["玄"],
    "紫": ["紫"], "褐": ["褐"], "灰": ["灰"], "粉": ["粉"],
    "黛": ["黛"], "缥": ["缥"], "缟": ["缟"],
}


def match_colors(poem):
    """为一句诗匹配最佳4个颜色"""
    line = poem["line"]
    colors = load_colors()

    # Find color keywords in poem
    found_keywords = set()
    for ch, keywords in COLOR_MAP.items():
        if ch in line:
            found_keywords.update(keywords)

    if not found_keywords:
        # No color word found, fallback to showing random-ish colors
        # Use the first 4 colors as default
        return [(c, 0, "无直接颜色词") for c in colors[:4]]

    # Score each color by how many keywords it matches
    scored = []
    for c in colors:
        cname = c["name"]
        score = 0
        matched = []
        for kw in found_keywords:
            if kw in cname:
                score += len(kw)  # Longer match = better match
                matched.append(kw)
        if score > 0:
            scored.append((c, score, ",".join(matched)))

    scored.sort(key=lambda x: (-x[1], x[0]["name"]))

    # If fewer than 4 matches, pad with neutral colors
    result = scored[:4]
    if len(result) < 4:
        # Add low-score colors as filler
        for c in colors:
            if len(result) >= 4:
                break
            if not any(s[0]["name"] == c["name"] for s in result):
                result.append((c, 0, "—"))

    return result[:4]


def load_colors():
    """加载颜色列表"""
    cs = json.loads(open(os.path.join(ROOT, "data", "colors.json"), encoding="utf-8").read())
    return cs


# ================= HTTP 服务 =================

POEMS = []
COLORS = []
current_index = 0


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = self.path.split("?")[0]
        if parsed in ("/", "/index.html"):
            html = open(os.path.join(ROOT, "_match.html"), encoding="utf-8").read()
            self._ok("text/html", html.encode("utf-8"))
        elif parsed == "/poem":
            self._serve_poem()
        elif parsed == "/reset":
            global current_index
            current_index = 0
            self._ok("application/json", json.dumps({"ok": True}).encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/save":
            self._handle_save()
        elif self.path == "/skip":
            self._handle_skip()
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_poem(self):
        global current_index, POEMS
        if current_index >= len(POEMS):
            self._ok("application/json", json.dumps({"done": True}).encode("utf-8"))
            return

        poem = POEMS[current_index]
        matches = match_colors(poem)

        resp = {
            "index": current_index,
            "total": len(POEMS),
            "poem": poem,
            "matches": [
                {
                    "name": m[0]["name"],
                    "pinyin": m[0]["pinyin"],
                    "hex": m[0]["hex"],
                    "rgb": m[0]["RGB"],
                    "reason": m[2],
                }
                for m in matches
            ],
        }
        self._ok("application/json", json.dumps(resp, ensure_ascii=False).encode("utf-8"))

    def _handle_save(self):
        global current_index
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        choice = body.get("choice", 0)  # 1-4
        poem = body.get("poem", {})

        if choice >= 1 and choice <= 4:
            # Get the current poem's matches
            matches = match_colors(poem)
            if choice <= len(matches):
                color = matches[choice - 1][0]
                pinyin = color["pinyin"]

                # Append poem to color's poetry file
                fp = os.path.join(ROOT, "data", "poetry", pinyin + ".json")
                data = json.loads(open(fp, encoding="utf-8").read()) if os.path.exists(fp) else {"entries": []}
                data["entries"].append({
                    "line": poem["line"],
                    "title": poem["title"],
                    "author": poem["author"],
                    "type": "诗",
                    "matchTier": 2,
                    "verified": True,
                    "_color": color["name"],
                    "_hex": color["hex"],
                })
                n = len(data["entries"])
                data["coverage"] = f"{min(n, 5)}/5"
                json.dump(data, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                subprocess.run(
                    [sys.executable, os.path.join(ROOT, "scripts", "regen_frontend.py")],
                    cwd=ROOT,
                    check=False,
                )

        current_index += 1
        self._serve_poem()

    def _handle_skip(self):
        global current_index
        current_index += 1
        self._serve_poem()

    def _ok(self, ct, body):
        self.send_response(200)
        self.send_header("Content-type", f"{ct}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    sys.stdout.write("Loading poems...\n"); sys.stdout.flush()
    POEMS = parse_poems()
    COLORS = load_colors()
    sys.stdout.write(f"Loaded {len(POEMS)} poems, {len(COLORS)} colors\n")
    sys.stdout.write(f"Opening http://127.0.0.1:{PORT}/\n")
    sys.stdout.write("Press 1-4 to select color, S to skip\n")
    sys.stdout.flush()

    threading.Timer(0.5, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}/")).start()

    server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\nStopped.\n"); sys.stdout.flush()
        server.shutdown()
