import json
from pathlib import Path

root = Path("data")
colors = json.loads((root / "colors.json").read_text(encoding="utf-8"))
poetry_dir = root / "poetry"

print(f"Total: {len(colors)}")
for c in colors:
    p = poetry_dir / f"{c['pinyin']}.json"
    n = 0
    if p.exists():
        n = len(json.loads(p.read_text(encoding="utf-8")).get("entries", []))
    flag = " ★" if n >= 3 else (" +" if n >= 1 else "  ")
    print(f"{flag} {c['name']:12s} {c['pinyin']:25s} RGB{c['RGB']} poems={n}")
