#!/usr/bin/env python3
"""从 colors.json 生成内嵌色板 js/palette.js，避免 fetch 失败。"""

import json
import math
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
COLORS_PATH = SCRIPT_DIR / "../data/colors.json"
OUT_PATH = SCRIPT_DIR / "../js/palette.js"


def rgb_to_lab(r, g, b):
    def lin(c):
        c /= 255
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92

    rr, gg, bb = lin(r), lin(g), lin(b)
    x = (rr * 0.4124 + gg * 0.3576 + bb * 0.1805) * 100
    y = (rr * 0.2126 + gg * 0.7152 + bb * 0.0722) * 100
    z = (rr * 0.0193 + gg * 0.1192 + bb * 0.9505) * 100

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else (7.787 * t) + (16 / 116)

    fx, fy, fz = f(x / 95.047), f(y / 100), f(z / 108.883)
    return [round((116 * fy) - 16, 4), round(500 * (fx - fy), 4), round(200 * (fy - fz), 4)]


def main():
    colors = json.loads(COLORS_PATH.read_text(encoding="utf-8"))
    seen = set()
    palette = []
    for c in colors:
        key = c["pinyin"]
        if key in seen:
            continue
        seen.add(key)
        r, g, b = c["RGB"]
        palette.append({
            "name": c["name"],
            "pinyin": c["pinyin"],
            "hex": c["hex"],
            "rgb": c["RGB"],
            "lab": rgb_to_lab(r, g, b),
        })

    lines = [
        "/** 自动生成 — 运行 scripts/gen_palette.py 更新 */",
        f"const COLOR_PALETTE = {json.dumps(palette, ensure_ascii=False, separators=(',', ':'))};",
    ]
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"写入 {len(palette)} 色 → {OUT_PATH}")


if __name__ == "__main__":
    main()
