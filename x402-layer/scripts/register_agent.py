#!/usr/bin/env python3
"""
x402 ERC-8004 Agent Registration (Worker API)

Registers an ERC-8004 / Solana-8004 agent through the worker endpoint:
POST /agent/erc8004/register

This flow is x402-payment protected. The script handles:
1) 402 challenge fetch
2) payment signing (Base private key or Solana signer)
3) final paid registration request
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

import requests

from awal_bridge import awal_pay_url
from network_selection import pick_payment_option
from solana_signing import create_solana_xpayment_from_accept, load_solana_wallet_address
from wallet_signing import is_awal_mode, load_wallet_address

API_BASE = (os.getenv("X402_API_BASE") or "https://api.x402layer.cc").rstrip("/")


def _is_solana_network(network: str) -> bool:
    return network in ("solanaMainnet", "solanaDevnet")


def _resolve_owner_address(network: str, owner_address: Optional[str]) -> str:
    if owner_address:
        return owner_address
    if _is_solana_network(network):
        sol_wallet = load_solana_wallet_address()
        if not sol_wallet:
            raise ValueError(
                "Solana registration requires ownerAddress. Set --owner-address or configure SOLANA_SECRET_KEY/SOLANA_WALLET_ADDRESS."
            )
        return sol_wallet
    wallet = load_wallet_address(required=True)
    if not wallet:
        raise ValueError("Failed to resolve WALLET_ADDRESS")
    return wallet


def register_agent(
    name: str,
    description: str,
    endpoint: str,
    network: str,
    owner_address: Optional[str] = None,
    image: Optional[str] = None,
) -> Dict[str, Any]:
    owner = _resolve_owner_address(network, owner_address)
    url = f"{API_BASE}/agent/erc8004/register"

    body: Dict[str, Any] = {
        "name": name,
        "description": description,
        "endpoint": endpoint,
        "network": network,
        "ownerAddress": owner,
    }
    if image:
        body["image"] = image

    print(f"Registering agent: {name}")
    print(f"Network: {network}")
    print(f"Endpoint: {endpoint}")
    print("Requesting payment challenge...")

    challenge_resp = requests.post(url, json=body, timeout=30)
    if challenge_resp.status_code not in (402, 200, 201):
        return {
            "error": f"Unexpected status: {challenge_resp.status_code}",
            "response": challenge_resp.text,
        }

    if challenge_resp.status_code in (200, 201):
        # Endpoint may return direct success in trusted environments.
        return challenge_resp.json()

    challenge = challenge_resp.json()

    if is_awal_mode():
        wallet = load_wallet_address(required=False)
        headers = {"x-wallet-address": wallet} if wallet else None
        print("Payment mode: AWAL")
        result = awal_pay_url(url, method="POST", data=body, headers=headers)
        return result if isinstance(result, dict) else {"result": result}

    try:
        selected_network, selected_option, signer = pick_payment_option(challenge, context="agent registration")
    except Exception as exc:
        return {"error": str(exc)}

    if selected_network == "base":
        if signer is None:
            return {"error": "Internal error: missing Base signer"}
        x_payment = signer.create_x402_payment_header(
            pay_to=selected_option["payTo"],
            amount=int(selected_option["maxAmountRequired"]),
        )
        payer_wallet = signer.wallet
    else:
        x_payment = create_solana_xpayment_from_accept(selected_option)
        payer_wallet = load_solana_wallet_address() or owner

    paid_resp = requests.post(
        url,
        json=body,
        headers={
            "X-Payment": x_payment,
            "x-wallet-address": payer_wallet,
        },
        timeout=60,
    )

    print(f"Payment network used: {selected_network}")
    print(f"Response: {paid_resp.status_code}")

    if paid_resp.status_code in (200, 201):
        return paid_resp.json()
    return {"error": paid_resp.text}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Register an ERC-8004/Solana-8004 agent via worker API",
    )
    parser.add_argument("name", help="Agent display name")
    parser.add_argument("description", help="Agent description")
    parser.add_argument("endpoint", help="Primary service endpoint URL")
    parser.add_argument(
        "--network",
        default="baseSepolia",
        choices=["base", "baseSepolia", "solanaMainnet", "solanaDevnet"],
        help="Target registration network",
    )
    parser.add_argument("--owner-address", help="Owner wallet address (auto-resolved if omitted)")
    parser.add_argument("--image", help="Optional image URL")
    args = parser.parse_args()

    result = register_agent(
        name=args.name,
        description=args.description,
        endpoint=args.endpoint,
        network=args.network,
        owner_address=args.owner_address,
        image=args.image,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        sys.exit(1)

