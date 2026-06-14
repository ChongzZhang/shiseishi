#!/usr/bin/env python3
"""从 vendor 作者表 + 语料库作者，导出 data/author-dynasty.json（供 GitHub Pages 无 vendor 时使用）。"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from dynasty import MANUAL_AUTHOR, load_author_dynasty

ROOT = SCRIPT_DIR.parent
POETRY_DIR = ROOT / "data" / "poetry"
OUT = ROOT / "data" / "author-dynasty.json"

# vendor 中未收录的语料作者
EXTRA = {
    "北朝民歌": "北朝",
    "陆叡": "宋",
    "高文秀": "元",
    "周邦彦": "宋",
}


def main():
    full = load_author_dynasty()
    corpus: set[str] = set()
    for path in POETRY_DIR.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        for e in data.get("entries", []):
            a = (e.get("author") or "").strip()
            if a:
                corpus.add(a)

    embedded: dict[str, str] = {}
    for author in sorted(corpus):
        if author in full:
            embedded[author] = full[author]
        elif author in MANUAL_AUTHOR:
            embedded[author] = MANUAL_AUTHOR[author]
    for author in corpus:
        if author in EXTRA:
            embedded[author] = EXTRA[author]
    for author in corpus:
        if author in MANUAL_AUTHOR:
            embedded[author] = MANUAL_AUTHOR[author]

    missing = sorted(corpus - set(embedded))
    OUT.write_text(json.dumps(embedded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"写入 {len(embedded)} 位作者 → {OUT}")
    if missing:
        print(f"仍缺失 {len(missing)} 位: {', '.join(missing)}")


if __name__ == "__main__":
    main()
