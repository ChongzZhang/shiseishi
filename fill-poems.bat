@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo   色谱寻诗 - 无诗色补诗
echo   唐三百 / 宋词  -^> 添加 / 舍弃
echo.
python _fill_poems.py
pause
