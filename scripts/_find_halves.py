import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POETRY_DIR = os.path.join(ROOT, "data", "poetry")

sys.stdout.reconfigure(encoding="utf-8")

half = []
for fn in sorted(os.listdir(POETRY_DIR)):
    if not fn.endswith(".json"):
        continue
    data = json.load(open(os.path.join(POETRY_DIR, fn), encoding="utf-8"))
    for i, e in enumerate(data.get("entries", [])):
        line = e.get("line", "").strip()
        parts = [p.strip() for p in re.split(r"[，,]", line) if p.strip()]
        if len(parts) < 2:
            half.append({
                "file": fn,
                "index": i,
                "color": data.get("color"),
                "pinyin": data.get("pinyin"),
                "line": line,
                "title": e.get("title", ""),
                "author": e.get("author", ""),
            })

print(f"half lines: {len(half)}")
for h in half:
    print(json.dumps(h, ensure_ascii=False))
