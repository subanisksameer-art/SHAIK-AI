@echo off
title SHAIK-AI Setup
color 0B
echo.
echo  ====================================================
echo       SHAIK-AI -- Installing Dependencies
echo  ====================================================
echo.

:: Find python
set PYTHON=python
where python >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Users\pc\AppData\Local\Programs\Python\Python314\python.exe" set PYTHON=C:\Users\pc\AppData\Local\Programs\Python\Python314\python.exe
    if exist "C:\Users\pc\AppData\Local\Programs\Python\Python313\python.exe" set PYTHON=C:\Users\pc\AppData\Local\Programs\Python\Python313\python.exe
    if exist "C:\Users\pc\AppData\Local\Programs\Python\Python312\python.exe" set PYTHON=C:\Users\pc\AppData\Local\Programs\Python\Python312\python.exe
    if exist "C:\Users\pc\AppData\Local\Programs\Python\Python311\python.exe" set PYTHON=C:\Users\pc\AppData\Local\Programs\Python\Python311\python.exe
)

echo [Python] %PYTHON%
echo.
echo Installing packages... (internet required)
echo.

"%PYTHON%" -m pip install --upgrade pip
"%PYTHON%" -m pip install SpeechRecognition pyttsx3 sounddevice scipy numpy

echo.
echo ====================================================
echo  Done! Now run START_SHAIK.bat to launch SHAIK-AI
echo ====================================================
pause
