# -*- coding: utf-8 -*-
"""删除错误意象条目。只保留能找到确切古诗原文的。找不到的就清空（后续从 colors.json 删除该色名）。"""

import json
from pathlib import Path

ROOT = Path(r"C:\Users\zhangcz\Desktop\游戏\识色赋诗")
POETRY = ROOT / "data/poetry"

def save(pinyin, entries):
    p = POETRY / f"{pinyin}.json"
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    data["entries"] = entries
    data["coverage"] = f"{len(entries)}/5"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def clear(pinyin, reason):
    save(pinyin, [])
    print(f"  CLEAR {pinyin}: {reason}")

# ============================================================
# 清理错误意象
# ============================================================

# 蟾绿 — "蟾绿"是现代小说原创词，古诗中不存在
# 之前的 "明月松间照"、"月出惊山鸟" 和蟾绿毫无关系
clear("chanlv", "现代小说原创色名，古诗中不存在")

# 嫩灰 — "天街小雨润如酥" 是写春雨，"烟笼寒水" 是写秦淮夜景，都不是"灰色"
# 古诗中"嫩灰"不存在，春寒薄雾也不是明确的灰色意象
clear("nenhui", "古诗中无'嫩灰'色名，春雨薄雾不等于灰色")

# 鸢尾蓝 — "石上溪荪发紫茸" 溪荪是紫色不是蓝色
# 鸢尾在唐宋诗中极少见，只有李德裕此句提到且是紫色
clear("yuanweilan", "古诗中鸢尾罕见，仅有一句写紫色，非蓝色")

# 燕蓝 — 燕子+蓝天意象过于牵强
# "几处早莺争暖树，谁家新燕啄春泥" — 春燕确实对，但"蓝"是生硬附加的
# 古诗中不存在"燕蓝"这个概念
clear("yanlan", "古诗中无'燕蓝'色名，燕子意象不等于蓝色")

# 莓红 — "雨久莓苔紫" 是紫色，"小儿垂钓" 只有莓苔没有红色
# "莓红"在古诗中没有直接对应
clear("meihong", "莓苔多为绿色/紫色，非红色")

# 淡赭 — "碧阑干映赭黄袍" 写的是帝王袍色
# 保留作为真实例子，但赭黄袍 ≠ 淡赭
# 淡赭在古诗中确实出现极少，但赭黄是真实颜色词，可保留
save("danzhe", [])  # 暂时清空，等用户决定

# 覆盆子红 — 苏轼信札不是诗
# 重新确认：覆盆子在古诗中几乎没有
clear("fupenzihong", "覆盆子只见于苏轼信札，非诗句")

# 睛蓝 — 这个保留，因为"青天/碧空/晴空"确实是蓝色天空
# 保留
print("  KEEP jinglan: 青天/碧空直接对应蓝天")

# 芽绿 — 保留，草芽/柳芽确实是嫩绿色
print("  KEEP yalv: 草芽/柳芽确实是嫩绿色")

# 苍蓝 — "天苍苍" 苍天=深蓝，"高标跨苍穹" 天空
# 保留
print("  KEEP canglan: 苍天/苍穹直接对应深蓝天色")

# 槿紫 — 槿花是紫色花，真实
print("  KEEP jinzi: 槿花即木槿，真实存在")

# 葡萄酒红 — 葡萄酒确实红色
print("  KEEP putaojiuhong: 葡萄酒直接对应")

# 玫瑰紫 — 玫瑰真实存在
print("  KEEP meiguizi: 玫瑰真实存在")

# 夹竹桃红 — 夹竹桃真实存在
print("  KEEP jiazhutaohong: 夹竹桃真实存在")

# 蛙绿 — 蛙声+绿色田园，确实关联
print("  KEEP walv: 蛙声+绿野直接对应自然绿色")

print("\n===== 清理完成 =====")
print("清空: chanlv nenhui yuanweilan yanlan meihong danzhe fupenzihong (7个)")
print("保留: jinglan yalv canglan jinzi putaojiuhong meiguizi jiazhutaohong walv (8个)")
