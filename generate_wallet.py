"""
AgentPay - Test Wallet Generator
Generates a new Ethereum wallet for testing
"""
from web3 import Web3

print("=" * 60)
print("AgentPay - Test Wallet Generator")
print("=" * 60)
print()
print("⚠️  WARNING: This is for TESTNET ONLY!")
print("   Never use this wallet for real funds.")
print()

# Generate new account
account = Web3().eth.account.create()

print("Generated new wallet:")
print()
print(f"Address:     {account.address}")
print(f"Private Key: {account.key.hex()}")
print()
print("=" * 60)
print()
print("Next steps:")
print()
print("1. Copy these values to your .env file:")
print(f"   WALLET_ADDRESS={account.address}")
print(f"   PRIVATE_KEY={account.key.hex()}")
print()
print("2. Get test funds:")
print("   - USDC: https://faucet.circle.com (Base Sepolia)")
print("   - ETH:  https://coinbase.com/faucets/base-ethereum-sepolia-faucet")
print()
print("3. Verify setup:")
print("   python verify_setup.py")
print()
print("=" * 60)
