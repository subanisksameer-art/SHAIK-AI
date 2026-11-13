@echo off
echo Installing SHAIK-AI dependencies...
python -m pip install -r requirements.txt
echo.
echo Done! Run SHAIK-AI with:
echo   run.bat           (voice mode)
echo   run.bat --text    (keyboard mode)
echo   run.bat --test "open Chrome"  (single command test)
pause
