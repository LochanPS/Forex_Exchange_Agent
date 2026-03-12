@echo off
REM AgentPay - Automated Setup Script (Windows)

echo ============================================================
echo AgentPay - Automated Setup
echo ============================================================
echo.

REM Check Python version
echo Checking Python version...
python --version || (echo Error: Python 3.11 required && exit /b 1)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install -r requirements-dev.txt

REM Create .env if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo ✓ .env created - please fill in your API keys
) else (
    echo ✓ .env already exists
)

REM Generate test invoices
echo Generating test invoices...
python generate_invoice.py

REM Run tests
echo Running tests...
pytest tests/test_compliance.py -v

echo.
echo ============================================================
echo ✓ Setup complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Edit .env and add your API keys
echo 2. Run: python generate_wallet.py (to create test wallet)
echo 3. Get test funds from faucets
echo 4. Run: python verify_setup.py (to verify)
echo 5. Run: python main.py (to start the agent)
echo.
pause
