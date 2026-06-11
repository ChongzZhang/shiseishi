"""色名 → 汉语拼音（用于展示，与内部 id 字段 pinyin 区分）。"""

from __future__ import annotations

import re


def _is_hash_id(s: str) -> bool:
    return bool(re.fullmatch(r"c[0-9a-f]{3,6}", s or ""))


def name_to_pinyin(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return ""
    try:
        from pypinyin import Style, pinyin

        parts = pinyin(name, style=Style.NORMAL, errors="default")
        return "".join(p[0] for p in parts if p and p[0])
    except ImportError:
        pass
    return ""


def display_pinyin(color: dict) -> str:
    """展示用拼音：优先 namePinyin，否则由色名生成，绝不显示 hash id。"""
    if color.get("namePinyin"):
        return color["namePinyin"]
    name_py = name_to_pinyin(color.get("name", ""))
    if name_py:
        return name_py
    p = color.get("pinyin", "")
    if p and not _is_hash_id(p):
        return p
    return name_py or p
