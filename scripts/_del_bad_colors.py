import json
from pathlib import Path
ROOT = Path(r"C:\Users\zhangcz\Desktop\游戏\识色赋诗")

cs = json.loads((ROOT / "data/colors.json").read_text(encoding="utf-8"))
remove = {"chanlv","nenhui","yuanweilan","yanlan","meihong","danzhe","fupenzihong"}
kept = [c for c in cs if c["pinyin"] not in remove]
print(f"Removed: {len(remove)}")
print(f"  " + ", ".join(c['name'] for c in cs if c['pinyin'] in remove))
(ROOT / "data/colors.json").write_text(
    json.dumps(kept, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# clean orphans
poetry_dir = ROOT / "data/poetry"
valid = {c["pinyin"] for c in kept}
count = 0
for f in poetry_dir.glob("*.json"):
    if f.stem not in valid:
        f.unlink()
        count += 1
print(f"Orphans deleted: {count}")
print(f"Final: {len(kept)} colors, {len(list(poetry_dir.glob('*.json')))} poetry files")
