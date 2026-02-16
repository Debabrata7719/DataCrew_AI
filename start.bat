@echo off
echo ========================================
echo   DebAI - Email Assistant Launcher
echo ========================================
echo.

echo [1/3] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo.

echo [2/3] Installing/Updating dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [3/3] Starting DebAI Server...
echo.
echo ========================================
echo   Server will start on:
echo   - Frontend: http://127.0.0.1:8000/app/
echo   - API Docs: http://127.0.0.1:8000/docs
echo ========================================
echo.

python -m src.main
