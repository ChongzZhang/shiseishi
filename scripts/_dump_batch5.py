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

start = next(i for i, c in enumerate(ordered) if c["pinyin"] == "danlvhui")
out = []
for c in ordered[start : start + 60]:
    p = root / "data/poetry" / f"{c['pinyin']}.json"
    if not p.exists():
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    if not d.get("entries"):
        continue
    out.append(f"\n=== {d['color']} ({c['pinyin']}) ===")
    for i, e in enumerate(d["entries"], 1):
        out.append(f"{i}. {e['line']} | {e['author']}《{e['title']}》")

Path(__file__).with_name("_review_batch5.txt").write_text("\n".join(out), encoding="utf-8")
print("batch5 from idx", start, "nonempty", len([x for x in out if x.startswith("\n===")]))
