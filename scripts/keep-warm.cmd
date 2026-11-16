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
rem Kutish uchun `timeout` ishlatilmaydi: u konsol bo'lmagan oqimda (Task
rem Scheduler, Git Bash, pipe) darhol chiqib ketadi va tsikl sekundiga bir marta
rem aylanadi. `ping -n` esa har qanday muhitda ishlaydi.
setlocal EnableDelayedExpansion
if "%KEEP_WARM_URL%"=="" (set "URL=https://taklifnoma-1.onrender.com/api/health/") else (set "URL=%KEEP_WARM_URL%")
if "%KEEP_WARM_INTERVAL%"=="" (set "INTERVAL=240") else (set "INTERVAL=%KEEP_WARM_INTERVAL%")
set "LOG=%~dp0..\keep-warm.log"

if /I "%~1"=="--once" (
  call :ping
  if not "!CODE!"=="200" (
    call :wait 15
    call :ping
  )
  if "!CODE!"=="200" (exit /b 0) else (exit /b 1)
)

echo keep-warm: %URL% har %INTERVAL%s ping qilinadi. To'xtatish: Ctrl+C
:loop
call :ping
if not "!CODE!"=="200" (
  call :wait 20
  call :ping
)
call :wait %INTERVAL%
goto loop

:ping
set "CODE="
for /f "delims=" %%C in ('curl -s -H "X-Keep-Warm: windows" -o "%TEMP%\keep-warm.json" -w "%%{http_code}" --max-time 45 "%URL%" 2^>nul') do set "CODE=%%C"
if "!CODE!"=="" set "CODE=000"
echo %DATE% %TIME%  HTTP !CODE!  >> "%LOG%"
echo %DATE% %TIME%  HTTP !CODE!
if "!CODE!"=="200" (exit /b 0) else (exit /b 1)

:wait
rem %1 = soniya; ping har ~1 soniya javob beradi
set /a "_ticks=%~1+1"
ping -n !_ticks! 127.0.0.1 >nul
exit /b 0
