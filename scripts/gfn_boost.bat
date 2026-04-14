@echo off
:: ============================================================
::  GFN BOOST — PC Optimization Launcher
::  Lobotto Framework | Priscilla's MSI WE75
::
::  Double-click to run. Right-click -> Run as Administrator
::  for power plan changes to fully apply.
:: ============================================================
title GFN BOOST - Optimizing...
powershell -ExecutionPolicy Bypass -File "%~dp0optimize.ps1"
pause
