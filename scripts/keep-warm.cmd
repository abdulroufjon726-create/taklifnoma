@echo off
rem Taklifnoma backend'ini uyg'oq ushlab turadigan pinger (Windows).
rem Render bepul instansiyasi 15 daqiqa harakatsizlikdan keyin uxlaydi.
rem Har 4 daqiqada /api/health/ ga ping yuboriladi — u bazaga SELECT 1 qiladi,
rem shuning uchun Postgres ham uyg'oq qoladi.
rem
rem Ishlatish:
rem   Bir marta:      scripts\keep-warm.cmd --once
rem   Doimiy tsikl:   scripts\keep-warm.cmd
rem   Avtomatik (Task Scheduler, kompyuter yoniq turganda, har 5 daqiqada):
rem     schtasks /create /tn "Taklifnoma keep-warm" /sc minute /mo 5 /f ^
rem       /tr "cmd /c \"%CD%\scripts\keep-warm.cmd\" --once"
rem     O'chirish:  schtasks /delete /tn "Taklifnoma keep-warm" /f
rem
rem Kompyuter o'chsa yoki uxlasa ping ham to'xtaydi — u holda Render yana uxlaydi.
setlocal EnableDelayedExpansion
if "%KEEP_WARM_URL%"=="" (set "URL=https://taklifnoma-1.onrender.com/api/health/") else (set "URL=%KEEP_WARM_URL%")
if "%KEEP_WARM_INTERVAL%"=="" (set "INTERVAL=240") else (set "INTERVAL=%KEEP_WARM_INTERVAL%")
set "LOG=%~dp0..\keep-warm.log"

if /I "%~1"=="--once" (
  call :ping
  exit /b !ERRORLEVEL!
)

echo keep-warm: %URL% har %INTERVAL%s ping qilinadi. To'xtatish: Ctrl+C
:loop
call :ping
if not "!CODE!"=="200" (
  timeout /t 20 /nobreak >nul
  call :ping
)
timeout /t %INTERVAL% /nobreak >nul
goto loop

:ping
set "CODE="
for /f "delims=" %%C in ('curl -s -o "%TEMP%\keep-warm.json" -w "%%{http_code}" --max-time 45 "%URL%" 2^>nul') do set "CODE=%%C"
if "!CODE!"=="" set "CODE=000"
echo %DATE% %TIME%  HTTP !CODE!  >> "%LOG%"
echo %DATE% %TIME%  HTTP !CODE!
if "!CODE!"=="200" (exit /b 0) else (exit /b 1)
