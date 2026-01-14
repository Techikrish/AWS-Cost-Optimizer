# AWS Cost Optimizer - Windows Setup Script

@echo off
echo 🚀 AWS Cost Optimizer - Installation Script
echo ===========================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is required but not installed. Please install Python 3.8+
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed. Please install Node.js 16+
    exit /b 1
)

echo ✅ Python and Node.js found

REM Setup Backend
echo.
echo 📦 Setting up Backend...
cd backend
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo ✅ Backend dependencies installed
cd ..

REM Setup Frontend
echo.
echo 📦 Setting up Frontend...
cd frontend
call npm install
echo ✅ Frontend dependencies installed
cd ..

echo.
echo ✅ Installation complete!
echo.
echo 🚀 To start the application:
echo.
echo Command Prompt 1 (Backend):
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python main.py
echo.
echo Command Prompt 2 (Frontend):
echo   cd frontend
echo   npm run dev
echo.
echo Then open http://localhost:3000 in your browser
echo.
echo 📖 See README.md for complete documentation
