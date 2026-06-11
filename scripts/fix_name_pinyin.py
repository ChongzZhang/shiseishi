#!/usr/bin/env python3
"""为 colors.json 每条写入正确的 namePinyin（展示用汉语拼音）。"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
COLORS_PATH = ROOT / "data" / "colors.json"

sys.path.insert(0, str(SCRIPT_DIR))
from pinyin_util import name_to_pinyin


def main():
    colors = json.loads(COLORS_PATH.read_text(encoding="utf-8"))
    n = 0
    for c in colors:
        py = name_to_pinyin(c["name"])
        if py and c.get("namePinyin") != py:
            c["namePinyin"] = py
            n += 1
        elif py:
            c["namePinyin"] = py
    COLORS_PATH.write_text(json.dumps(colors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"更新 namePinyin: {n} 条（共 {len(colors)} 色）")


if __name__ == "__main__":
    main()
