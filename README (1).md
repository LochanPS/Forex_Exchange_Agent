# ⚡ AgentPay

> **An AI agent that reads a cross-border invoice, validates it, and settles it in USDC — fully autonomously. No human in the loop.**

```
PDF drops in → fields extracted → compliance checked → USDC fires → tx_hash confirmed → done.
Under 30 seconds. On-chain. Real.
```

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Chain: Base](https://img.shields.io/badge/chain-Base-0052FF.svg)](https://base.org)
[![Stablecoin: USDC](https://img.shields.io/badge/stablecoin-USDC-2775CA.svg)](https://www.circle.com/usdc)

Built for the **"It's Handled."** Hackathon at Razorpay HQ, Bangalore — March 14, 2026.
YC RFS: **AI-Powered Agencies** + **Stablecoin Financial Services** (Spring 2026).

---

## Table of Contents

1. [What This Is](#what-this-is)
2. [Testnet vs Mainnet](#testnet-vs-mainnet)
3. [How It Works](#how-it-works)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [Prerequisites](#prerequisites)
7. [Installation](#installation)
8. [Configuration](#configuration)
9. [Running AgentPay](#running-agentpay)
10. [Testing](#testing)
11. [Docker](#docker)
12. [Production Deployment](#production-deployment)
13. [Security](#security)
14. [Logging & Observability](#logging--observability)
15. [Troubleshooting](#troubleshooting)
16. [Roadmap](#roadmap)
17. [Contributing](#contributing)
18. [Resources](#resources)
19. [License](#license)

---

## What This Is

Cross-border B2B payments in 2026 still take 1–3 business days, cost $25–$45 per wire, and require a human to log in and click approve. For an AI agent managing 40 supplier relationships, that's 40 human bottlenecks per payment cycle.

AgentPay removes that bottleneck. You drop a PDF invoice into a folder. The agent:

1. **Reads** it — extracts vendor, amount, wallet address, and due date using Claude tool use
2. **Validates** it — checks the vendor against a counterparty list, enforces spend limits
3. **Pays** it — signs and submits a USDC transaction via x402 or direct ERC-20 transfer
4. **Receipts** it — writes a settlement record and prints the block explorer link

Four Python modules. One workflow. Zero human approvals for policy-compliant transactions.

---

## Testnet vs Mainnet

This is the most important thing to understand before you run anything.

### What changes between environments

| | Testnet (Base Sepolia) | Mainnet (Base) |
|--|----------------------|----------------|
| **Purpose** | Development, demos, hackathons | Real production payments |
| **USDC value** | Zero — free from faucet | Real USD-backed USDC |
| **ETH for gas** | Free from faucet | Costs real ETH (~$0.001/tx on Base) |
| **Chain ID** | `84532` | `8453` |
| **RPC URL** | `https://sepolia.base.org` | `https://mainnet.base.org` |
| **USDC contract** | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| **Block explorer** | [sepolia.basescan.org](https://sepolia.basescan.org) | [basescan.org](https://basescan.org) |
| **Wallet security** | Local private key in `.env` is acceptable | **Never** store a raw private key — use MPC custody |

### For the hackathon
Run on **Base Sepolia testnet**. Free USDC, free gas, identical code path, real block explorer confirmation. A judge watching `sepolia.basescan.org` sees a confirmed on-chain transaction — there is no visual or functional difference from mainnet. Do not use real money under a 5-hour time constraint.

### For production
Set `NETWORK=mainnet` in `.env` and follow the [Production Deployment](#production-deployment) section. The application code does not change. The infrastructure and security requirements around it do.

---

## How It Works

### The Two Operations

| # | Operation | Input | Output |
|---|-----------|-------|--------|
| 1 | Invoice ingestion + compliance validation | PDF file | `{vendor, usdc_amount, dest_wallet, status: PASS or HOLD, reason}` |
| 2 | USDC payment execution | Validated JSON from Op 1 | Transaction hash + block explorer URL, confirmed on-chain |

### Agent Flow

```
┌──────────────────────────────────────────────────────────────┐
│  main.py — Folder watcher (watchdog)                         │
│  Detects new PDF in inbox/ → triggers pipeline               │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│  agent.py — Claude Sonnet (claude-sonnet-4-20250514)         │
│  1. PyMuPDF extracts raw text from PDF                       │
│  2. Claude tool call: extract_invoice_fields(pdf_text)       │
│  3. Returns structured JSON:                                 │
│     {vendor, amount_usd, usdc_amount, dest_wallet,           │
│      due_date, invoice_id, currency}                         │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│  compliance.py                                               │
│  Check 1: dest_wallet in approved_counterparties             │
│  Check 2: usdc_amount <= AGENT_SPEND_LIMIT                   │
│  Returns: {status: "PASS" | "HOLD", reason: str}             │
└──────────┬───────────────────────────┬───────────────────────┘
           │ PASS                      │ HOLD
           ▼                           ▼
┌──────────────────────┐    ┌─────────────────────────────┐
│  payment.py          │    │  exceptions/ folder          │
│                      │    │  JSON written, pipeline stop │
│  Try x402 path:      │    └─────────────────────────────┘
│  → x402 payment      │
│    header + USDC tx  │
│                      │
│  Fallback path:      │
│  → web3.py ERC-20    │
│    USDC transfer     │
│                      │
│  Returns: tx_hash    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  receipt.py                                                  │
│  Writes JSON receipt → settled/                              │
│  Renders HTML receipt → settled/                             │
│  Logs tx_hash + block explorer URL to terminal + log file    │
└──────────────────────────────────────────────────────────────┘
```

### x402 vs web3.py — Understanding the Payment Paths

AgentPay attempts x402 first. If the SDK is unavailable or takes too long to configure, it falls back automatically to a direct ERC-20 USDC transfer via web3.py.

| | x402 Path | web3.py Fallback |
|--|-----------|-----------------|
| **What it is** | HTTP-native payment protocol | Direct ERC-20 `transfer()` call |
| **Settlement** | On-chain ✅ | On-chain ✅ |
| **Demo result** | Real tx_hash on block explorer | Real tx_hash on block explorer |
| **Setup time** | 15–30 min | 5 min |
| **Production path** | Yes — target architecture | Transitional — replace with x402 post-hackathon |

Both paths produce a confirmed, on-chain transaction. There is no difference in the demo.

---

## Tech Stack

| Component | Library / Service | Version | Install | Docs |
|-----------|------------------|---------|---------|------|
| Language | Python | `3.11` | [python.org](https://www.python.org/downloads/) | — |
| LLM | Claude Sonnet via Anthropic SDK | `anthropic>=0.49.0` | `pip install anthropic` | [docs.anthropic.com](https://docs.anthropic.com) |
| PDF Parsing | PyMuPDF | `pymupdf>=1.24.0` | `pip install pymupdf` | [pymupdf.readthedocs.io](https://pymupdf.readthedocs.io) |
| Blockchain | web3.py | `web3>=7.0.0` | `pip install web3` | [web3py.readthedocs.io](https://web3py.readthedocs.io) |
| HTTP Client | httpx | `httpx>=0.27.0` | `pip install httpx` | [python-httpx.org](https://www.python-httpx.org) |
| Folder Watcher | watchdog | `watchdog>=4.0.0` | `pip install watchdog` | [python-watchdog.readthedocs.io](https://python-watchdog.readthedocs.io) |
| Env Management | python-dotenv | `python-dotenv>=1.0.0` | `pip install python-dotenv` | [github.com/theskumar/python-dotenv](https://github.com/theskumar/python-dotenv) |
| Test PDF Gen | fpdf2 | `fpdf2>=2.7.9` | `pip install fpdf2` | [py-fpdf2.readthedocs.io](https://py-fpdf2.readthedocs.io) |
| Payment Protocol | x402 SDK (optional) | `x402>=0.1.0` | `pip install x402` | [x402.org](https://x402.org) |
| Network | Base (EVM L2) | Chain ID: `8453` / `84532` | — | [base.org](https://base.org) |
| Stablecoin | USDC (Circle) | — | — | [circle.com/usdc](https://www.circle.com/usdc) |

---

## Project Structure

```
agentpay/
│
├── main.py                  # Entry point — folder watcher, orchestrates pipeline
├── agent.py                 # Claude tool-use call: PDF text → structured JSON
├── compliance.py            # Counterparty whitelist + spend limit enforcement
├── payment.py               # x402 payment (web3.py ERC-20 fallback)
├── receipt.py               # Terminal output + JSON/HTML receipt generator
├── generate_invoice.py      # Creates typed test PDFs for demo and testing
│
├── inbox/                   # Drop PDF invoices here — watcher picks them up
├── settled/                 # Confirmed payment receipts (JSON + HTML)
├── exceptions/              # HOLD invoices — failed compliance checks
├── logs/                    # Application logs (auto-created on first run)
│
├── tests/
│   ├── test_agent.py        # Unit tests for invoice extraction (Claude mocked)
│   ├── test_compliance.py   # Unit tests for validation logic
│   ├── test_payment.py      # Payment tests (web3 mocked — no real tx)
│   └── fixtures/
│       ├── valid_invoice.pdf
│       └── over_limit_invoice.pdf
│
├── abi/
│   └── usdc.json            # USDC ERC-20 ABI (required for web3.py calls)
│
├── Dockerfile               # Container definition
├── docker-compose.yml       # Local container orchestration
│
├── .env                     # Your secrets — NEVER commit this
├── .env.example             # Safe template — copy and fill in
├── .gitignore               # Ensures .env and private keys are never committed
├── requirements.txt         # Core Python dependencies
├── requirements-dev.txt     # Dev and test dependencies (pytest, black, etc.)
└── README.md                # This file
```

---

## Prerequisites

### 1. Python 3.11

**macOS**
```bash
# Install Homebrew if you don't have it:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install python@3.11
python3.11 --version
# Python 3.11.x
```

**Ubuntu / Debian**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y
python3.11 --version
```

**Windows**
Download from [python.org/downloads](https://www.python.org/downloads/release/python-3110/). During install, check **"Add Python to PATH"**.

---

### 2. Git
```bash
# macOS
brew install git

# Ubuntu
sudo apt install git -y

# Verify
git --version
```

---

### 3. Get Your API Keys — Do This First

#### Anthropic API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up / log in → **API Keys** → **Create Key**
3. Copy — it starts with `sk-ant-...`
4. Keep it secret. It goes in `.env` only.

#### RPC URL

**Testnet — Base Sepolia, no account needed:**
```
https://sepolia.base.org
```

**Testnet with higher rate limits (free Alchemy account):**
1. Sign up at [dashboard.alchemy.com](https://dashboard.alchemy.com)
2. Create App → **Base** → **Base Sepolia** → copy the HTTPS endpoint

**Mainnet — production only:**
```
https://mainnet.base.org
```

---

### 4. Set Up a Wallet

> ⚠️ For testnet: generate a throwaway key. Never use a real wallet for development.
> For production: see [Security](#security) — raw private keys are not acceptable.

Generate a throwaway test wallet:
```bash
python3 -c "
from web3 import Web3
acc = Web3().eth.account.create()
print('Address:', acc.address)
print('Private Key:', acc.key.hex())
"
```

Save both values. They go in `.env`.

---

### 5. Get Test Funds — Do This Immediately

Faucets can be slow. Request funds while you set up everything else.

**Test USDC (Base Sepolia):**
1. Go to [faucet.circle.com](https://faucet.circle.com)
2. Select **Base Sepolia** → paste your wallet address → request

**Test ETH for gas (Base Sepolia):**
1. Go to [coinbase.com/faucets/base-ethereum-sepolia-faucet](https://coinbase.com/faucets/base-ethereum-sepolia-faucet)
2. Paste your wallet address → request

You need both. ETH pays gas. USDC is what the agent sends.

---

## Installation

### Step 1 — Clone the repository
```bash
git clone https://github.com/your-username/agentpay.git
cd agentpay
```

### Step 2 — Create a virtual environment
```bash
python3.11 -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# Confirm — your prompt should show (venv)
which python
```

### Step 3 — Install dependencies
```bash
# Core
pip install -r requirements.txt

# Dev and test (optional but recommended)
pip install -r requirements-dev.txt
```

### Step 4 — Configure environment variables
```bash
cp .env.example .env
# Open .env and fill in every value — see Configuration section below
```

### Step 5 — Generate a test invoice
```bash
python generate_invoice.py
# Creates inbox/sample_invoice.pdf
```

### Step 6 — Verify your setup
```bash
python3 -c "
import os
from dotenv import load_dotenv
from web3 import Web3
load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv('BASE_TESTNET_RPC_URL')))
print('Connected:', w3.is_connected())
print('Chain ID:', w3.eth.chain_id)
# 84532 = Base Sepolia (testnet)
# 8453  = Base mainnet
"
```

Expected:
```
Connected: True
Chain ID: 84532
```

---

## Configuration

All configuration lives in `.env`. Never commit this file.

```env
# ── NETWORK ──────────────────────────────────────────────────────
# "testnet" = Base Sepolia | "mainnet" = Base mainnet
NETWORK=testnet

# ── ANTHROPIC ────────────────────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-your-key-here

# ── WALLET ───────────────────────────────────────────────────────
# Testnet: local key in .env is fine
# Mainnet: use MPC custody — never a raw private key in production
PRIVATE_KEY=0xyour-private-key-here
WALLET_ADDRESS=0xyour-wallet-address-here

# ── RPC URLS ─────────────────────────────────────────────────────
BASE_TESTNET_RPC_URL=https://sepolia.base.org
BASE_MAINNET_RPC_URL=https://mainnet.base.org

# ── USDC CONTRACT ADDRESSES ──────────────────────────────────────
USDC_TESTNET_ADDRESS=0x036CbD53842c5426634e7929541eC2318f3dCF7e
USDC_MAINNET_ADDRESS=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

# ── AGENT POLICY ─────────────────────────────────────────────────
AGENT_SPEND_LIMIT=5000

# ── PAYMENT PATH ─────────────────────────────────────────────────
# "x402" tries x402 first, falls back to web3 automatically
# "web3" forces direct ERC-20 transfer — use this at the hackathon
PAYMENT_PATH=x402

# ── LOGGING ──────────────────────────────────────────────────────
LOG_LEVEL=INFO
LOG_FILE=logs/agentpay.log
```

### Environment Variable Reference

| Variable | Required | Testnet Value | Mainnet Value |
|----------|----------|---------------|---------------|
| `NETWORK` | ✅ | `testnet` | `mainnet` |
| `ANTHROPIC_API_KEY` | ✅ | Same key | Same key |
| `PRIVATE_KEY` | ✅ | Throwaway test key | Remove — use MPC |
| `WALLET_ADDRESS` | ✅ | Test address | MPC wallet address |
| `BASE_TESTNET_RPC_URL` | Testnet | `https://sepolia.base.org` | — |
| `BASE_MAINNET_RPC_URL` | Mainnet | — | `https://mainnet.base.org` |
| `USDC_TESTNET_ADDRESS` | Testnet | `0x036CbD...` | — |
| `USDC_MAINNET_ADDRESS` | Mainnet | — | `0x833589...` |
| `AGENT_SPEND_LIMIT` | ✅ | `5000` | Set per company policy |
| `PAYMENT_PATH` | Optional | `web3` (hackathon) | `x402` (production) |
| `LOG_LEVEL` | Optional | `DEBUG` | `INFO` |

---

## Running AgentPay

### Start the agent
```bash
python main.py
```

### Trigger a payment — happy path
```bash
cp inbox/sample_invoice.pdf inbox/test_run.pdf
```

Expected terminal output:
```
2026-03-14 12:30:01 INFO  [AgentPay]   Watcher started. Monitoring inbox/
2026-03-14 12:30:04 INFO  [AgentPay]   New invoice detected: test_run.pdf
2026-03-14 12:30:04 INFO  [agent]      Extracting invoice fields...
2026-03-14 12:30:05 INFO  [agent]      Vendor:  Acme Supplies Ltd
2026-03-14 12:30:05 INFO  [agent]      Amount:  1,200.00 USDC
2026-03-14 12:30:05 INFO  [agent]      Wallet:  0xAbC...123
2026-03-14 12:30:05 INFO  [compliance] Counterparty: APPROVED
2026-03-14 12:30:05 INFO  [compliance] Spend: 1,200 / 5,000 USDC — WITHIN LIMIT
2026-03-14 12:30:05 INFO  [compliance] → Status: PASS
2026-03-14 12:30:05 INFO  [payment]    Submitting USDC transfer to Base Sepolia...
2026-03-14 12:30:08 INFO  [payment]    ✓ tx_hash:  0x4f2a9c...e1b7
2026-03-14 12:30:08 INFO  [payment]    ✓ Explorer: https://sepolia.basescan.org/tx/0x4f2a9c...e1b7
2026-03-14 12:30:08 INFO  [receipt]    Saved: settled/receipt_test_run.json
2026-03-14 12:30:08 INFO  [receipt]    HTML:  settled/receipt_test_run.html
```

Paste the tx_hash into [sepolia.basescan.org](https://sepolia.basescan.org) — confirmed USDC transfer to the correct address.

### Trigger a compliance HOLD
```bash
cp tests/fixtures/over_limit_invoice.pdf inbox/
```

Expected:
```
2026-03-14 12:31:10 INFO    [compliance] Spend: 8,500 / 5,000 USDC — EXCEEDS LIMIT
2026-03-14 12:31:10 WARNING [compliance] → Status: HOLD
2026-03-14 12:31:10 INFO    [AgentPay]   Exception saved: exceptions/hold_over_limit_invoice.json
```

---

## Testing

### Run all tests
```bash
pytest tests/ -v
```

### Run a specific module
```bash
pytest tests/test_compliance.py -v
pytest tests/test_agent.py -v
pytest tests/test_payment.py -v
```

### What is mocked

The test suite mocks all external calls so tests run without API keys, a live blockchain, or real funds:

- **Claude API** — `tests/test_agent.py` patches `anthropic.Anthropic.messages.create` with a fixture response
- **web3 transaction** — `tests/test_payment.py` patches `web3.eth.send_raw_transaction` with a mock tx_hash

Tests run fully offline, in CI, and spend nothing.

### Coverage report
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

---

## Docker

### Build the image
```bash
docker build -t agentpay:latest .
```

### Run with Docker Compose
```bash
docker-compose up
```

`inbox/`, `settled/`, `exceptions/`, and `logs/` are mounted as volumes so data persists outside the container.

### Drop an invoice into the running container
```bash
docker cp sample_invoice.pdf agentpay_app_1:/app/inbox/
```

---

## Production Deployment

Everything that changes when you move from testnet to real money.

### 1. Switch network
```env
NETWORK=mainnet
BASE_MAINNET_RPC_URL=https://mainnet.base.org
USDC_MAINNET_ADDRESS=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
```

### 2. Replace local private key with MPC custody

A raw private key in `.env` is not acceptable for production. Options:

| Option | Best For | Link |
|--------|----------|------|
| **Privy** | Startups, developer-friendly | [privy.io](https://www.privy.io) |
| **Fireblocks** | Enterprise, institutional-grade | [fireblocks.com](https://www.fireblocks.com) |
| **Coinbase CDP Wallet API** | If already using CDP as x402 facilitator | [docs.cdp.coinbase.com](https://docs.cdp.coinbase.com) |

Remove `PRIVATE_KEY` from `.env`. The custody provider signs transactions through their SDK — your application never holds the key.

### 3. Replace mock compliance with real sanctions screening

| Option | What It Does | Link |
|--------|-------------|------|
| **Chainalysis KYT** | Real-time wallet risk + OFAC screening | [chainalysis.com](https://www.chainalysis.com) |
| **Elliptic** | Transaction monitoring + sanctions | [elliptic.co](https://www.elliptic.co) |
| **TRM Labs** | Blockchain intelligence API | [trmlabs.com](https://www.trmlabs.com) |

### 4. Use a production-grade RPC endpoint

The public RPC endpoints are rate-limited and not suitable for production volume. Use a dedicated endpoint:

- [Alchemy](https://dashboard.alchemy.com) — free tier available, paid for production
- [Infura](https://infura.io) — same model
- [QuickNode](https://quicknode.com) — lower latency

### 5. Run as a persistent systemd service

```ini
# /etc/systemd/system/agentpay.service
[Unit]
Description=AgentPay Invoice Settlement Agent
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/agentpay
ExecStart=/opt/agentpay/venv/bin/python main.py
Restart=always
RestartSec=5
EnvironmentFile=/opt/agentpay/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable agentpay
sudo systemctl start agentpay
sudo systemctl status agentpay
```

### Production checklist

- [ ] `NETWORK=mainnet`
- [ ] `PRIVATE_KEY` removed — MPC custody configured
- [ ] Real sanctions screening API integrated
- [ ] RPC from Alchemy or Infura — not public endpoint
- [ ] `LOG_LEVEL=INFO` — not `DEBUG`
- [ ] Logs shipping to aggregator (Datadog, CloudWatch, Loki)
- [ ] Watcher running as systemd service with `Restart=always`
- [ ] `.env` permissions: `chmod 600 .env`
- [ ] No inbound ports exposed — this is a worker, not a server
- [ ] Alerting on HOLD events and payment failures

---

## Security

### Non-negotiable rules

**Never commit `.env`.**
Your `.gitignore` must include:
```
.env
*.key
*.pem
venv/
__pycache__/
logs/
settled/
exceptions/
```

Verify before every push:
```bash
git status  # .env must never appear here
```

If you accidentally commit `.env`:
```bash
git rm --cached .env
echo ".env" >> .gitignore
git commit -m "remove .env from tracking"
# Then immediately rotate every key in that file
```

**Never use a raw private key in production.**
A key in a file can be exposed via log outputs, error traces, debugging sessions, or server breaches. Use MPC custody for any real funds.

**Rotate your Anthropic API key if it leaks.**
Go to [console.anthropic.com](https://console.anthropic.com) → API Keys → delete the exposed key → create a new one immediately.

**USDC contract addresses are fixed in config — never from user input.**
`payment.py` reads the contract address from your `.env` only. No external party can redirect payments by providing a different contract address.

**Validate wallet addresses before signing.**
`payment.py` calls `Web3.is_checksum_address()` on every destination wallet before constructing a transaction. A malformed address fails loudly.

---

## Logging & Observability

AgentPay uses Python's standard `logging` module with structured output. Logs go to both stdout and `logs/agentpay.log`.

| Level | When it fires |
|-------|--------------|
| `DEBUG` | Every step — raw PDF text, Claude responses (development only) |
| `INFO` | Normal operation: invoice detected, compliance result, tx_hash confirmed |
| `WARNING` | HOLD events, RPC retries, rate limit backoff |
| `ERROR` | Failed transactions, unreadable PDFs, compliance errors |

Follow logs in real time:
```bash
tail -f logs/agentpay.log
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'fitz'`**
```bash
pip install pymupdf
```
PyMuPDF is installed as `pymupdf` but imported as `fitz`. The names differ.

---

**`web3.exceptions.ProviderConnectionError`**
Switch to the backup public RPC:
```env
BASE_TESTNET_RPC_URL=https://base-sepolia-rpc.publicnode.com
```
Or get a free Alchemy endpoint.

---

**`anthropic.RateLimitError`**
Switch to Haiku in `agent.py` — same tool use API, faster:
```python
model="claude-haiku-4-5"  # instead of claude-sonnet-4-20250514
```

---

**`PDF text extraction returns empty string`**
Your PDF is scanned (image-based). PyMuPDF extracts text from typed PDFs only. Regenerate:
```bash
python generate_invoice.py
```

---

**x402 SDK fails to import or configure**
Force the web3.py fallback — do not spend more than 30 minutes on this:
```env
PAYMENT_PATH=web3
```
Payment still settles on-chain. Demo is identical.

---

**USDC balance shows 0**
Confirm you're on the right chain:
```bash
python3 -c "
from web3 import Web3; import os; from dotenv import load_dotenv
load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('BASE_TESTNET_RPC_URL')))
print('Chain ID:', w3.eth.chain_id)  # Must be 84532
"
```
Then request USDC again from [faucet.circle.com](https://faucet.circle.com).

---

**Transaction submitted but not on block explorer after 30 seconds**
Check your ETH balance for gas:
```bash
python3 -c "
from web3 import Web3; import os; from dotenv import load_dotenv
load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('BASE_TESTNET_RPC_URL')))
bal = w3.eth.get_balance(os.getenv('WALLET_ADDRESS'))
print('ETH balance (wei):', bal)
print('ETH balance:', w3.from_wei(bal, 'ether'))
# If 0: request test ETH from the faucet
"
```

---

## Roadmap

This build is a functional slice of a larger system.

| Feature | Description | Priority |
|---------|-------------|----------|
| Full x402 protocol | HTTP-native payment with payment header — replaces direct ERC-20 | High |
| Kite AI identity (Kite Passport) | Hierarchical DID replaces raw private key — agent-native auth | High |
| Real sanctions screening | Chainalysis KYT replaces mock approved list | High |
| FX oracle | Chainlink / Pyth real-time INR→USDC rate at point of payment | Medium |
| Smart contract escrow | Milestone-based fund release — pays on delivery confirmation | Medium |
| ERP sync | Azure Service Bus → SAP/Oracle invoice reconciliation | Medium |
| Multi-agent orchestration | Specialist sub-agents for FX, compliance, and routing | Medium |
| Policy console | Web UI for finance teams to manage spend limits and rules | Low |
| FATF Travel Rule | Embed originator/beneficiary data for cross-border compliance | Low |

Full architecture spec: `AgentPay_PRD_v1.0_March2026.docx`
Research and market analysis: `AgentPay_Research_Document_March2026.docx`

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Write tests for what you add
4. Run the suite: `pytest tests/ -v`
5. Format: `black . && isort .`
6. Open a PR with a clear description of what changed and why

Do not open PRs that add dependencies without justification. Keep it lean.

---

## Resources

| Resource | Link |
|----------|------|
| Anthropic Console | [console.anthropic.com](https://console.anthropic.com) |
| Anthropic Python SDK | [docs.anthropic.com](https://docs.anthropic.com) |
| Claude Tool Use Guide | [docs.anthropic.com/tool-use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) |
| x402 Protocol Spec | [x402.org](https://x402.org) |
| Base Documentation | [docs.base.org](https://docs.base.org) |
| Base Sepolia Explorer | [sepolia.basescan.org](https://sepolia.basescan.org) |
| Base Mainnet Explorer | [basescan.org](https://basescan.org) |
| Base Sepolia RPC | `https://sepolia.base.org` |
| Base Mainnet RPC | `https://mainnet.base.org` |
| Circle USDC Faucet | [faucet.circle.com](https://faucet.circle.com) |
| Base ETH Faucet | [coinbase.com/faucets](https://coinbase.com/faucets/base-ethereum-sepolia-faucet) |
| Alchemy (RPC) | [dashboard.alchemy.com](https://dashboard.alchemy.com) |
| web3.py Docs | [web3py.readthedocs.io](https://web3py.readthedocs.io) |
| PyMuPDF Docs | [pymupdf.readthedocs.io](https://pymupdf.readthedocs.io) |
| Privy (MPC Wallets) | [privy.io](https://www.privy.io) |
| Chainalysis KYT | [chainalysis.com](https://www.chainalysis.com) |
| Kite AI | [kite.ai](https://kite.ai) |

---

## License

MIT — build on it, fork it, ship it.

---

*AgentPay — "It's Handled."*
*Razorpay HQ, Bangalore — March 14, 2026*
