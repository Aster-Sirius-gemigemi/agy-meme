@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  python -B -X utf8 scripts\desktop.py uninstall
) else (
  py -3 -B -X utf8 scripts\desktop.py uninstall
)
if errorlevel 1 pause
