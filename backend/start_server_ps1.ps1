# PowerShell script to start Flask server with auto-restart
# Run this in PowerShell: .\start_server_ps1.ps1

Write-Host "Starting Edvance Flask Server..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Function to start server
function Start-FlaskServer {
    try {
        Write-Host "Starting Flask server at $(Get-Date)" -ForegroundColor Cyan
        python run_server.py
    }
    catch {
        Write-Host "Server error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Auto-restart loop
while ($true) {
    Start-FlaskServer
    Write-Host "Server stopped. Restarting in 5 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}
