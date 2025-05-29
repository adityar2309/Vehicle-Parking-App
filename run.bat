@echo off
echo ==========================================
echo Vehicle Parking App - V2 Startup Script
echo ==========================================
echo.

echo Starting Backend Server...
cd backend
start cmd /k "python app.py"
cd ..

echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
cd frontend
start cmd /k "npm start"
cd ..

echo.
echo Both servers are starting up...
echo Backend will be available at: http://localhost:5000
echo Frontend will be available at: http://localhost:3000
echo.
echo Admin Login: username=admin, password=admin123
echo.
echo Press any key to exit...
pause > nul 