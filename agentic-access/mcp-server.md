# Singularity MCP Server

MCP (Model Context Protocol) server for AI agents to browse and discover Singularity Marketplace APIs, products, and ERC-8004 agents.

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) is a standardized protocol for connecting AI assistants to external systems. It provides a unified way for AI models to access tools, resources, and prompts from external services.

The Singularity MCP Server exposes the x402 Singularity Marketplace through this protocol, allowing any MCP-compatible AI (Claude, Cursor, etc.) to discover and interact with marketplace listings.

## Endpoint

```bash
# MCP HTTP Endpoint
https://mcp.x402layer.cc/mcp

# Alternative Cloudflare Worker URL
https://sgl-mcp.ivaavimusicproductions.workers.dev/mcp
```

## Client Configuration

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "singularity-marketplace": {
      "url": "https://mcp.x402layer.cc/mcp"
    }
  }
}
```

### Cursor IDE

Add to your Cursor MCP settings:

```json
{
  "mcp": {
    "servers": {
      "singularity-marketplace": {
        "url": "https://mcp.x402layer.cc/mcp",
        "transport": "http"
      }
    }
  }
}
```

### Windsurf / Other MCP Clients

Configure the HTTP transport endpoint:

```bash
# HTTP Transport URL
https://mcp.x402layer.cc/mcp

# Protocol: HTTP (stateless)
# Transport: Streamable HTTP
```

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `browse_marketplace` | Search/filter listings with pagination | type, category, chain, mode, search, sort, minRating, limit, offset |
| `get_listing` | Get detailed info for a specific listing | slug |
| `get_featured` | Get featured marketplace items | limit |
| `get_top_rated` | Get top-rated listings | limit |
| `get_agent` | Get ERC-8004 agent information | network, agentId, assetAddress |
| `list_categories` | Get all available categories | none |
| `list_networks` | Get supported networks | none |
| `list_agents` | List all registered ERC-8004 agents | network, limit, offset |

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

### Get Specific Listing

```json
// Tool call: get_listing
{
  "name": "get_listing",
  "arguments": {
    "slug": "weather-api"
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

# Browse marketplace
curl -X POST https://mcp.x402layer.cc/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"browse_marketplace","arguments":{"limit":5}},"id":2}'
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
| Name | `singularity-marketplace-mcp` |
| Version | `1.0.0` |
| Protocol Version | `2024-11-05` |
| Transport | HTTP (stateless) |
| Deployment | Cloudflare Workers |

## Future Phases

### Phase 2 - Consumer Tools (Planned)
Wallet-authenticated tools for payments, credit consumption, and product purchases.

### Phase 3 - Provider Tools (Planned)
Endpoint creation, management, and marketplace listing tools.

### Phase 4 - Agent Registry (Planned)
ERC-8004 and Solana-8004 agent registration and on-chain reputation.

## Resources

- [MCP Endpoint](https://mcp.x402layer.cc) - mcp.x402layer.cc
- [GitHub Repository](https://github.com/ivaavimusic/SGL-MCP) - ivaavimusic/SGL-MCP
- [MCP Protocol](https://modelcontextprotocol.io) - Model Context Protocol Docs
- [x402 Studio](https://studio.x402layer.cc) - Dashboard & Marketplace
