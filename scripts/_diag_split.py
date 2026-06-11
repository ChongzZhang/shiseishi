# -*- coding: utf-8 -*-
"""诊断脚本：对于每条诗句，找出色名在句中出现的位置并标注上下文。
标注规则：
  [前字]  → 色名第一个字前面那个字
  【色名】 → 色名本身
  [后字]  → 色名最后一个字后面那个字

输出到 _split_review.txt，供人工审查拆分误配。
"""

import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POETRY = ROOT / "data" / "poetry"

def find_color_in_line(color_name, line):
    """在 line 中查找 color_name 的所有出现位置（含标点清理后的位置映射）"""
    # 清理标点空格，保留原句位置映射
    cleaned = re.sub(r'[，。！？、；：""''（）《》\s]', '', line)
    positions = []
    start = 0
    while True:
        idx = cleaned.find(color_name, start)
        if idx == -1:
            break
        # 映射回原句找到大致位置
        cnt = 0
        orig_pos = 0
        for i, ch in enumerate(line):
            if re.match(r'[，。！？、；：""''（）《》\s]', ch):
                continue
            if cnt == idx + len(color_name):
                break
            if cnt >= idx:
                pass
            cnt += 1
            orig_pos = i + 1
        # 简化：直接标出 cleaned 中的位置，显示原句
        positions.append(idx)
        start = idx + 1
    return positions, cleaned

def context(line, color_name):
    """返回带标记的上下文"""
    cleaned = re.sub(r'[，。！？、；：""''（）《》\s]', '', line)
    results = []
    start = 0
    while True:
        idx = cleaned.find(color_name, start)
        if idx == -1:
            break
        before = cleaned[max(0, idx-1):idx] if idx > 0 else "（句首）"
        after = cleaned[idx+len(color_name):idx+len(color_name)+1] if idx+len(color_name) < len(cleaned) else "（句尾）"
        span = cleaned[idx:idx+len(color_name)]
        results.append(f"    [{before}]【{span}】[{after}]  ← 原文: {line.strip()}")
        start = idx + 1
    return results

def main():
    lines_out = []
    issues = 0
    total_entries = 0

    for f in sorted(POETRY.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        color_name = data["color"]
        entries = data.get("entries", [])
        if not entries:
            continue

        flagged = False
        for i, e in enumerate(entries):
            total_entries += 1
            ctx = context(e["line"], color_name)
            if ctx:
                if not flagged:
                    lines_out.append(f"\n{'='*60}")
                    lines_out.append(f"【{color_name}】{data.get('coverage','')}")
                    flagged = True
                lines_out.extend(ctx)
                issues += 1

    Path(__file__).with_name("_split_review.txt").write_text(
        "\n".join(lines_out), encoding="utf-8"
    )
    print(f"总条目: {total_entries}")
    print(f"含色名的条目: {issues}")
    print(f"输出: _split_review.txt")

if __name__ == "__main__":
    main()
