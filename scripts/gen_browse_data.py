#!/usr/bin/env python3
"""生成内嵌数据 js/colors-data.js 与 js/poetry-bundle.js，browse 页无需 fetch。"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from dynasty import infer_dynasty
from pinyin_util import name_to_pinyin
ROOT = SCRIPT_DIR.parent
COLORS_PATH = ROOT / "data/colors.json"
POETRY_DIR = ROOT / "data/poetry"
INDEX_PATH = ROOT / "data/poetry-index.json"
PREVIEW_PATH = ROOT / "data/poetry-preview.txt"
OUT_COLORS = ROOT / "js/colors-data.js"
OUT_POETRY = ROOT / "js/poetry-bundle.js"


def load_poetry_library():
    library = {}
    for path in sorted(POETRY_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        pinyin = data.get("pinyin") or path.stem
        entries = data.get("entries") or []
        enriched = []
        for e in entries:
            item = dict(e)
            item["dynasty"] = infer_dynasty(item)
            enriched.append(item)
        n = len(enriched)
        coverage = data.get("coverage")
        if not coverage or coverage == "0/5" and n:
            coverage = f"{min(n, 5)}/5"
        library[pinyin] = {
            "color": data.get("color", pinyin),
            "pinyin": pinyin,
            "hex": data.get("hex", "#888888"),
            "coverage": coverage,
            "entries": enriched,
        }
    return library


def sync_poetry_index(colors, library):
    """按 colors.json 的拼音与 poetry 文件实际条目，重建 poetry-index.json。"""
    index = {}
    for c in colors:
        p = c["pinyin"]
        index[p] = bool(library.get(p, {}).get("entries"))
    INDEX_PATH.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return index


def write_preview(library, index):
    lines = [
        "识色赋诗 — 诗句库文字预览",
        "=" * 40,
        f"总计颜色文件: {len(library)}",
        f"有诗句: {sum(1 for v in index.values() if v)}",
        f"满覆盖 5/5: {sum(1 for p, d in library.items() if d.get('coverage') == '5/5')}",
        "",
        "以下为例条（完整数据见 data/poetry/*.json）",
        "",
    ]
    samples = [
        "yanzhihong", "tianlan", "cuilv", "dianqing", "yuebai",
        "zhuhong", "meiguihong", "molihuang", "qianhui", "anlan",
    ]
    for pinyin in samples:
        d = library.get(pinyin)
        if not d or not d["entries"]:
            continue
        lines.append(f"【{d['color']}】{d['hex']}  ({d['coverage']})")
        for e in d["entries"]:
            lines.append(f"  · {e['line']}")
            lines.append(f"    —— {e['author']}《{e['title']}》")
        lines.append("")

    PREVIEW_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"预览 → {PREVIEW_PATH}")


def enrich_colors(colors):
    out = []
    for c in colors:
        item = dict(c)
        if not item.get("namePinyin"):
            item["namePinyin"] = name_to_pinyin(item.get("name", ""))
        out.append(item)
    return out


def main():
    colors = enrich_colors(json.loads(COLORS_PATH.read_text(encoding="utf-8")))
    library = load_poetry_library()
    index = sync_poetry_index(colors, library)

    OUT_COLORS.write_text(
        "/** 自动生成 — scripts/gen_browse_data.py */\n"
        f"const COLORS_DATA = {json.dumps(colors, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )
    OUT_POETRY.write_text(
        "/** 自动生成 — scripts/gen_browse_data.py */\n"
        f"const POETRY_LIBRARY = {json.dumps(library, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )
    write_preview(library, index)
    with_poems = sum(1 for v in index.values() if v)
    print(f"写入 {len(colors)} 色 → {OUT_COLORS}")
    print(f"写入 {len(library)} 色诗句 → {OUT_POETRY}")
    print(f"同步索引 → {INDEX_PATH}（{with_poems} 有诗 / {len(index) - with_poems} 无诗）")


if __name__ == "__main__":
    main()
