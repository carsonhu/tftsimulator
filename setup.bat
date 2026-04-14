@echo off
echo Creating virtual environment...
set PYTHON_CMD=python

REM Try to find a stable Python version using py launcher
py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Found Python 3.12, using it...
    set PYTHON_CMD=py -3.12
) else (
    py -3.11 --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo Found Python 3.11, using it...
        set PYTHON_CMD=py -3.11
    )
)

if not exist .venv (
    %PYTHON_CMD% -m venv .venv
) else (
    echo Virtual environment already exists.
)

echo Activating virtual environment...
call .venv\Scripts\activate

echo Upgrading pip and installing build tools...
python -m pip install --upgrade pip
pip install setuptools wheel

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete! You can now run 'run_app.bat'.
pause
