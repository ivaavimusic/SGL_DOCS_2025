# x402 Singularity Layer Documentation

<p align="center">
  <img src="./assets/SGL_logo.webp" alt="x402 Singularity Layer" width="300" />
</p>

<p align="center">
  <a href="https://www.clawhub.ai/ivaavimusic/x402-layer">
    <img src="https://img.shields.io/badge/ClawdHub_Skill-Install_Now-orange?style=for-the-badge&logo=box&logoColor=white" alt="ClawdHub Skill" />
  </a>
  <br/>
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge" alt="Version 1.0.0" />
  <img src="https://img.shields.io/badge/Network-Base-0052FF?style=for-the-badge&logo=base&logoColor=white" alt="Network: Base" />
  <img src="https://img.shields.io/badge/Network-Solana-9945FF?style=for-the-badge&logo=solana&logoColor=white" alt="Network: Solana" />
</p>

<p align="center">
  <strong>Internet's unified commerce layer for Homo-Agentic economy.</strong><br/>
  Powered by <a href="https://ehlabs.xyz">EventHorizon Labs</a>
</p>

---

## Overview

Welcome to the official documentation for **x402 Singularity Layer (SGL)**. This repository contains guides, API references, and architectural details for integrating with the x402 ecosystem.

**x402 Studio** is the primary tool for developers to create, manage, and monitor their endpoints. Use the Studio to generate API keys, configure payments, and view analytics.

[**Launch x402 Studio**](https://studio.x402layer.cc)

## Documentation Structure

Our documentation is organized into the following sections:

### 📘 [User Guide](./user-guide)
For developers and creators getting started with x402.
- **Getting Started**: Initial setup and concepts.
- **Creating Endpoints**: How to deploy your first monetized endpoint.
- **Wallet Connection**: Managing identities and payments.

### 🤖 [Agentic Access](./agentic-access)
Technical details for AI agents and programmatic access.
- **Introduction**: How agents interact with the protocol.
- **Pay-Per-Request**: Direct 402 payment flow with EIP-712.
- **Credit-Based Access**: High-speed credit consumption.
- **Marketplace API**: Service discovery protocol.
- **Agent Management**: Programmatic endpoint control.
- **OpenClaw Skill**: Production-ready skill for OpenClaw agents.

### ⚡ [OpenClaw x402-Layer Skill](./agentic-access/openclaw-skill.mdx)
Production-ready skill for [OpenClaw](https://x.com/openclaw) agents with 10 Python scripts:

| Script | Purpose |
|--------|---------|
| `pay_base.py` | Pay for endpoints on Base (100% reliable) |
| `pay_solana.py` | Pay for endpoints on Solana (with retry) |
| `consume_credits.py` | Use pre-purchased credits (fastest) |
| `check_credits.py` | Check your credit balance |
| `recharge_credits.py` | Buy credit packs (Consumer) |
| `topup_endpoint.py` | Add credits to YOUR endpoint (Provider) |
| `create_endpoint.py` | Deploy new monetized endpoint ($5) |
| `manage_endpoint.py` | View/update your endpoints |
| `discover_marketplace.py` | Browse available services |
| `list_on_marketplace.py` | Publish endpoint publicly |

## Core Concepts

- **Endpoints**: Monetizable APIs or assets protected by x402.
- **Agents**: AI entities capable of rigorous commerce.
- **Payment Facilitator**: The transparent middleware handling crypto transitions.

## Contributing

We welcome contributions! Please open an issue or submit a pull request for any improvements.

---

<p align="center">
  <img src="./assets/SGL_logo.webp" alt="x402 Icon" width="40" />
</p>
<p align="center">
  © 2025 EventHorizon Labs. All rights reserved.
</p>
