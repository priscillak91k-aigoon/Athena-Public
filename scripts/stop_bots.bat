@echo off
:: Stop all Athena bots
taskkill /f /fi "windowtitle eq Athena-Telegram" 2>nul
taskkill /f /fi "windowtitle eq Athena-Discord" 2>nul
echo [Athena] All bots stopped.
timeout /t 3
