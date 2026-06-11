#!/usr/bin/env python3
"""从 colors.json 删除所有无诗句的颜色，并清理对应 poetry 文件。"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLORS_PATH = ROOT / "data" / "colors.json"
POETRY_DIR = ROOT / "data" / "poetry"


def has_poems(pinyin: str) -> bool:
    fp = POETRY_DIR / f"{pinyin}.json"
    if not fp.exists():
        return False
    data = json.loads(fp.read_text(encoding="utf-8"))
    return bool(data.get("entries"))


def main():
    colors = json.loads(COLORS_PATH.read_text(encoding="utf-8"))
    kept = []
    removed = []

    for c in colors:
        if has_poems(c["pinyin"]):
            kept.append(c)
        else:
            removed.append(c)
            fp = POETRY_DIR / f"{c['pinyin']}.json"
            if fp.exists():
                fp.unlink()

    COLORS_PATH.write_text(
        json.dumps(kept, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    valid = {c["pinyin"] for c in kept}
    orphans = 0
    for fp in POETRY_DIR.glob("*.json"):
        if fp.stem not in valid:
            fp.unlink()
            orphans += 1

    print(f"删除无诗色名: {len(removed)}")
    for c in removed:
        print(f"  - {c['name']} ({c['pinyin']})")
    if orphans:
        print(f"清理孤立 poetry 文件: {orphans}")
    print(f"保留: {len(kept)} 色")

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "regen_frontend.py")],
        cwd=str(ROOT),
        check=True,
    )


if __name__ == "__main__":
    main()
