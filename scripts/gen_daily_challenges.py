#!/usr/bin/env python3
"""从色诗意象对照.md + new/manifest.json 生成 daily-challenges.json。"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "assets" / "color-bookmarks" / "色诗意象对照.md"
MANIFEST_PATH = ROOT / "assets" / "color-bookmarks" / "new" / "manifest.json"
OUT_PATH = ROOT / "assets" / "color-bookmarks" / "daily-challenges.json"


def parse_md_table(text: str) -> dict[str, dict]:
    """解析总表，按色名索引。"""
    by_name: dict[str, dict] = {}
    in_table = False
    for line in text.splitlines():
        if line.strip().startswith("| 序号 |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.strip().startswith("|") or line.strip().startswith("| ---"):
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 8:
            continue
        try:
            int(cols[0])
        except ValueError:
            continue
        name = cols[1]
        hex_val = cols[2].strip().lower()
        pinyin = cols[3]
        by_name[name] = {
            "name": name,
            "hex": hex_val,
            "pinyin": pinyin,
            "imagery": cols[5],
            "hintLine": cols[6],
            "hintSource": cols[7],
        }
        if line.strip().startswith("|>") or (cols[0] == "" and "说明" in line):
            break
    return by_name


def main() -> None:
    md_text = MD_PATH.read_text(encoding="utf-8")
    by_name = parse_md_table(md_text)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    colors = []
    missing = []
    for entry in manifest:
        name = entry["name"]
        meta = by_name.get(name)
        if not meta:
            missing.append(name)
            meta = {
                "imagery": "",
                "hintLine": "",
                "hintSource": "",
            }
        colors.append({
            "pinyin": entry["pinyin"],
            "name": name,
            "hex": entry.get("hex") or meta.get("hex", ""),
            "file": entry["file"],
            "imagery": meta.get("imagery", ""),
            "hintLine": meta.get("hintLine", ""),
            "hintSource": meta.get("hintSource", ""),
        })

    colors.sort(key=lambda c: c["pinyin"])

    out = {
        "version": 1,
        "timezone": "Asia/Shanghai",
        "epoch": "2026-01-01",
        "colors": colors,
    }
    OUT_PATH.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"已写入 {len(colors)} 色 → {OUT_PATH}")
    if missing:
        print(f"  警告 — md 中未找到意象: {', '.join(missing)}")


if __name__ == "__main__":
    main()
