@echo off
REM Developer setup: everything run_app.bat installs, plus the test/analysis
REM extras (pytest, matplotlib), then runs the suite to prove it works.
REM You do NOT need this just to launch the app -- run_app.bat self-installs.
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "VENV_PY=.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    set "PY="
    for %%V in (3.13 3.12 3.11) do (
        if not defined PY (
            py -%%V --version >/dev/null 2>&1 && set "PY=py -%%V"
        )
    )
    if not defined PY (
        py -3 --version >/dev/null 2>&1 && set "PY=py -3"
    )
    if not defined PY (
        echo Could not find Python. Install 3.12 or newer from python.org.
        pause
        exit /b 1
    )
    echo Creating virtual environment with !PY! ...
    !PY! -m venv .venv
    if errorlevel 1 goto :fail
)

echo Installing runtime + dev dependencies ...
"%VENV_PY%" -m pip install --upgrade pip --quiet
if errorlevel 1 goto :fail
"%VENV_PY%" -m pip install -r requirements-dev.txt
if errorlevel 1 goto :fail

REM Keep run_app.bat from redoing the runtime install on its next launch.
set "REQ_HASH="
for /f "skip=1 delims=" %%H in ('certutil -hashfile requirements.txt SHA256') do (
    if not defined REQ_HASH set "REQ_HASH=%%H"
)
> ".venv\requirements.sha256" echo !REQ_HASH!

echo.
echo Running the test suite ...
"%VENV_PY%" -m pytest -q

echo.
echo Setup complete. Use run_app.bat to launch the app.
pause
goto :eof

:fail
echo.
echo Setup failed - see the output above.
pause
exit /b 1
