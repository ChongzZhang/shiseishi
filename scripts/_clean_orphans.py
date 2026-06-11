import json
from pathlib import Path
ROOT = Path(r"C:\Users\zhangcz\Desktop\游戏\识色赋诗")
cs = json.loads((ROOT / "data/colors.json").read_text(encoding="utf-8"))
valid = {c["pinyin"] for c in cs}
poetry_dir = ROOT / "data/poetry"
count = 0
for f in poetry_dir.glob("*.json"):
    if f.stem not in valid:
        f.unlink()
        count += 1
print(f"Deleted {count} orphan poetry files")
# recount
valid_files = sorted(poetry_dir.glob("*.json"))
total = 0
for f in valid_files:
    data = json.loads(f.read_text(encoding="utf-8"))
    total += len(data.get("entries", []))
print(f"Remaining: {len(valid_files)} files, {total} entries")
