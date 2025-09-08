@echo off
echo Starting Flask Server (Auto-restart on crash)...
cd /d "%~dp0"

:restart
echo Starting server at %date% %time%
python run_server.py
echo Server crashed or stopped. Restarting in 5 seconds...
timeout /t 5 /nobreak > nul
goto restart
