import json
from pathlib import Path
ROOT = Path(r"C:\Users\zhangcz\Desktop\游戏\识色赋诗")
poetry_dir = ROOT / "data/poetry"
files = sorted(poetry_dir.glob("*.json"))
total = 0
for f in files:
    data = json.loads(f.read_text(encoding="utf-8"))
    n = len(data.get("entries", []))
    total += n
print(f"JSON files: {len(files)}")
print(f"Total entries: {total}")
