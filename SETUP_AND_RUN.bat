@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "VENV=%USERPROFILE%\TutorVenv"

echo ================================================
echo   Personalized Adaptive Learning Tutor
echo   Windows setup + run
echo ================================================
echo.

REM Prefer the normal Python command. Fall back to the Python Launcher if needed.
where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
) else (
    where py >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=py"
    ) else (
        echo ERROR: Python was not found on PATH.
        echo Please install Python 3.11+ and make sure "Add Python to PATH" is enabled.
        pause
        exit /b 1
    )
)

echo Using Python command: %PYTHON_CMD%
echo.

if not exist "%VENV%\Scripts\python.exe" (
    echo Creating a clean virtual environment at:
    echo %VENV%
    "%PYTHON_CMD%" -m venv "%VENV%"
    if errorlevel 1 (
        echo.
        echo Could not create the virtual environment.
        pause
        exit /b 1
    )
)

echo.
echo Installing/updating required packages...
"%VENV%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error
"%VENV%\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 goto :error

echo.
echo Starting Streamlit...
echo.
"%VENV%\Scripts\python.exe" -m streamlit run "%~dp0app.py"
exit /b %errorlevel%

:error
echo.
echo Installation failed. Please send a screenshot of this window.
pause
exit /b 1
