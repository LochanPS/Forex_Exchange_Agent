"""
AgentPay - Payment Execution
Handles USDC transfers via web3.py (ERC-20)
"""
import os
import json
import logging
from web3 import Web3
from eth_account import Account

logger = logging.getLogger(__name__)


def execute_payment(invoice_data: dict) -> dict:
    """
    Execute USDC payment on Base blockchain
    Returns: {tx_hash, explorer_url, status}
    """
    network = os.getenv("NETWORK", "testnet")
    dest_wallet = invoice_data["dest_wallet"]
    usdc_amount = float(invoice_data["usdc_amount"])
    
    logger.info(f"Executing payment: {usdc_amount} USDC to {dest_wallet}")
    
    # Load configuration
    if network == "mainnet":
        rpc_url = os.getenv("BASE_MAINNET_RPC_URL")
        usdc_address = os.getenv("USDC_MAINNET_ADDRESS")
        explorer_base = "https://basescan.org"
    else:
        rpc_url = os.getenv("BASE_TESTNET_RPC_URL")
        usdc_address = os.getenv("USDC_TESTNET_ADDRESS")
        explorer_base = "https://sepolia.basescan.org"
    
    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to {network} RPC")
    
    logger.info(f"Connected to {network} (Chain ID: {w3.eth.chain_id})")
    
    # Load wallet
    private_key = os.getenv("PRIVATE_KEY")
    wallet_address = os.getenv("WALLET_ADDRESS")
    account = Account.from_key(private_key)
    
    # Validate destination address
    if not Web3.is_checksum_address(dest_wallet):
        dest_wallet = Web3.to_checksum_address(dest_wallet)
    
    # Load USDC contract ABI
    with open("abi/usdc.json", "r") as f:
        usdc_abi = json.load(f)
    
    usdc_contract = w3.eth.contract(
        address=Web3.to_checksum_address(usdc_address),
        abi=usdc_abi
    )
    
    # Convert amount to USDC units (6 decimals)
    amount_in_units = int(usdc_amount * 10**6)
    
    # Build transaction
    nonce = w3.eth.get_transaction_count(wallet_address)
    
    tx = usdc_contract.functions.transfer(
        dest_wallet,
        amount_in_units
    ).build_transaction({
        'from': wallet_address,
        'nonce': nonce,
        'gas': 100000,
        'maxFeePerGas': w3.eth.gas_price,
        'maxPriorityFeePerGas': w3.to_wei(1, 'gwei'),
    })
    
    # Sign and send transaction
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_hash_hex = tx_hash.hex()
    
    logger.info(f"✓ tx_hash: {tx_hash_hex}")
    
    # Wait for confirmation
    logger.info("Waiting for transaction confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    
    if receipt['status'] == 1:
        explorer_url = f"{explorer_base}/tx/{tx_hash_hex}"
        logger.info(f"✓ Explorer: {explorer_url}")
        
        return {
            "tx_hash": tx_hash_hex,
            "explorer_url": explorer_url,
            "status": "confirmed",
            "block_number": receipt['blockNumber']
        }
    else:
        raise Exception("Transaction failed on-chain")
