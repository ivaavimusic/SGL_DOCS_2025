# x402Compute API Reference

Base URL: `https://compute.x402layer.cc`

## Endpoints

### GET /compute/plans

List available compute plans with pricing.

**Query Parameters:**
- `type` (optional): Filter by plan type — `vps`, `vhp`, `vdc`, `vcg` (GPU)

**Response:**
```json
{
  "plans": [
    {
      "id": "vcg-a100-1c-2g-6gb",
      "vcpu_count": 12,
      "ram": 120832,
      "disk": 1600,
      "bandwidth": 10240,
      "monthly_cost": 90,
      "type": "GPU",
      "gpu_vram_gb": 80,
      "gpu_type": "NVIDIA A100",
      "locations": ["lax", "ewr", "ord"]
    }
  ],
  "count": 1
}
```

Prices include the platform markup and are in USD. The x402 payment amount is calculated as `monthly_cost * duration_months` converted to USDC atomic units (6 decimals).

---

### GET /compute/regions

List available deployment regions.

**Response:**
```json
{
  "regions": [
    {
      "id": "lax",
      "city": "Los Angeles",
      "country": "US",
      "continent": "North America"
    }
  ]
}
```

---

### GET /compute/os

List available operating system images.

**Response:**
```json
{
  "os_options": [
    {
      "id": 2284,
      "name": "Ubuntu 24.04 LTS x64",
      "arch": "x64",
      "family": "ubuntu"
    }
  ]
}
```

---

### POST /compute/provision

Provision a new compute instance. Returns `402 Payment Required` with payment challenge.

**Request Body:**
```json
{
  "plan": "vcg-a100-1c-2g-6gb",
  "region": "lax",
  "os_id": 2284,
  "label": "my-gpu-instance",
  "duration_months": 1,
  "network": "base"
}
```

**Headers:**
- `x-wallet-address`: Your wallet address
- `X-Payment`: Base64-encoded x402 payment payload (after 402 challenge)

**402 Challenge Response:**
```json
{
  "x402Version": 1,
  "accepts": [
    {
      "scheme": "exact",
      "network": "base",
      "maxAmountRequired": "90000000",
      "resource": "https://compute.x402layer.cc/compute/provision",
      "payTo": "0x...",
      "extra": { "name": "USD Coin", "version": "2" }
    }
  ]
}
```

**Success Response (200):**
```json
{
  "success": true,
  "order": {
    "id": "uuid",
    "vultr_instance_id": "...",
    "plan": "vcg-a100-1c-2g-6gb",
    "region": "lax",
    "status": "active",
    "ip_address": "1.2.3.4",
    "expires_at": "2026-03-17T00:00:00Z"
  },
  "tx_hash": "0x..."
}
```

---

### GET /compute/instances

List your active instances.

**Query Parameters:**
- `wallet`: Your wallet address

**Headers:**
- `x-wallet-address`: Your wallet address (alternative to query param)

---

### GET /compute/instances/:id

Get details for a specific instance.

**Headers:**
- `x-wallet-address`: Your wallet address

---

### DELETE /compute/instances/:id

Destroy an instance immediately.

**Headers:**
- `x-wallet-address`: Your wallet address (must match the order's user_wallet)

---

### POST /compute/instances/:id/extend

Extend an instance's lifetime. Returns `402 Payment Required` with payment challenge.

**Request Body:**
```json
{
  "extend_hours": 720,
  "network": "base"
}
```

**Headers:**
- `x-wallet-address`: Your wallet address
- `X-Payment`: Base64-encoded x402 payment payload (after 402 challenge)
