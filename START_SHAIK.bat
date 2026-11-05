@echo off
title SHAIK-AI Voice Assistant
color 0A
cls

echo.
echo  ====================================================
echo       SHAIK-AI -- Personal Voice OS Assistant
echo  ====================================================
echo.

:: ── Find Python ─────────────────────────────────────────────────────────────
set PYTHON=

:: Try common paths
if exist "C:\Users\pc\AppData\Local\Programs\Python\Python314\python.exe" (
    set PYTHON=C:\Users\pc\AppData\Local\Programs\Python\Python314\python.exe
)
if exist "C:\Users\pc\AppData\Local\Programs\Python\Python313\python.exe" (
    set PYTHON=C:\Users\pc\AppData\Local\Programs\Python\Python313\python.exe
)
if exist "C:\Users\pc\AppData\Local\Programs\Python\Python312\python.exe" (
    set PYTHON=C:\Users\pc\AppData\Local\Programs\Python\Python312\python.exe
)
if exist "C:\Users\pc\AppData\Local\Programs\Python\Python311\python.exe" (
    set PYTHON=C:\Users\pc\AppData\Local\Programs\Python\Python311\python.exe
)
if exist "C:\Python314\python.exe" (
    set PYTHON=C:\Python314\python.exe
)
if exist "C:\Python313\python.exe" (
    set PYTHON=C:\Python313\python.exe
)
if exist "C:\Python312\python.exe" (
    set PYTHON=C:\Python312\python.exe
)

:: Try PATH python as last resort
if "%PYTHON%"=="" (
    where python >nul 2>&1
    if %errorlevel%==0 set PYTHON=python
)

if "%PYTHON%"=="" (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

echo [OK] Python found: %PYTHON%
echo.

:: ── Install dependencies if missing ─────────────────────────────────────────
echo Checking dependencies...
"%PYTHON%" -c "import speech_recognition" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing SpeechRecognition...
    "%PYTHON%" -m pip install SpeechRecognition --quiet
)

"%PYTHON%" -c "import pyttsx3" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pyttsx3...
    "%PYTHON%" -m pip install pyttsx3 --quiet
)

"%PYTHON%" -c "import sounddevice" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing sounddevice...
    "%PYTHON%" -m pip install sounddevice scipy numpy --quiet
)

echo [OK] All dependencies ready.
echo.

:: ── Mode Selection ───────────────────────────────────────────────────────────
echo Choose mode:
echo   [1] Voice Mode   (Microphone - speak your commands)
echo   [2] Text Mode    (Keyboard   - type your commands)
echo   [3] Quick Test   (Test a single command)
echo.
set /p MODE="Enter 1, 2, or 3: "

if "%MODE%"=="1" (
    echo.
    echo Starting VOICE MODE... speak after the prompt!
    echo Say: "open Chrome", "go to YouTube", "search for news", etc.
    echo Say: "exit" to quit.
    echo.
    "%PYTHON%" main.py
)

if "%MODE%"=="2" (
    echo.
    echo Starting TEXT MODE... type your commands below.
    echo.
    "%PYTHON%" main.py --text
)

if "%MODE%"=="3" (
    echo.
    set /p TESTCMD="Enter test command: "
    "%PYTHON%" main.py --test "%TESTCMD%"
)

echo.
pause
