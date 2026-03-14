# Singularity MCP Server

MCP (Model Context Protocol) server for the x402 Studio platform. Browse the Singularity Marketplace, manage endpoints, configure webhooks, and interact with ERC-8004 agents across Base, Ethereum, Polygon, BSC, Monad, and Solana.

> ✅ **v1.1.0** - Phase 2 release with platform management tools

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) is a standardized protocol for connecting AI assistants to external systems. It provides a unified way for AI models to access tools, resources, and prompts from external services.

The Singularity MCP Server exposes the x402 Studio platform through this protocol, allowing any MCP-compatible AI (Claude, Cursor, etc.) to discover marketplace listings, manage endpoints, configure webhooks, and interact with on-chain agents.

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

## Discovery Tools (Phase 1 — No Auth)

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

## Management Tools (Phase 2 — API Key Auth)

Manage your x402 endpoints: view details, check stats, configure webhooks, and delete endpoints. Requires your endpoint API key (`sk_live_*` or `sk_test_*`).

| Tool | Description | Parameters | Auth |
|------|-------------|------------|------|
| `get_endpoint_details` | Full endpoint info including credit balance | slug, apiKey | 🔐 Required |
| `get_endpoint_stats` | Usage analytics (requests, revenue, success rate) | slug, apiKey (optional) | 📊 Optional |
| `set_webhook` | Set/update webhook URL, returns signing secret | slug, webhookUrl, apiKey | 🔐 Required |
| `remove_webhook` | Remove webhook from endpoint | slug, apiKey | 🔐 Required |
| `delete_endpoint` | ⚠️ Permanently delete endpoint | slug, apiKey, confirm | 🔐 Required |

> 🔒 **Security:** API keys are passed per-request and never stored or logged by the MCP server. Keys are validated to match the `sk_live_*` / `sk_test_*` format before being forwarded to the upstream API.

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
// Tool call: browse_marketplace
{
  "name": "browse_marketplace",
  "arguments": {
    "category": "ai",
    "sort": "rating",
    "limit": 10
  }
}
```

### Get Endpoint Details (Phase 2)

```json
// Tool call: get_endpoint_details
{
  "name": "get_endpoint_details",
  "arguments": {
    "slug": "my-api-endpoint",
    "apiKey": "sk_live_your_api_key_here"
  }
}
```

### Set Webhook (Phase 2)

```json
// Tool call: set_webhook
{
  "name": "set_webhook",
  "arguments": {
    "slug": "my-api-endpoint",
    "webhookUrl": "https://my-server.com/webhook",
    "apiKey": "sk_live_your_api_key_here"
  }
}

// Response includes signing secret (save it!)
{
  "success": true,
  "webhook": {
    "url": "https://my-server.com/webhook",
    "signing_secret": "whsec_abc123...",
    "note": "Save this secret — it will not be shown again"
  }
}
```

### Get ERC-8004 Agent

```json
// Tool call: get_agent (EVM)
{
  "name": "get_agent",
  "arguments": {
    "network": "base",
    "agentId": 1
  }
}

// Tool call: get_agent (Solana)
{
  "name": "get_agent",
  "arguments": {
    "network": "solana",
    "assetAddress": "AssetAddress123..."
  }
}
```

### Direct API Testing

```bash
# Test MCP initialize
curl -X POST https://mcp.x402layer.cc/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'

# List all tools (should return 13)
curl -X POST https://mcp.x402layer.cc/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":2}'

# Browse marketplace
curl -X POST https://mcp.x402layer.cc/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"browse_marketplace","arguments":{"limit":5}},"id":3}'
```

## Categories

`ai`, `data`, `finance`, `utility`, `social`, `gaming`, `education`, `study`

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
| Name | `singularity-mcp` |
| Version | `1.1.0` |
| Protocol Version | `2024-11-05` |
| Transport | HTTP (stateless) |
| Deployment | Cloudflare Workers |
| Total Tools | 13 (8 discovery + 5 management) |

## Roadmap

### Phase 1 - Marketplace Discovery ✅
8 read-only tools for browsing listings, agents, categories, and networks.

### Phase 2 - Platform Management ✅
5 authenticated tools for endpoint details, stats, webhooks, and deletion.

### Phase 2.5 - Extended Management (Planned)
Endpoint field updates, product management, and owner-wide listing tools.

### Phase 3 - Consumer Tools (Planned)
Wallet-authenticated tools for payments, credit consumption, and product purchases.

### Phase 4 - Agent Registry (Planned)
ERC-8004 and Solana-8004 agent registration and on-chain reputation.

## Resources

- [MCP Endpoint](https://mcp.x402layer.cc) - mcp.x402layer.cc
- [GitHub Repository](https://github.com/ivaavimusic/SGL-MCP) - ivaavimusic/SGL-MCP
- [MCP Protocol](https://modelcontextprotocol.io) - Model Context Protocol Docs
- [x402 Studio](https://studio.x402layer.cc) - Dashboard & Marketplace
