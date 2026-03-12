# AgentPay - Quick Start Guide

## Setup (5 minutes)

### 1. Create your .env file
```bash
cp .env.example .env
```

### 2. Get API Keys

#### Google Gemini API Key (Free)
1. Go to https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Copy the key and paste into `.env` as `GOOGLE_API_KEY`

#### Base Sepolia RPC (Free - No signup needed)
Already set in `.env.example`:
```
BASE_TESTNET_RPC_URL=https://sepolia.base.org
```

### 3. Generate Test Wallet
```bash
python -c "from web3 import Web3; acc = Web3().eth.account.create(); print('Address:', acc.address); print('Private Key:', acc.key.hex())"
```

Copy both values into `.env`:
- `WALLET_ADDRESS=0x...`
- `PRIVATE_KEY=0x...`

### 4. Get Test Funds

#### Test USDC (Required)
1. Go to https://faucet.circle.com
2. Select "Base Sepolia"
3. Paste your wallet address
4. Click "Request"

#### Test ETH for Gas (Required)
1. Go to https://coinbase.com/faucets/base-ethereum-sepolia-faucet
2. Paste your wallet address
3. Click "Request"

### 5. Verify Setup
```bash
python verify_setup.py
```

All checks should show ✓

## Running AgentPay

### Start the Agent
```bash
python main.py
```

You should see:
```
AgentPay - Autonomous Invoice Settlement Agent
Watcher started. Monitoring inbox/ for new invoices...
```

### Test Payment (Happy Path)
In another terminal:
```bash
cp inbox/sample_invoice.pdf inbox/test_run.pdf
```

Watch the logs - you'll see:
1. Invoice detected
2. Fields extracted by Gemini
3. Compliance checks pass
4. USDC payment submitted
5. Transaction hash + block explorer link
6. Receipt saved to `settled/`

### Test Compliance Hold
```bash
cp tests/fixtures/over_limit_invoice.pdf inbox/
```

This invoice exceeds the $5,000 spend limit and will be saved to `exceptions/`

## Troubleshooting

### "GOOGLE_API_KEY not set"
Make sure you copied `.env.example` to `.env` and filled in your API key

### "Failed to connect to RPC"
Try the backup RPC:
```
BASE_TESTNET_RPC_URL=https://base-sepolia-rpc.publicnode.com
```

### "USDC balance shows 0"
Wait 1-2 minutes after requesting from faucet, then check:
```bash
python -c "from web3 import Web3; import os; from dotenv import load_dotenv; load_dotenv(); w3 = Web3(Web3.HTTPProvider(os.getenv('BASE_TESTNET_RPC_URL'))); print('Chain:', w3.eth.chain_id)"
```

Should show `Chain: 84532` (Base Sepolia)

## What's Next?

- Check `settled/` for payment receipts (JSON + HTML)
- View transactions on https://sepolia.basescan.org
- Modify `compliance.py` to add more counterparties
- Adjust `AGENT_SPEND_LIMIT` in `.env`

## Production Deployment

See README.md section "Production Deployment" for:
- Switching to mainnet
- MPC custody setup
- Real sanctions screening
- Production RPC endpoints
