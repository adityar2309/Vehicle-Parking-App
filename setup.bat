@echo off
echo ==========================================
echo Vehicle Parking App - Setup Script
echo ==========================================
echo.

echo Setting up Backend...
cd backend
echo Creating virtual environment...
python -m venv venv
echo Activating virtual environment...
call venv\Scripts\activate
echo Installing Python dependencies...
pip install -r requirements.txt
cd ..

echo.
echo Setting up Frontend...
cd frontend
echo Installing Node.js dependencies...
npm install
cd ..

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To run the application:
echo 1. Run setup.bat (this file) - Done!
echo 2. Run run.bat to start both servers
echo.
echo Or run manually:
echo Backend: cd backend && venv\Scripts\activate && python app.py
echo Frontend: cd frontend && npm start
echo.
pause 