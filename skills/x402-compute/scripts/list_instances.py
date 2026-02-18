#!/usr/bin/env python3
"""
x402Compute — List your compute instances.

Usage:
  python list_instances.py
"""

import json
import sys

import requests

from wallet_signing import load_wallet_address

BASE_URL = "https://compute.x402layer.cc"


def list_instances() -> dict:
    """List all compute instances for the current wallet."""
    wallet = load_wallet_address(required=True)

    response = requests.get(
        f"{BASE_URL}/compute/instances",
        headers={"x-wallet-address": wallet},
        params={"wallet": wallet},
        timeout=30,
    )

    if response.status_code != 200:
        return {"error": f"HTTP {response.status_code}", "response": response.text[:500]}

    data = response.json()
    instances = data.get("instances", data.get("orders", []))

    print(f"Found {len(instances)} instance(s)")
    for inst in instances:
        status = inst.get("status", "unknown")
        label = inst.get("label", inst.get("id", "N/A"))
        ip = inst.get("ip_address", "pending")
        plan = inst.get("plan", "N/A")
        expires = inst.get("expires_at", "N/A")
        print(f"  [{status:8s}] {label:20s}  {plan:30s}  IP: {ip:16s}  Expires: {expires}")

    return data


if __name__ == "__main__":
    result = list_instances()
    if "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)
