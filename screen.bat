@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo   色谱寻诗 - 快速筛选
echo   → 接受 / ← 拒绝
echo.
python _screen.py
pause
