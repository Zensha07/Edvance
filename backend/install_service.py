#!/usr/bin/env python3
"""
Script to install Flask server as a Windows service
Run this as Administrator to install the service
"""

import os
import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import subprocess

class FlaskService(win32serviceutil.ServiceFramework):
    _svc_name_ = "EdvanceFlaskServer"
    _svc_display_name_ = "Edvance Flask Server"
    _svc_description_ = "Flask server for Edvance education platform"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        self.main()

    def main(self):
        # Change to the backend directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(backend_dir)
        
        # Start the Flask server
        try:
            subprocess.run([sys.executable, "run_server.py"], check=True)
        except subprocess.CalledProcessError as e:
            servicemanager.LogErrorMsg(f"Flask server error: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(FlaskService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(FlaskService)
