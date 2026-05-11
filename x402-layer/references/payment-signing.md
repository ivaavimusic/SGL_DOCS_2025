# Payment Signing Reference

## Critical Understanding

x402 uses EIP-712 typed data signatures for TransferWithAuthorization. The facilitator verifies signatures and settles the payment.

## Base (EVM) - EIP-712 Signing

### Domain (Base USDC)
```python
domain = {
    "name": "USD Coin",
    "version": "2",
    "chainId": 8453,
    "verifyingContract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
}
```

### Types
```python
types = {
    "TransferWithAuthorization": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "validAfter", "type": "uint256"},
        {"name": "validBefore", "type": "uint256"},
        {"name": "nonce", "type": "bytes32"},
    ]
}
```

### Signing
```python
from eth_account import Account
from eth_account.messages import encode_typed_data
import os, time

message = {
    "from": wallet,
    "to": challenge["payTo"],
    "value": int(challenge["maxAmountRequired"]),
    "validAfter": 0,
    "validBefore": int(time.time()) + 3600,
    "nonce": os.urandom(32),
}

encoded = encode_typed_data(domain, types, message)
signed = Account.sign_message(encoded, private_key)
```

## MegaETH (EVM) - ERC-2612 Permit Signing

MegaETH uses USDm which supports native ERC-2612 `permit()`. The embedded facilitator calls `permit()` + `transferFrom()` on-chain — gasless for the payer.

### Domain (MegaETH USDm)
```python
domain = {
    "name": "MegaUSD",
    "version": "1",
    "chainId": 4326,
    "verifyingContract": "0xFAfDdbb3FC7688494971a79cc65DCa3EF82079E7"
}
```

### Types
```python
types = {
    "Permit": [
        {"name": "owner", "type": "address"},
        {"name": "spender", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
    ]
}
```

### Signing
```python
from eth_account import Account
from eth_account.messages import encode_typed_data
import time

message = {
    "owner": wallet,
    "spender": challenge["payTo"],
    "value": int(challenge["maxAmountRequired"]),  # 18-decimal USDm
    "nonce": nonce_from_contract,  # read from USDm.nonces(owner)
    "deadline": int(time.time()) + 3600,
}

encoded = encode_typed_data(domain, types, message)
signed = Account.sign_message(encoded, private_key)
```

### Key differences from Base
- USDm uses **18 decimals** (vs USDC's 6): `$1.00` = `1000000000000000000`
- ERC-2612 Permit (not EIP-3009 TransferWithAuthorization)
- Nonce is sequential (read from contract), not random bytes32
- MegaETH has ~10ms blocks and near-zero gas — settlements are near-instant

## Solana - SPL Transfer

Solana uses SPL Token transfers with base64 encoding.

## Coinbase Agentic Wallet (AWAL) Mode

You can avoid direct key management by using AWAL:

```bash
python {baseDir}/scripts/awal_cli.py run auth login agent@example.com
python {baseDir}/scripts/awal_cli.py run auth verify <flow_id> <otp>
python {baseDir}/scripts/awal_cli.py pay-url https://api.x402layer.cc/e/weather-data
```

## OpenWallet / OWS Mode

You can also use OWS as an optional local wallet backend:

```bash
npm install -g @open-wallet-standard/core
export OWS_WALLET="hackathon-wallet"

python {baseDir}/scripts/ows_cli.py sign-message --chain ethereum --wallet hackathon-wallet --message "hello"
python {baseDir}/scripts/ows_cli.py pay-url https://api.x402layer.cc/e/weather-data --wallet hackathon-wallet
```

This rollout keeps OWS optional-first:
- use OWS for pay/discover/sign-message flows
- use private-key mode where the script still needs direct low-level transaction construction

## X-Payment Header Format

Base64 encode the payment JSON:
```python
import json, base64
x_payment = base64.b64encode(json.dumps(payload).encode()).decode()
```
