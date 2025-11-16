@echo off
echo ================================
echo Virtual Trial Room Setup
echo ================================
echo.

echo Checking Python installation...
python --version
echo.

echo Installing dependencies...
pip install -r requirements.txt
echo.

if not exist .env (
    echo WARNING: No .env file found!
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo Please edit .env and add your GEMINI_API_KEY
    echo Get your API key from: https://makersuite.google.com/app/apikey
    echo.
) else (
    echo .env file found
)

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo To start the application:
echo   python app.py
echo.
echo Then open your browser to:
echo   http://localhost:5000
echo.
pause
