@echo off
REM One-click local launch: creates the venv on first run, reinstalls when
REM requirements.txt changes, then starts Streamlit. No prior setup needed.
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "VENV_PY=.venv\Scripts\python.exe"

REM --- find an interpreter, newest first (only used to create the venv) ---
if not exist "%VENV_PY%" (
    set "PY="
    for %%V in (3.13 3.12 3.11) do (
        if not defined PY (
            py -%%V --version >nul 2>&1 && set "PY=py -%%V"
        )
    )
    if not defined PY (
        py -3 --version >nul 2>&1 && set "PY=py -3"
    )
    if not defined PY (
        python --version >nul 2>&1 && set "PY=python"
    )
    if not defined PY (
        echo Could not find Python. Install 3.12 or newer from python.org,
        echo tick "Add python.exe to PATH", then run this again.
        pause
        exit /b 1
    )
    echo Creating virtual environment with !PY! ...
    !PY! -m venv .venv
    if errorlevel 1 goto :fail
    echo.
)

REM --- reinstall only when requirements.txt has actually changed ---
set "REQ_HASH="
for /f "skip=1 delims=" %%H in ('certutil -hashfile requirements.txt SHA256') do (
    if not defined REQ_HASH set "REQ_HASH=%%H"
)
set "STAMP=.venv\requirements.sha256"
set "OLD_HASH="
if exist "%STAMP%" set /p OLD_HASH=<"%STAMP%"

if not "!REQ_HASH!"=="!OLD_HASH!" (
    echo Installing dependencies ^(requirements.txt changed^) ...
    "%VENV_PY%" -m pip install --upgrade pip --quiet
    if errorlevel 1 goto :fail
    "%VENV_PY%" -m pip install -r requirements.txt
    if errorlevel 1 goto :fail
    > "%STAMP%" echo !REQ_HASH!
    echo.
)

echo Starting Streamlit ^(Ctrl+C to stop^) ...
"%VENV_PY%" -m streamlit run app.py
goto :eof

:fail
echo.
echo Setup failed - see the output above.
pause
exit /b 1
