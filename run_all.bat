@echo off
echo Starting both Python Backend and .NET Web API...

:: Start Python Backend in a new window
start "Python Backend" cmd /k "run.bat"

:: Wait for Python backend to start
timeout /t 5

:: Start .NET Web API
echo Starting .NET Web API...
cd ChatBotAPI
start "ChatBot API" cmd /k "dotnet run"

echo Both applications are starting...
echo Python Backend will be available at: http://localhost:9000
echo .NET Web API will be available at: http://localhost:7000
echo.
echo Press Ctrl+C in each window to stop the applications. 