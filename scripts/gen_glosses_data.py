#!/usr/bin/env python3
"""从 data/color_glosses.json 生成 js/glosses-data.js（主站识色卡片用）。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GLOSSES_PATH = ROOT / "data" / "color_glosses.json"
OUT_PATH = ROOT / "js" / "glosses-data.js"


def main() -> None:
    data = json.loads(GLOSSES_PATH.read_text(encoding="utf-8"))
    by_pinyin: dict[str, str] = {}
    for c in data.get("colors", []):
        gloss = c.get("gloss")
        if gloss and not c.get("gloss_skip"):
            by_pinyin[c["pinyin"]] = gloss

    OUT_PATH.write_text(
        "/** 自动生成 — scripts/gen_glosses_data.py */\n"
        f"const COLOR_GLOSSES = {json.dumps(by_pinyin, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )
    print(f"写入 {len(by_pinyin)} 条释义 → {OUT_PATH}")


if __name__ == "__main__":
    main()
