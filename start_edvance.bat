@echo off
echo ========================================
echo    Starting Edvance Education Platform
echo ========================================
echo.
echo Starting Flask Server...
cd backend
start "Edvance Flask Server" cmd /k "start_server_forever.bat"
echo.
echo Flask server is starting...
echo.
echo Opening frontend in browser...
timeout /t 3 /nobreak > nul
start "" "frontend/index.html"
echo.
echo ========================================
echo Server should be running on:
echo http://localhost:5001
echo.
echo Frontend opened in browser
echo ========================================
pause
