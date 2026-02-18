# x402-compute Changelog

## [1.0.4] - 2026-02-18

### Added
- `POST /compute/instances/:id/password` one-time password fallback endpoint support
- `scripts/get_one_time_password.py` helper script

### Changed
- Kept SSH public key as default/recommended access path
- Added fallback workflow docs for non-SSH provisioning

---

## [1.0.3] - 2026-02-18

### Added
- Signed request auth headers (Base + Solana) for all management endpoints
- API key support for agent access (`create_api_key.py`)
- SSH public key provisioning (`--ssh-public-key` / `--ssh-key-file`)

### Changed
- Provisioning uses `prepaid_hours` (hours) instead of `duration_months`

### Security
- Passwords are no longer returned; SSH key access is required

---

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
