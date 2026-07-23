#!/usr/bin/env python3
"""
x402Compute — Agent Pods: deploy an always-on hosted OpenClaw agent and talk to it
through its OpenAI-compatible adapter.

A pod IS a compute order — the pod id returned by `deploy` is the compute order id and is
used for every pod + lifecycle call. See references/agent-pods.md for the full surface.

Auth (two surfaces):
  - Owner calls (catalog is public; deploy / list / get / create-key are owner-authed) use the
    SAME compute auth as the rest of this skill: COMPUTE_API_KEY (X-API-Key) or wallet-signing
    keys, loaded by wallet_signing.create_compute_auth_headers.
  - Adapter calls (chat / models) use the pod-scoped integration key `sk-sglpod-int-…` as
    `Authorization: Bearer …`. Provide it with --key or the POD_INTEGRATION_KEY env var.

Credentials are read ONLY from explicit environment variables. No .env auto-loading here.

Usage:
  python agent_pod.py catalog
  python agent_pod.py list
  python agent_pod.py get <pod_id>
  python agent_pod.py deploy --ai-mode managed --tier pro --plan <plan_id> \
      --prepaid-hours 720 --telegram <bot_token> --use-credits
  python agent_pod.py deploy --ai-mode byok --plan <plan_id> --prepaid-hours 720 \
      --llm-base-url https://openrouter.ai/api/v1 --llm-api-key <key> --model openai/gpt-4o-mini --use-credits
  python agent_pod.py create-key <pod_id> --name my-integration
  python agent_pod.py chat <pod_id> "What's on my calendar today?" --key sk-sglpod-int-...
"""

import argparse
import json
import os
import sys
from typing import Dict, Optional

import requests

from wallet_signing import create_compute_auth_headers

BASE_URL = "https://compute.x402layer.cc"


def _owner_headers(method: str, path: str, body_json: str = "") -> Dict[str, str]:
    """Compute auth headers (X-API-Key from COMPUTE_API_KEY, or wallet signature)."""
    headers = create_compute_auth_headers(method, path, body_json)
    if body_json:
        headers["Content-Type"] = "application/json"
    return headers


def catalog() -> dict:
    """Public: deployable agents, managed tiers/models, channels, pricing."""
    resp = requests.get(f"{BASE_URL}/pods/catalog", timeout=30)
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "response": resp.text[:500]}
    return resp.json()


def list_pods() -> dict:
    path = "/pods"
    resp = requests.get(f"{BASE_URL}/pods", headers=_owner_headers("GET", path), timeout=30)
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "response": resp.text[:500]}
    return resp.json()


def get_pod(pod_id: str) -> dict:
    path = f"/pods/{pod_id}"
    resp = requests.get(f"{BASE_URL}{path}", headers=_owner_headers("GET", path), timeout=30)
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "response": resp.text[:500]}
    return resp.json()


def deploy(
    ai_mode: str,
    plan: str,
    prepaid_hours: int,
    agent_id: str = "openclaw",
    tier: Optional[str] = None,
    model: Optional[str] = None,
    telegram: Optional[str] = None,
    discord: Optional[str] = None,
    llm_base_url: Optional[str] = None,
    llm_api_key: Optional[str] = None,
    llm_api: Optional[str] = None,
    use_credits: bool = False,
    network: Optional[str] = None,
) -> dict:
    """Deploy a pod via POST /pods (owner / compute auth).

    Managed (we run the LLM, metered from credits): pick --tier starter|pro|max.
    BYOK (your own OpenAI-compatible key): pass --llm-base-url/--llm-api-key/--model.
    Pay from credits with --use-credits, else omit it to settle via x402 (402 flow — use the
    dashboard or the x402 provision path to complete payment).
    """
    body: dict = {
        "agent_id": agent_id,
        "ai_mode": ai_mode,
        "plan": plan,
        "prepaid_hours": prepaid_hours,
    }
    if ai_mode == "managed":
        if not tier:
            return {"error": "managed mode requires --tier (starter|pro|max)"}
        body["tier"] = tier
        if model:
            body["model"] = model
    else:  # byok
        if not (llm_base_url and llm_api_key):
            return {"error": "byok mode requires --llm-base-url and --llm-api-key"}
        body["llm_base_url"] = llm_base_url
        body["llm_api_key"] = llm_api_key
        body["llm_api"] = llm_api or "openai-completions"
        if model:
            body["model"] = model
    channels: dict = {}
    if telegram:
        channels["telegram"] = telegram
    if discord:
        channels["discord"] = discord
    if channels:
        body["channels"] = channels
    if use_credits:
        body["use_credits"] = True
    if network:
        body["network"] = network

    body_json = json.dumps(body, separators=(",", ":"))
    path = "/pods"
    resp = requests.post(
        f"{BASE_URL}/pods", data=body_json, headers=_owner_headers("POST", path, body_json), timeout=120,
    )
    if resp.status_code == 402:
        return {
            "error": "402 Payment Required — pod requires x402 payment.",
            "hint": "Deploy with --use-credits, or complete the x402 payment flow via the dashboard.",
            "challenge": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text[:500],
        }
    if resp.status_code not in (200, 201):
        return {"error": f"HTTP {resp.status_code}", "response": resp.text[:2000]}
    return resp.json()


def create_key(pod_id: str, name: str = "API key") -> dict:
    """Create an sk-sglpod-int-* integration key for the OpenAI adapter (owner / compute auth)."""
    body_json = json.dumps({"name": name}, separators=(",", ":"))
    path = f"/pods/{pod_id}/api-keys"
    resp = requests.post(
        f"{BASE_URL}{path}", data=body_json, headers=_owner_headers("POST", path, body_json), timeout=30,
    )
    if resp.status_code == 404:
        return {"error": "OpenAI adapter is not enabled for this pod (feature-flagged)."}
    if resp.status_code not in (200, 201):
        return {"error": f"HTTP {resp.status_code}", "response": resp.text[:500]}
    return resp.json()


def chat(pod_id: str, message: str, key: Optional[str] = None) -> dict:
    """Call the pod's OpenAI-compatible adapter (Bearer sk-sglpod-int-*), non-streaming."""
    key = key or os.getenv("POD_INTEGRATION_KEY")
    if not key:
        return {"error": "Provide the integration key via --key or POD_INTEGRATION_KEY (sk-sglpod-int-...)."}
    body_json = json.dumps(
        {"model": "agent-pod", "stream": False, "messages": [{"role": "user", "content": message}]},
        separators=(",", ":"),
    )
    resp = requests.post(
        f"{BASE_URL}/pods/{pod_id}/v1/chat/completions",
        data=body_json,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        timeout=120,
    )
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "response": resp.text[:500]}
    return resp.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent Pods: deploy + OpenAI adapter")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("catalog", help="List deployable agents, tiers, channels, pricing (public)")
    sub.add_parser("list", help="List your pods")

    p_get = sub.add_parser("get", help="Get one pod (details + heartbeat + masked creds)")
    p_get.add_argument("pod_id")

    p_dep = sub.add_parser("deploy", help="Deploy a pod (POST /pods)")
    p_dep.add_argument("--agent-id", default="openclaw", help="Agent to deploy (default: openclaw)")
    p_dep.add_argument("--ai-mode", required=True, choices=["managed", "byok"])
    p_dep.add_argument("--tier", choices=["starter", "pro", "max"], help="Managed tier")
    p_dep.add_argument("--plan", required=True, help="Machine plan id (from GET /compute/plans)")
    p_dep.add_argument("--prepaid-hours", type=int, default=720, help="Prepaid runtime hours (min 24; default 720)")
    p_dep.add_argument("--model", help="Managed model override (must be in tier list) or byok model id")
    p_dep.add_argument("--telegram", help="Telegram bot token")
    p_dep.add_argument("--discord", help="Discord bot token")
    p_dep.add_argument("--llm-base-url", help="BYOK: OpenAI-compatible base URL")
    p_dep.add_argument("--llm-api-key", help="BYOK: your LLM API key")
    p_dep.add_argument("--llm-api", choices=["openai-completions", "openai-responses", "anthropic-messages", "google-generative"],
                       help="BYOK: LLM API shape (default openai-completions)")
    p_dep.add_argument("--use-credits", action="store_true", help="Pay from platform credits (else x402)")
    p_dep.add_argument("--network", help="x402 network for non-Base payment (e.g. solana, robinhood, megaeth)")

    p_key = sub.add_parser("create-key", help="Create an sk-sglpod-int-* adapter integration key")
    p_key.add_argument("pod_id")
    p_key.add_argument("--name", default="API key", help="Key label")

    p_chat = sub.add_parser("chat", help="Call the pod OpenAI adapter (non-streaming)")
    p_chat.add_argument("pod_id")
    p_chat.add_argument("message")
    p_chat.add_argument("--key", help="Integration key (sk-sglpod-int-...); else POD_INTEGRATION_KEY env")

    args = parser.parse_args()

    if args.command == "catalog":
        result = catalog()
    elif args.command == "list":
        result = list_pods()
    elif args.command == "get":
        result = get_pod(args.pod_id)
    elif args.command == "deploy":
        result = deploy(
            ai_mode=args.ai_mode, plan=args.plan, prepaid_hours=args.prepaid_hours,
            agent_id=args.agent_id, tier=args.tier, model=args.model,
            telegram=args.telegram, discord=args.discord,
            llm_base_url=args.llm_base_url, llm_api_key=args.llm_api_key, llm_api=args.llm_api,
            use_credits=args.use_credits, network=args.network,
        )
        if "pod" in result:
            pod = result["pod"]
            print("✅ Pod deployed!")
            print(f"   ID:        {pod.get('id')}   (use this for all pod + lifecycle calls)")
            print(f"   Agent:     {pod.get('display_name')} ({pod.get('agent_id')})")
            print(f"   AI mode:   {pod.get('ai_mode')}  tier={pod.get('tier')}  model={pod.get('model')}")
            print(f"   Channels:  {', '.join(pod.get('channels') or []) or 'none'}")
            if pod.get("managed_ai_key"):
                print(f"   Managed AI key (shown once): {pod['managed_ai_key']}")
            print("   Next: python agent_pod.py create-key <id>  →  chat via the OpenAI adapter.")
            sys.exit(0)
    elif args.command == "create-key":
        result = create_key(args.pod_id, name=args.name)
        if result.get("key"):
            print("✅ Integration key created (shown ONCE — store it securely):")
            print(f"   Key:      {result['key']}")
            print(f"   Base URL: {result.get('base_url')}")
            print("   Call it:  Authorization: Bearer <key>, model 'agent-pod', stream:false")
            sys.exit(0)
    elif args.command == "chat":
        result = chat(args.pod_id, args.message, key=args.key)
        if "choices" in result:
            try:
                print(result["choices"][0]["message"]["content"])
            except (KeyError, IndexError, TypeError):
                print(json.dumps(result, indent=2))
            sys.exit(0)
    else:
        parser.error("unknown command")

    if isinstance(result, dict) and "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)
    print(json.dumps(result, indent=2))
