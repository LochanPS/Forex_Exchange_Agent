#!/bin/bash
# AgentPay - Automated Setup Script (Linux/macOS)

echo "============================================================"
echo "AgentPay - Automated Setup"
echo "============================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3.11 required"; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env created - please fill in your API keys"
else
    echo "✓ .env already exists"
fi

# Generate test invoices
echo "Generating test invoices..."
python generate_invoice.py

# Run tests
echo "Running tests..."
pytest tests/test_compliance.py -v

echo ""
echo "============================================================"
echo "✓ Setup complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run: python generate_wallet.py (to create test wallet)"
echo "3. Get test funds from faucets"
echo "4. Run: python verify_setup.py (to verify)"
echo "5. Run: python main.py (to start the agent)"
echo ""
