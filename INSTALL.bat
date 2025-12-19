@echo off
cls
echo ==========================================
echo   TalentScout - Installation Script
echo   100%% Python Implementation
echo ==========================================
echo.

echo [1/4] Installing all Python dependencies...
echo This may take a few minutes...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed!
    pause
    exit /b 1
)

echo.
echo [2/4] Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo.
echo [3/4] Setting up environment file...
if not exist "backend\.env" (
    copy backend\.env.example backend\.env
    echo [OK] Created backend\.env from example
) else (
    echo [OK] backend\.env already exists
)

echo.
echo [4/4] Running system test...
python test_setup.py

echo.
echo ==========================================
echo   Installation Complete!
echo ==========================================
echo.
echo NEXT STEPS:
echo 1. Edit backend\.env and add your GEMINI_API_KEY
echo    Get it FREE from: https://aistudio.google.com/app/apikey
echo.
echo 2. Configure DATABASE_URL in backend\.env
echo    (or use SQLite for testing)
echo.
echo 3. Run: START.bat to launch the application
echo.
pause
