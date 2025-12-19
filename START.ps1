# TalentScout Quick Start Script for Windows
# This script helps you run the application easily

Write-Host "=================================="  -ForegroundColor Cyan
Write-Host "  TalentScout AI Hiring Assistant" -ForegroundColor Cyan
Write-Host "  Powered by Google Gemini 2.0   " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/5] Checking Python..." - ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "      Python installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "      ERROR: Python not found!" -ForegroundColor Red
    Write-Host "      Please install Python 3.9+ from python.org" -ForegroundColor Red
    pause
    exit 1
}

# Check if backend dependencies are installed
Write-Host "[2/5] Checking backend dependencies..." -ForegroundColor Yellow
if (Test-Path "backend/app") {
    Write-Host "      Backend found!" -ForegroundColor Green
} else {
    Write-Host "      ERROR: Backend folder not found!" -ForegroundColor Red
    pause
    exit 1
}

# Check if .env exists
Write-Host "[3/5] Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path "backend/.env") {
    Write-Host "      .env file found!" -ForegroundColor Green
} else {
    Write-Host "      WARNING: .env not found. Creating from example..." -ForegroundColor Yellow
    Copy-Item "backend/.env.example" "backend/.env"
    Write-Host "      IMPORTANT: Edit backend/.env and add your GEMINI_API_KEY!" -ForegroundColor Red
    Write-Host "      Get your FREE key from: https://aistudio.google.com/app/apikey" -ForegroundColor Cyan
    Write-Host ""
    $response = Read-Host "      Have you added your Gemini API key? (y/n)"
    if ($response -ne "y") {
        Write-Host "      Please add your API key to backend/.env first!" -ForegroundColor Red
        pause
        exit 1
    }
}

# Install backend dependencies
Write-Host "[4/5] Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "      Backend dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "      ERROR installing dependencies!" -ForegroundColor Red
    Set-Location ..
    pause
    exit 1
}
Set-Location ..

# Install Streamlit
Write-Host "[5/5] Installing Streamlit..." -ForegroundColor Yellow
pip install -r requirements-streamlit.txt -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "      Streamlit installed!" -ForegroundColor Green
} else {
    Write-Host "      ERROR installing Streamlit!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "=================================="  -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Starting application..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening 2 terminals:" -ForegroundColor Yellow
Write-Host "  1. Backend API (FastAPI)" -ForegroundColor Yellow
Write-Host "  2. Streamlit UI" -ForegroundColor Yellow
Write-Host ""

# Start backend in new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host 'Starting FastAPI Backend...' -ForegroundColor Cyan; python main.py"

# Wait a bit for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start Streamlit in new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Starting Streamlit UI...' -ForegroundColor Cyan; streamlit run streamlit_app.py"

Write-Host ""
Write-Host "=================================="  -ForegroundColor Green
Write-Host "  Application Started!" -ForegroundColor Green  
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Cyan
Write-Host "  Streamlit UI:  http://localhost:8501" -ForegroundColor White
Write-Host "  Backend API:   http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
pause
