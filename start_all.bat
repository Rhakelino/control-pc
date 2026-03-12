@echo off
chcp 65001 >nul
title Kaell Voice Assistant - All Services
echo.
echo ========================================
echo    Starting All Kaell Services...
echo ========================================
echo.
cd /d "d:\My Projects\python\kaell-assistan-v2"

echo Starting Web Server...
start "Kaell Web" cmd /k "cd /d \"d:\My Projects\python\kaell-assistan-v2\" && python web_server.py"

timeout /t 3 >nul

echo Starting Telegram Bot...
start "Kaell Telegram" cmd /k "cd /d \"d:\My Projects\python\kaell-assistan-v2\" && python telegram_bot.py"

echo.
echo All services started!
echo.
pause
