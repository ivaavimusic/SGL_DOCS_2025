#!/usr/bin/env python3
"""
x402 Marketplace Listing Management

List, update, or unlist your endpoint on the x402 marketplace.

Usage:
    # List/Update endpoint on marketplace
    python list_on_marketplace.py my-api --category ai --description "AI analysis"

    # Update with images
    python list_on_marketplace.py my-api --category ai --description "AI analysis" \\
        --logo https://example.com/logo.png --banner https://example.com/banner.jpg

    # Unlist from marketplace
    python list_on_marketplace.py my-api --unlist

Categories: ai, data, finance, utility, social, gaming

Environment Variables:
    WALLET_ADDRESS - Your wallet address (must match endpoint owner)
"""

import os
import sys
import json
import argparse
import requests

API_BASE = "https://api.x402layer.cc"

def load_wallet():
    """Load wallet address from environment."""
    wallet = os.getenv("WALLET_ADDRESS")
    if not wallet:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            wallet = os.getenv("WALLET_ADDRESS")
        except ImportError:
            pass

    if not wallet:
        print("Error: Set WALLET_ADDRESS environment variable")
        sys.exit(1)
    return wallet

def list_endpoint(slug: str, category: str = None, description: str = None,
                  logo_url: str = None, banner_url: str = None, tags: list = None) -> dict:
    """
    List or update an endpoint on the marketplace.

    Args:
        slug: Endpoint slug
        category: Marketplace category (ai, data, finance, utility, social, gaming)
        description: Public description
        logo_url: Logo image URL
        banner_url: Banner image URL
        tags: Optional list of tags
    """
    wallet = load_wallet()

    url = f"{API_BASE}/api/marketplace/list"
    headers = {"x-wallet-address": wallet}

    data = {"slug": slug}

    if category:
        data["category"] = category
    if description:
        data["description"] = description
    if logo_url:
        data["logo_url"] = logo_url
    if banner_url:
        data["banner_url"] = banner_url
    if tags:
        data["tags"] = tags

    action = "Updating" if category or description else "Listing"
    print(f"{action} endpoint: {slug}")
    if category:
        print(f"  Category: {category}")
    if description:
        print(f"  Description: {description[:50]}{'...' if len(description) > 50 else ''}")
    if logo_url:
        print(f"  Logo: {logo_url}")
    if banner_url:
        print(f"  Banner: {banner_url}")

    response = requests.post(url, json=data, headers=headers)

    if response.status_code in [200, 201]:
        result = response.json()
        if result.get("success"):
            print(f"\\n✅ Endpoint '{slug}' is now listed on marketplace!")
        else:
            print(f"\\n⚠️ {result.get('message', 'Operation completed')}")
        return result
    else:
        print(f"\\n❌ Error: {response.status_code}")
        return {"error": response.text}

def unlist_endpoint(slug: str) -> dict:
    """Remove an endpoint from the marketplace."""
    wallet = load_wallet()

    url = f"{API_BASE}/api/marketplace/unlist"
    headers = {"x-wallet-address": wallet}
    data = {"slug": slug}

    print(f"Unlisting endpoint: {slug} from marketplace...")

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"\\n✅ Endpoint '{slug}' removed from marketplace")
        return result
    else:
        print(f"\\n❌ Error: {response.status_code}")
        return {"error": response.text}

def main():
    parser = argparse.ArgumentParser(
        description="Manage x402 marketplace listing for your endpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List on marketplace (minimum required)
  python list_on_marketplace.py my-api --category ai --description "My AI API"

  # Update existing listing with images
  python list_on_marketplace.py my-api --logo https://example.com/logo.png

  # Unlist from marketplace
  python list_on_marketplace.py my-api --unlist
        """
    )

    parser.add_argument("slug", help="Endpoint slug")
    parser.add_argument("--category", choices=["ai", "data", "finance", "utility", "social", "gaming"],
                        help="Marketplace category")
    parser.add_argument("--description", help="Public description")
    parser.add_argument("--logo", help="Logo image URL")
    parser.add_argument("--banner", help="Banner image URL")
    parser.add_argument("--tags", nargs="+", help="Optional tags")
    parser.add_argument("--unlist", action="store_true", help="Remove from marketplace")

    args = parser.parse_args()

    if args.unlist:
        result = unlist_endpoint(args.slug)
    else:
        # At least category or description should be provided for listing
        if not args.category and not args.description and not args.logo and not args.banner:
            print("Error: At least one of --category, --description, --logo, or --banner is required")
            print("Use --help for usage information")
            sys.exit(1)
        result = list_endpoint(
            args.slug,
            category=args.category,
            description=args.description,
            logo_url=args.logo,
            banner_url=args.banner,
            tags=args.tags
        )

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
