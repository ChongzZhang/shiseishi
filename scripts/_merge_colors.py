# -*- coding: utf-8 -*-
"""
合并相近色 + 删现代色名，目标从 519 → ~130。
策略：
  1. 给每个色打分（诗句数 + 非现代名加分）
  2. 按 RGB 距离聚类，每个聚类保留最高分的色
  3. 零诗句且现代名直接剔除
"""

import json, math
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
POETRY = ROOT / "data" / "poetry"

# ---- 现代/工业色名特征词 ----
MODERN_TOKENS = [
    "电气石", "尼罗", "海军", "柏林", "大理", "嘉陵", "飞燕",
    "羽扇", "胆矾", "钴", "锌", "景泰", "安安", "品蓝", "品红",
    "战舰", "钢蓝", "钢青",
    "番茄", "咖啡", "可可",
    "蛋白石", "汉白玉",
    "宫殿", "田园", "草原",
    "麦苗", "苹果", "薄荷", "瓦松", "田螺", "白屈菜",
    "河豚", "蒽油", "槲寄生", "云杉", "艾背",
    "鹦鹉", "油绿", "槐花黄绿",
    "牛角", "水牛", "沙鱼", "海参", "鲸鱼", "鱼尾",
    "玛瑙", "野菊", "满天星", "野葡萄", "龙葵", "暗龙胆",
    "剑锋", "山梗", "螺甸", "晶石",
    "古鼎", "乌梅", "芡食",
    "黄昏", "狼烟", "长石", "莽丛", "松霜", "嫩菊", "玉髓", "海沬",
    "芽绿", "蝶黄", "鱼肚", "珍珠灰", "雁灰",
    "淡牵牛", "凤信", "萝兰", "芝兰", "菱锰", "龙须",
    "洋葱", "海象", "古铜紫",
    "扁豆花", "白芨", "嫩菱", "菠根", "酢酱草",
    "鹞冠", "磨石", "火鹅", "晶红",
    "暗紫苑", "金鱼紫", "草珠", "高粱", "满江",
    "暗蓝紫", "淡蓝紫", "远天蓝", "星蓝", "湖水蓝", "秋波蓝", "涧石蓝",
    "虹蓝", "晴山蓝", "蝶翅", "海涛", "云水", "云山",
    "远山紫", "淡青紫", "青蛤壳", "豆蔻紫", "扁豆紫", "芥花紫",
    "葛巾紫", "牵牛紫", "龙睛鱼", "荸荠紫",
    "淡藤萝", "藤萝紫", "淡蓝灰", "云峰白", "井天蓝", "鸥蓝",
    "月影白", "星灰", "清水蓝", "瀑布蓝", "孔雀蓝", "竹篁绿",
    "美蝶绿", "蔻梢绿", "蓝绿", "翠蓝", "冰山蓝", "虾壳青",
    "晚波蓝", "蜻蜓蓝", "玉鈫蓝", "夏云灰", "灰蓝", "深灰蓝",
    "玉簪绿", "青矾绿", "草原远绿", "梧枝绿", "浪花绿", "海王绿",
    "明灰", "淡绿灰", "飞泉绿", "深海绿", "淡翠绿", "明绿",
    "翠绿", "淡绿", "葱绿", "孔雀绿", "艾绿",
    "松霜绿", "蛋白石绿", "薄荷绿", "瓦松绿", "荷叶绿",
    "田螺绿", "白屈菜绿", "河豚灰", "蒽油绿", "槲寄生绿",
    "云杉绿", "嫩菊绿", "艾背绿", "嘉陵水绿", "玉髓绿", "鲜绿",
    "宝石绿", "海沬绿", "橄榄石绿", "芦苇绿", "槐花黄绿",
    "苹果绿", "芽绿", "蝶黄", "橄榄黄绿", "鹦鹉绿",
    "象牙白", "汉白玉", "鱼肚白", "珍珠灰", "雁灰",
    "云水蓝", "晴山蓝", "涧石蓝", "蝶翅蓝", "海涛蓝",
    "燕颔蓝", "牵牛花蓝", "飞燕草蓝",
    "海天蓝", "远天蓝", "井天蓝", "云峰白", "月影白",
    "鸥蓝", "孔雀蓝", "清水蓝", "瀑布蓝",
    "竹篁绿", "美蝶绿", "蔻梢绿",
    "蓟粉红", "樱草紫", "芦穗灰", "隐红灰", "苋菜紫", "暮云灰", "斑鸠灰",
    "丁香淡紫", "丹紫红", "深牵牛紫",
    "暗龙胆紫", "晶石紫", "尼罗蓝", "远天蓝", "羽扇豆蓝", "柏林蓝",
    "飞燕草蓝", "安安蓝", "鲸鱼灰", "海参灰", "沙鱼灰",
    "水牛灰", "牛角灰", "战舰灰", "瓦罐灰",
    "暗蓝", "鸽蓝", # 暗蓝只有1条，鸽蓝也不行
]

def is_modern(name):
    for t in MODERN_TOKENS:
        if t in name:
            return True
    return False

# ---- 加载 ----
raw = json.loads((ROOT / "data" / "colors.json").read_text(encoding="utf-8"))
seen = set()
colors = []
for c in raw:
    if c["pinyin"] not in seen:
        seen.add(c["pinyin"])
        colors.append(c)

def poetry_count(pinyin):
    p = POETRY / f"{pinyin}.json"
    if not p.exists():
        return 0
    return len(json.loads(p.read_text(encoding="utf-8")).get("entries", []))

def score(c):
    n = poetry_count(c["pinyin"])
    pts = n * 15               # 诗句分: 0–75
    if not is_modern(c["name"]):
        pts += 25              # 传统名加分
    return pts, n

def rgb_dist(a, b):
    ra, ga, ba = a["RGB"]
    rb, gb, bb = b["RGB"]
    return math.sqrt((ra - rb) ** 2 + (ga - gb) ** 2 + (ba - bb) ** 2)

# ---- 预过滤：零诗句 且 现代名 → 直接丢掉 ----
# 其他零诗句但传统名也暂时留着（可能出现在聚类中但不会当选代表）
print("=== 预过滤 ===")
dropped = 0
keep = []
for c in colors:
    n = poetry_count(c["pinyin"])
    mod = is_modern(c["name"])
    if n == 0 and mod:
        dropped += 1
        continue
    keep.append(c)
print(f"  零诗句+现代名 剔除: {dropped}")
print(f"  剩余: {len(keep)}")

# ---- 聚类 ----
# 贪心：按得分降序排列，每个色作为中心时吸收阈值内的未分配色
scored = [(c, *score(c)) for c in keep]
scored.sort(key=lambda x: x[1], reverse=True)  # 按总分降序

def cluster(scored_list, th):
    assigned = set()
    clusters = []
    for c, pts, n in scored_list:
        if c["pinyin"] in assigned:
            continue
        group = [c]
        assigned.add(c["pinyin"])
        for c2, pts2, n2 in scored_list:
            if c2["pinyin"] in assigned:
                continue
            if rgb_dist(c, c2) <= th:
                group.append(c2)
                assigned.add(c2["pinyin"])
        clusters.append(group)
    return clusters

# 二分找阈值，目标 ~130 聚类
lo, hi = 15, 65
best = None
for _ in range(15):
    mid = (lo + hi) // 2
    cl = cluster(scored, mid)
    nc = len(cl)
    if nc <= 130:
        best = (mid, cl)
        hi = mid
    else:
        lo = mid + 1

if best is None:
    best = (65, cluster(scored, 65))

th, clusters = best
print(f"\n=== 聚类结果 ===")
print(f"  阈值: ΔRGB ≤ {th}")
print(f"  聚类数: {len(clusters)}")

# ---- 输出合并后的 colors ----
merged = [group[0] for group in clusters]  # 每组第一个（得分最高）
orig_idx = {c["pinyin"]: i for i, c in enumerate(colors)}
merged.sort(key=lambda c: orig_idx.get(c["pinyin"], 9999))

out_colors = []
for c in merged:
    out_colors.append({
        "CMYK": c.get("CMYK", [0, 0, 0, 0]),
        "RGB": c["RGB"],
        "hex": c["hex"],
        "name": c["name"],
        "pinyin": c["pinyin"],
    })

(ROOT / "data" / "colors.json").write_text(
    json.dumps(out_colors, ensure_ascii=False), encoding="utf-8"
)

# 统计
has_poetry = sum(1 for c in merged if poetry_count(c["pinyin"]) > 0)
modern_left = sum(1 for c in merged if is_modern(c["name"]))
print(f"\n=== 最终结果 ===")
print(f"  合并后色数: {len(merged)}")
print(f"  有诗句: {has_poetry}")
print(f"  残留现代名: {modern_left}")
print(f"  零诗句传统名: {len(merged) - has_poetry - modern_left}")

# ---- 显示合并详情 ----
print(f"\n=== 合并详情（聚类≥2）===")
for group in clusters:
    if len(group) > 1:
        rep = group[0]["name"]
        merged_in = [c["name"] for c in group[1:]]
        print(f"  {rep} ← {', '.join(merged_in)}")

# ---- 清理无对应 poetry 的文件 ----
# 不删文件，但标记
print(f"\n=== 零诗句色名（传统名但没有匹配到诗）===")
for c in merged:
    if poetry_count(c["pinyin"]) == 0:
        print(f"  {c['name']} ({c['pinyin']})")
