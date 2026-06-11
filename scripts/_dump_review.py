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

start = next(i for i, c in enumerate(ordered) if c["name"] == "海棠红")
out = []
for c in ordered[start : start + 50]:
    p = root / "data/poetry" / f"{c['pinyin']}.json"
    if not p.exists():
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    out.append(f"\n=== {d['color']} ({c['pinyin']}) ===")
    for i, e in enumerate(d.get("entries", []), 1):
        out.append(f"{i}. {e['line']} | {e['author']}《{e['title']}》 tier{e.get('matchTier', '?')}")

Path(__file__).with_name("_review_batch.txt").write_text("\n".join(out), encoding="utf-8")
print("written", len(out), "lines")
