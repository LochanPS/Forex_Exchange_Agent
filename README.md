# ⚡ AgentPay

> **An AI agent that reads a cross-border invoice, validates it, and pays it in USDC — fully autonomously. No human in the loop. You watch it happen.**

```
PDF drops in → fields extracted → compliance checked → USDC fires → tx_hash printed → done.
Under 30 seconds. On-chain. Real.
```

Built for the **"It's Handled."** Hackathon Challenge at Razorpay HQ, Bangalore — March 14, 2026.  
YC RFS Alignment: **AI-Powered Agencies** + **Stablecoin Financial Services** (Spring 2026).

---

## What This Is

Cross-border B2B payments in 2026 still take 1–3 business days, cost $25–$45 per wire, and require a human to log in and click approve. AgentPay kills that bottleneck.

You drop a PDF invoice into a folder. The agent:
1. **Reads** it — extracts vendor, amount, wallet address, due date using Claude tool use
2. **Validates** it — checks the vendor against an approved counterparty list, enforces spend limits
3. **Pays** it — signs and submits a USDC transaction on Base Sepolia via x402
4. **Receipts** it — writes a settlement record and prints the block explorer link

Four Python files. One workflow. Zero human approvals for routine transactions.

---

## The Two Operations (That's It. That's The Build.)

| # | Operation | What It Produces |
|---|-----------|-----------------|
| 1 | Invoice ingestion + compliance validation | Structured JSON: `{vendor, usdc_amount, dest_wallet, status: PASS or HOLD}` |
| 2 | USDC payment execution via x402 | Transaction hash + Base Sepolia block explorer link, confirmed on-chain |

Everything else — ERP sync, FX hedging, multi-agent orchestration, smart contract escrow — is post-hackathon. Don't build it today.

---

## Tech Stack

| Component | Tool | Version | Why |
|-----------|------|---------|-----|
| Language | Python | 3.11 | One language, no switching |
| LLM | Claude Sonnet (`claude-sonnet-4-20250514`) | via Anthropic SDK `0.49+` | Native tool use for structured extraction |
| PDF Parsing | PyMuPDF (`fitz`) | `1.24+` | Single install, fast, reliable on typed PDFs |
| Payment Protocol | x402-python SDK | `0.1+` | HTTP-native USDC payments |
| Payment Fallback | web3.py | `7.0+` | Direct ERC-20 USDC transfer if x402 blocks |
| HTTP Client | httpx | `0.27+` | Async-ready, x402 fallback requests |
| Blockchain | Base Sepolia (testnet) | — | Free test USDC, EVM-compatible, instant finality |
| Env Management | python-dotenv | `1.0+` | Loads `.env` cleanly |
| Sample Invoice Gen | fpdf2 | `2.7+` | Generate typed test PDFs programmatically |

---

## Project Structure

```
agentpay/
├── main.py              # Entry point — folder watcher, orchestrates the flow
├── agent.py             # Claude tool-use call: PDF text → structured JSON
├── compliance.py        # Counterparty whitelist + spend limit enforcement
├── payment.py           # x402 payment execution (web3.py fallback included)
├── receipt.py           # Terminal output + HTML receipt generator
├── generate_invoice.py  # Creates sample_invoice.pdf for testing
│
├── inbox/               # Drop your PDF invoices here
├── settled/             # Confirmed payment receipts land here
├── exceptions/          # HOLD invoices land here (failed compliance)
│
├── .env                 # Your secrets — never commit this
├── .env.example         # Template — copy this to .env and fill it in
├── requirements.txt     # All Python dependencies
└── sample_invoice.pdf   # Pre-generated test invoice (run generate_invoice.py)
```

---

## Prerequisites

### 1. Python 3.11

**macOS (Homebrew)**
```bash
brew install python@3.11
```

**Ubuntu / Debian**
```bash
sudo apt update && sudo apt install python3.11 python3.11-venv python3-pip -y
```

**Windows**  
Download the installer from [python.org/downloads](https://www.python.org/downloads/release/python-3110/) — check **"Add Python to PATH"** during install.

Verify:
```bash
python3.11 --version
# Python 3.11.x
```

---

### 2. Get Your API Keys (Do This First)

#### Anthropic API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up / log in → **API Keys** → **Create Key**
3. Copy the key — it starts with `sk-ant-...`

#### Base Sepolia RPC URL
No account needed — use the free public RPC:
```
https://sepolia.base.org
```
Or get a faster dedicated endpoint free from [Alchemy](https://dashboard.alchemy.com):
1. Sign up → **Create App** → select **Base** → **Base Sepolia**
2. Copy the HTTPS endpoint

#### Test Wallet Private Key
Generate a throwaway test wallet (never use a real wallet for this):
```bash
python3 -c "from web3 import Web3; acc = Web3().eth.account.create(); print('Address:', acc.address); print('Key:', acc.key.hex())"
```
Save both the address and the private key.

#### Get Free Test USDC
1. Go to [faucet.circle.com](https://faucet.circle.com)
2. Select **Base Sepolia** → paste your wallet address → request USDC
3. Also grab test ETH for gas from [coinbase.com/faucets/base-ethereum-sepolia-faucet](https://coinbase.com/faucets/base-ethereum-sepolia-faucet)

> ⚠️ **Do this before anything else.** Faucets can be slow. Get your test funds while you set up the rest.

---

## Installation

### Step 1 — Clone the repo
```bash
git clone https://github.com/your-username/agentpay.git
cd agentpay
```

### Step 2 — Create a virtual environment
```bash
python3.11 -m venv venv

# Activate it:
# macOS / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

This installs everything. Takes 60–90 seconds. If any package fails, see the [Troubleshooting](#troubleshooting) section.

### Step 4 — Set up your environment variables
```bash
cp .env.example .env
```

Open `.env` and fill in your values:
```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Wallet (NEVER use a real wallet — testnet only)
PRIVATE_KEY=0xyour-private-key-here
WALLET_ADDRESS=0xyour-wallet-address-here

# Base Sepolia RPC
BASE_RPC_URL=https://sepolia.base.org

# USDC Contract on Base Sepolia
USDC_CONTRACT_ADDRESS=0x036CbD53842c5426634e7929541eC2318f3dCF7e

# Agent spend limit in USDC
AGENT_SPEND_LIMIT=5000
```

> The USDC contract address above is Circle's official USDC deployment on Base Sepolia. Do not change it.

### Step 5 — Generate a test invoice
```bash
python generate_invoice.py
```

This creates `sample_invoice.pdf` in the root directory — a typed PDF with vendor name, amount, and a test wallet address pre-loaded into the approved counterparty list.

### Step 6 — Verify your setup
```bash
python3 -c "
from web3 import Web3
import os
from dotenv import load_dotenv
load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('BASE_RPC_URL')))
print('Connected:', w3.is_connected())
print('Chain ID:', w3.eth.chain_id)  # Should be 84532 for Base Sepolia
"
```

You should see:
```
Connected: True
Chain ID: 84532
```

---

## Running AgentPay

### The Full Flow
```bash
python main.py
```

The watcher starts and monitors the `inbox/` folder. Now drop your invoice:
```bash
cp sample_invoice.pdf inbox/
```

Watch the terminal. Within 30 seconds you should see:
```
[AgentPay] New invoice detected: sample_invoice.pdf
[EXTRACT]  Vendor: Acme Supplies Ltd
[EXTRACT]  Amount: 1,200.00 USDC
[EXTRACT]  Wallet: 0xAbC...123
[COMPLY]   ✓ Counterparty: APPROVED
[COMPLY]   ✓ Spend limit: 1,200 / 5,000 USDC — WITHIN LIMIT
[COMPLY]   → Status: PASS
[PAY]      Submitting USDC transfer to Base Sepolia...
[PAY]      ✓ Transaction hash: 0x4f2a...c9e1
[PAY]      ✓ Explorer: https://sepolia.basescan.org/tx/0x4f2a...c9e1
[RECEIPT]  Saved to: settled/receipt_sample_invoice.json
[RECEIPT]  HTML receipt: settled/receipt_sample_invoice.html
```

Paste that transaction hash into [sepolia.basescan.org](https://sepolia.basescan.org). Confirmed USDC transfer. That's the demo.

### Test the HOLD path
```bash
cp test_invoices/over_limit_invoice.pdf inbox/
```

Expected output:
```
[COMPLY]   ✗ Amount 8,500 USDC exceeds agent spend limit of 5,000 USDC
[COMPLY]   → Status: HOLD
[HOLD]     Saved to: exceptions/hold_over_limit_invoice.json
```

---

## How It Works (The Agent Flow)

```
┌─────────────────────────────────────────────────────────┐
│                      main.py                            │
│              (Folder watcher — detects PDF)             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                      agent.py                           │
│   PyMuPDF extracts raw text from PDF                    │
│   Claude Sonnet tool call → structured JSON             │
│   {vendor, amount_usd, usdc_amount, dest_wallet,        │
│    due_date, invoice_id}                                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   compliance.py                         │
│   Check dest_wallet in approved_counterparties          │
│   Check usdc_amount <= AGENT_SPEND_LIMIT                │
│   Returns {status: PASS | HOLD, reason}                 │
└──────────┬───────────────────────────┬──────────────────┘
           │ PASS                      │ HOLD
           ▼                           ▼
┌──────────────────┐         ┌──────────────────────────┐
│   payment.py     │         │   exceptions/ folder     │
│  x402 request    │         │   JSON written, stop.    │
│  (web3 fallback) │         └──────────────────────────┘
│  tx_hash returned│
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                     receipt.py                          │
│   JSON receipt → settled/ folder                        │
│   HTML receipt → settled/ folder                        │
│   Terminal: tx_hash + block explorer URL                │
└─────────────────────────────────────────────────────────┘
```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | Your Anthropic API key from console.anthropic.com |
| `PRIVATE_KEY` | ✅ Yes | Test wallet private key (hex, starts with 0x) |
| `WALLET_ADDRESS` | ✅ Yes | Corresponding test wallet address |
| `BASE_RPC_URL` | ✅ Yes | Base Sepolia RPC — use `https://sepolia.base.org` |
| `USDC_CONTRACT_ADDRESS` | ✅ Yes | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` |
| `AGENT_SPEND_LIMIT` | Optional | Max USDC per transaction. Default: `5000` |

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'fitz'`**  
PyMuPDF installs as `fitz` but the package name changed:
```bash
pip install pymupdf
```

**`web3.exceptions.ProviderConnectionError`**  
The public RPC is occasionally slow. Switch to:
```bash
# In .env:
BASE_RPC_URL=https://base-sepolia-rpc.publicnode.com
```

**`anthropic.RateLimitError`**  
Switch to Haiku in `agent.py` — same tool use API, faster and cheaper:
```python
model="claude-haiku-4-5"  # swap from claude-sonnet-4-20250514
```

**`PDF text extraction returns empty string`**  
Your PDF is scanned (image-based), not typed. Regenerate a typed PDF:
```bash
python generate_invoice.py
```

**x402 SDK import errors**  
Skip it entirely. Open `payment.py` and set:
```python
USE_X402 = False  # Forces web3.py ERC-20 path
```
The payment still settles on-chain. The demo still works.

**Test USDC balance is 0**  
Check [faucet.circle.com](https://faucet.circle.com) and request again. Also confirm you're on Base Sepolia (chain ID 84532), not mainnet.

---

## x402 vs web3.py — Which Path Are You On?

AgentPay tries x402 first. If it fails or takes too long to set up, it falls back to a direct ERC-20 USDC transfer via web3.py. Both paths settle on-chain. Both produce a real tx_hash. The difference:

| | x402 Path | web3.py Fallback |
|--|-----------|-----------------|
| What it is | HTTP-native payment protocol | Direct ERC-20 token transfer |
| Setup time | 15–30 min | 5 min |
| Demo result | On-chain ✅ | On-chain ✅ |
| Post-hackathon? | Production path | Replace with x402 |

At a hackathon, if x402 setup takes more than 30 minutes — switch to the fallback. The result is the same to a judge watching a block explorer.

---

## The Demo Script (Memorise This)

> *"Right now, every cross-border B2B payment requires a human to log in and press approve. We built an agent that reads an invoice, validates it against compliance rules, and pays it in USDC — fully autonomously. Watch."*

Then drop the PDF. Say nothing. Let the terminal run. Point at the block explorer.

The silence between dropping the file and the tx_hash appearing is the demo. Do not fill it with words.

---

## What's Next (Post-Hackathon Roadmap)

| Feature | Description |
|---------|-------------|
| Real x402 integration | Full x402 protocol flow for API-gated payments |
| Kite AI identity | Kite Passport hierarchical DID replacing local private key |
| OFAC sanctions API | Chainalysis wallet screening replacing mock approved list |
| FX oracle | Chainlink / Pyth real-time INR→USDC rate at point of payment |
| Smart contract escrow | Milestone-based fund release — pays on delivery confirmation |
| ERP sync | Azure Service Bus → SAP/Oracle invoice reconciliation |
| Policy console | Web UI for finance teams to define spend limits and rules |
| Multi-agent orchestration | Specialist sub-agents for FX, compliance, and payment routing |

Full architecture is documented in `AgentPay_PRD_v1.0_March2026.docx` and `AgentPay_Research_Document_March2026.docx`.

---

## Resources

| Resource | Link |
|----------|------|
| Anthropic Console | [console.anthropic.com](https://console.anthropic.com) |
| Anthropic Python SDK docs | [docs.anthropic.com](https://docs.anthropic.com) |
| x402 Protocol spec | [x402.org](https://x402.org) |
| Base Sepolia explorer | [sepolia.basescan.org](https://sepolia.basescan.org) |
| Base Sepolia public RPC | `https://sepolia.base.org` |
| Circle USDC faucet | [faucet.circle.com](https://faucet.circle.com) |
| Base ETH faucet (gas) | [coinbase.com/faucets](https://coinbase.com/faucets/base-ethereum-sepolia-faucet) |
| web3.py docs | [web3py.readthedocs.io](https://web3py.readthedocs.io) |
| PyMuPDF docs | [pymupdf.readthedocs.io](https://pymupdf.readthedocs.io) |
| Kite AI | [kite.ai](https://kite.ai) |

---

## License

MIT — build on it, ship it, make money with it.

---

*AgentPay — "It's Handled."*  
*Razorpay HQ, Bangalore — March 14, 2026*
