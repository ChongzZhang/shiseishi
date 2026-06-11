"""
色谱寻诗 - 无诗色补诗工具
从唐三百、宋词中为无诗句颜色各找 5 联候选，← 舍弃  → 添加
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
RAW = os.path.join(ROOT, "data", "raw")
PORT = 8770

try:
    from opencc import OpenCC
    CC = OpenCC("t2s")
    def t2s(t):
        return CC.convert(t) if t else t
except ImportError:
    def t2s(t):
        return t


BLACKLIST = re.compile(
    "玄宗|玄武|金陵|金门|金谷|金吾|金石|金舆|黄金|金樽|金屋|金风|金波"
    "|明珠|明月|明星|天明|清明|光明|月明|灯明|明镜|明时|明朝|明日"
    "|青楼|司马青衫|青鸟|踏青|青阳"
    "|白玉|白帝|白衣|白首|白屋|白水"
    "|赤壁|赤帝|赤城|赤松"
    "|黄泉|黄昏|黄花|黄莺|黄鹤"
    "|紫微|紫宸|紫陌|紫府|紫烟"
    "|丹墀|丹陛|丹心|丹青"
    "|碧落|碧空|碧霄|碧海"
    "|红楼|红尘|红颜"
)


def extract_couplets(poem_text):
    poem_text = re.sub(r"\(押\w+韻\)", "", poem_text)
    poem_text = poem_text.replace("○", " ")
    sentences = re.split(r"[。！？]", poem_text)
    couplets = []
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        if "，" not in sent and "," not in sent:
            if len(sent) >= 7 and not BLACKLIST.search(sent):
                couplets.append(sent)
            continue
        halves = [h.strip() for h in re.split(r"[，,]", sent) if h.strip()]
        if len(halves) < 2:
            continue
        for i in range(len(halves) - 1):
            if len(halves[i]) >= 3 and len(halves[i + 1]) >= 3:
                pair = halves[i] + "，" + halves[i + 1]
                if not BLACKLIST.search(pair):
                    couplets.append(pair)
    return couplets


def load_all_couplets():
    """加载唐三百 + 宋词全部联，转简体"""
    results = []

    tang = os.path.join(RAW, "tang300.txt")
    if os.path.exists(tang):
        text = open(tang, encoding="utf-8").read()
        for block in re.split(r"\n(?=詩名:)", text):
            title = author = poem = ""
            for line in block.split("\n"):
                line = line.strip()
                if line.startswith("詩名:"):
                    title = t2s(line[3:].strip())
                elif line.startswith("作者:"):
                    author = t2s(line[3:].strip())
                elif line.startswith("詩文:"):
                    poem = line[3:].strip()
            if poem:
                for cp in extract_couplets(poem):
                    results.append({
                        "line": t2s(cp),
                        "title": title,
                        "author": author,
                        "source": "唐诗三百首",
                    })

    song = os.path.join(RAW, "song300.txt")
    if os.path.exists(song):
        text = open(song, encoding="utf-8").read()
        for block in re.split(r"\n(?=詞牌:)", text):
            title = author = poem = ""
            for line in block.split("\n"):
                line = line.strip()
                if line.startswith("詞牌:"):
                    title = t2s(line[3:].strip())
                elif line.startswith("作者:"):
                    author = t2s(line[3:].strip())
                elif line.startswith("詞文:"):
                    poem = line[3:].strip()
            if poem:
                for cp in extract_couplets(poem):
                    results.append({
                        "line": t2s(cp),
                        "title": title,
                        "author": author,
                        "source": "宋词三百首",
                    })

    return results


def load_existing_lines():
    lines = set()
    poetry_dir = os.path.join(ROOT, "data", "poetry")
    for fn in os.listdir(poetry_dir):
        if not fn.endswith(".json"):
            continue
        data = json.loads(open(os.path.join(poetry_dir, fn), encoding="utf-8").read())
        for e in data.get("entries", []):
            lines.add(e.get("line", "").strip())
    return lines


def match_keywords(color_name):
    """生成搜索关键词，优先级从高到低"""
    name = color_name.strip()
    kws = []
    if len(name) >= 2:
        kws.append(name)
    if len(name) >= 3:
        kws.append(name[:2])
        kws.append(name[1:])
    if len(name) >= 4:
        kws.append(name[:2])
        kws.append(name[2:])
    for ch in name:
        if ch not in kws and len(ch) == 1:
            kws.append(ch)
    # 去重保序
    seen = set()
    out = []
    for k in kws:
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out


def score_match(line, color_name, kw):
    if kw not in line:
        return 0
    score = len(kw) * 10
    if kw == color_name:
        score += 50
    if line.find(kw) == 0:
        score += 5
    return score


def find_candidates(color, all_couplets, existing_lines, limit=5):
    name = color["name"]
    keywords = match_keywords(name)
    scored = []
    seen = set()

    for item in all_couplets:
        line = item["line"]
        if line in existing_lines or line in seen:
            continue
        best = 0
        matched_kw = ""
        for kw in keywords:
            s = score_match(line, name, kw)
            if s > best:
                best = s
                matched_kw = kw
        if best > 0:
            scored.append((best, matched_kw, item))
            seen.add(line)

    scored.sort(key=lambda x: (-x[0], x[2]["line"]))
    return [{"match": m, **item} for _, m, item in scored[:limit]]


def build_queue():
    colors = json.loads(open(os.path.join(ROOT, "data", "colors.json"), encoding="utf-8").read())
    poetry_dir = os.path.join(ROOT, "data", "poetry")
    all_couplets = load_all_couplets()
    existing = load_existing_lines()

    queue = []
    for c in colors:
        fp = os.path.join(poetry_dir, c["pinyin"] + ".json")
        n = 0
        if os.path.exists(fp):
            n = len(json.loads(open(fp, encoding="utf-8").read()).get("entries", []))
        if n > 0:
            continue

        cands = find_candidates(c, all_couplets, existing, limit=5)
        queue.append({
            "name": c["name"],
            "pinyin": c["pinyin"],
            "hex": c["hex"],
            "rgb": c["RGB"],
            "candidates": cands,
            "found": len(cands),
        })

    return queue


# 运行时状态
QUEUE = []
current_color_idx = 0
current_poem_idx = 0
added_count = 0


def regen_frontend():
    script = os.path.join(ROOT, "scripts", "regen_frontend.py")
    subprocess.run([sys.executable, script], cwd=ROOT, check=False)


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = self.path.split("?")[0]
        if parsed in ("/", "/index.html"):
            html = open(os.path.join(ROOT, "_fill_poems.html"), encoding="utf-8").read()
            self._ok("text/html", html.encode("utf-8"))
        elif parsed == "/state":
            self._serve_state()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/accept":
            self._accept()
        elif self.path == "/skip":
            self._skip()
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_state(self):
        global current_color_idx, current_poem_idx, QUEUE, added_count

        if current_color_idx >= len(QUEUE):
            self._ok("application/json", json.dumps({
                "done": True,
                "added": added_count,
                "colors": len(QUEUE),
            }, ensure_ascii=False).encode("utf-8"))
            return

        color = QUEUE[current_color_idx]
        cands = color["candidates"]

        if current_poem_idx >= len(cands) or current_poem_idx >= 5:
            current_color_idx += 1
            current_poem_idx = 0
            self._serve_state()
            return

        if not cands:
            resp = {
                "done": False,
                "empty_color": True,
                "color": {
                    "name": color["name"],
                    "pinyin": color["pinyin"],
                    "hex": color["hex"],
                    "rgb": color["rgb"],
                },
                "color_index": current_color_idx,
                "color_total": len(QUEUE),
                "poem_index": 0,
                "poem_total": 0,
                "added": added_count,
            }
            current_color_idx += 1
            current_poem_idx = 0
            self._ok("application/json", json.dumps(resp, ensure_ascii=False).encode("utf-8"))
            return

        poem = cands[current_poem_idx]
        resp = {
            "done": False,
            "empty_color": False,
            "color": {
                "name": color["name"],
                "pinyin": color["pinyin"],
                "hex": color["hex"],
                "rgb": color["rgb"],
            },
            "poem": {
                "line": poem["line"],
                "title": poem["title"],
                "author": poem["author"],
                "source": poem["source"],
                "match": poem.get("match", ""),
            },
            "color_index": current_color_idx,
            "color_total": len(QUEUE),
            "poem_index": current_poem_idx,
            "poem_total": min(5, len(cands)),
            "found_for_color": color["found"],
            "added": added_count,
        }
        self._ok("application/json", json.dumps(resp, ensure_ascii=False).encode("utf-8"))

    def _accept(self):
        global current_color_idx, current_poem_idx, added_count

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        color = body.get("color", {})
        poem = body.get("poem", {})
        pinyin = color.get("pinyin", "")

        fp = os.path.join(ROOT, "data", "poetry", pinyin + ".json")
        if os.path.exists(fp):
            data = json.loads(open(fp, encoding="utf-8").read())
        else:
            data = {
                "color": color.get("name", ""),
                "pinyin": pinyin,
                "hex": color.get("hex", ""),
                "entries": [],
            }

        data["entries"].append({
            "line": poem.get("line", ""),
            "title": poem.get("title", ""),
            "author": poem.get("author", ""),
            "type": "诗",
            "matchTier": 2,
            "verified": True,
            "source": poem.get("source", ""),
            "_color": color.get("name", ""),
            "_hex": color.get("hex", ""),
        })
        n = len(data["entries"])
        data["coverage"] = f"{min(n, 5)}/5"
        json.dump(data, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        added_count += 1
        current_poem_idx += 1
        regen_frontend()
        self._serve_state()

    def _skip(self):
        global current_poem_idx
        current_poem_idx += 1
        self._serve_state()

    def _ok(self, ct, body):
        self.send_response(200)
        self.send_header("Content-type", f"{ct}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    sys.stdout.write("Building search index...\n")
    sys.stdout.flush()
    QUEUE = build_queue()
    total_cands = sum(c["found"] for c in QUEUE)
    sys.stdout.write(f"Colors without poems: {len(QUEUE)}\n")
    sys.stdout.write(f"Total candidates: {total_cands}\n")
    sys.stdout.write(f"Opening http://127.0.0.1:{PORT}/\n")
    sys.stdout.write("-> add  <- skip\n")
    sys.stdout.flush()

    threading.Timer(0.5, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}/")).start()
    server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\nStopped.\n")
        sys.stdout.flush()
        server.shutdown()
