# Singularity Layer MCP

MCP for Singularity Layer. Discover listings, manage endpoints and products, run payment-backed endpoint flows, consume public product and credit-pack purchase flows, and use ERC-8004 agents through authenticated MCP tools.

> ✅ **v1.5.0** Phase 3B consumer payment tooling shipped on March 22, 2026. PAT-first auth remains live, and MCP now exposes product purchases, endpoint credit-pack purchases, endpoint creation, and top-up payment flows.

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) is a standardized protocol for connecting AI assistants to external systems. It provides a unified way for AI models to access tools, resources, and prompts from external services.

The Singularity Layer MCP server exposes the broader platform through this protocol, combining marketplace discovery, endpoint and product management, and ERC-8004 agent access in a single MCP surface.

## Release & Registry Status

| Field | Value |
|-------|-------|
| Registry Package | `io.github.ivaavimusic/singularity` |
| Registry Title | `Singularity Layer MCP` |
| Status | `active` |
| Runtime Version | `1.5.0` |
| Registry Package Version | `1.5.0` |
| Published | `March 22, 2026` |
| Website | `https://studio.x402layer.cc/docs/agentic-access/mcp-server` |

The runtime server name remains `singularity-mcp`, while the official registry package is `io.github.ivaavimusic/singularity`.

## Endpoint

```bash
# MCP HTTP Endpoint
https://mcp.x402layer.cc/mcp

# Alternative Cloudflare Worker URL
https://sgl-mcp.ivaavimusicproductions.workers.dev/mcp
```

## Quick Install

### Cursor IDE

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "singularity": {
      "url": "https://mcp.x402layer.cc/mcp"
    }
  }
}
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "singularity": {
      "url": "https://mcp.x402layer.cc/mcp"
    }
  }
}
```

### Antigravity / Codex CLI

Add to `~/.codex/mcp.json` (global) or `.codex/mcp.json` (project):

```json
{
  "mcpServers": {
    "singularity": {
      "url": "https://mcp.x402layer.cc/mcp",
      "transport": "http"
    }
  }
}
```

### Windsurf / Other MCP Clients

```bash
# HTTP Transport URL
https://mcp.x402layer.cc/mcp

# Protocol: HTTP (stateless)
# Transport: Streamable HTTP
```

## PAT Authentication

Personal access tokens are now the default account-level credential for MCP. Create them in `Dashboard -> Settings -> PAT` and use `accessToken` for owner-wide MCP automation. Legacy endpoint keys remain supported for endpoint-scoped flows.

| Scope | Use For |
|-------|---------|
| `mcp:read` | Owner inventory, endpoint details, and stats |
| `mcp:endpoints:write` | Endpoint updates and webhook management |
| `mcp:products:write` | Product updates |
| `mcp:*` | Full MCP access |

> Live validation on March 22, 2026 confirmed that read-only PATs cannot perform writes, endpoint-write PATs cannot mutate products, product-write PATs cannot mutate endpoints, revoked or expired PATs are rejected cleanly, and PAT-backed endpoint top-up challenges now return a valid `402`.

## Discovery Tools (Phase 1 - No Auth)

Browse and discover marketplace listings, agents, and categories. No authentication required.

| Tool | Description | Parameters |
|------|-------------|------------|
| `browse_marketplace` | Search/filter listings with pagination | type, category, chain, mode, search, sort, minRating, limit, offset |
| `get_listing` | Get detailed info for a specific listing | slug |
| `get_featured` | Get featured marketplace items | limit |
| `get_top_rated` | Get top-rated listings | limit |
| `get_agent` | Get ERC-8004 agent information | network, agentId, assetAddress |
| `list_categories` | List all available categories | none |
| `list_networks` | List supported blockchain networks | none |
| `list_agents` | List all registered ERC-8004 agents | network, limit, offset |

## Management Tools (Phase 2 + 2.5 - PAT First)

Manage your x402 endpoints and products through authenticated MCP tools. Use `accessToken` with a scoped `sgl_pat_*` token for owner-wide automation. Legacy endpoint keys in the `x402_*` format remain supported where noted.

| Tool | Description | Parameters | Auth |
|------|-------------|------------|------|
| `get_endpoint_details` | Full endpoint info including credit balance | slug, accessToken or apiKey | `mcp:read` |
| `get_endpoint_stats` | Usage analytics (requests, revenue, success rate) | slug, accessToken or apiKey (optional) | `mcp:read` if PAT is used |
| `list_my_endpoints` | List endpoints in owner scope, with safe fallback to endpoint-only scope | accessToken or apiKey | `mcp:read` |
| `update_endpoint` | Update allowlisted endpoint fields, pricing, listing flags, and webhook settings | slug, accessToken or apiKey, allowlisted fields | `mcp:endpoints:write` |
| `list_my_products` | List products in owner scope | accessToken or apiKey | `mcp:read` |
| `update_product` | Update allowlisted product metadata, pricing, branding, and listing state | id or slug, accessToken or apiKey, allowlisted fields | `mcp:products:write` |
| `set_webhook` | Set/update webhook URL, returns signing secret | slug, webhookUrl, accessToken or apiKey | `mcp:endpoints:write` |
| `remove_webhook` | Remove webhook from endpoint | slug, accessToken or apiKey | `mcp:endpoints:write` |
| `delete_endpoint` | Permanently delete endpoint | slug, accessToken or apiKey, confirm | `mcp:endpoints:write` |

## Phase 3 Payment Tools

MCP can now request payment challenges and complete endpoint creation, endpoint top-up, public product purchase, and public credit-pack purchase flows. Consumer purchase tools wrap the existing public purchase contracts only and do not act as a generic paid endpoint proxy.

| Tool | Description | Parameters | Auth |
|------|-------------|------------|------|
| `request_endpoint_creation_payment` | Request the x402 challenge needed to create a new agent endpoint | accessToken, slug, name, originUrl, walletAddress, chain, endpoint config | `mcp:endpoints:write` |
| `create_endpoint_with_payment` | Create the endpoint after a paying client returns an `X-Payment` payload | accessToken, endpoint config, paymentPayload | `mcp:endpoints:write` |
| `request_endpoint_topup_payment` | Request the x402 challenge to add credits to an existing agent endpoint | slug, topupAmount, accessToken or apiKey | `mcp:endpoints:write` or legacy `X-API-Key` |
| `topup_endpoint_with_payment` | Complete an endpoint top-up after the paying client returns an `X-Payment` payload | slug, topupAmount, paymentPayload, accessToken or apiKey | `mcp:endpoints:write` or legacy `X-API-Key` |
| `request_product_purchase_payment` | Request the x402 challenge for a public product purchase | productIdOrSlug, clientReferenceId, metadata | none |
| `purchase_product_with_payment` | Complete a public product purchase after the paying client returns an `X-Payment` payload | productIdOrSlug, paymentPayload, clientReferenceId, metadata | none |
| `request_endpoint_credit_purchase_payment` | Request the x402 challenge for a public endpoint credit-pack purchase | slug, walletAddress, clientReferenceId, metadata | none |
| `purchase_endpoint_credits_with_payment` | Complete a public endpoint credit-pack purchase after the paying client returns an `X-Payment` payload | slug, paymentPayload, walletAddress, clientReferenceId, metadata | none |

> Security note: PATs and legacy endpoint keys are passed per-request and never stored by the MCP server. Production PATs use `sgl_pat_*`, production keys use `x402_*`, legacy `sk_*` keys remain accepted, and older agent-created endpoints without a linked dashboard user stay intentionally constrained to endpoint-only scope.
>
> Contract note: product tools only wrap `/p/:slug-or-id` and credit purchase tools only wrap `/e/:slug?action=purchase`. Some current credit endpoints still include `purchase_url` and `credit_package` with an informational `Missing x-wallet-address header` field because that is the current upstream worker contract.

## Available Resources

| URI | Description |
|-----|-------------|
| `singularity://featured` | Featured marketplace listings |
| `singularity://top-rated` | Top rated listings |
| `singularity://categories` | Available categories |
| `singularity://networks` | Supported blockchain networks |
| `singularity://agents` | All registered ERC-8004 agents |
| `singularity://listing/{slug}` | Individual listing details |
| `singularity://agent/{network}/{id}` | Agent details by network and ID |

## Usage Examples

### Browse Marketplace

```json
{
  "name": "browse_marketplace",
  "arguments": {
    "category": "ai",
    "sort": "rating",
    "limit": 10
  }
}
```

### Get Endpoint Details

```json
{
    "name": "get_endpoint_details",
  "arguments": {
    "slug": "my-api-endpoint",
    "accessToken": "sgl_pat_your_token_here"
  }
}
```

### Set Webhook

```json
{
    "name": "set_webhook",
  "arguments": {
    "slug": "my-api-endpoint",
    "webhookUrl": "https://my-server.com/webhook",
    "accessToken": "sgl_pat_your_token_here"
  }
}
```

### Get ERC-8004 Agent

```json
{
  "name": "get_agent",
  "arguments": {
    "network": "base",
    "agentId": 1
  }
}
```

## Direct API Testing

```bash
# Test MCP initialize
curl -X POST https://mcp.x402layer.cc/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'

# List all tools (should return 25)
curl -X POST https://mcp.x402layer.cc/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":2}'

# Browse marketplace
curl -X POST https://mcp.x402layer.cc/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"browse_marketplace","arguments":{"limit":5}},"id":3}'
```

## Supported Networks

| Network | Chain Type | Filter Value |
|---------|------------|--------------|
| Base | EVM | `base` |
| Ethereum | EVM | `ethereum` |
| Polygon | EVM | `polygon` |
| BNB Smart Chain | EVM | `bsc` |
| Monad | EVM | `monad` |
| Solana | Solana | `solana` |

## Server Metadata

| Property | Value |
|----------|-------|
| Runtime Name | `singularity-mcp` |
| Registry Package | `io.github.ivaavimusic/singularity` |
| Registry Title | `Singularity Layer MCP` |
| Registry Status | `active` |
| Version | `1.5.0` runtime / `1.5.0` registry package |
| Protocol Version | `2024-11-05` |
| Transport | HTTP (stateless) |
| Deployment | Cloudflare Workers |
| Total Tools | 25 (8 discovery + 9 management + 8 payment) |

## Roadmap

### Phase 1 - Marketplace Discovery
8 read-only tools for browsing listings, agents, categories, and networks.

### Phase 2 - Platform Management
5 authenticated tools for endpoint details, stats, webhooks, and deletion.

### Phase 2.5 - Extended Management
Owner-scoped endpoint and product inventory, plus allowlisted endpoint and product updates.

### Phase 2.6 - PAT-First Alignment
PAT-first docs, scoped PAT validation, and explicit scope guidance for owner-level MCP automation.

### Phase 3 - Payment Flows
Endpoint creation and top-ups, plus public product purchases and endpoint credit-pack purchases.

### Phase 4 - Agent Registry
ERC-8004 and Solana-8004 agent registration and on-chain reputation.

## Resources

- [MCP Endpoint](https://mcp.x402layer.cc)
- [MCP Registry](https://registry.modelcontextprotocol.io/?q=singularity)
- [MCP Protocol](https://modelcontextprotocol.io)
- [x402 Studio](https://studio.x402layer.cc)
