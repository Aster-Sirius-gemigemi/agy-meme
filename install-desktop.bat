@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  python -B -X utf8 scripts\desktop.py install
) else (
  py -3 -B -X utf8 scripts\desktop.py install
)
set "result=%errorlevel%"
if not "%result%"=="0" pause
exit /b %result%
