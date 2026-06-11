@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo   色谱寻诗 - Public Server
echo.

:: Kill any old process on port 8766
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8766 " ^| findstr "LISTENING"') do (
    echo Cleaning up old process (PID: %%a^)
    taskkill /PID %%a /F >nul 2>&1
)

python _serve_public.py

pause
