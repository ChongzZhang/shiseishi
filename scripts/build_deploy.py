#!/usr/bin/env python3
"""生成仅含对外静态资源的 dist/ 目录，用于 GitHub Pages / Cloudflare Pages。"""

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

# 明确白名单：不复制 scripts、vendor、管理工具、原始 data 源文件等
COPY_FILES = [
    "index.html",
    "css/style.css",
    "js/poetry-ui.js",
    "js/palette.js",
    "js/poetry-bundle.js",
    "js/extract.js",
    "js/match.js",
    "js/app.js",
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


def main():
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

    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "_headers").write_text(HEADERS, encoding="utf-8")
    (DIST / "404.html").write_text(NOT_FOUND_HTML, encoding="utf-8")
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")

    file_count = sum(1 for _ in DIST.rglob("*") if _.is_file())
    print(f"已生成 {DIST}")
    print(f"  文件数: {file_count}")
    print("  未包含: scripts/, vendor/, data/poetry/, data/colors.json, 管理工具等")
    if missing:
        print("  警告 — 缺失源文件:")
        for m in missing:
            print(f"    - {m}")


if __name__ == "__main__":
    main()
