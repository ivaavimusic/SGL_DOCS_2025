#!/usr/bin/env python3
"""
x402Compute — Get details for a specific instance.

Usage:
  python instance_details.py <instance_id>
"""

import json
import sys

import requests

from wallet_signing import load_wallet_address

BASE_URL = "https://compute.x402layer.cc"


def get_instance_details(instance_id: str) -> dict:
    """Get details for a specific compute instance."""
    wallet = load_wallet_address(required=True)

    response = requests.get(
        f"{BASE_URL}/compute/instances/{instance_id}",
        headers={"x-wallet-address": wallet},
        timeout=30,
    )

    if response.status_code != 200:
        return {"error": f"HTTP {response.status_code}", "response": response.text[:500]}

    data = response.json()
    order = data.get("order", data)

    print(f"Instance Details:")
    print(f"  ID:       {order.get('id', instance_id)}")
    print(f"  Status:   {order.get('status', 'unknown')}")
    print(f"  Plan:     {order.get('plan', 'N/A')}")
    print(f"  Region:   {order.get('region', 'N/A')}")
    print(f"  IP:       {order.get('ip_address', 'pending')}")
    print(f"  Label:    {order.get('label', 'N/A')}")
    print(f"  Expires:  {order.get('expires_at', 'N/A')}")
    print(f"  Created:  {order.get('created_at', 'N/A')}")

    if order.get("vultr_instance_id"):
        print(f"  Vultr ID: {order['vultr_instance_id']}")

    # Show credentials when available (after provisioning completes)
    if order.get("vultr_default_password"):
        print(f"\n  🔐 Credentials:")
        print(f"     IP:       {order.get('ip_address', 'pending')}")
        print(f"     Password: {order['vultr_default_password']}")
    if order.get("vultr_v6_main_ip"):
        print(f"     IPv6:     {order['vultr_v6_main_ip']}")

    return data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python instance_details.py <instance_id>")
        sys.exit(1)

    result = get_instance_details(sys.argv[1])
    if "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)
