"""
AgentPay - Setup Verification Script
Checks that all dependencies and configuration are correct
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("AgentPay - Setup Verification")
print("=" * 60)
print()

# Check Python version
print("✓ Python version:", sys.version.split()[0])

# Check required directories
dirs = ["inbox", "settled", "exceptions", "logs", "abi", "tests"]
print("\nDirectories:")
for d in dirs:
    exists = Path(d).exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {d}/")

# Check environment variables
print("\nEnvironment Variables:")
required_vars = {
    "GOOGLE_API_KEY": "Google Gemini API key",
    "PRIVATE_KEY": "Wallet private key",
    "WALLET_ADDRESS": "Wallet address",
    "BASE_TESTNET_RPC_URL": "Base Sepolia RPC URL",
    "USDC_TESTNET_ADDRESS": "USDC testnet contract",
    "AGENT_SPEND_LIMIT": "Agent spend limit",
    "NETWORK": "Network (testnet/mainnet)"
}

all_set = True
for var, desc in required_vars.items():
    value = os.getenv(var)
    if value and value != f"your-{var.lower().replace('_', '-')}-here":
        print(f"  ✓ {var}")
    else:
        print(f"  ✗ {var} - {desc}")
        all_set = False

# Check dependencies
print("\nDependencies:")
try:
    import google.genai
    print("  ✓ google-genai")
except ImportError:
    print("  ✗ google-genai")
    all_set = False

try:
    import fitz
    print("  ✓ pymupdf (fitz)")
except ImportError:
    print("  ✗ pymupdf")
    all_set = False

try:
    from web3 import Web3
    print("  ✓ web3")
except ImportError:
    print("  ✗ web3")
    all_set = False

try:
    from watchdog.observers import Observer
    print("  ✓ watchdog")
except ImportError:
    print("  ✗ watchdog")
    all_set = False

# Test blockchain connection
print("\nBlockchain Connection:")
try:
    from web3 import Web3
    rpc_url = os.getenv("BASE_TESTNET_RPC_URL")
    if rpc_url:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if w3.is_connected():
            chain_id = w3.eth.chain_id
            print(f"  ✓ Connected to Base Sepolia (Chain ID: {chain_id})")
        else:
            print(f"  ✗ Failed to connect to {rpc_url}")
            all_set = False
    else:
        print("  ✗ BASE_TESTNET_RPC_URL not set")
        all_set = False
except Exception as e:
    print(f"  ✗ Connection error: {e}")
    all_set = False

print()
print("=" * 60)
if all_set:
    print("✓ Setup complete! Ready to run AgentPay.")
    print("\nNext steps:")
    print("  1. Run: python main.py")
    print("  2. Drop a PDF invoice into inbox/")
    print("  3. Watch the magic happen!")
else:
    print("✗ Setup incomplete. Please fix the issues above.")
    print("\nQuick fixes:")
    print("  1. Copy .env.example to .env")
    print("  2. Fill in all required values in .env")
    print("  3. Run: pip install -r requirements.txt")
print("=" * 60)
