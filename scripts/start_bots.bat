@echo off
:: ═══════════════════════════════════════════════════════════
:: Athena Bots Launcher — starts unified bots in background
:: Run this at startup or whenever you want bots online
:: ═══════════════════════════════════════════════════════════

cd /d "%~dp0.."
echo [Athena] Starting bots from: %cd%

:: Kill any existing bot processes first
taskkill /f /fi "windowtitle eq Athena-Telegram" 2>nul
taskkill /f /fi "windowtitle eq Athena-Discord" 2>nul
timeout /t 1 /nobreak >nul

:: Start Lobotto Telegram Bot (unified: conversation + reminders)
start "Athena-Telegram" /min python scripts/lobotto_telegram.py
echo [OK] Lobotto Telegram Bot started (conversation + reminders)

:: Start Lobotto Discord Bot (v2 — proactive)
start "Athena-Discord" /min python scripts/discord_bot.py
echo [OK] Lobotto Discord Bot started (v2 — proactive)

:: Start Deploy Server (Sync button backend — port 7338)
taskkill /f /fi "windowtitle eq Athena-Deploy" 2>nul
start "Athena-Deploy" /min python scripts/deploy_server.py
echo [OK] Deploy Server started (port 7338 — Sync button backend)

echo.
echo [Athena] All services running in minimized windows.
echo          To stop: run stop_bots.bat or close via Task Manager
timeout /t 5
