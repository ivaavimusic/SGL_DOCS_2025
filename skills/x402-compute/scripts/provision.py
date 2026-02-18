#!/usr/bin/env python3
"""
x402Compute — Provision a new compute instance.

Handles the full x402 payment flow:
1. POST /compute/provision → get 402 challenge
2. Sign USDC TransferWithAuthorization locally
3. Resend with X-Payment header → instance provisioned

Usage:
  python provision.py <plan_id> <region> [--months N] [--os-id ID] [--label NAME] [--network base|solana]

Example:
  python provision.py vcg-a100-1c-2g-6gb lax --months 1 --label "my-gpu"
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


def provision_instance(
    plan: str,
    region: str,
    months: int = 1,
    os_id: int = 2284,
    label: str = "x402-instance",
    network: str = "base",
) -> dict:
    """Provision a compute instance with x402 payment."""
    wallet = load_wallet_address(required=True)

    body = {
        "plan": plan,
        "region": region,
        "os_id": os_id,
        "label": label,
        "duration_months": months,
        "network": network,
    }

    print(f"Provisioning {plan} in {region} for {months} month(s)...")

    # Step 1: Get 402 challenge
    response = requests.post(
        f"{BASE_URL}/compute/provision",
        json=body,
        headers={
            "Content-Type": "application/json",
            "x-wallet-address": wallet,
        },
        timeout=30,
    )

    if response.status_code == 200:
        print("Instance provisioned (no payment required)")
        return response.json()

    if response.status_code != 402:
        return {"error": f"Unexpected status {response.status_code}", "response": response.text[:500]}

    challenge = response.json()

    if is_awal_mode():
        print("AWAL mode not yet supported for compute provisioning. Use private-key mode.")
        return {"error": "AWAL not supported for compute yet"}

    signer = load_payment_signer()
    base_option = _find_base_accept_option(challenge)

    pay_to = base_option["payTo"]
    amount = int(base_option["maxAmountRequired"])
    print(f"Payment required: {amount} atomic USDC units (${amount / 1_000_000:.2f})")

    x_payment = signer.create_x402_payment_header(pay_to=pay_to, amount=amount)

    # Step 2: Pay and provision
    response = requests.post(
        f"{BASE_URL}/compute/provision",
        json=body,
        headers={
            "Content-Type": "application/json",
            "X-Payment": x_payment,
            "x-wallet-address": signer.wallet,
        },
        timeout=120,
    )

    print(f"Response: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        order = data.get("order", {})
        print(f"✅ Instance provisioned!")
        print(f"   ID:      {order.get('id', 'N/A')}")
        print(f"   IP:      {order.get('ip_address', 'pending')}")
        print(f"   Plan:    {order.get('plan', plan)}")
        print(f"   Expires: {order.get('expires_at', 'N/A')}")
        if data.get("tx_hash"):
            print(f"   TX:      {data['tx_hash']}")
        return data

    return {"error": f"Provisioning failed: {response.status_code}", "response": response.text[:500]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Provision a compute instance")
    parser.add_argument("plan", help="Plan ID (e.g. vcg-a100-1c-2g-6gb)")
    parser.add_argument("region", help="Region ID (e.g. lax)")
    parser.add_argument("--months", type=int, default=1, help="Duration in months (default: 1)")
    parser.add_argument("--os-id", type=int, default=2284, help="OS image ID (default: 2284 = Ubuntu 24.04)")
    parser.add_argument("--label", default="x402-instance", help="Instance label")
    parser.add_argument("--network", default="base", choices=["base", "solana"], help="Payment network")
    args = parser.parse_args()

    result = provision_instance(
        plan=args.plan,
        region=args.region,
        months=args.months,
        os_id=args.os_id,
        label=args.label,
        network=args.network,
    )
    if "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)
