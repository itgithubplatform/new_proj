@echo off
cls
echo ==========================================
echo   TalentScout AI Hiring Assistant
echo   100%% Python - Gemini 2.0 Powered
echo ==========================================
echo.
echo [INFO] This is a Python-only application
echo [INFO] Using: FastAPI Backend + Streamlit UI + ChromaDB
echo.

REM Check if .env exists
if not exist "backend\.env" (
    echo [WARNING] .env file not found!
    echo [ACTION] Creating from .env.example...
    copy backend\.env.example backend\.env
    echo.
    echo [IMPORTANT] Please edit backend\.env and add your GEMINI_API_KEY
    echo [HELP] Get FREE API key: https://aistudio.google.com/app/apikey
    echo.
    pause
)

echo [1/2] Starting Backend API (FastAPI + Gemini 2.0)...
start "TalentScout Backend" cmd /k "cd backend && python main.py"

timeout /t 3 /nobreak > nul

echo [2/2] Starting Streamlit UI...
start "TalentScout Streamlit" cmd /k "streamlit run streamlit_app.py"

echo.
echo ==========================================
echo   Application Started Successfully!
echo ==========================================
echo.
echo   Streamlit UI:   http://localhost:8501
echo   Backend API:    http://localhost:8000/docs
echo   Health Check:   http://localhost:8000/health
echo.
echo [TIP] Close both terminal windows to stop the app
echo.
pause
