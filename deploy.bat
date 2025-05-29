@echo off
echo ==========================================
echo Vehicle Parking App - GitHub Upload
echo ==========================================
echo.

echo This script will help you upload your project to GitHub.
echo Make sure you have Git installed and a GitHub account ready.
echo.

echo Step 1: Initialize Git Repository
echo.
git --version
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in PATH.
    echo Please install Git from: https://git-scm.com/download/windows
    pause
    exit /b 1
)

echo Git is installed. Proceeding...
echo.

echo Initializing Git repository...
git init

echo Adding all files...
git add .

echo Creating initial commit...
git commit -m "Initial commit: Vehicle Parking App with MongoDB"

echo.
echo ==========================================
echo Next Steps:
echo ==========================================
echo.
echo 1. Go to GitHub.com and create a new repository
echo    - Repository name: vehicle-parking-app
echo    - Description: A modern vehicle parking management system
echo    - Make it Public (or Private if you prefer)
echo    - DO NOT initialize with README
echo.
echo 2. Copy the repository URL (e.g., https://github.com/USERNAME/vehicle-parking-app.git)
echo.
echo 3. Run these commands (replace USERNAME with your GitHub username):
echo    git remote add origin https://github.com/USERNAME/vehicle-parking-app.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 4. Follow the deployment guide in deploy.md for cloud deployment
echo.
pause 