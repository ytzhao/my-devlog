@echo off
chcp 65001 >nul
cd /d "%~dp0.."
set DEVLOG_ROOT=%CD%
echo 🖍️ Starting Web Highlight Server...
echo    DEVLOG_ROOT=%DEVLOG_ROOT%
python tools\web_highlight_server.py
pause
