#!/usr/bin/env python3
"""从 assets/color-bookmarks/new/*.png 生成 manifest.json。"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEW_DIR = ROOT / "assets" / "color-bookmarks" / "new"
COLORS_PATH = ROOT / "data" / "colors.json"
OUT_PATH = NEW_DIR / "manifest.json"

# 不参与成就的书签（拼音）
EXCLUDE_PINYIN = {"mushanzi"}


def load_color_lookup() -> tuple[dict[str, dict], dict[str, dict]]:
    colors = json.loads(COLORS_PATH.read_text(encoding="utf-8"))
    by_pinyin: dict[str, dict] = {}
    by_name: dict[str, dict] = {}
    for c in colors:
        if c.get("pinyin"):
            by_pinyin[c["pinyin"]] = c
        if c.get("name"):
            by_name[c["name"]] = c
    return by_pinyin, by_name


def parse_filename(path: Path) -> tuple[str, str] | None:
    stem = path.stem
    m = re.match(r"^(.+?)_(.+)$", stem)
    if not m:
        return None
    return m.group(1), m.group(2)


def main() -> None:
    by_pinyin, by_name = load_color_lookup()
    entries = []

    for png in sorted(NEW_DIR.glob("*.png")):
        parsed = parse_filename(png)
        if not parsed:
            print(f"  跳过（无法解析文件名）: {png.name}")
            continue
        pinyin, name = parsed
        if pinyin in EXCLUDE_PINYIN:
            print(f"  排除: {png.name}")
            continue

        meta = by_pinyin.get(pinyin) or by_name.get(name)
        hex_val = meta.get("hex", "") if meta else ""
        if not hex_val:
            print(f"  警告 — 未找到 hex: {png.name}")

        entries.append({
            "pinyin": pinyin,
            "name": name,
            "hex": hex_val,
            "file": png.name,
        })

    OUT_PATH.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"已写入 {len(entries)} 条 → {OUT_PATH}")


if __name__ == "__main__":
    main()
