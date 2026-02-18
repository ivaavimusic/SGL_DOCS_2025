# x402-compute Changelog

## [1.0.1] - 2026-02-18

### Fixed
- `instance_details.py` now displays VPS credentials (root password, IPv6) when available
- Previously, the API returned `vultr_default_password` but the script wasn't showing it

### Security
- Confirmed wallet-based access control: users can only view/manage their own instances
- Instance credentials (password) are per-VPS, not Vultr account credentials

---

## [1.0.0] - 2026-02-17

### Added
- Initial release
- Provision GPU/VPS instances with USDC payment on Base or Solana
- Browse compute plans with filtering by type (GPU/VPS/High-Perf/Dedicated)
- Browse deployment regions
- List and view instance details
- Extend instance lifetime with additional payment
- Destroy instances
- Support for private key or Coinbase Agentic Wallet (AWAL) authentication
- CLI scripts for all operations
- Security guidance for wallet management
