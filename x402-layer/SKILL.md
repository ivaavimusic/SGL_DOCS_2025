---
name: x402-layer
version: 1.0.0
description: |
  This skill should be used when the user asks to "create x402 endpoint",
  "deploy monetized API", "pay for API with USDC", "check x402 credits",
  "consume API credits", "list endpoint on marketplace", "buy API credits",
  "topup endpoint", "browse x402 marketplace", or manage x402 Singularity
  Layer operations on Base or Solana networks.
homepage: https://studio.x402layer.cc/docs/agentic-access/openclaw-skill
metadata:
  clawdbot:
    emoji: "⚡"
    homepage: https://studio.x402layer.cc
    os:
      - linux
      - darwin
    requires:
      bins:
        - python3
      env:
        - WALLET_ADDRESS
        - PRIVATE_KEY
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
---


# x402 Singularity Layer

x402 is a **Web3 payment layer** enabling AI agents to:
- 💰 **Pay** for API access using USDC
- 🚀 **Deploy** monetized endpoints
- 🔍 **Discover** services via marketplace
- 📊 **Manage** endpoints and credits

**Networks:** Base (EVM) • Solana  
**Currency:** USDC  
**Protocol:** HTTP 402 Payment Required

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r {baseDir}/requirements.txt
```

### 2. Set Up Wallet
```bash
# For Base (EVM)
export PRIVATE_KEY="0x..."
export WALLET_ADDRESS="0x..."

# For Solana (optional)
export SOLANA_SECRET_KEY="[1,2,3,...]"  # JSON array
```

---

## Scripts Overview

### 🛒 CONSUMER MODE (Buying Services)

| Script | Purpose |
|--------|---------|
| `pay_base.py` | Pay for endpoint on Base network |
| `pay_solana.py` | Pay for endpoint on Solana network |
| `consume_credits.py` | Use pre-purchased credits (fast) |
| `consume_product.py` | Purchase digital products (files) |
| `check_credits.py` | Check your credit balance |
| `recharge_credits.py` | Buy credit packs for an endpoint |
| `discover_marketplace.py` | Browse available services |

### 🏭 PROVIDER MODE (Selling Services)

| Script | Purpose |
|--------|---------|
| `create_endpoint.py` | Deploy new monetized endpoint ($5) |
| `manage_endpoint.py` | View/update your endpoints |
| `topup_endpoint.py` | Recharge YOUR endpoint with credits |
| `list_on_marketplace.py` | Update marketplace listing |

---

## Security: API Key Verification

> [!IMPORTANT]
> When you create an endpoint, x402 acts as a proxy to your origin server. You MUST verify that requests are coming from x402.

1. **Get your API Key**: Returned when you run `create_endpoint.py`.
2. **Verify Headers**: Your origin server MUST check for this header in every request:
   ```http
   x-api-key: <YOUR_API_KEY>
   ```
   If the header is missing or incorrect, reject the request (401 Unauthorized).

---

## Credit System: How It Works

> [!WARNING]
> **Credits are NOT test credits!** They are consumed with every API request.

### Flow

```
User pays $0.01 → Your wallet receives payment → 1 credit deducted from your endpoint
```

### Economics

| Item | Value |
|------|-------|
| **Creation cost** | $5 (one-time) |
| **Starting credits** | 20,000 credits |
| **Recharge rate** | 500 credits per $1 |
| **Consumption** | 1 credit per API request |
| **Your earnings** | Whatever price you set per call |

### Example

1. **Create endpoint**: Pay $5, get 20,000 credits
2. **Set price**: $0.01 per call
3. **User calls your API 1,000 times**: You earn $10, 1,000 credits deducted
4. **Remaining**: 19,000 credits + $10 profit
5. **Credits run low?** Recharge with `topup_endpoint.py`

### What Happens When Credits = 0?

Your endpoint **stops working** and returns an error. Users cannot access it until you recharge.

---

## Consumer Flows

### A. Pay-Per-Request (Recommended)

```bash
# Pay with Base (EVM) - 100% reliable
python {baseDir}/scripts/pay_base.py https://api.x402layer.cc/e/weather-data

# Pay with Solana - includes retry logic
python {baseDir}/scripts/pay_solana.py https://api.x402layer.cc/e/weather-data
```

### B. Credit-Based Access (Fastest)

Pre-purchase credits for instant access without blockchain latency:

```bash
# Check your balance
python {baseDir}/scripts/check_credits.py weather-data

# Buy credits (consumer purchasing credits)
python {baseDir}/scripts/recharge_credits.py weather-data pack_100

# Use credits for instant access
python {baseDir}/scripts/consume_credits.py https://api.x402layer.cc/e/weather-data
```

### C. Discover Services

```bash
# Browse all services
python {baseDir}/scripts/discover_marketplace.py

# Search by keyword
python {baseDir}/scripts/discover_marketplace.py search weather
```

---

## Provider Flows

### A. Create Endpoint ($5 one-time)

Deploy your own monetized API:

**Basic (not listed on marketplace):**
```bash
python {baseDir}/scripts/create_endpoint.py my-api "My AI Service" https://api.example.com 0.01 --no-list
```

**With marketplace listing (recommended):**
```bash
python {baseDir}/scripts/create_endpoint.py my-api "My AI Service" https://api.example.com 0.01 \
    --category ai \
    --description "AI-powered data analysis API" \
    --logo https://example.com/logo.png \
    --banner https://example.com/banner.jpg
```

**Available categories:** `ai`, `data`, `finance`, `utility`, `social`, `gaming`

> **Note**: Save the `API Key` from the output and use it to secure your origin server.

> ⚠️ **IMPORTANT - How Credits Work:**
> - **Cost:** $5 one-time, includes **20,000 credits** (NOT test credits!)
> - **Consumption:** 1 credit is deducted for **each API request** to your endpoint
> - **When credits reach 0:** Your endpoint **stops working** until you recharge
> - **Recharge:** Use `topup_endpoint.py` to add more credits ($1 = 500 credits)
> - **Users pay YOU:** Each user payment goes to your wallet, then 1 credit is used

Includes 20,000 starting credits.

### B. Manage Your Endpoint

```bash
# List your endpoints
python {baseDir}/scripts/manage_endpoint.py list

# View stats
python {baseDir}/scripts/manage_endpoint.py stats my-api

# Update price
python {baseDir}/scripts/manage_endpoint.py update my-api --price 0.02
```

### C. Recharge Your Endpoint (Required to Keep It Working)

**Your endpoint consumes 1 credit per request.** When credits run out, it stops working. Recharge to keep it active:

```bash
# Add $10 worth of credits (5,000 credits at 500 credits/$1)
python {baseDir}/scripts/topup_endpoint.py my-api 10

# Check remaining credits first
python {baseDir}/scripts/manage_endpoint.py stats my-api
```

> ⚠️ **Remember:** `topup_endpoint.py` is for **providers** to recharge THEIR endpoint.
> `recharge_credits.py` is for **consumers** to buy credits at someone else's endpoint.

### D. Marketplace Listing Management

Marketplace listing can be done **during creation** OR **separately afterward**:

**Option 1: During Creation** (Recommended)
```bash
python {baseDir}/scripts/create_endpoint.py my-api "My API" https://api.example.com 0.01 \
    --category ai \
    --description "AI-powered analysis" \
    --logo https://example.com/logo.png \
    --banner https://example.com/banner.jpg
```

**Option 2: After Creation** (Update or List Later)
```bash
# List or update marketplace listing
python {baseDir}/scripts/list_on_marketplace.py my-api \
    --category ai \
    --description "AI-powered analysis" \
    --logo https://example.com/logo.png \
    --banner https://example.com/banner.jpg

# Unlist from marketplace
python {baseDir}/scripts/list_on_marketplace.py my-api --unlist
```

> **Tip:** Use `list_on_marketplace.py` to update your listing anytime - change category, description, or images without recreating the endpoint.

---

## Payment Technical Details

### Base (EVM) - EIP-712 Signatures

Uses USDC `TransferWithAuthorization` (EIP-3009):
- Gasless for payer
- Facilitator settles on-chain
- 100% reliable

### Solana - Versioned Transactions

Uses `VersionedTransaction` with `MessageV0`:
- Facilitator pays gas (from `extra.feePayer`)
- SPL Token `TransferChecked` instruction
- ~75% success rate (retry logic included)

---

## Environment Reference

| Variable | Required For | Description |
|----------|--------------|-------------|
| `PRIVATE_KEY` | Base payments | EVM private key (0x...) |
| `WALLET_ADDRESS` | All operations | Your wallet address |
| `SOLANA_SECRET_KEY` | Solana payments | JSON array of bytes |

---

## API Base URL

- **Endpoints:** `https://api.x402layer.cc/e/{slug}`
- **Marketplace:** `https://api.x402layer.cc/api/marketplace`
- **Credits:** `https://api.x402layer.cc/api/credits/*`
- **Agent API:** `https://api.x402layer.cc/agent/*`

---

## Resources

- 📖 **Documentation:** [studio.x402layer.cc/docs/agentic-access/openclaw-skill](https://studio.x402layer.cc/docs/agentic-access/openclaw-skill)
- 💻 **GitHub Docs:** [github.com/ivaavimusic/SGL_DOCS_2025](https://github.com/ivaavimusic/SGL_DOCS_2025)
- 🐦 **OpenClaw:** [x.com/openclaw](https://x.com/openclaw)
- 🌐 **x402 Studio:** [studio.x402layer.cc](https://studio.x402layer.cc)

---

## Known Issues

⚠️ **Solana payments** have ~75% success rate due to facilitator-side fee payer infrastructure issue. Retry logic is included in `pay_solana.py`. **Base (EVM) payments are 100% reliable** and recommended for production.
