#!/usr/bin/env python3
"""每种颜色只保留一条最贴切诗句；20 种书签色固定为 daily-challenges 意象句。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from dynasty import infer_dynasty

ROOT = SCRIPT_DIR.parent
POETRY_DIR = ROOT / "data" / "poetry"
DAILY_PATH = ROOT / "assets" / "color-bookmarks" / "daily-challenges.json"
COLORS_PATH = ROOT / "data" / "colors.json"

# 耳熟能详作者加权
FAMOUS_AUTHORS = {
    "李白", "杜甫", "白居易", "王维", "李商隐", "杜牧", "孟浩然", "王昌龄", "岑参",
    "柳宗元", "刘禹锡", "韩愈", "贺知章", "张若虚", "王之涣", "高适", "刘长卿",
    "韦应物", "张继", "孟郊", "温庭筠", "李贺", "王勃", "陈子昂", "张九龄",
    "苏轼", "辛弃疾", "李清照", "陆游", "欧阳修", "王安石", "柳永", "晏殊",
    "范仲淹", "杨万里", "范成大", "黄庭坚", "秦观", "周邦彦", "姜夔", "林逋",
    "宋祁", "齐己", "贾岛", "杜牧", "元稹", "张籍", "李绅", "曹植", "陶渊明",
}

# 非书签色：仅对自动打分明显不如名句的情况指定整句关键词
MANUAL_PICKS: dict[str, str] = {
    "yuebai": "唯见江心秋月白",
    "c36d8": "两个黄鹂鸣翠柳",
    "c7e3a": "竹色溪下绿",
    "c3abb": "湖光秋月两相和",
    "haiqing": "海阔山遥翠作堆",
    "c4b6c": "朱门酒肉臭",
    "c2ff3": "红酥手",
    "weilan": "平岸小桥千嶂抱",
    "c10501": "忽如一夜春风来",
    "c128ec": "缟素",
    "meiguihong": "云想衣裳花想容",
    "fengyehong": "停车坐爱枫林晚",
}


def load_pinned() -> dict[str, dict]:
    daily = json.loads(DAILY_PATH.read_text(encoding="utf-8"))
    return {c["pinyin"]: c for c in daily["colors"]}


def parse_source(hint_source: str) -> tuple[str, str, str]:
    """返回 author, title, type。"""
    m = re.match(r"^(.+?)《(.+?)》$", hint_source.strip())
    if not m:
        return hint_source, hint_source, "诗"
    author, title = m.group(1), m.group(2)
    if "序" in title and "词" not in title:
        return author, title, "文"
    if "·" in title or "其" in title or any(
        k in title for k in ("浣溪沙", "菩萨蛮", "清平调", "苏幕遮", "破阵子", "玉楼春", "蓦山溪", "摊破")
    ):
        return author, title, "词"
    if "新乐府" in title or "乐府" in title:
        return author, title, "诗"
    return author, title, "诗"


def make_pinned_entry(challenge: dict) -> dict:
    author, title, ptype = parse_source(challenge["hintSource"])
    entry = {
        "line": challenge["hintLine"],
        "title": title,
        "author": author,
        "type": ptype,
        "source": "curated:bookmark-imagery",
        "matchTier": 1,
        "verified": True,
    }
    entry["dynasty"] = infer_dynasty(entry)
    return entry


def score_entry(entry: dict, color_name: str) -> float:
    line = entry.get("line", "")
    score = 0.0
    if color_name and color_name in line:
        score += 120
    # 双字色名首字实写（如「石榴红」→「石」不计，「石榴」计）
    if len(color_name) >= 3 and color_name[:2] in line:
        score += 20

    tier = entry.get("matchTier", 5)
    score += max(0, (6 - tier)) * 12

    t = entry.get("type", "")
    if t == "诗":
        score += 35
    elif t == "词":
        score += 22
    elif t in ("曲", "赋"):
        score += 12
    else:
        score += 5

    author = entry.get("author", "")
    if author in FAMOUS_AUTHORS:
        score += 28

    # 写景：对仗句、较长但完整
    if "，" in line or "。" in line or "；" in line:
        score += 8
    if 10 <= len(line) <= 28:
        score += 6

    return score


def pick_entry(entries: list[dict], color_name: str, pinyin: str) -> dict | None:
    if not entries:
        return None
    needle = MANUAL_PICKS.get(pinyin)
    if needle:
        for e in entries:
            if needle in e.get("line", ""):
                return e
    best = max(entries, key=lambda e: score_entry(e, color_name))
    return best


def curate_file(path: Path, pinned: dict[str, dict] | None) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    pinyin = data.get("pinyin") or path.stem
    color_name = data.get("color", "")

    if pinned and pinyin in pinned:
        entry = make_pinned_entry(pinned[pinyin])
    else:
        entries = data.get("entries") or []
        chosen = pick_entry(entries, color_name, pinyin)
        if not chosen:
            return data
        entry = dict(chosen)
        entry.pop("_color", None)
        entry.pop("_hex", None)
        if "dynasty" not in entry:
            entry["dynasty"] = infer_dynasty(entry)

    data["entries"] = [entry]
    data["coverage"] = "1/5"
    return data


def main() -> None:
    pinned = load_pinned()
    pinned_set = set(pinned.keys())
    updated = 0

    for path in sorted(POETRY_DIR.glob("*.json")):
        pinyin = path.stem
        new_data = curate_file(path, pinned if pinyin in pinned_set else None)
        path.write_text(json.dumps(new_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        updated += 1

    print(f"已筛选 {updated} 个色文件，每种保留 1 条诗句")
    print(f"  书签色固定意象句: {len(pinned_set)} 种")


if __name__ == "__main__":
    main()
