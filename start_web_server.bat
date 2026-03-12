@echo off
chcp 65001 >nul
title Kaell Voice Assistant - Web Server
echo.
echo ========================================
echo    Starting Kaell Web Server...
echo ========================================
echo.
cd /d "d:\My Projects\python\kaell-assistan-v2"
python web_server.py
pause
