@echo off
echo ==========================================
echo MongoDB Installation for Windows
echo ==========================================
echo.

echo This script will help you install MongoDB Community Server.
echo.
echo Option 1: Download MongoDB Community Server manually
echo Go to: https://www.mongodb.com/try/download/community
echo Select: Windows x64
echo Version: 7.0 (Current)
echo Package: msi
echo.
echo Option 2: Use Chocolatey (if installed)
choco --version >nul 2>&1
if %errorlevel% == 0 (
    echo Chocolatey detected. Installing MongoDB...
    choco install mongodb -y
    if %errorlevel% == 0 (
        echo MongoDB installed successfully!
        echo Starting MongoDB service...
        net start MongoDB
    ) else (
        echo MongoDB installation failed via Chocolatey.
        echo Please try manual installation.
    )
) else (
    echo Chocolatey not found.
    echo.
    echo Manual Installation Steps:
    echo 1. Go to: https://www.mongodb.com/try/download/community
    echo 2. Download MongoDB Community Server for Windows
    echo 3. Run the installer
    echo 4. Choose "Complete" installation
    echo 5. Install MongoDB as a Service
    echo 6. Install MongoDB Compass (optional GUI)
    echo.
    echo After installation, MongoDB should start automatically.
    echo You can verify by running: mongod --version
)

echo.
echo ==========================================
echo Alternative: Use MongoDB Atlas (Cloud)
echo ==========================================
echo For quick testing, you can use MongoDB Atlas:
echo 1. Go to: https://www.mongodb.com/atlas
echo 2. Create a free account
echo 3. Create a free cluster
echo 4. Get connection string
echo 5. Update .env file with: MONGODB_URI=your_connection_string
echo.
pause 