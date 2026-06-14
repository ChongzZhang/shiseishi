#!/usr/bin/env python3
"""扫描语料库中可疑的朝代标注。"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from dynasty import infer_dynasty, is_cipai, load_author_dynasty

ROOT = SCRIPT_DIR.parent
POETRY_DIR = ROOT / "data" / "poetry"
OUT = ROOT / "scripts" / "dynasty_audit.txt"

# 常见宋词人（不应标为唐）
SONG_CI_POETS = {
    "周邦彦", "李清照", "苏轼", "辛弃疾", "姜夔", "吴文英", "史达祖", "周邦彦",
    "张炎", "王沂孙", "蒋捷", "周密", "吴文英", "贺铸", "秦观", "柳永", "晏殊",
    "晏几道", "欧阳修", "范仲淹", "陆游", "杨万里", "范成大", "陆叡",
}


def main():
    authors = load_author_dynasty()
    issues: list[str] = []

    for path in sorted(POETRY_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        color = data.get("color", path.stem)
        for e in data.get("entries", []):
            author = (e.get("author") or "").strip()
            title = (e.get("title") or "").strip()
            stored = e.get("dynasty", "")
            inferred = infer_dynasty(e)
            ptype = e.get("type", "")

            if inferred != stored and stored:
                issues.append(
                    f"不一致 | {color} | {author}《{title}》stored={stored} inferred={inferred}"
                )
            if inferred == "唐" and author in SONG_CI_POETS:
                issues.append(
                    f"宋词人标唐 | {color} | {author}《{title}》type={ptype}"
                )
            if is_cipai(title) and inferred == "唐":
                issues.append(
                    f"词牌标唐 | {color} | {author}《{title}》"
                )
            if author and author in authors and inferred != authors[author]:
                issues.append(
                    f"与作者表不符 | {color} | {author}《{title}》"
                    f"表={authors[author]} inferred={inferred}"
                )

    OUT.write_text("\n".join(issues) if issues else "未发现可疑朝代", encoding="utf-8")
    print(f"扫描完成：{len(issues)} 条可疑 → {OUT}")


if __name__ == "__main__":
    main()
