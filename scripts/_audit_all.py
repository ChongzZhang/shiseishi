# -*- coding: utf-8 -*-
"""全面审查所有 111 个色名的诗句，输出审查报告到文件。"""

import json, sys, io
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
POETRY = ROOT / "data" / "poetry"
COLORS_PATH = ROOT / "data" / "colors.json"

colors = json.loads(COLORS_PATH.read_text(encoding="utf-8"))

lines_seen = Counter()
long_entries = []
check_entries = []

for c in sorted(colors, key=lambda x: x["pinyin"]):
    pinyin = c["pinyin"]
    name = c["name"]
    p = POETRY / f"{pinyin}.json"
    if not p.exists():
        continue
    data = json.loads(p.read_text(encoding="utf-8"))
    entries = data.get("entries", [])

    for i, e in enumerate(entries):
        line = e.get("line", "")
        author = e.get("author", "")
        title = e.get("title", "")

        lines_seen[line] += 1

        # 1. 长段 > 30 字视为过长
        if len(line) > 30:
            long_entries.append({
                "color": name, "pinyin": pinyin, "idx": i,
                "line": line, "title": title, "author": author,
                "len": len(line),
            })

        # 2. 拆分检测
        cn = name
        if len(cn) == 2:
            idx = line.find(cn)
            if idx >= 0:
                before = line[max(0, idx - 1):idx] if idx > 0 else "(start)"
                after = line[idx + 2:idx + 3] if idx + 2 < len(line) else "(end)"
                # 如果前后都是非标点符号，可能有问题
                check_entries.append({
                    "color": name, "pinyin": pinyin, "idx": i,
                    "line": line, "title": title, "author": author,
                    "context": f"[{before}]{cn}[{after}]",
                })

# ========== 输出 ==========
out = ROOT / "_audit_report.txt"
lines = []

def w(s):
    lines.append(s)
    print(s)

w("=" * 70)
w("重复诗句（被多个色名引用）：")
w("=" * 70)
for line, cnt in lines_seen.most_common():
    if cnt > 1:
        w(f"  [{cnt}x] {line[:100]}")

w(f"\n{'='*70}")
w(f"过长诗句 (>30字) {len(long_entries)} 处：")
w("=" * 70)
for iss in long_entries:
    w(f"  [{iss['len']}字] {iss['color']:8s} | {iss['line'][:80]}")
    w(f"         {iss['title']} - {iss['author']}")

w(f"\n{'='*70}")
w(f"拆分检查 ({len(check_entries)} 处，需人工判断):")
w("=" * 70)
for iss in check_entries:
    w(f"  {iss['color']:8s} {iss['context']:30s} | {iss['line'][:60]}")
    w(f"         {iss['title']} - {iss['author']}")

w(f"\n{'='*70}")
w("每色诗句详情：")
w("=" * 70)
for c in sorted(colors, key=lambda x: x["pinyin"]):
    p = POETRY / f"{c['pinyin']}.json"
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        entries = data.get("entries", [])
        w(f"\n--- {c['name']} ({c['pinyin']}) {len(entries)}条 ---")
        for i, e in enumerate(entries):
            w(f"  [{i}] {e['line'][:100]}")
            w(f"      {e['title']} | {e['author']}")

out.write_text("\n".join(lines), encoding="utf-8")
print(f"\n报告已写入: {out}")
