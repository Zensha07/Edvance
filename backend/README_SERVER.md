# Flask Server Startup Options

This directory contains multiple ways to run the Flask server persistently:

## Option 1: Simple Batch File (Recommended for Development)
```bash
# Double-click or run:
start_server.bat
```
- Starts the server once
- Keeps window open to see logs
- Easy to stop with Ctrl+C

## Option 2: Auto-Restart Batch File (Recommended for Production)
```bash
# Double-click or run:
start_server_forever.bat
```
- Automatically restarts server if it crashes
- Runs continuously
- Good for production use

## Option 3: PowerShell Script (Advanced)
```powershell
# Run in PowerShell:
.\start_server_ps1.ps1
```
- More control and logging
- Auto-restart on crash
- Better error handling

## Option 4: Windows Service (Advanced - Requires Admin)
```bash
# Install service (Run as Administrator):
python install_service.py install

# Start service:
python install_service.py start

# Stop service:
python install_service.py stop

# Remove service:
python install_service.py remove
```

## Quick Start
1. Double-click `start_server_forever.bat`
2. Server will start on http://localhost:5001
3. Keep the window open - server will auto-restart if needed

## Server Features
- Teacher Profile Management
- Student Profile Management  
- Notes Upload & Download
- Video Upload & Online Playback
- Auto-reload on code changes (debug mode)
