#!/usr/bin/env python3
"""
x402 Agentic Endpoint Creation

Create a new monetized API endpoint on the x402 network.
Cost: $5 USDC (includes 20,000 credits)

IMPORTANT: Credits are NOT test credits!
- Each API request to your endpoint consumes 1 credit
- When credits reach 0, your endpoint stops working
- You must recharge (topup) to keep your endpoint active
- Users pay YOU per request, 1 credit is deducted for infrastructure

Usage:
    python create_endpoint.py <slug> <name> <origin_url> <price> [options]

Example:
    python create_endpoint.py my-api "My API Service" https://api.example.com 0.01

With Marketplace Listing:
    python create_endpoint.py my-api "My API" https://api.example.com 0.01 \\
        --category ai --description "AI-powered analysis" \\
        --logo https://example.com/logo.png --banner https://example.com/banner.jpg

Environment Variables:
    PRIVATE_KEY - Your EVM private key (0x...)
    WALLET_ADDRESS - Your wallet address (0x...)

Options:
    --category        Marketplace category (ai, data, finance, utility, social, gaming)
    --description     Public description for marketplace
    --logo            Logo image URL for marketplace listing
    --banner          Banner image URL for marketplace listing
    --no-list         Create endpoint WITHOUT listing on marketplace
"""

import os
import sys
import json
import time
import base64
import requests
from eth_account import Account

API_BASE = "https://api.x402layer.cc"
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDC_NAME = "USD Coin"
USDC_VERSION = "2"

def load_credentials():
    """Load wallet credentials from environment."""
    private_key = os.getenv("PRIVATE_KEY")
    wallet = os.getenv("WALLET_ADDRESS")
    if not private_key or not wallet:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            private_key = os.getenv("PRIVATE_KEY")
            wallet = os.getenv("WALLET_ADDRESS")
        except ImportError:
            pass
    
    if not private_key or not wallet:
        print("Error: Set PRIVATE_KEY and WALLET_ADDRESS environment variables")
        sys.exit(1)
    return private_key, wallet

def create_endpoint(slug: str, name: str, origin_url: str, price: float, chain: str = "base",
                     category: str = None, description: str = None, logo_url: str = None,
                     banner_url: str = None, list_on_marketplace: bool = True) -> dict:
    """
    Create a new agentic endpoint.

    Args:
        slug: URL-friendly identifier (e.g., "my-api")
        name: Human-readable name
        origin_url: Your backend API URL
        price: Price per call in USD (e.g., 0.01)
        chain: Payment chain (base, solana, or both)
        category: Marketplace category (ai, data, finance, utility, social, gaming)
        description: Public description for marketplace
        logo_url: Logo image URL for marketplace listing
        banner_url: Banner image URL for marketplace listing
        list_on_marketplace: Whether to list on marketplace (default: True)

    Returns:
        Endpoint details including API key
    """
    private_key, wallet = load_credentials()
    
    url = f"{API_BASE}/agent/endpoints"
    
    data = {
        "name": name,
        "slug": slug,
        "origin_url": origin_url,
        "chain": chain,
        "wallet_address": wallet,
        "price": price,
        "currency": "USDC",
        "list_on_marketplace": list_on_marketplace
    }

    # Add optional marketplace listing fields
    if category:
        data["category"] = category
    if description:
        data["description"] = description
    if logo_url:
        data["image_url"] = logo_url
    if banner_url:
        data["banner_url"] = banner_url
    
    print(f"Creating endpoint: {slug}")
    print(f"Origin: {origin_url}")
    print(f"Price: ${price} per call")
    print(f"Chain: {chain}")
    print(f"List on Marketplace: {list_on_marketplace}")
    if category:
        print(f"Category: {category}")
    if logo_url:
        print(f"Logo: {logo_url}")
    if banner_url:
        print(f"Banner: {banner_url}")
    print("Cost: $5 USDC (includes 20,000 credits)")
    print("\nIMPORTANT: Each request consumes 1 credit. Recharge to keep endpoint active!")
    
    # Step 1: Get 402 challenge
    response = requests.post(url, json=data, headers={"x-wallet-address": wallet})
    
    if response.status_code != 402:
        return {"error": f"Unexpected status: {response.status_code}", "response": response.text}
    
    challenge = response.json()
    
    # Find Base payment option
    base_option = None
    for opt in challenge.get("accepts", []):
        if opt.get("network") == "base":
            base_option = opt
            break
    
    if not base_option:
        return {"error": "No Base payment option available"}
    
    # Step 2: Sign EIP-712 payment
    pay_to = base_option["payTo"]
    amount = int(base_option["maxAmountRequired"])
    # Nonce must be bytes32 (0x + 64 hex chars = 32 bytes)
    import secrets
    nonce = "0x" + secrets.token_hex(32)
    valid_after = 0
    valid_before = int(time.time()) + 3600
    
    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"}
            ],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"}
            ]
        },
        "primaryType": "TransferWithAuthorization",
        "domain": {
            "name": USDC_NAME,
            "version": USDC_VERSION,
            "chainId": 8453,
            "verifyingContract": USDC_ADDRESS
        },
        "message": {
            "from": wallet,
            "to": pay_to,
            "value": amount,
            "validAfter": valid_after,
            "validBefore": valid_before,
            "nonce": nonce
        }
    }
    
    account = Account.from_key(private_key)
    signed = account.sign_typed_data(
        typed_data["domain"],
        {"TransferWithAuthorization": typed_data["types"]["TransferWithAuthorization"]},
        typed_data["message"]
    )
    
    payload = {
        "x402Version": 1,
        "scheme": "exact",
        "network": "base",
        "payload": {
            "signature": signed.signature.hex(),
            "authorization": {
                "from": wallet,
                "to": pay_to,
                "value": str(amount),
                "validAfter": str(valid_after),
                "validBefore": str(valid_before),
                "nonce": nonce
            }
        }
    }
    
    x_payment = base64.b64encode(json.dumps(payload).encode()).decode()
    
    # Step 3: Complete creation
    response = requests.post(
        url,
        json=data,
        headers={
            "X-Payment": x_payment,
            "x-wallet-address": wallet
        }
    )
    
    print(f"Response: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"\\n✅ Endpoint created!")
        print(f"URL: https://api.x402layer.cc/e/{slug}")
        if "api_key" in result:
            print(f"API Key: {result['api_key']}")
            print("\nWARNING: SECURITY ACTION REQUIRED")
            print("---------------------------------------------------------------")
            print(f"IMPORTANT: You obtained an API Key for your endpoint.")
            print(f"You MUST verify the 'x-api-key' header in your origin server ({origin_url}).")
            print(f"Expected Header: 'x-api-key': '{result['api_key']}'")
            print("Requests missing this header should be rejected (401 Unauthorized).")
            print("---------------------------------------------------------------\n")
        return result
    else:
        return {"error": response.text}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create a new x402 monetized endpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic endpoint (not listed on marketplace)
  python create_endpoint.py my-api "My API" https://api.example.com 0.01 --no-list

  # Listed on marketplace with full details
  python create_endpoint.py my-api "My AI Service" https://api.example.com 0.01 \\
      --category ai --description "AI-powered data analysis" \\
      --logo https://example.com/logo.png --banner https://example.com/banner.jpg

Categories: ai, data, finance, utility, social, gaming
        """
    )

    parser.add_argument("slug", help="URL-friendly identifier (e.g., 'my-api')")
    parser.add_argument("name", help="Human-readable name")
    parser.add_argument("origin_url", help="Your backend API URL")
    parser.add_argument("price", type=float, help="Price per call in USD (e.g., 0.01)")
    parser.add_argument("--chain", choices=["base", "solana", "both"], default="base",
                        help="Payment chain (default: base)")
    parser.add_argument("--category", choices=["ai", "data", "finance", "utility", "social", "gaming"],
                        help="Marketplace category (required for listing)")
    parser.add_argument("--description", help="Public description for marketplace")
    parser.add_argument("--logo", help="Logo image URL for marketplace listing")
    parser.add_argument("--banner", help="Banner image URL for marketplace listing")
    parser.add_argument("--no-list", action="store_true",
                        help="Create endpoint WITHOUT listing on marketplace")

    args = parser.parse_args()

    # If no marketplace options provided, don't list by default
    list_on_marketplace = not args.no_list and (args.category or args.description or args.logo or args.banner)

    result = create_endpoint(
        slug=args.slug,
        name=args.name,
        origin_url=args.origin_url,
        price=args.price,
        chain=args.chain,
        category=args.category,
        description=args.description,
        logo_url=args.logo,
        banner_url=args.banner,
        list_on_marketplace=list_on_marketplace
    )
    print(json.dumps(result, indent=2))
