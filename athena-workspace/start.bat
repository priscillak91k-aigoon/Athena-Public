@echo off
title Lobotto Workspace
echo.
echo  ==========================================
echo   Lobotto Workspace ^| http://localhost:7337
echo  ==========================================
echo.
echo  Starting server...
echo  Press Ctrl+C to stop.
echo.
cd /d "%~dp0.."
python athena-workspace\server.py
pause
