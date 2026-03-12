@echo off
chcp 65001 >nul
title Kaell Voice Assistant - Telegram Bot (Auto-Restart)

:loop
cls
echo ==============================================
echo    Starting Kaell Telegram Bot...
echo    Status: MONITORING MODE (Auto-Restart)
echo ==============================================
echo.

cd /d "d:\My Projects\python\kaell-assistan-v2"
python telegram_bot.py

echo.
echo ================================================
echo    Bot stopped. Restarting in 5 seconds...
echo    Press Ctrl+C to stop completely.
echo ================================================
echo.

ping -n 6 127.0.0.1 >nul
goto loop