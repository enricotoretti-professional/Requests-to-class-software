@echo off
setlocal
set "PAGE=%~dp0index.html"
set "CHROME="

for %%P in ("%ProgramFiles%\Google\Chrome\Application\chrome.exe" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" "%LocalAppData%\Google\Chrome\Application\chrome.exe") do (
  if not defined CHROME if exist "%%~P" set "CHROME=%%~P"
)

if defined CHROME (
  start "" "%CHROME%" "%PAGE%"
  exit /b 0
)

where chrome.exe >nul 2>nul
if not errorlevel 1 (
  start "" chrome.exe "%PAGE%"
  exit /b 0
)

echo Google Chrome was not found. Install Chrome or open index.html in Chrome manually.
pause
exit /b 1
