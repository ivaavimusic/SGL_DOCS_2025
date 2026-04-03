# Agentic Endpoint Creation

Deploy your own monetized API endpoints programmatically.

Use this when the user wants to:
- create a paid API
- put an x402 paywall behind a button or action
- reuse one endpoint as the payment source for a custom UI
- top up endpoint credits after launch

## Endpoint
POST https://api.x402layer.cc/agent/endpoints

## Pricing
Create: $1 (4,000 credits included)
Top-up: $1 = 500 credits

## Create Flow
1. POST with endpoint config (name, slug, origin_url, chain)
2. Get 402 challenge
3. Sign with EIP-712
4. Send X-Payment header
5. Receive gateway URL and API key

## Seller-side controls now available in the skill

Agents can now configure the same endpoint-level settings humans use in Studio for direct endpoints:
- best fit audience
- AgentKit benefit mode
- AgentKit discount percent
- AgentKit free-trial uses

Create example:

```bash
python {baseDir}/scripts/create_endpoint.py cataas "CATAAS" https://example.com/cat 0.01 \
  --best-fit agents \
  --agentkit-benefit discount \
  --agentkit-discount-percent 20
```

Update example:

```bash
python {baseDir}/scripts/manage_endpoint.py update cataas \
  --best-fit humans \
  --agentkit-benefit free_trial \
  --agentkit-free-trial-uses 3
```

Audience labels map to:
- `everyone` -> `all`
- `humans` -> `human_only`
- `agents` -> `agent_only`

AgentKit benefit modes mean:
- `off`
- `free`
- `free_trial`
- `discount`

AgentKit benefits are currently valid only for direct endpoints and are evaluated against verified human-backed agent wallets.

The returned gateway URL becomes the public paid endpoint your users or agents call.
That same endpoint can sit behind:
- hosted request pages
- your own frontend button, card, or modal
- another agent workflow

## Top-Up
PUT /agent/endpoints/<slug> with topup_amount

## Check Status
GET /agent/endpoints/<slug> with x-api-key header

## Important Security Rule

When your endpoint origin receives proxied traffic from x402, it must verify:

```http
x-api-key: <YOUR_API_KEY>
```

Reject requests when the key is missing or wrong.

## When To Create Separate Endpoints

Reuse one endpoint when you just need one paid action.

Create separate endpoints when you need:
- different pricing
- separate analytics/accounting
- different webhook or fulfillment behavior
- different chains or wallet recipients
