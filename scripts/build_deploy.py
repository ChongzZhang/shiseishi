#!/usr/bin/env python3
"""生成仅含对外静态资源的 dist/ 目录，用于 GitHub Pages / Cloudflare Pages。"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
NEW_BOOKMARKS = ROOT / "assets" / "color-bookmarks" / "new"

# 明确白名单：不复制 scripts、vendor、管理工具、原始 data 源文件等
COPY_FILES = [
    "index.html",
    "achievements.html",
    "daily.html",
    "css/style.css",
    "js/poetry-ui.js",
    "js/palette.js",
    "js/poetry-bundle.js",
    "js/extract.js",
    "js/match.js",
    "js/app.js",
    "js/achievements.js",
    "js/achievements-page.js",
    "js/daily.js",
    "js/daily-page.js",
    "js/colors-data.js",
    "js/rgb-index-data.js",
    "js/browse.js",
    "data/poetry-preview.txt",
]

BROWSE_FOOTER = """    <footer class="site-footer">
      <p>色名参考 <a href="https://zhongguose.com/" target="_blank" rel="noopener">中国色</a> · 诗句来自开源古典文集 · <a href="data/poetry-preview.txt" target="_blank" rel="noopener">诗句预览</a></p>
    </footer>"""

HEADERS = """/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
"""

NOT_FOUND_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>页面未找到 — 色谱寻诗</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <div class="page" style="text-align:center;padding:4rem 1rem">
    <h1>页面未找到</h1>
    <p><a href="index.html">返回色谱寻诗</a></p>
  </div>
</body>
</html>
"""


def patch_browse_html(src: str) -> str:
    return re.sub(
        r"<footer class=\"site-footer\">.*?</footer>",
        BROWSE_FOOTER.strip(),
        src,
        count=1,
        flags=re.DOTALL,
    )


def regen_bookmark_manifest() -> None:
    script = ROOT / "scripts" / "gen_new_bookmark_manifest.py"
    subprocess.run([sys.executable, str(script)], check=True, cwd=ROOT)


def regen_daily_challenges() -> None:
    script = ROOT / "scripts" / "gen_daily_challenges.py"
    subprocess.run([sys.executable, str(script)], check=True, cwd=ROOT)


def copy_daily_challenges() -> bool:
    src = ROOT / "assets" / "color-bookmarks" / "daily-challenges.json"
    if not src.is_file():
        print("  警告 — 未找到 daily-challenges.json")
        return False
    dst = DIST / "assets" / "color-bookmarks" / "daily-challenges.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def copy_new_bookmarks() -> int:
    """复制 manifest 中列出的新书签 PNG 与 manifest.json。"""
    manifest_src = NEW_BOOKMARKS / "manifest.json"
    if not manifest_src.is_file():
        print("  警告 — 未找到 new/manifest.json，跳过书签资源")
        return 0

    import json

    manifest = json.loads(manifest_src.read_text(encoding="utf-8"))
    out_dir = DIST / "assets" / "color-bookmarks" / "new"
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manifest_src, out_dir / "manifest.json")

    count = 1
    for entry in manifest:
        png = NEW_BOOKMARKS / entry["file"]
        if not png.is_file():
            print(f"  警告 — 缺失书签 PNG: {entry['file']}")
            continue
        shutil.copy2(png, out_dir / entry["file"])
        count += 1
    return count


def main():
    regen_bookmark_manifest()
    regen_daily_challenges()

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    missing = []
    for rel in COPY_FILES:
        src = ROOT / rel
        dst = DIST / rel
        if not src.is_file():
            missing.append(rel)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    browse_src = (ROOT / "browse.html").read_text(encoding="utf-8")
    (DIST / "browse.html").write_text(patch_browse_html(browse_src), encoding="utf-8")

    bookmark_count = copy_new_bookmarks()
    daily_ok = copy_daily_challenges()

    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "_headers").write_text(HEADERS, encoding="utf-8")
    (DIST / "404.html").write_text(NOT_FOUND_HTML, encoding="utf-8")
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")

    file_count = sum(1 for _ in DIST.rglob("*") if _.is_file())
    print(f"已生成 {DIST}")
    print(f"  文件数: {file_count}")
    print(f"  成就书签: {bookmark_count} 个文件（含 manifest）")
    print(f"  每日挑战: {'已包含' if daily_ok else '缺失'}")
    print("  未包含: scripts/, vendor/, data/poetry/, data/colors.json, 管理工具等")
    if missing:
        print("  警告 — 缺失源文件:")
        for m in missing:
            print(f"    - {m}")


if __name__ == "__main__":
    main()
