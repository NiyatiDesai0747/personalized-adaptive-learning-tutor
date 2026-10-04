@echo off
setlocal
cd /d "%~dp0"
set "VENV=%USERPROFILE%\TutorVenv"
if not exist "%VENV%\Scripts\python.exe" (
  echo TutorVenv not found. Please run SETUP_AND_RUN.bat first.
  pause
  exit /b 1
)
"%VENV%\Scripts\python.exe" -m streamlit run "%~dp0app.py"
