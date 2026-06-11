"""根据诗句条目的 author / source / type / 词牌 推断朝代。"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor" / "chinese-poetry"

# 占位 source（批量脚本写入的假路径，不可信）
PLACEHOLDER_SOURCES = (
    "poet.tang.json#0",
    "poet.song.0.json#0",
)

# 常见词牌（标题即词牌时多为宋词）
CIPAI = {
    "如梦令", "虞美人", "蝶恋花", "浣溪沙", "菩萨蛮", "鹧鸪天", "临江仙",
    "满江红", "水龙吟", "念奴娇", "沁园春", "摸鱼儿", "贺新郎", "青玉案",
    "江城子", "定风波", "洞仙歌", "踏莎行", "苏幕遮", "点绛唇", "谒金门",
    "阮郎归", "鹊桥仙", "霜天晓角", "眼儿媚", "醉花阴", "声声慢", "永遇乐",
    "武陵春", "减字木兰花", "木兰花", "瑞鹤仙", "齐天乐", "八声甘州",
    "扬州慢", "长亭怨慢", "暗香", "疏影", "风入松", "玉楼春", "朝中措",
    "好事近", "渔家傲", "忆秦娥", "清平乐", "丑奴儿", "南乡子", "西江月",
    "望江南", "忆王孙", "行香子", "最高楼", "唐多令", "石州慢", "六州歌头",
    "兰陵王", "西河", "霓裳中序第一", "宴清都", "绮罗香", "夜飞鹊", "花犯",
    "过春楼", "瑞龙吟", "风流子", "应天长", "惜红衣", "侧犯", "法曲献仙音",
    "渡江云", "解连环", "拜星月", "倒犯", "大酺", "花心动", "渔家傲引",
    "天香", "汉宫春", "月上海棠", "庆宫春", "湘春曲", "探春慢", "醉吟仙",
    "法曲献仙音", "淡黄柳", "正宫", "越调", "双调", "中吕", "黄钟",
    "凤凰阁", "秋霁", "淡黄柳", "贺新郎", "思远人", "蝶恋花",
}

# 手动补充 / 覆盖
MANUAL_AUTHOR: dict[str, str] = {
    "曹雪芹": "清",
    "纳兰性德": "清",
    "陶渊明": "东晋",
    "谢灵运": "东晋",
    "曹操": "汉",
    "曹植": "汉",
    "李煜": "五代",
    "冯延巳": "五代",
    "李弥逊": "宋",
    "陈棣": "宋",
    "太宗皇帝": "唐",
    "高宗皇帝": "唐",
    "中宗皇帝": "唐",
    "玄宗皇帝": "唐",
    "德宗皇帝": "唐",
    "文宗皇帝": "唐",
    "武宗皇帝": "唐",
    "宣宗皇帝": "唐",
    "僖宗皇帝": "唐",
    "高祖皇帝": "唐",
    "则天皇后": "唐",
    "宋太宗": "宋",
    "宋徽宗": "宋",
}


def _simplified(name: str) -> str:
    try:
        from opencc import OpenCC
        return OpenCC("t2s").convert(name)
    except ImportError:
        return name


def _load_names(path: Path, dynasty: str, out: dict[str, str]) -> None:
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return
    for item in data:
        name = _simplified((item.get("name") or "").strip())
        if name:
            out.setdefault(name, dynasty)


@lru_cache(maxsize=1)
def load_author_dynasty() -> dict[str, str]:
    mapping: dict[str, str] = dict(MANUAL_AUTHOR)
    _load_names(VENDOR / "全唐诗" / "authors.tang.json", "唐", mapping)
    _load_names(VENDOR / "全唐诗" / "authors.song.json", "宋", mapping)
    _load_names(VENDOR / "宋词" / "author.song.json", "宋", mapping)
    _load_names(VENDOR / "五代诗词" / "nantang" / "authors.json", "五代", mapping)
    return mapping


def is_placeholder_source(source: str) -> bool:
    if not source:
        return False
    return any(p in source for p in PLACEHOLDER_SOURCES)


def is_cipai(title: str) -> bool:
    if not title:
        return False
    t = title.strip()
    if t in CIPAI:
        return True
    # 减字木兰花、念奴娇・赤壁怀古 等
    base = re.split(r"[・·\s]", t)[0].strip()
    return base in CIPAI


def infer_dynasty(entry: dict) -> str:
    author = (entry.get("author") or "").strip()
    source = entry.get("source") or ""
    ptype = entry.get("type") or ""
    title = entry.get("title") or ""

    authors = load_author_dynasty()

    # 1. 作者表（最可靠）
    if author in authors:
        return authors[author]

    # 2. 特殊作品
    if author == "曹雪芹" or "红楼梦" in title:
        return "清"

    # 3. 可信来源
    if not is_placeholder_source(source):
        if any(x in source for x in ("宋词", "ci.song", "宋词三百首")):
            return "宋"
        if "元曲" in source:
            return "元"
        if "poet.song" in source:
            return "宋"
        if "唐诗三百首" in source or "poet.tang" in source:
            return "唐"
        if "诗经" in source:
            return "先秦"
        if "幽梦影" in source or "纳兰" in source:
            return "清"

    # 4. 体裁 / 词牌
    if ptype == "词" or is_cipai(title):
        return "宋"
    if ptype == "曲":
        return "元"

    # 5. 诗体兜底（仅未知作者）
    if ptype == "诗":
        return "唐"

    return ""
