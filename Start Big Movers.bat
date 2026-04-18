@echo off
title Big Movers Dashboard
cd /d "%~dp0"

echo Starting Big Movers server...
start "" python Big_movers_server.py

echo Waiting for server to start...
timeout /t 3 /nobreak >nul

start "" http://127.0.0.1:5051

echo Server is running. Close this window to keep it running in background.
echo Press any key to STOP the server.
pause >nul

:: Kill the Flask server when user presses a key
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5051"') do taskkill /PID %%a /F >nul 2>&1
echo Server stopped.
