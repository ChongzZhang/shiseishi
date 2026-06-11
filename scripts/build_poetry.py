#!/usr/bin/env python3
"""离线构建：为每种中国传统色检索并验证诗句（含意象联想补搜）。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

try:
    import yaml
    from opencc import OpenCC
except ImportError:
    print("请先安装依赖: python -m pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

cc = OpenCC("t2s")

SUFFIXES = (
    "色", "红", "绿", "蓝", "黄", "紫", "白", "黑", "灰", "褐", "赭", "丹", "青", "橙", "棕", "绯", "玄", "素",
    "兰", "粉", "铜", "银", "金", "墨", "漆", "黛", "绯", "绛", "缃", "翠", "碧", "赤", "朱", "绯",
)
PREFIXES = ("淡", "浅", "深", "暗", "明", "苍", "嫩", "老", "新", "鲜", "轻", "重", "半", "微", "极", "精", "纯")
COLOR_IMAGERY = (
    "染", "妆", "裙", "衣", "裳", "袍", "锦", "罗", "纨", "素", "彩", "色", "颜", "粉", "朱", "丹",
    "花", "叶", "瓣", "蕊", "霞", "云", "霜", "雪", "露", "波", "水", "山", "林", "竹", "梅", "桃",
    "唇", "颊", "面", "肤", "血", "泪", "酒", "茶", "烟", "墨", "灯", "烛", "旗", "帆", "壁", "砖",
)
SINGLE_CHAR_OK = set("苹梅竹荷莲菊兰桂柳枫桃杏梨李松柏梧桐榆桑藤苔芦萍藻鸥雁凫鹭鹄鲸蚌螺蟹虾龙虎豹狐马牛羊犬鸡鹅鸭莺蝶蜂蝉萤鱼霞月云雪霜露冰烟玉金银朱丹赤紫青碧翠黄白黑灰")

CORPUS_DIRS = [
    "全唐诗", "宋词", "五代诗词", "诗经", "元曲", "幽梦影", "纳兰性德", "四书五经", "蒙学", "论语",
]

TARGET = 5
TIER_MAP = {400: 1, 300: 2, 200: 3, 100: 4}
BUCKET_CAP = TARGET * 8


def to_simplified(text: str) -> str:
    return cc.convert(text)


def extract_core(name: str) -> str:
    s = name
    for suf in SUFFIXES:
        if len(s) > 1 and s.endswith(suf):
            s = s[: -len(suf)]
            break
    return s if len(s) >= 1 else name


def strip_prefix(s: str) -> str:
    for p in PREFIXES:
        if s.startswith(p) and len(s) > len(p) + 1:
            return s[len(p):]
    return s


def normalize_line(line: str) -> str:
    line = to_simplified(line)
    return re.sub(r"[，。、；：！？「」『』""''（）\(\)\[\]【】…—·\s]", "", line)


def poem_type_from_path(rel: str) -> str:
    if "宋词" in rel:
        return "词"
    if "元曲" in rel:
        return "曲"
    return "诗"


def song_bonus(source: str) -> int:
    return 10 if ("宋词" in source or "poet.song" in source) else 0


def load_alias_map(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {str(k): list(dict.fromkeys(v)) for k, v in raw.items() if isinstance(v, list)}


def resolve_keywords(name: str, core: str, manual: dict, aliases: dict[str, list[str]]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    def add(*words: str) -> None:
        for w in words:
            w = w.strip()
            if not w or w in seen:
                continue
            if len(w) >= 2 or w in SINGLE_CHAR_OK:
                seen.add(w)
                found.append(w)

    if name in manual:
        for kw in manual[name].get("keywords", []):
            add(kw)

    bases = {core, strip_prefix(core)}
    for base in list(bases):
        if not base:
            continue
        add(base)
        if len(base) >= 2:
            add(base[:2])
        if len(base) >= 3:
            add(base[-2:])
        for key, vals in aliases.items():
            if key in base or base in key:
                add(*vals)
        for key, vals in aliases.items():
            if len(key) >= 2 and key in base:
                add(*vals)

    return found[:16]


def score_line(line: str, color_name: str, core: str, keywords: list[str]) -> int | None:
    if color_name in line:
        return 400
    if core and len(core) >= 2 and core in line:
        if any(k in line for k in COLOR_IMAGERY):
            return 300
        return 200
    if keywords and any(kw in line for kw in keywords):
        return 100
    return None


def ensure_corpus(corpus_path: Path) -> None:
    if corpus_path.exists() and any(corpus_path.iterdir()):
        return
    corpus_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"克隆 chinese-poetry → {corpus_path}（约 3–8 分钟）…", flush=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", "https://github.com/chinese-poetry/chinese-poetry.git", str(corpus_path)],
        check=True,
    )


def iter_corpus_files(corpus_path: Path):
    for sub in CORPUS_DIRS:
        d = corpus_path / sub
        if d.exists():
            yield from d.rglob("*.json")


def load_poems(fp: Path, rel: str):
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return
    if not isinstance(data, list):
        return
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        author = to_simplified(item.get("author") or item.get("writer") or "佚名")
        title = to_simplified(item.get("title") or item.get("rhythmic") or "无题")
        paras = item.get("paragraphs") or item.get("content") or []
        if isinstance(paras, str):
            paras = [paras]
        ptype = poem_type_from_path(rel)
        if item.get("rhythmic"):
            rhythmic = to_simplified(item["rhythmic"])
            title = rhythmic if title == rhythmic else f"{rhythmic}·{title}"
            ptype = "词"
        for line in paras:
            if line and isinstance(line, str):
                yield {
                    "line": to_simplified(line.strip()),
                    "title": title,
                    "author": author,
                    "type": ptype,
                    "source": f"{rel}#{idx}",
                }


def build_records(corpus_path: Path) -> list[dict]:
    records: list[dict] = []
    files = list(iter_corpus_files(corpus_path))
    print(f"读取 {len(files)} 个 JSON 文件…", flush=True)
    t0 = time.time()
    for i, fp in enumerate(files):
        rel = str(fp.relative_to(corpus_path)).replace("\\", "/")
        records.extend(load_poems(fp, rel))
        if (i + 1) % 200 == 0:
            print(f"  已读 {i + 1}/{len(files)} 文件，{len(records)} 句", flush=True)
    print(f"语料共 {len(records)} 句（{time.time() - t0:.1f}s）", flush=True)
    return records


def bucket_matches(records: list[dict], colors: list[dict], manual: dict, aliases: dict[str, list[str]]) -> dict[str, list[tuple[int, dict]]]:
    meta = []
    for c in colors:
        core = extract_core(c["name"])
        meta.append({
            "name": c["name"],
            "pinyin": c["pinyin"],
            "hex": c["hex"],
            "core": core,
            "keywords": resolve_keywords(c["name"], core, manual, aliases),
        })

    buckets: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    print("扫描语料：色名直匹配…", flush=True)
    t0 = time.time()

    for i, rec in enumerate(records):
        line = rec["line"]
        for m in meta:
            tier = score_line(line, m["name"], m["core"], keywords=[])
            if tier is None:
                continue
            score = tier + song_bonus(rec["source"])
            entry = {**rec, "matchTier": TIER_MAP[tier], "verified": True}
            if len(buckets[m["pinyin"]]) < BUCKET_CAP:
                buckets[m["pinyin"]].append((score, entry))

        if (i + 1) % 100000 == 0:
            print(f"  已扫描 {i + 1}/{len(records)} 句", flush=True)

    print(f"直匹配完成（{time.time() - t0:.1f}s）", flush=True)

    need_imagery = [m for m in meta if len(buckets[m["pinyin"]]) < TARGET and m["keywords"]]
    print(f"意象补搜 {len(need_imagery)} 种颜色（含已有/零覆盖）…", flush=True)
    t1 = time.time()

    for i, rec in enumerate(records):
        line = rec["line"]
        for m in need_imagery:
            if len(buckets[m["pinyin"]]) >= BUCKET_CAP:
                continue
            tier = score_line(line, m["name"], m["core"], m["keywords"])
            if tier != 100:
                continue
            matched = [kw for kw in m["keywords"] if kw in line]
            kw_bonus = max(len(kw) * 6 for kw in matched)
            score = tier + kw_bonus + song_bonus(rec["source"])
            entry = {**rec, "matchTier": 4, "verified": True, "matchVia": "imagery"}
            buckets[m["pinyin"]].append((score, entry))

        if (i + 1) % 100000 == 0:
            print(f"  意象扫描 {i + 1}/{len(records)} 句", flush=True)

    print(f"意象补搜完成（{time.time() - t1:.1f}s）", flush=True)
    return buckets


def pick_top(buckets: dict[str, list[tuple[int, dict]]], pinyin: str) -> list[dict]:
    scored = buckets.get(pinyin, [])
    scored.sort(key=lambda x: (-x[0], x[1]["line"]))
    result: list[dict] = []
    seen: set[str] = set()
    for _, entry in scored:
        norm = normalize_line(entry["line"])
        if norm in seen:
            continue
        seen.add(norm)
        result.append(entry)
        if len(result) >= TARGET:
            break
    return result


def write_index(out_dir: Path, colors: list[dict]) -> dict[str, bool]:
    index: dict[str, bool] = {}
    for c in colors:
        fp = out_dir / f"{c['pinyin']}.json"
        if fp.exists():
            data = json.loads(fp.read_text(encoding="utf-8"))
            index[c["pinyin"]] = bool(data.get("entries"))
        else:
            index[c["pinyin"]] = False
    return index


def main():
    parser = argparse.ArgumentParser(description="构建识色赋诗诗句库")
    parser.add_argument("--corpus", type=Path, default=Path("../vendor/chinese-poetry"))
    parser.add_argument("--colors", type=Path, default=Path("../data/colors.json"))
    parser.add_argument("--out", type=Path, default=Path("../data/poetry"))
    parser.add_argument("--imagery", type=Path, default=Path("color_imagery.yaml"))
    parser.add_argument("--aliases", type=Path, default=Path("imagery_aliases.yaml"))
    parser.add_argument("--index-only", action="store_true")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    corpus_path = (script_dir / args.corpus).resolve()
    colors_path = (script_dir / args.colors).resolve()
    out_dir = (script_dir / args.out).resolve()
    imagery_path = (script_dir / args.imagery).resolve()
    aliases_path = (script_dir / args.aliases).resolve()

    colors = json.loads(colors_path.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.index_only:
        index = write_index(out_dir, colors)
        (out_dir.parent / "poetry-index.json").write_text(
            json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"索引已写入，共 {sum(index.values())} 种颜色有诗句")
        return

    ensure_corpus(corpus_path)
    manual = yaml.safe_load(imagery_path.read_text(encoding="utf-8")) if imagery_path.exists() else {}
    aliases = load_alias_map(aliases_path)

    records = build_records(corpus_path)
    buckets = bucket_matches(records, colors, manual, aliases)

    index: dict[str, bool] = {}
    zero_coverage: list[str] = []
    stats = {"full": 0, "partial": 0, "zero": 0}
    imagery_hits = 0

    print("写入各色 JSON…", flush=True)
    seen_pinyin: set[str] = set()
    for c in colors:
        name, pinyin, hex_val = c["name"], c["pinyin"], c["hex"]
        if pinyin in seen_pinyin:
            continue
        seen_pinyin.add(pinyin)

        entries = pick_top(buckets, pinyin)
        imagery_hits += sum(1 for e in entries if e.get("matchVia") == "imagery")
        coverage = f"{len(entries)}/{TARGET}"
        payload = {"color": name, "pinyin": pinyin, "hex": hex_val, "entries": entries, "coverage": coverage}
        (out_dir / f"{pinyin}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        index[pinyin] = len(entries) > 0
        if len(entries) == 0:
            zero_coverage.append(name)
            stats["zero"] += 1
        elif len(entries) < TARGET:
            stats["partial"] += 1
        else:
            stats["full"] += 1

    (out_dir.parent / "poetry-index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    report = [
        f"总计颜色: {len(seen_pinyin)}",
        f"满覆盖 ({TARGET}/{TARGET}): {stats['full']}",
        f"部分覆盖: {stats['partial']}",
        f"零覆盖: {stats['zero']}",
        f"意象匹配入选句数: {imagery_hits}",
        "",
        "零覆盖色名:",
        *zero_coverage,
    ]
    report_path = script_dir / "build_report.txt"
    report_path.write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report[:7]), flush=True)
    print(f"报告: {report_path}", flush=True)


if __name__ == "__main__":
    main()
