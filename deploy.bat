@echo off
echo ==========================================
echo Vehicle Parking App - Google Cloud Deploy
echo ==========================================
echo.

echo This script will deploy your backend to Google Cloud App Engine
echo Project ID: ttsai-461209
echo.

REM Check if gcloud is installed
echo Checking Google Cloud CLI installation...
gcloud --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Google Cloud CLI is not installed or not in PATH.
    echo Please install from: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

echo Google Cloud CLI is installed. ✓
echo.

REM Set the project
echo Setting Google Cloud project...
gcloud config set project ttsai-461209
if %errorlevel% neq 0 (
    echo ERROR: Failed to set project. Please check your project ID.
    pause
    exit /b 1
)

echo Project set successfully. ✓
echo.

REM Navigate to backend directory
echo Navigating to backend directory...
cd /d "%~dp0backend"
if not exist "app.yaml" (
    echo ERROR: app.yaml not found in backend directory.
    echo Please make sure you're running this from the project root.
    pause
    exit /b 1
)

echo Found app.yaml file. ✓
echo.

REM Show current configuration
echo ==========================================
echo Current Deployment Configuration:
echo ==========================================
echo Project ID: ttsai-461209
echo App Engine URL: https://ttsai-461209.de.r.appspot.com
echo Backend Directory: %CD%
echo.

REM Ask for confirmation
set /p confirm="Deploy to Google Cloud App Engine? (y/N): "
if /i not "%confirm%"=="y" (
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo ==========================================
echo Starting Deployment...
echo ==========================================
echo.

REM Deploy to App Engine
echo Deploying backend to App Engine...
gcloud app deploy --quiet
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Deployment failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Deployment Successful! 🎉
echo ==========================================
echo.
echo Backend URL: https://ttsai-461209.de.r.appspot.com
echo Frontend URL: https://vehicle-parking-app.netlify.app
echo.
echo The CORS configuration has been updated to allow:
echo - https://vehicle-parking-app.netlify.app
echo - http://localhost:3000
echo.
echo ==========================================
echo Testing Deployment:
echo ==========================================
echo.
echo Testing health endpoint...
curl -s https://ttsai-461209.de.r.appspot.com/health
if %errorlevel% neq 0 (
    echo.
    echo Warning: Could not test health endpoint (curl not available)
    echo You can manually test: https://ttsai-461209.de.r.appspot.com/health
)

echo.
echo.
echo ==========================================
echo Deployment Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Test your frontend at: https://vehicle-parking-app.netlify.app
echo 2. Login should now work without CORS errors
echo 3. Monitor logs: gcloud app logs tail -s default
echo.
pause 