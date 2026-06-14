#!/usr/bin/env python3
"""修正诗句条目的 type / source / dynasty 元数据。"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from dynasty import infer_dynasty, is_cipai, is_placeholder_source, load_author_dynasty

ROOT = SCRIPT_DIR.parent
POETRY_DIR = ROOT / "data" / "poetry"
AUTHORS = load_author_dynasty()


def fix_entry(e: dict) -> tuple[dict, list[str]]:
    changes: list[str] = []
    e = dict(e)

    src = e.get("source") or ""
    if is_placeholder_source(src):
        e.pop("source", None)
        changes.append("删除占位 source")

    title = (e.get("title") or "").strip()
    author = (e.get("author") or "").strip()
    ptype = e.get("type") or ""

    if is_cipai(title) and ptype != "词":
        e["type"] = "词"
        changes.append(f"type 诗→词（词牌《{title}》）")

    if author in AUTHORS and ptype == "诗" and is_cipai(title):
        e["type"] = "词"
        changes.append("宋词人+词牌 → 词")

    dynasty = infer_dynasty(e)
    if dynasty:
        if e.get("dynasty") != dynasty:
            e["dynasty"] = dynasty
            changes.append(f"朝代 → {dynasty}")
    elif "dynasty" in e:
        del e["dynasty"]
        changes.append("清除错误朝代")

    return e, changes


def main():
    total_changes = 0
    report: list[str] = []

    for path in sorted(POETRY_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        file_changed = False
        new_entries = []
        for e in data.get("entries", []):
            fixed, changes = fix_entry(e)
            new_entries.append(fixed)
            if changes:
                file_changed = True
                total_changes += 1
                report.append(
                    f"{data.get('color')} | {fixed.get('author')}《{fixed.get('title')}》"
                    f" → {', '.join(changes)}"
                )
        if file_changed:
            data["entries"] = new_entries
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    log = ROOT / "scripts" / "fix_poetry_metadata_report.txt"
    log.write_text("\n".join(report) if report else "无修改", encoding="utf-8")
    print(f"修正 {total_changes} 条 → {log}")


if __name__ == "__main__":
    main()
