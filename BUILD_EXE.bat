@echo off
title SHAIK-AI — Build Windows EXE
color 0A
echo.
echo  =====================================================
echo       SHAIK-AI — Build Installer (.exe)
echo  =====================================================
echo.

:: Install PyInstaller
python -m pip install pyinstaller --quiet
echo [1/3] PyInstaller ready.

:: Generate icons
python make_icons.py
echo [2/3] Icons created.

:: Build EXE
pyinstaller --noconfirm --onefile --windowed ^
  --name "SHAIK-AI" ^
  --icon "static/icon-192.png" ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import flask ^
  --hidden-import pyttsx3 ^
  --hidden-import speech_recognition ^
  app.py

echo.
echo [3/3] Build complete!
echo.
echo  Your EXE is at: dist\SHAIK-AI.exe
echo  Share that file — anyone can run it on Windows!
echo.
pause
