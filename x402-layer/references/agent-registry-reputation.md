# Agent Registry and Reputation (ERC-8004 / Solana-8004)

Use this reference when the user asks to register an agent on-chain or submit on-chain feedback/reputation.

## Registration

Script:

```bash
python {baseDir}/scripts/register_agent.py \
  "Agent Name" \
  "Agent description" \
  "https://api.example.com/agent" \
  --network baseSepolia
```

Supported networks:

- `base`, `baseSepolia`
- `ethereum`, `ethereumSepolia`
- `polygon`, `polygonAmoy`
- `bsc`, `bscTestnet`
- `monad`, `monadTestnet`
- `solanaMainnet`, `solanaDevnet`

Auth variables used by worker-backed routes:

- `WORKER_REGISTRATION_API_KEY`
- `X402_API_BASE` (optional override)

## Reputation Feedback

EVM feedback example:

```bash
python {baseDir}/scripts/submit_feedback.py \
  --network base \
  --agent-id 123 \
  --rating 5 \
  --comment "High quality responses"
```

Solana feedback example:

```bash
python {baseDir}/scripts/submit_feedback.py \
  --network solanaMainnet \
  --asset-address <SOLANA_ASSET_ADDRESS> \
  --rating 4 \
  --comment "Reliable execution"
```

Auth variables:

- `WORKER_FEEDBACK_API_KEY`
- `X402_API_BASE` (optional override)

## Operational Notes

- Use the same network domain for registration and feedback whenever possible.
- Handle duplicate/exists responses gracefully for idempotent registration flows.
- Preserve on-chain identifiers (`agent_id` or `asset_address`) in your agent metadata store for future feedback calls.
