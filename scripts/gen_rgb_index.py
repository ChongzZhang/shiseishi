#!/usr/bin/env python3
"""从 zhongguose_full.json 生成完整 RGB 索引 js/rgb-index-data.js。"""

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
FULL_PATH = ROOT / "data" / "zhongguose_full.json"
COLORS_PATH = ROOT / "data" / "colors.json"
POETRY_INDEX = ROOT / "data" / "poetry-index.json"
OUT_PATH = ROOT / "js" / "rgb-index-data.js"

import sys

sys.path.insert(0, str(SCRIPT_DIR))
from pinyin_util import display_pinyin, name_to_pinyin


def hex_to_rgb(hex_val: str) -> list[int]:
    h = hex_val.lstrip("#")
    if len(h) != 6:
        return [0, 0, 0]
    return [int(h[i : i + 2], 16) for i in (0, 2, 4)]


def flatten_zhongguose() -> list[dict]:
    full = json.loads(FULL_PATH.read_text(encoding="utf-8"))
    rows = []
    seen_hex = set()
    for group in full:
        for c in group.get("colors", []):
            name = (c.get("name") or "").strip()
            hex_val = (c.get("hex") or "").strip().lower()
            if not name or not hex_val or not re.match(r"^#[0-9a-fA-F]{6}$", hex_val):
                continue
            if hex_val in seen_hex:
                continue
            seen_hex.add(hex_val)
            rgb = hex_to_rgb(hex_val)
            rows.append({
                "name": name,
                "hex": hex_val,
                "RGB": rgb,
            })
    return rows


def main():
    game_colors = json.loads(COLORS_PATH.read_text(encoding="utf-8"))
    poetry_index = {}
    if POETRY_INDEX.exists():
        poetry_index = json.loads(POETRY_INDEX.read_text(encoding="utf-8"))

    by_hex = {}
    by_name = {}
    for c in game_colors:
        py = name_to_pinyin(c["name"]) or (
            c["pinyin"] if not re.fullmatch(r"c[0-9a-f]{3,6}", c.get("pinyin", "")) else ""
        )
        entry = {
            **c,
            "namePinyin": py or display_pinyin(c),
            "hasPoetry": bool(poetry_index.get(c["pinyin"])),
            "gameId": c["pinyin"],
        }
        by_hex[c["hex"].lower()] = entry
        by_name[c["name"]] = entry

    index = []
    for row in flatten_zhongguose():
        hex_l = row["hex"].lower()
        game = by_hex.get(hex_l) or by_name.get(row["name"])
        if game:
            item = {
                "name": game["name"],
                "namePinyin": game["namePinyin"],
                "hex": game["hex"],
                "RGB": game["RGB"],
                "hasPoetry": game["hasPoetry"],
                "gameId": game["gameId"],
                "inGame": True,
            }
        else:
            py = name_to_pinyin(row["name"])
            item = {
                "name": row["name"],
                "namePinyin": py,
                "hex": row["hex"],
                "RGB": row["RGB"],
                "hasPoetry": False,
                "gameId": None,
                "inGame": False,
            }
        index.append(item)

    index.sort(key=lambda x: x["name"])

    # 补充游戏色板中有、全库未收录的条目
    indexed_hex = {x["hex"].lower() for x in index}
    for c in game_colors:
        if c["hex"].lower() in indexed_hex:
            continue
        py = display_pinyin({**c, "namePinyin": name_to_pinyin(c["name"])})
        index.append({
            "name": c["name"],
            "namePinyin": py,
            "hex": c["hex"],
            "RGB": c["RGB"],
            "hasPoetry": bool(poetry_index.get(c["pinyin"])),
            "gameId": c["pinyin"],
            "inGame": True,
        })
    index.sort(key=lambda x: x["name"])

    index = [x for x in index if x["hasPoetry"]]

    OUT_PATH.write_text(
        "/** 自动生成 — scripts/gen_rgb_index.py */\n"
        f"const RGB_INDEX_DATA = {json.dumps(index, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )
    in_game = sum(1 for x in index if x["inGame"])
    with_poetry = sum(1 for x in index if x["hasPoetry"])
    print(f"写入 {len(index)} 条 → {OUT_PATH}（游戏色 {in_game}，有诗 {with_poetry}）")


if __name__ == "__main__":
    main()
