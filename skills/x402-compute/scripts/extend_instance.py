#!/usr/bin/env python3
"""
x402Compute — Extend an instance's lifetime.

Handles the full x402 payment flow:
1. POST /compute/instances/:id/extend → get 402 challenge
2. Sign USDC TransferWithAuthorization locally
3. Resend with X-Payment header → instance extended

Usage:
  python extend_instance.py <instance_id> [--hours N] [--network base|solana]

Example:
  python extend_instance.py abc-123 --hours 720  # extend by 1 month
"""

import argparse
import json
import sys

import requests

from wallet_signing import is_awal_mode, load_payment_signer, load_wallet_address

BASE_URL = "https://compute.x402layer.cc"


def _find_base_accept_option(challenge: dict) -> dict:
    for option in challenge.get("accepts", []):
        network = str(option.get("network", "")).lower()
        if network == "base" or "8453" in network:
            return option
    raise ValueError("No Base payment option found in 402 challenge")


def extend_instance(instance_id: str, hours: int = 720, network: str = "base") -> dict:
    """Extend a compute instance with x402 payment."""
    wallet = load_wallet_address(required=True)

    body = {
        "extend_hours": hours,
        "network": network,
    }

    print(f"Extending instance {instance_id} by {hours} hours...")

    # Step 1: Get 402 challenge
    response = requests.post(
        f"{BASE_URL}/compute/instances/{instance_id}/extend",
        json=body,
        headers={
            "Content-Type": "application/json",
            "x-wallet-address": wallet,
        },
        timeout=30,
    )

    if response.status_code == 200:
        print("Instance extended (no payment required)")
        return response.json()

    if response.status_code != 402:
        return {"error": f"Unexpected status {response.status_code}", "response": response.text[:500]}

    challenge = response.json()

    if is_awal_mode():
        print("AWAL mode not yet supported for compute extension. Use private-key mode.")
        return {"error": "AWAL not supported for compute yet"}

    signer = load_payment_signer()
    base_option = _find_base_accept_option(challenge)

    pay_to = base_option["payTo"]
    amount = int(base_option["maxAmountRequired"])
    print(f"Payment required: {amount} atomic USDC units (${amount / 1_000_000:.2f})")

    x_payment = signer.create_x402_payment_header(pay_to=pay_to, amount=amount)

    # Step 2: Pay and extend
    response = requests.post(
        f"{BASE_URL}/compute/instances/{instance_id}/extend",
        json=body,
        headers={
            "Content-Type": "application/json",
            "X-Payment": x_payment,
            "x-wallet-address": signer.wallet,
        },
        timeout=60,
    )

    print(f"Response: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        order = data.get("order", {})
        print(f"✅ Instance extended!")
        print(f"   New Expiry: {order.get('expires_at', 'N/A')}")
        if data.get("tx_hash"):
            print(f"   TX: {data['tx_hash']}")
        return data

    return {"error": f"Extension failed: {response.status_code}", "response": response.text[:500]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extend a compute instance")
    parser.add_argument("instance_id", help="Instance ID to extend")
    parser.add_argument("--hours", type=int, default=720, help="Hours to extend (default: 720 = ~1 month)")
    parser.add_argument("--network", default="base", choices=["base", "solana"], help="Payment network")
    args = parser.parse_args()

    result = extend_instance(
        instance_id=args.instance_id,
        hours=args.hours,
        network=args.network,
    )
    if "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)
