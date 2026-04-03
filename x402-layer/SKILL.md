---
name: x402-layer
version: 1.10.4
description: |
  x402-layer helps agents pay for APIs with USDC, deploy monetized endpoints,
  manage credits/webhooks/marketplace listings, and handle wallet-first ERC-8004 registration/discovery/management/reputation on Base, Ethereum, Polygon, BSC, Monad, and Solana.
  Use this skill when the user asks to "create x402 endpoint",
  "deploy monetized API", "pay for API with USDC", "check x402 credits",
  "consume API credits", "list endpoint on marketplace", "buy API credits",
  "topup endpoint", "browse x402 marketplace", "set up webhook",
  "receive payment notifications", "manage endpoint webhook",
  "verify webhook payment", "verify payment genuineness",
  "integrate crypto payments into my app", "add USDC payments to my platform",
  "sell with x402", "build a paywall with webhooks",
  "register ERC-8004 agent", "register Solana 8004 agent",
  "submit on-chain reputation feedback", "rate ERC-8004 agent",
  "use World AgentKit", "unlock human-backed agent wallet discount",
  "check if an endpoint has an AgentKit benefit", "open support chat",
  use "Coinbase Agentic Wallet (AWAL)", "OpenWallet", "OWS",
  "openwallet.sh", or use optional Singularity MCP
  access with a dashboard PAT to manage x402 Singularity Layer operations
  on Base, Ethereum, Polygon, BSC, Monad, or Solana networks.
homepage: https://docs.x402layer.cc/agentic-access/openclaw-skill
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
        - node
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
---

# x402 Singularity Layer

x402 is a Web3 payment layer where humans and agents can sell and consume APIs, products, and credits.
This skill can sign wallet messages, submit on-chain transactions, call x402/studio APIs, and manage monetized endpoint infrastructure.
This skill covers the full Singularity Layer lifecycle:
- pay/consume services
- create/manage/list endpoints
- integrate custom payment flows into an app or platform
- receive and verify webhook payment events
- register agents and submit on-chain reputation feedback
- optionally use Singularity MCP for owner-scoped dashboard and control-plane actions

Networks: Base, Ethereum, Polygon, BSC, Monad, Solana  
Currency: USDC  
Protocol: HTTP 402 Payment Required

> **Security-first usage:** No secret environment variable is universally required for installation. Set only the minimum variables needed for the exact runbook you are using. Prefer AWAL, OWS, API keys, or ephemeral wallets over long-lived mainnet private keys whenever possible.

---

## Intent Router

Use this routing first, then load the relevant reference doc.

| User intent | Primary path | Reference |
|---|---|---|
| Integrate crypto payments into an app/platform | `create_endpoint.py`, `manage_webhook.py`, `verify_webhook_payment.py`, `consume_product.py`, `recharge_credits.py` | `references/payments-integration.md`, `references/webhooks-verification.md`, `references/agentic-endpoints.md` |
| Pay/consume endpoint or product | `pay_base.py`, `pay_solana.py`, `consume_credits.py`, `consume_product.py`, `ows_cli.py` | `references/pay-per-request.md`, `references/credit-based.md`, `references/agentkit-benefits.md`, `references/openwallet-ows.md` |
| Discover/search marketplace | `discover_marketplace.py` | `references/marketplace.md`, `references/agentkit-benefits.md` |
| Create/edit/list endpoint | `create_endpoint.py`, `manage_endpoint.py`, `list_on_marketplace.py`, `topup_endpoint.py` | `references/agentic-endpoints.md`, `references/marketplace.md`, `references/agentkit-benefits.md` |
| Manage dashboard/platform control plane with PAT-backed access | `Singularity MCP` tools such as `list_my_endpoints`, `update_endpoint`, `list_my_products`, `update_product`, `set_webhook`, `remove_webhook`, `request_endpoint_creation_payment` | `references/mcp-control-plane.md`, `references/agentic-endpoints.md`, `references/marketplace.md` |
| Configure/verify webhooks | `manage_webhook.py`, `verify_webhook_payment.py` | `references/webhooks-verification.md` |
| Register/discover/manage/rate agents (ERC-8004/Solana-8004) | `register_agent.py`, `list_agents.py`, `list_my_endpoints.py`, `update_agent.py`, `submit_feedback.py` | `references/agent-registry-reputation.md` |
| Human-backed agent wallet benefits (World AgentKit) | `pay_base.py`, `discover_marketplace.py` | `references/agentkit-benefits.md` |
| Support and buyer/seller messaging | `support_auth.py`, `support_threads.py`, `xmtp_support.mjs` | `references/xmtp-support.md` |
| Use OpenWallet / OWS as an optional wallet backend | `ows_cli.py` | `references/openwallet-ows.md`, `references/pay-per-request.md`, `references/payment-signing.md` |

---

## Quick Start

### 1) Install Skill Dependencies
```bash
pip install -r {baseDir}/requirements.txt
```

### 2) Choose Wallet Mode

Option A: private keys
```bash
export PRIVATE_KEY="0x..."
export WALLET_ADDRESS="0x..."
# Solana optional
export SOLANA_SECRET_KEY="base58-or-[1,2,3,...]"
```

Option B: Coinbase AWAL
```bash
# Install Coinbase AWAL skill (shortcut)
npx skills add coinbase/agentic-wallet-skills
export X402_USE_AWAL=1
```

Option C: OpenWallet / OWS
```bash
npm install -g @open-wallet-standard/core
export OWS_WALLET="hackathon-wallet"
```

Use private-key mode for deep ERC-8004 registration and any on-chain update path that still needs direct transaction signing. AWAL remains useful for x402 payment flows. OWS is optional-first for pay/discover/sign-message flows plus wallet-auth list/support flows through `ows_cli.py` and the shared wallet helpers.

### 3) Optional Dashboard / MCP Mode

If the user provides a dashboard PAT, the agent can also use Singularity MCP for owner-scoped account actions:

```bash
export SINGULARITY_PAT="sgl_pat_..."
```

Use MCP when the task is about:
- listing all endpoints or products owned by the dashboard user
- updating endpoint or product settings
- setting or removing webhooks
- requesting endpoint creation or top-up payment challenges in an owner-scoped way

Keep the direct scripts for:
- actual request payments and local signing
- AWAL-driven pay/discover flows
- OWS-driven pay/discover/sign-message flows
- support and XMTP flows
- wallet-first ERC-8004 / Solana-8004 registration and updates

Security note: scripts read only explicit process environment variables. `.env` files are not auto-loaded.
Least-privilege note: the skill supports multiple credential types, but no single runbook needs all of them. Read-only discovery needs no secrets. PAT, API-key, AWAL, OWS, EVM, and Solana signing flows should be treated as separate capability paths, and users should set only the smallest subset required for the task in front of them.
Risk note: this skill can sign messages, submit transactions, and call x402/studio APIs. Prefer AWAL, OWS, PATs, endpoint API keys, or throwaway wallets over long-lived private keys when possible.

---

## Script Inventory

### Consumer
| Script | Purpose |
|---|---|
| `pay_base.py` | Pay endpoint on Base, with optional AgentKit benefit flow |
| `pay_solana.py` | Pay endpoint on Solana |
| `consume_credits.py` | Consume using credits |
| `consume_product.py` | Purchase digital products/files |
| `check_credits.py` | Check credit balance |
| `recharge_credits.py` | Buy endpoint credit packs |
| `discover_marketplace.py` | Browse/search marketplace and inspect AgentKit benefits |
| `support_auth.py` | Authenticate a wallet for support APIs |
| `support_threads.py` | Check support eligibility, open/list/show/close/reopen support threads |
| `xmtp_support.mjs` | Send and read XMTP support messages for a support thread |
| `awal_cli.py` | Run AWAL auth/pay/discover commands |
| `ows_cli.py` | Run OpenWallet / OWS wallet, pay, discover, sign-message, and agent-key commands |

### Provider
| Script | Purpose |
|---|---|
| `create_endpoint.py` | Deploy endpoint ($1 one-time, includes 4,000 credits) |
| `manage_endpoint.py` | List/update endpoint settings |
| `topup_endpoint.py` | Recharge provider endpoint credits |
| `list_on_marketplace.py` | List/unlist/update marketplace listing |
| `manage_webhook.py` | Set/remove/check endpoint webhook URL |
| `verify_webhook_payment.py` | Verify webhook signature + receipt genuineness (PyJWT/JWKS) |

### Agent Registry + Reputation
| Script | Purpose |
|---|---|
| `register_agent.py` | Register ERC-8004/Solana-8004 agent with image/version/tags and endpoint binding support |
| `list_agents.py` | List ERC-8004 agents owned by the configured wallet or linked dashboard user |
| `list_my_endpoints.py` | List platform endpoints that can be linked to ERC-8004 agents |
| `update_agent.py` | Update existing ERC-8004/Solana-8004 agent metadata, visibility, and endpoint bindings |
| `submit_feedback.py` | Submit on-chain reputation feedback |

---

## Core Security Requirements

### API Key Verification at Origin (mandatory)
When x402 proxies traffic to your origin, verify:
```http
x-api-key: <YOUR_API_KEY>
```
Reject requests when missing/invalid.

### Credit Economics (provider side)
- Endpoint creation: $1 one-time
- Starting credits: 4,000
- Top-up rate: 500 credits per $1
- Consumption: 1 credit per request
- If credits hit 0, endpoint stops serving until recharged

---

## Fast Runbooks

### A) Integrate Payments Into Your App
```bash
# 1. Create or reuse a paid endpoint
python {baseDir}/scripts/create_endpoint.py my-api "My API" https://api.example.com 0.01

# 2. Add server-side fulfillment
python {baseDir}/scripts/manage_webhook.py set my-api https://my-server.com/webhook

# 3. Verify webhook signatures and payment receipts server-side
python {baseDir}/scripts/verify_webhook_payment.py \
  --body-file ./webhook.json \
  --signature 't=1700000000,v1=<hex>' \
  --secret '<YOUR_SIGNING_SECRET>' \
  --required-source-slug my-api \
  --require-receipt
```

### B) Pay and Consume
```bash
python {baseDir}/scripts/pay_base.py https://api.x402layer.cc/e/weather-data
python {baseDir}/scripts/pay_base.py https://api.x402layer.cc/e/weather-data --agentkit auto
python {baseDir}/scripts/pay_solana.py https://api.x402layer.cc/e/weather-data
python {baseDir}/scripts/consume_credits.py https://api.x402layer.cc/e/weather-data

# Optional OWS backend
python {baseDir}/scripts/ows_cli.py pay-url https://api.x402layer.cc/e/weather-data --wallet hackathon-wallet
```

### C) Discover/Search Marketplace
```bash
python {baseDir}/scripts/discover_marketplace.py
python {baseDir}/scripts/discover_marketplace.py search weather
python {baseDir}/scripts/discover_marketplace.py details weather-api

# Optional OWS discovery path
python {baseDir}/scripts/ows_cli.py discover weather
```

### D) Create and Manage Endpoint
```bash
python {baseDir}/scripts/create_endpoint.py my-api "My API" https://api.example.com 0.01
python {baseDir}/scripts/manage_endpoint.py list
python {baseDir}/scripts/manage_endpoint.py update my-api --price 0.02
python {baseDir}/scripts/topup_endpoint.py my-api 10
```

### E) List/Update in Marketplace
```bash
python {baseDir}/scripts/list_on_marketplace.py my-api \
  --category ai \
  --description "AI-powered analysis" \
  --logo https://example.com/logo.png \
  --banner https://example.com/banner.jpg
```

### F) Webhook Setup and Genuineness Verification
```bash
python {baseDir}/scripts/manage_webhook.py set my-api https://my-server.com/webhook
python {baseDir}/scripts/manage_webhook.py info my-api
python {baseDir}/scripts/manage_webhook.py remove my-api
```

Webhook verification helper:
```bash
python {baseDir}/scripts/verify_webhook_payment.py \
  --body-file ./webhook.json \
  --signature 't=1700000000,v1=<hex>' \
  --secret '<YOUR_SIGNING_SECRET>' \
  --required-source-slug my-api \
  --require-receipt
```

### G) World AgentKit Benefits
```bash
# Inspect whether a listing advertises a verified human-backed agent wallet benefit
python {baseDir}/scripts/discover_marketplace.py details weather-data

# Attempt Base payment with AgentKit if the endpoint advertises a benefit
python {baseDir}/scripts/pay_base.py https://api.x402layer.cc/e/weather-data --agentkit auto

# Require AgentKit qualification instead of silently falling back
python {baseDir}/scripts/pay_base.py https://api.x402layer.cc/e/weather-data --agentkit required
```

### H) XMTP Support Threads
```bash
# Authenticate the current wallet for support APIs
python {baseDir}/scripts/support_auth.py login

# Check whether support is available for a listing
python {baseDir}/scripts/support_threads.py eligibility endpoint weather-data

# Open or reuse the support thread
python {baseDir}/scripts/support_threads.py open endpoint weather-data

# Read and send XMTP messages for a support thread
node {baseDir}/scripts/xmtp_support.mjs messages <thread_id>
node {baseDir}/scripts/xmtp_support.mjs send <thread_id> "Need help with this endpoint"
```

### H2) OpenWallet / OWS
```bash
# List local OWS wallets
python {baseDir}/scripts/ows_cli.py wallet-list

# Sign a message without exporting a raw private key
python {baseDir}/scripts/ows_cli.py sign-message --chain ethereum --wallet hackathon-wallet --message "hello"

# Create an OWS agent API key
python {baseDir}/scripts/ows_cli.py key-create --name codex-agent --wallet hackathon-wallet
```

OWS now works well for wallet lookup, challenge signing, marketplace discovery, support auth, and wallet-auth list flows. Deep ERC-8004 registration and on-chain agent update transactions still require direct signing keys.

### I) MCP Owner-Scoped Control Plane
```bash
# Set a dashboard PAT only for owner-scoped control-plane actions
export SINGULARITY_PAT="sgl_pat_..."

# Then use Singularity MCP for owner inventory/config operations such as:
# - list_my_endpoints
# - update_endpoint
# - list_my_products
# - update_product
# - set_webhook
# - remove_webhook
# - request_endpoint_creation_payment
```

### J) Agent Registration + Reputation
```bash
python {baseDir}/scripts/list_my_endpoints.py

python {baseDir}/scripts/register_agent.py \
  "My Agent" \
  "Autonomous service agent" \
  --network baseSepolia \
  --image https://example.com/agent.png \
  --version 1.10.0 \
  --tag finance \
  --tag automation \
  --endpoint-id <ENDPOINT_UUID> \
  --custom-endpoint https://api.example.com/agent

python {baseDir}/scripts/list_agents.py --network baseSepolia

python {baseDir}/scripts/update_agent.py \
  --network baseSepolia \
  --agent-id 123 \
  --version 1.4.1 \
  --tag finance \
  --tag automation \
  --endpoint-id <ENDPOINT_UUID> \
  --public

# The same EVM flow also supports:
#   --network ethereum
#   --network polygon
#   --network bsc
#   --network monad

python {baseDir}/scripts/submit_feedback.py \
  --network base \
  --agent-id 123 \
  --rating 5 \
  --comment "High quality responses"
```

---

## References

Load only what is needed for the user task:

- `references/payments-integration.md`:
  product-vs-endpoint-vs-credits decision guide plus webhook/receipt fulfillment patterns.
- `references/pay-per-request.md`:
  EIP-712/Solana payment flow and low-level signing details.
- `references/credit-based.md`:
  credit purchase + consumption behavior and examples.
- `references/marketplace.md`:
  search/list/unlist marketplace endpoints.
- `references/agentkit-benefits.md`:
  discover, qualify for, and pay with World AgentKit human-backed agent wallet benefits.
- `references/agentic-endpoints.md`:
  endpoint creation/top-up/status API behavior.
- `references/webhooks-verification.md`:
  webhook events, signature verification, and receipt cross-checks.
- `references/agent-registry-reputation.md`:
  ERC-8004/Solana-8004 registration, discovery, management, and feedback rules.
- `references/xmtp-support.md`:
  how support chat works in Studio, what needs human setup, and how agents should coordinate with users.
- `references/mcp-control-plane.md`:
  when to use Singularity MCP, what PAT scopes are needed, and which owner-scoped actions should prefer MCP over direct scripts.
- `references/openwallet-ows.md`:
  optional OpenWallet / OWS wallet backend guidance, install commands, and current scope.
- `references/payment-signing.md`:
  exact signing domains/types/header payload details.

---

## Environment Reference

No single task needs every variable below. Use least privilege and set only what the current script requires.

### Common

| Variable | Used by | Notes |
|---|---|---|
| `WALLET_ADDRESS` | most Base/EVM flows | primary wallet address |
| `PRIVATE_KEY` | Base private-key mode, support auth, XMTP helper | EVM signing key |
| `X402_USE_AWAL` | AWAL mode | set `1` |
| `X402_AUTH_MODE` | auth selection | `auto`, `private-key`, `awal` |
| `X402_PREFER_NETWORK` | network selection | `base`, `solana` |
| `X402_AGENTKIT_MODE` | optional AgentKit behavior | `off`, `auto`, `required` |
| `X402_API_BASE` | API override | default `https://api.x402layer.cc` |
| `OWS_WALLET` | OWS wrapper flows | wallet name or ID for `ows_cli.py` |
| `OWS_BIN` | OWS wrapper flows | optional explicit path to the `ows` executable |

### Optional MCP Control Plane

| Variable | Used by | Notes |
|---|---|---|
| `SINGULARITY_PAT` | Singularity MCP owner-scoped management flows | optional PAT in `sgl_pat_*` format; not required for install or normal script usage |

### Provider and Marketplace Management

| Variable | Used by | Notes |
|---|---|---|
| `X_API_KEY` | endpoint/webhook/listing management | endpoint API key |
| `API_KEY` | fallback for management scripts | interchangeable fallback with `X_API_KEY` |

### Solana

| Variable | Used by | Notes |
|---|---|---|
| `SOLANA_SECRET_KEY` | Solana private-key mode | base58 secret or JSON array bytes |
| `SOLANA_WALLET_ADDRESS` | Solana override and listing helpers | optional |
| `WALLET_ADDRESS_SECONDARY` | dual-chain endpoint mode | optional |

### Support and XMTP

| Variable | Used by | Notes |
|---|---|---|
| `SUPPORT_AGENT_TOKEN` | support thread scripts | optional reuse of prior login |
| `X402_STUDIO_BASE_URL` | `support_auth.py`, `support_threads.py` | optional Studio API base override |
| `X402_API_BASE_URL` | support thread scripts | default `https://api.x402layer.cc` |
| `XMTP_ENV` | `xmtp_support.mjs` | default `production` |
| `XMTP_DB_PATH` | `xmtp_support.mjs` | optional persistent DB path override |

### Agent Registry and Feedback

| Variable | Used by | Notes |
|---|---|---|
| `WORKER_FEEDBACK_API_KEY` | `submit_feedback.py` | only needed for reputation feedback writes |
| `BASE_RPC_URL` and other chain RPC URLs | `register_agent.py` | optional RPC overrides for agent registration |

---

## API Base Paths

- Endpoints: `https://api.x402layer.cc/e/{slug}`
- Marketplace: `https://api.x402layer.cc/api/marketplace`
- Credits: `https://api.x402layer.cc/api/credits/*`
- Agent routes: `https://api.x402layer.cc/agent/*`
- MCP: `https://mcp.x402layer.cc/mcp`

---

## Resources

- Docs: https://docs.x402layer.cc/agentic-access/openclaw-skill
- MCP docs: https://studio.x402layer.cc/docs/agentic-access/mcp-server
- SDK docs: https://studio.x402layer.cc/docs/developer/sdk-receipts
- GitHub docs repo: https://github.com/ivaavimusic/SGL_DOCS_2025
- x402 Studio: https://studio.x402layer.cc

---

## Known Issue

Solana exact-payment flows must use the `feePayer` returned by the challenge and keep the transaction compute-unit limit within facilitator requirements. `pay_solana.py` and `solana_signing.py` handle this for the current PayAI-backed flow; prefer Base when you need the simplest production path.

OpenWallet / OWS support is optional-first in this release: use it for pay/discover/sign-message flows and wallet-auth list/support flows, but keep private-key mode for deep wallet-first registration and on-chain update transaction paths. OWS execution now requires a local `ows` binary (or `OWS_BIN`) instead of fetching code on demand via runtime `npx`.


---

## Credential safety

This skill supports many optional workflows, so it can work with many credential types. That does **not** mean you should set all of them.

Preferred order of safety when possible:
1. Read-only discovery with no secrets
2. Endpoint API keys or PATs for scoped control-plane actions
3. AWAL or OWS for delegated/local wallet access
4. Dedicated throwaway private keys for direct signing

Do not export a long-lived high-value custody wallet into the environment just to browse, inspect, or test small flows.
