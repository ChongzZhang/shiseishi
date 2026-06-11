@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo   色谱寻诗 — 生成安全发布包 (dist/)
echo.

python scripts\regen_frontend.py
if errorlevel 1 (
    echo 前端数据刷新失败
    pause
    exit /b 1
)

python scripts\build_deploy.py
if errorlevel 1 (
    echo 发布包构建失败
    pause
    exit /b 1
)

echo.
echo   完成。dist/ 目录仅含对外静态资源。
echo.
echo   GitHub Pages:
echo     1. 将本仓库推送到 GitHub
echo     2. Settings - Pages - Source 选 GitHub Actions
echo     3. push 到 main 分支后自动部署
echo.
echo   Cloudflare Pages:
echo     1. 连接 GitHub 仓库，或手动上传 dist/ 文件夹
echo     2. Build command: python scripts/build_deploy.py
echo     3. Output directory: dist
echo.
pause
