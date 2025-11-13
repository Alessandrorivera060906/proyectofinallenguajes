@echo off
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8502 ^| findstr LISTENING') do taskkill /PID %%a /F
pause
