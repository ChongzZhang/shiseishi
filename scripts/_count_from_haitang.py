import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
colors = json.loads((root / "data/colors.json").read_text(encoding="utf-8"))
seen = set()
ordered = []
for c in colors:
    if c["pinyin"] not in seen:
        seen.add(c["pinyin"])
        ordered.append(c)

start = 238  # 海棠红
for i, c in enumerate(ordered[start:], start):
    p = root / "data/poetry" / f"{c['pinyin']}.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        n = len(d.get("entries", []))
        if n > 0:
            print(i, c["name"], c["pinyin"], n)
