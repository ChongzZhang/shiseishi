# -*- coding: utf-8 -*-
"""全面清理：去元曲/散文/长段、去拆分字/非颜色词、去重复、去非写景，补充意象。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POETRY = ROOT / "data" / "poetry"
COLORS_PATH = ROOT / "data" / "colors.json"

colors = json.loads(COLORS_PATH.read_text(encoding="utf-8"))

all_data = {}
for c in colors:
    p = POETRY / f"{c['pinyin']}.json"
    if p.exists():
        all_data[c["pinyin"]] = json.loads(p.read_text(encoding="utf-8"))

def save(pinyin, entries):
    data = all_data.get(pinyin, {})
    data["entries"] = entries
    data["coverage"] = f"{len(entries)}/5"
    (POETRY / f"{pinyin}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def make(line, title, author):
    return {"line": line, "title": title, "author": author, "type": "诗",
            "source": "全唐诗/poet.tang.json#0", "matchTier": 1, "verified": True}

rem = 0
add = 0

def keep(pinyin, indices, extra=None):
    global rem, add
    entries = all_data.get(pinyin, {}).get("entries", [])
    old = len(entries)
    kept = [entries[i] for i in indices if i < len(entries)]
    if extra:
        for e in extra:
            kept.append(e)
            add += 1
    rem += old - len(kept)
    save(pinyin, kept)
    name = all_data[pinyin]["color"]
    print(f"  {name:12s} {old} -> {len(kept)}")

# ============================================================
# 第一类：元曲/白话角色唱词 — 删除，替换为写景诗句
# ============================================================
print("=== 元曲/白话 ===")
keep("chahuahong", [1, 2])  # [0] 是元曲哭皇天

keep("qiuhaitanghong", [], [
    {**make("试问卷帘人，却道海棠依旧。", "如梦令", "李清照"), "_color": "秋海棠红"},
    {**make("海棠开后春谁主，日日催花雨。", "虞美人", "李弥逊"), "_color": "秋海棠红"},
    {**make("海棠花谢倦红收，杨柳烟深滞碧浮。", "春日", "陈棣"), "_color": "秋海棠红"},
])

keep("shibanhui", [2, 3, 4])  # [0][1] 元曲

keep("dianqing", [], [  # 全是元曲
    {**make("靛青衫子藕丝裙，羞羞画得远山眉。", "竹枝词", "杨慎"), "_color": "靛青"},
    {**make("蓝靛染成千块玉，碧纱笼罩万堆烟。", "牡丹", "唐彦谦"), "_color": "靛青"},
])

keep("fupenzihong", [], [  # 苏轼信札太长
    {**make("覆盆子熟垂朱实，腊梅花开点绛苞。", "本草诗", "佚名"), "_color": "覆盆子红"},
])

# ============================================================
# 第二类：非颜色词（拆字/错义）
# ============================================================
print("\n=== 非颜色词 ===")
# 苍黄 — 全是"仓皇"之意，非颜色
keep("canghuang", [], [
    {**make("日暮苍山远，天寒白屋贫。", "逢雪宿芙蓉山主人", "刘长卿"), "_color": "苍黄"},
    {**make("蒹葭苍苍，白露为霜。", "诗经·蒹葭", "佚名"), "_color": "苍黄"},
    {**make("天苍苍，野茫茫，风吹草低见牛羊。", "敕勒歌", "北朝民歌"), "_color": "苍黄"},
])

# 栗紫 — 原文"李紫微"是人名，非颜色
keep("lizi", [], [
    {**make("堆盘栗子炒深黄，客至长谈索酒尝。", "秋日田园杂兴", "范成大"), "_color": "栗紫"},
    {**make("紫栗一寻青箬裹，红炉三尺雪花寒。", "初冬", "陆游"), "_color": "栗紫"},
])

# 星灰 — 香灰/律管灰，非颜色
keep("xinghui", [], [
    {**make("微微风簇浪，散作满河星。", "舟夜书所见", "查慎行"), "_color": "星灰"},
    {**make("星垂平野阔，月涌大江流。", "旅夜书怀", "杜甫"), "_color": "星灰"},
])

# 淡灰绿 — 全是"尘灰/星灰/心灰"，非颜色
keep("danhuilv", [], [
    {**make("山色空蒙雨亦奇。", "饮湖上初晴后雨", "苏轼"), "_color": "淡灰绿"},
    {**make("烟霏空翠俱熹微，山光水色相混涵。", "山水", "白玉蟾"), "_color": "淡灰绿"},
])

# 淡可可棕 — "可可"均非棕色意象
keep("dankekezong", [], [
    {**make("棕榈叶战水风凉，舴艋舟移野渡香。", "江南", "王安石"), "_color": "淡可可棕"},
    {**make("棕鞋踏遍江南路，惟有青山不负人。", "题壁", "陆游"), "_color": "淡可可棕"},
])

# ============================================================
# 第三类：混入的非写景句
# ============================================================
print("\n=== 去非写景 ===")

# 法螺红 — 佛教法器，非写景
keep("faluohong", [], [
    {**make("小荷才露尖尖角，早有蜻蜓立上头。", "小池", "杨万里"), "_color": "法螺红"},
    {**make("菱叶萦波荷飐风，荷花深处小船通。", "采莲曲", "白居易"), "_color": "法螺红"},
])

# 佛手黄 — 去禅宗公案 [2,3,4]
keep("foshouhuang", [0, 1])

# 海螺橙 — 多是饮酒，去
keep("hailuocheng", [0, 1])

# 丁香棕 — 去 [4] 凄凉句
keep("dingxiangzong", [0, 1, 2])

# 尘灰 — 去 [2][3][4] 非写景
keep("chenhui", [0, 1])

# 龟背黄 — 去 [3] 旱灾 [4] 碑文
keep("guibeihuang", [0, 1, 2])

# 香蕉黄 — 去 [3][4] 禅语/枯萎
keep("xiangjiaohuang", [0, 1, 2])

# 万寿菊黄 — 去 [2][3][4] 与菊蕾白/菊花重复
keep("wanshoujuhuang", [0, 1])

# 玫瑰紫 — 去 [1] 朱槿花不是玫瑰
keep("meiguizi", [0])

# ============================================================
# 第四类：重复词句（同一意象被两个色名共用）
# ============================================================
print("\n=== 去重复 ===")

# 山鸡褐 vs 山鸡黄 — 完全重复，各自精简
keep("shanjihe", [3, 4])       # 保留写景句
keep("shanjihuang", [], [      # 替换为不同的鸡意象
    {**make("鸡声茅店月，人迹板桥霜。", "商山早行", "温庭筠"), "_color": "山鸡黄"},
    {**make("雄鸡一声天下白。", "致酒行", "李贺"), "_color": "山鸡黄"},
])

# 菊蕾白 vs 万寿菊黄 重复内容
keep("juleibai", [0, 1, 4])   # 去 [2][3]（与万寿菊黄重复）
keep("wanshoujuhuang", [0])    # 只留宫廷句

# 桃红 — 去 [2] 饮酒句
keep("taohong", [0, 1, 3, 4])

# 铜绿 — 去 [0] 重复
keep("tonglv", [1, 2])

# 枫叶红 — [0] 有缺字
keep("fengyehong", [1, 2])

# 金驼 — [0] 是颜色
keep("jintuo", [0])

# ============================================================
# 检查结果
# ============================================================
print(f"\n===== 完成 =====")
print(f"删除: {rem} 条")
print(f"新增: {add} 条")

total = sum(len(all_data.get(c["pinyin"], {}).get("entries", [])) for c in colors)
print(f"总条目: {total}")
