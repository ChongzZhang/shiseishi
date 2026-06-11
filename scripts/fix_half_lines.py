#!/usr/bin/env python3
"""将无逗号分句的半句补为完整联（上句，下句）。"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POETRY = ROOT / "data" / "poetry"

# old_line_prefix -> new full couplet
FIXES: dict[str, dict] = {
    "酣酣日脚紫烟浮": {
        "line": "酣酣日脚紫烟浮，妍暖破轻裘。",
        "type": "词",
    },
    "白头宫女在": {
        "line": "白头宫女在，闲坐说玄宗。",
        "type": "诗",
    },
    "看浩荡、千崖秋色": {
        "line": "赖有高楼百尺，看浩荡、千崖秋色。",
        "type": "词",
    },
    "小窗愁黛澹秋山": {
        "line": "乡梦窄，水天宽，小窗愁黛澹秋山。",
        "type": "词",
    },
    "红杏枝头花几许": {
        "line": "红杏枝头花几许，啼痕止恨清明雨。",
        "type": "词",
    },
    "绛唇初点粉红新。": {
        "line": "绛唇初点粉红新，凤镜临妆已逼真。",
        "type": "词",
    },
    "露濯文犀和粉绿。": {
        "line": "露濯文犀和粉绿，未容浓翠伴桃红。",
        "type": "词",
    },
    "丹桂红蕖又晚秋。": {
        "line": "壮志世难酬，丹桂红蕖又晚秋。",
        "type": "词",
    },
    "明绿染春丝。": {
        "line": "垂杨袅袅蘸清漪，明绿染春丝。",
        "type": "词",
    },
    "不是花红是玉红。": {
        "line": "多谢春工，不是花红是玉红。",
        "type": "词",
    },
}


def main():
    changed = []
    for path in sorted(POETRY.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        file_changed = False
        for e in data.get("entries", []):
            line = e.get("line", "")
            for old, fix in FIXES.items():
                if line.strip() == old or line.strip().startswith(old.rstrip("。")):
                    if line != fix["line"]:
                        changed.append((data.get("color"), line, fix["line"]))
                        e["line"] = fix["line"]
                        if fix.get("type"):
                            e["type"] = fix["type"]
                        file_changed = True
                    break
        if file_changed:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"fixed {len(changed)} lines")
    for color, old, new in changed:
        print(f"  [{color}] {old} -> {new}")

    if changed:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "regen_frontend.py")],
            cwd=str(ROOT),
            check=True,
        )


if __name__ == "__main__":
    main()
