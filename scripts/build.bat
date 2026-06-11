@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  识色赋诗 — 诗句库构建
echo  首次运行需联网克隆语料，全程约 5–15 分钟，请耐心等待。
echo.
python -m pip install -r requirements.txt -q
python build_poetry.py
python gen_palette.py
python gen_browse_data.py
echo.
pause
