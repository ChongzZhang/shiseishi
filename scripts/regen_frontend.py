#!/usr/bin/env python3
"""补诗/筛诗后刷新 browse 页与游戏用的内嵌 JS 数据包。"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def regen_frontend(verbose=True):
    fix = SCRIPTS / "fix_poetry_metadata.py"
    if fix.exists():
        if verbose:
            print("Running fix_poetry_metadata.py...")
        subprocess.run([sys.executable, str(fix)], cwd=str(SCRIPTS), check=True)
    for name in ("fix_name_pinyin.py", "gen_browse_data.py", "gen_rgb_index.py", "gen_palette.py", "gen_rarity.py", "gen_glosses_data.py"):
        if verbose:
            print(f"Running {name}...")
        subprocess.run(
            [sys.executable, str(SCRIPTS / name)],
            cwd=str(SCRIPTS),
            check=True,
        )


if __name__ == "__main__":
    regen_frontend()
