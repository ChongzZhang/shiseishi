#!/usr/bin/env python3
"""为游戏 130 色生成统一句式释义：取○○之○○。"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLORS_PATH = ROOT / "data" / "colors.json"
ZGS_PATH = ROOT / "data" / "zhongguose_full.json"
OUT_PATH = ROOT / "data" / "color_glosses.json"

SUFFIX_MAP = {
    "红": "之红", "黄": "之黄", "绿": "之绿", "蓝": "之蓝", "紫": "之紫",
    "白": "之白", "黑": "之黑", "灰": "之灰", "青": "之青", "棕": "之棕",
    "橙": "之橙", "色": "之色", "综": "之褐",
}

PREFIX_TRIM = ("淡", "浅", "深", "明", "暗", "新", "鲜", "润")


def load_zgs_intros() -> dict[str, str]:
    data = json.loads(ZGS_PATH.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for group in data:
        for c in group.get("colors", []):
            name = c.get("name")
            intro = (c.get("intro") or "").strip()
            if name and intro:
                out[name] = intro
    return out


def intro_to_gloss(intro: str) -> str | None:
    intro = intro.split("。")[0].split("（")[0].strip()
    intro = intro.split("，")[0].strip()
    if intro.startswith("即"):
        body = intro[1:].strip()
        return f"取{body.rstrip('色')}之色。" if body else None
    m = re.match(r"^(.+?)的(颜色|色)", intro)
    if m:
        return f"取{m.group(1)}之色。"
    if "如" in intro and "色" in intro:
        m = re.search(r"如(.+?)的", intro)
        if m:
            return f"取{m.group(1)}之色。"
    if len(intro) <= 12:
        return f"即{intro}。"
    return None


def name_heuristic(name: str) -> str:
    if len(name) == 1:
        defaults = {
            "彤": "取丹饰之赤色。",
            "缟": "取素缯之白。",
            "黛": "取画眉黛之青黑。",
            "黯": "取深黑之黯。",
        }
        return defaults.get(name, f"取{name}之色。")
    prefix = name
    tone = "之色"
    for p in PREFIX_TRIM:
        if name.startswith(p) and len(name) > len(p) + 1:
            prefix = name[len(p):]
            tone = f"之{ '淡' if p in '淡浅' else '深' if p == '深' else ''}{SUFFIX_MAP.get(name[-1], '色')}".replace("之之色", "之色")
            if p == "淡":
                return f"取{prefix}之淡{suffix_char(name)}。"
            if p == "浅":
                return f"取{prefix}之浅{suffix_char(name)}。"
            break
    for suf, rep in SUFFIX_MAP.items():
        if name.endswith(suf) and len(name) > len(suf):
            stem = name[: -len(suf)]
            if stem:
                return f"取{stem}{rep}。"
    return f"取{name}之色。"


def suffix_char(name: str) -> str:
    for s in "红黄绿蓝紫白黑灰青棕橙":
        if name.endswith(s):
            return s
    return "色"


def build_manual() -> dict[str, str]:
    """pinyin -> gloss，覆盖全部 130 色。"""
    return {
        "dingxiangzong": "取丁香花之棕紫。",
        "c6913": "取丁香花之淡紫。",
        "rubai": "取乳色之白。",
        "foshouhuang": "取佛手柑之黄。",
        "diaoyezong": "取凋叶之棕黄。",
        "beiguahuang": "取北瓜之橙黄。",
        "c12e18": "取墨染之灰。",
        "jiazhutaohong": "取夹竹桃花之红。",
        "yaohuang": "取姚黄牡丹之黄。",
        "c16352": "取鲜艳之红。",
        "cb2c2": "取嫩叶之初绿。",
        "chenhui": "取尘土之灰黄。",
        "shanjihu": "取山鸡羽之褐。",
        "yanshibrown": "取岩石之棕。",
        "cbc79": "取丹饰之赤色。",
        "xinhelv": "取新禾苗之绿。",
        "minglv": "取明丽之绿。",
        "anhaishuilv": "取深海之水绿。",
        "yuehui": "取月影之灰。",
        "yuebai": "取月华之白。",
        "c4b6c": "取朱砂之正红。",
        "xinghong": "取杏子之偏红。",
        "songbolv": "取松柏叶之深绿。",
        "pipahuang": "取枇杷之黄。",
        "zhaohong": "取枣实之深红。",
        "fengyehong": "取枫叶之红。",
        "c36d8": "取柳叶之绿。",
        "lizi": "取栗壳之紫褐。",
        "guihong": "取桂花之红。",
        "taohong": "取桃花之红。",
        "liuehuang": "取榴萼之黄。",
        "binglangzong": "取槟榔之综褐。",
        "c92a5": "取殷染之深红。",
        "maolv": "取毛羽之绿。",
        "shuilv": "取春水之绿。",
        "c3186": "取江水之青灰。",
        "c4190": "取江水之浅蓝。",
        "youcaihuang": "取油菜花之黄。",
        "qiantuose": "取浅驼毛之色。",
        "c15fce": "取海棠花之红。",
        "haiqing": "取海天之青。",
        "runhong": "取润泽之红。",
        "danhuilv": "取淡灰之绿。",
        "danjianghong": "取淡绛之红。",
        "danlv": "取淡绿之色。",
        "danpoppyhong": "取淡罂粟之红。",
        "dandousha": "取淡豆沙之红。",
        "danyinhui": "取淡银之灰。",
        "c3abb": "取湖水之蓝。",
        "tanshuilv": "取潭水之绿。",
        "huohong": "取火焰之红。",
        "yanhui": "取燕羽之灰。",
        "xuanse": "取天玄之赤黑。",
        "yuhong": "取玉色之红。",
        "meiguihui": "取玫瑰之灰。",
        "meiguizi": "取玫瑰之紫。",
        "meiguihong": "取玫瑰之红。",
        "daimaihuang": "取玳瑁之黄。",
        "gancaohuang": "取甘草之黄。",
        "shibanghui": "取石板之灰。",
        "c52e9": "取石榴花之浓红。",
        "bilv": "取碧玉之绿。",
        "bise": "取碧玉之色。",
        "bilan": "取碧空之蓝。",
        "qiuhaitanghong": "取秋海棠之红。",
        "qiuse": "取秋林之枯黄。",
        "qiuxiangse": "取秋香之浅黄绿。",
        "c7e3a": "取竹色之青。",
        "fenhong": "取帛赤白之浅红。",
        "fenlv": "取粉绿之色。",
        "ccb3c": "取赤蓝相间之紫。",
        "c1ce0": "取紫中带红之色。",
        "c83c23": "取绯帛之深红。",
        "c128ec": "取素缯之白。",
        "cuilv": "取翠色之深绿。",
        "feicuise": "取翡翠羽之绿。",
        "rouse": "取肌肤之浅红。",
        "yanzhi": "取胭脂之深红。",
        "yanhong": "取艳红之色。",
        "ailv": "取艾草之绿。",
        "luhui": "取芦花之灰。",
        "huabai": "取花发之斑白。",
        "yalv": "取新芽之绿。",
        "cangbai": "取苍白之灰白。",
        "canglv": "取苍色之绿。",
        "c141ba": "取苍翠之深绿。",
        "cfce2": "取苍色之灰蓝。",
        "canghuang": "取苍黄之杂色。",
        "tailv": "取苔色之绿。",
        "molihuang": "取茉莉花之黄。",
        "chahuahong": "取茶花之红。",
        "caohuilv": "取草灰之绿。",
        "juleibai": "取菊蕾之白。",
        "putaojiuhong": "取葡萄酒之红。",
        "haohuang": "取蒿草之黄。",
        "lanlv": "取蓝绿相间之色。",
        "weilan": "取晴空之蓝。",
        "ouhese": "取藕荷之浅紫。",
        "xiakeqing": "取虾壳之青。",
        "qingtinghong": "取蜻蜓之红。",
        "xiekehong": "取蟹壳之红。",
        "zuiguarou": "取醉瓜肉之色。",
        "jinzhanhuang": "取金盏花之黄。",
        "c10607": "取黄金之深黄。",
        "jinlianhuacheng": "取金莲花之橙。",
        "jintuo": "取金驼毛之色。",
        "tiezong": "取铁锈之棕。",
        "tonglv": "取铜锈之绿。",
        "yinzhu": "取银朱颜料之红。",
        "yinhui": "取银灰之色。",
        "c2cc1": "取银光之白。",
        "xuebai": "取积雪之白。",
        "shuangse": "取秋霜之白。",
        "qingbai": "取青白相间之色。",
        "caeec": "取青碧之鲜蓝。",
        "c141ba2": "x",
        "c00e09e": "取东方青之色。",
        "c6e02": "取葱叶之深绿。",
        "c065279": "x",
        "fengfanhuang": "取风帆之黄。",
        "xiangyehong": "取香叶之红。",
        "weizi": "取魏紫牡丹之紫。",
        "xianlv": "取鲜绿之色。",
        "c1724b": "取鹅雏嘴之浅黄。",
        "hehui": "取鹤羽之灰。",
        "hedinghong": "取鹤顶之红。",
        "c4a4266": "x",
        "c43f3": "取黛色之深蓝。",
        "c847f": "取深黑之黯。",
        "heise": "取熏火之纯黑。",
    }


def main() -> None:
    colors = json.loads(COLORS_PATH.read_text(encoding="utf-8"))
    zgs = load_zgs_intros()

    # Classical / zgs-refined overrides by pinyin (actual keys from colors.json)
    refined: dict[str, str] = {
        "cbc79": "取丹饰之赤色。",
        "c128ec": "取素缯之白。",
        "c4a4266": "取画眉黛之青黑。",
        "xuanse": "取天玄之赤黑。",
        "c4b6c": "取朱砂之正红。",
        "c00e09e": "取东方青之色。",
        "ccb3c": "取赤蓝相间之紫。",
        "c1ce0": "取紫中带红之色。",
        "heise": "取熏火之纯黑。",
        "cfce2": "取苍色之灰蓝。",
        "bise": "取碧玉之色。",
        "c065279": "取靛蓝染之蓝。",
        "fenhong": "取帛赤白之浅红。",
        "c92a5": "取殷染之深红。",
        "cfc9e": "取绯帛之深红。",
        "huohong": "取火焰之红。",
        "c52e9": "取石榴花之浓红。",
        "yanzhi": "取胭脂之深红。",
        "c1724b": "取鹅雏嘴之浅黄。",
        "qiuse": "取秋林之枯黄。",
        "c7e3a": "取竹色之青。",
        "c6e02": "取葱叶之深绿。",
        "ailv": "取艾草之绿。",
        "c141ba": "取苍翠之深绿。",
        "caeec": "取青碧之鲜蓝。",
        "c141ba_q": "x",
    }

    # 释义与色名同义复读，不写 gloss
    gloss_skip: dict[str, str] = {
        "淡绿": "释义与色名同义复读",
        "粉绿": "释义与色名同义复读",
        "艳红": "释义与色名同义复读",
        "鲜绿": "释义与色名同义复读",
        "银灰": "释义与色名同义复读",
        "醉瓜肉": "释义与色名同义复读",
        "黯": "单色字义即色名",
    }

    # name-based manual（123 条有释义；7 条见 gloss_skip）
    by_name: dict[str, str] = {
        "丁香棕": "取丁香花之棕紫。",
        "丁香色": "取丁香花之淡紫。",
        "乳白": "取乳色之白。",
        "佛手黄": "取佛手柑之黄。",
        "凋叶棕": "取凋叶之棕黄。",
        "北瓜黄": "取北瓜之橙黄。",
        "墨灰": "取墨染之灰。",
        "夹竹桃红": "取夹竹桃花之红。",
        "姚黄": "取姚黄牡丹之黄。",
        "嫣红": "取娇媚之红。",
        "嫩绿": "取嫩叶之初绿。",
        "尘灰": "取尘土之灰黄。",
        "山鸡褐": "取山鸡羽之褐。",
        "岩石棕": "取岩石之棕。",
        "彤": "取丹饰之赤色。",
        "新禾绿": "取新禾之黄绿。",
        "明绿": "取晴波之浅绿。",
        "暗海水绿": "取暗海泥之绿褐。",
        "月灰": "取月影之灰。",
        "月白": "取月华之白。",
        "朱红": "取朱砂之正红。",
        "杏红": "取杏子之偏红。",
        "松柏绿": "取松柏叶之深绿。",
        "枇杷黄": "取枇杷之黄。",
        "枣红": "取枣实之深红。",
        "枫叶红": "取枫叶之红。",
        "柳绿": "取柳叶之绿。",
        "栗紫": "取栗壳之紫褐。",
        "桂红": "取丹桂之红。",
        "桃红": "取桃花之红。",
        "榴萼黄": "取榴萼之黄。",
        "槟榔综": "取槟榔果之褐。",
        "殷红": "取殷染之深红。",
        "毛绿": "取鸭翎之绿。",
        "水绿": "取春水之绿。",
        "水色": "取秋水之浅青。",
        "水蓝": "取江水之浅蓝。",
        "油菜花黄": "取油菜花之黄。",
        "浅驼色": "取浅驼毛之褐。",
        "海棠红": "取海棠花之红。",
        "海青": "取海青羽之青。",
        "润红": "取珠晕之浅红。",
        "淡灰绿": "取苔痕之灰绿。",
        "淡绛红": "取淡绛之红。",
        "淡罂粟红": "取淡罂粟之红。",
        "淡豆沙": "取淡豆沙之红。",
        "淡银灰": "取淡银之灰。",
        "湖蓝": "取湖水之蓝。",
        "潭水绿": "取深潭藻色之绿。",
        "火红": "取火焰之红。",
        "燕羽灰": "取燕羽之灰。",
        "玄色": "取天玄之赤黑。",
        "玉红": "取旧玉沁之红。",
        "玫瑰灰": "取枯玫瑰之灰。",
        "玫瑰紫": "取玫瑰之紫。",
        "玫瑰红": "取玫瑰之红。",
        "玳瑁黄": "取玳瑁之黄。",
        "甘草黄": "取甘草之黄。",
        "石板灰": "取石板之灰。",
        "石榴红": "取石榴花之浓红。",
        "碧绿": "取碧玉之绿。",
        "碧色": "取碧玉之色。",
        "碧蓝": "取碧空之蓝。",
        "秋海棠红": "取秋海棠之红。",
        "秋色": "取秋林之枯黄。",
        "秋香色": "取秋香之浅黄绿。",
        "竹青": "取竹色之青。",
        "粉红": "取帛赤白之浅红。",
        "紫色": "取赤蓝相间之紫。",
        "绛紫": "取紫中带红之色。",
        "绯红": "取绯帛之深红。",
        "缟": "取素缯之白。",
        "翠绿": "取翠羽之深绿。",
        "翡翠色": "取翡翠羽之绿。",
        "肉色": "取肌肤之浅黄。",
        "胭脂": "取胭脂之深红。",
        "艾绿": "取艾草之绿。",
        "芦灰": "取芦花之灰。",
        "花白": "取花发之斑白。",
        "芽绿": "取新芽之绿。",
        "苍白": "取病容之灰白。",
        "苍绿": "取苍色之绿。",
        "苍翠": "取青松之苍翠。",
        "苍色": "取苍色之灰蓝。",
        "苍黄": "取日暮之苍黄。",
        "苔绿": "取苔色之绿。",
        "茉莉黄": "取茉莉花之黄。",
        "茶花红": "取茶花之红。",
        "草灰绿": "取草灰之绿。",
        "菊蕾白": "取菊蕾之白。",
        "葡萄酒红": "取葡萄酒之红。",
        "蒿黄": "取蒿草之黄。",
        "蓝绿": "取蓝绿相间之色。",
        "蔚蓝": "取晴空之蓝。",
        "藕荷色": "取藕荷之浅紫。",
        "虾壳青": "取虾壳之青。",
        "蜻蜓红": "取蜻蜓翅之红。",
        "蟹壳红": "取蟹壳之红。",
        "金盏黄": "取金盏花之黄。",
        "金色": "取黄金之深黄。",
        "金莲花橙": "取金莲花之橙。",
        "金驼": "取驼毛之金黄。",
        "铁棕": "取锻铁之棕。",
        "铜绿": "取铜锈之绿。",
        "银朱": "取银朱颜料之红。",
        "银白": "取银光之白。",
        "雪白": "取积雪之白。",
        "霜色": "取秋霜之白。",
        "青白": "取青白相间之色。",
        "青碧": "取碧玉青天之碧。",
        "青翠": "取春筠之青翠。",
        "青色": "取东方青之色。",
        "青葱": "取葱叶之深绿。",
        "靛蓝": "取靛蓝染之蓝。",
        "风帆黄": "取落日帆影之黄。",
        "香叶红": "取香叶花之浅红。",
        "魏紫": "取魏紫牡丹之紫。",
        "鹅黄": "取鹅雏嘴之浅黄。",
        "鹤灰": "取鹤羽之灰。",
        "鹤顶红": "取鹤顶之红。",
        "黛": "取画眉黛之青黑。",
        "黛蓝": "取黛色之深蓝。",
        "黑色": "取熏火之纯黑。",
    }

    entries = []
    classical = []
    from_zgs = []

    for c in colors:
        name = c["name"]
        pinyin = c["pinyin"]
        skipped = name in gloss_skip
        gloss = None if skipped else by_name.get(name)
        source = "manual"

        if not skipped and name in zgs:
            zg = intro_to_gloss(zgs[name])
            if zg and name not in by_name:
                gloss = zg
                source = "zhongguose"

        if not skipped and not gloss:
            gloss = name_heuristic(name)
            source = "heuristic"

        if not skipped and name in zgs and source == "manual":
            from_zgs.append(name)

        tier = "丙"
        if pinyin in refined or name in {
            "彤", "缟", "黛", "黯", "玄色", "朱红", "青色", "紫色", "黑色",
            "苍色", "碧色", "靛蓝", "胭脂", "银朱", "绯红", "殷红", "火红", "粉红",
        }:
            tier = "甲" if name in {"彤", "缟", "黛", "黯", "玄色", "朱红", "青色", "紫色", "黑色", "苍色", "碧色"} else "乙"

        entry: dict = {
            "name": name,
            "pinyin": pinyin,
            "hex": c.get("hex", ""),
            "tier": tier,
        }
        if skipped:
            entry["gloss"] = None
            entry["gloss_skip"] = True
            entry["skip_reason"] = gloss_skip[name]
            entry["source"] = "skip"
        else:
            entry["gloss"] = gloss
            entry["source"] = source
        entries.append(entry)
        if tier in ("甲", "乙"):
            classical.append(name)

    out = {
        "version": 1,
        "format": "取○○之○○。",
        "count": len(entries),
        "classical_count": len(classical),
        "colors": entries,
    }
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已写入 {len(entries)} 条 → {OUT_PATH}")
    print(f"  甲/乙类（古籍/染料向）: {len(classical)}")
    print(f"  有中国色 intro 可参考: {len(from_zgs)}")


if __name__ == "__main__":
    main()
