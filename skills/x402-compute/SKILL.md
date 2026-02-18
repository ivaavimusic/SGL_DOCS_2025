---
name: x402-compute
version: 1.0.3
description: |
  This skill should be used when the user asks to "provision GPU instance",
  "spin up a cloud server", "list compute plans", "browse GPU pricing",
  "extend compute instance", "destroy server instance", "check instance status",
  "list my instances", or manage x402 Singularity Compute / x402Compute
  infrastructure. Handles GPU and VPS provisioning with USDC payment on Base
  or Solana networks via the x402 payment protocol.
homepage: https://studio.x402layer.cc/docs/agentic-access/x402-compute
metadata:
  clawdbot:
    emoji: "🖥️"
    homepage: https://compute.x402layer.cc
    os:
      - linux
      - darwin
    requires:
      bins:
        - python3
      env:
        - WALLET_ADDRESS
        - PRIVATE_KEY
    credentials:
      primary: PRIVATE_KEY
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
---


# x402 Singularity Compute

Provision and manage GPU/VPS instances paid with USDC via the x402 payment protocol.

**Base URL:** `https://compute.x402layer.cc`  
**Networks:** Base (EVM) • Solana  
**Currency:** USDC  
**Protocol:** HTTP 402 Payment Required

**Access Note:** Provide an SSH public key when provisioning. Passwords are not returned by the API.

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r {baseDir}/requirements.txt
```

### 2. Set Up Wallet

#### Option A: Private Keys
```bash
export PRIVATE_KEY="0x..."
export WALLET_ADDRESS="0x..."
```

#### Option B: Coinbase Agentic Wallet (AWAL)
```bash
npx skills add coinbase/agentic-wallet-skills
export X402_USE_AWAL=1
export COMPUTE_API_KEY="x402c_..."   # required for compute management auth in AWAL mode
```

Create `COMPUTE_API_KEY` once with private-key mode:
```bash
python {baseDir}/scripts/create_api_key.py --label "my-agent"
```

---

## ⚠️ Security Notice

> **IMPORTANT**: This skill handles private keys for signing blockchain transactions.
>
> - **Never use your primary custody wallet** - Create a dedicated wallet with limited funds
> - **Private keys are used locally only** - They sign transactions locally and are never transmitted
> - **For testing**: Use a throwaway wallet with minimal USDC

---

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `browse_plans.py` | List available GPU/VPS plans with pricing |
| `browse_regions.py` | List deployment regions |
| `provision.py` | Provision a new instance (x402 payment) |
| `create_api_key.py` | Create an API key for agent access (optional) |
| `list_instances.py` | List your active instances |
| `instance_details.py` | Get details for a specific instance |
| `get_one_time_password.py` | Retrieve one-time root password fallback |
| `extend_instance.py` | Extend instance lifetime (x402 payment) |
| `destroy_instance.py` | Destroy an instance |

---

## Instance Lifecycle

```
Browse Plans → Provision (pay USDC) → Active → Extend / Destroy → Expired
```

Instances expire after their prepaid duration. Extend before expiry to keep them running.

---

## Workflows

### A. Browse and Provision

```bash
# List GPU plans
python {baseDir}/scripts/browse_plans.py

# Filter by type (gpu/vps/high-performance)
python {baseDir}/scripts/browse_plans.py --type vcg

# Check available regions
python {baseDir}/scripts/browse_regions.py

# Generate a dedicated SSH key once (recommended for agents)
ssh-keygen -t ed25519 -N "" -f ~/.ssh/x402_compute

# Provision an instance (triggers x402 payment)
python {baseDir}/scripts/provision.py vcg-a100-1c-2g-6gb lax --months 1 --label "my-gpu" --ssh-key-file ~/.ssh/x402_compute.pub

# ⚠️ After provisioning, wait 2-3 minutes for Vultr to complete setup
# Then fetch your instance details (IP, status):
python {baseDir}/scripts/instance_details.py <instance_id>
```

### B. Manage Instances

```bash
# Optional: create a reusable API key (avoids message signing each request)
python {baseDir}/scripts/create_api_key.py --label "my-agent"

# List all your instances
python {baseDir}/scripts/list_instances.py

# Get details for one instance
python {baseDir}/scripts/instance_details.py <instance_id>

# Optional fallback if no SSH key was provided during provisioning
python {baseDir}/scripts/get_one_time_password.py <instance_id>

# Extend by 1 month
python {baseDir}/scripts/extend_instance.py <instance_id> --hours 720

# Destroy
python {baseDir}/scripts/destroy_instance.py <instance_id>
```

---

## x402 Payment Flow

1. Request provision/extend → server returns `HTTP 402` with payment requirements
2. Script signs USDC `TransferWithAuthorization` (EIP-712) locally
3. Script resends request with `X-Payment` header containing signed payload
4. Server verifies payment, settles on-chain, provisions/extends instance

---

## Plan Types

| Type | Plan Prefix | Description |
|------|-------------|-------------|
| GPU | `vcg-*` | GPU-accelerated (A100, H100, etc.) |
| VPS | `vc2-*` | Standard cloud compute |
| High-Perf | `vhp-*` | High-performance dedicated |
| Dedicated | `vdc-*` | Dedicated bare-metal |

---

## Environment Reference

| Variable | Required For | Description |
|----------|--------------|-------------|
| `PRIVATE_KEY` | Base payments (private-key mode) | EVM private key (0x...) |
| `WALLET_ADDRESS` | All operations | Your wallet address |
| `COMPUTE_API_KEY` | AWAL mode / optional | Reusable API key for compute management endpoints |
| `X402_USE_AWAL` | AWAL mode | Set `1` to enable Coinbase Agentic Wallet for Base payments |
| `X402_AUTH_MODE` | Auth selection (optional) | `auto`, `private-key`, or `awal` |

---

## API Reference

For full endpoint details, see [references/api-reference.md](references/api-reference.md).

---

## Resources

- 📖 **Documentation:** [studio.x402layer.cc/docs/agentic-access/x402-compute](https://studio.x402layer.cc/docs/agentic-access/x402-compute)
- 🖥️ **Compute Dashboard:** [compute.x402layer.cc](https://compute.x402layer.cc)
- 🌐 **x402 Studio:** [studio.x402layer.cc](https://studio.x402layer.cc)
