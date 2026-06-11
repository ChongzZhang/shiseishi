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

idx = next(i for i, c in enumerate(ordered) if c["name"] == "海棠红")
print("idx", idx, "total", len(ordered))
for c in ordered[idx : idx + 100]:
    p = root / "data/poetry" / f"{c['pinyin']}.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        n = len(d.get("entries", []))
        print(c["name"], c["pinyin"], n, d.get("coverage", ""))
