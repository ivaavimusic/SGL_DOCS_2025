# SGL Grid — Provide Compute (Run a Node)

Become a **grid node operator**: serve confidential, OpenAI-compatible inference from your own
TEE-capable machine and earn **USDC + SGL** on every settled job. This is the *provider* side of
the grid (the consumer side — calling inference — is in the main SKILL under "SGL Grid — Inference").

Everything here is agent-runnable: the installer and the `sgl` CLI are plain shell commands. The
only step that needs an on-chain wallet transaction is **staking** (see Step 1), which is itself
agentic via the staking API / the `x402-layer` skill.

Node software (open source): `https://github.com/Singularity-Layer/sgl-network-node`

---

## Requirements (check before starting)

- **A TEE-capable machine.** A supported Trusted Execution Environment is mandatory — it's what lets
  the node serve prompts it cannot read. Examples: Apple Secure Enclave (`apple_se`), Intel TDX/SGX,
  AMD SEV-SNP, AWS Nitro.
- **Compute for the model** you'll serve — CPU/RAM (+ GPU/Metal where available). 3B-class models run
  on modest hardware; larger models need more.
- **≥ 50,000 $SGL staked** to your operator wallet (the minimum to register a compute node; the live
  figure is shown in the staking app). Non-custodial, withdrawable after a cooldown.
- **A Solana wallet** holding the stake — the node is bound to it.
- **Local inference runtime** `llama.cpp` (`brew install llama.cpp`) and a **GGUF model file**.
- Reliable power + network (uptime = job matching; honest downtime is never penalized).

---

## Step 1 — Stake $SGL (bond the operator wallet)

Stake at least the minimum (**50,000 SGL**) to the wallet you'll run the node under. Staking is
non-custodial and **only slashable for proven tampering — never for honest downtime**.

Agentic options:
- Use the **`x402-layer` skill** (staking module) or the **Staking Engine API**
  (`docs.x402layer.cc/staking` · API reference under "Staking Engine") to stake programmatically.
- Or stake in the app: `https://staking.x402layer.cc`.

Token: `$SGL` mint `5c4HyD2rSShqnTsf5z3SaoD2H3GE452u2CUuYjviBAGS` (Solana). Full model (tiers,
cooldowns, rewards, slashing) → `https://docs.x402layer.cc/staking/introduction`.

---

## Step 2 — Install the node CLI + runtime

```bash
# 1. Install the sgl node CLI (Singularity-Layer/sgl-network-node release)
curl -sSf https://grid.x402compute.cc/install.sh | sh

# 2. Local inference runtime
brew install llama.cpp            # macOS; see repo README for Linux

# 3. A GGUF model to serve, e.g.
#    ~/models/Llama-3.2-3B-Instruct-Q4_K_M.gguf

sgl --help                        # verify install
```

---

## Step 3 — Register the node (bind to the staked wallet)

Agentic / headless (no browser) — recommended for agents:

```bash
sgl init --wallet <STAKED_WALLET> --tee-type apple_se --models llama-3.2-3b
```

Interactive (browser approval) alternative:

```bash
sgl login --tee-type apple_se --models llama-3.2-3b
```

- `--wallet` — the Solana wallet holding your stake (required for `init`).
- `--tee-type` — TEE on this machine (default `apple_se`).
- `--models` — comma-separated model names you'll advertise.

---

## Step 4 — Attest the enclave

Only **attestation-verified** nodes receive jobs. Re-run after any binary update.

```bash
sgl attest
```

---

## Step 5 — Serve

Production (background service — survives reboots, logout, crashes, idle sleep):

```bash
sgl service install \
  --model-path ~/models/Llama-3.2-3B-Instruct-Q4_K_M.gguf \
  --model-name llama-3.2-3b \
  --resource-percent 50
```

Foreground test first (optional):

```bash
sgl start --model-path ~/models/Llama-3.2-3B-Instruct-Q4_K_M.gguf --model-name llama-3.2-3b
```

Verify it's live:

```bash
sgl status            # node + hardware + orchestrator connection
sgl service status    # background-service state
curl https://grid.x402compute.cc/grid/capacity   # your node should raise active_nodes / models
```

The node now registers, advertises its model(s), heartbeats, and starts receiving jobs.

---

## Maintenance & lifecycle

```bash
sgl off-grid          # planned downtime: stop NEW jobs cleanly (in-flight finish, no penalty)
sgl on-grid           # resume receiving jobs
```

- After updating the binary, re-run `sgl attest`.
- **Slashing is narrow:** only proven tampering with confidential-compute results is slashable.
  Honest downtime/maintenance is never slashed — it just means no new jobs while offline.

---

## CLI quick reference

| Command | Purpose |
|---|---|
| `sgl init --wallet <W>` | Register headless under a staked wallet (agentic) |
| `sgl login` | Register via browser approval |
| `sgl attest` | Submit hardware attestation (required before jobs; re-run after updates) |
| `sgl start` | Run in foreground (test) |
| `sgl service install` | Run as managed OS service (production) |
| `sgl service stop` / `service status` | Manage the background service |
| `sgl status` | Node + hardware + orchestrator status |
| `sgl off-grid` / `on-grid` | Maintenance mode toggle |

`sgl start` / `sgl service install` flags: `--model-path`, `--model-name`, `--resource-percent`
(1–100 preset), `--threads`, `--gpu-layers`, `--context-size`, `--max-jobs`, `--inference-port`
(default 8081), `--heartbeat-interval` (default 5s).

---

## Earnings

Operators earn a share of every settled job in **USDC + SGL**. Payout/claim details:
`https://docs.x402layer.cc/cloud/provide/earnings`. Reward split is 80/5/10/5 (node/stakers/team/burn);
see the staking rewards docs.

## Docs

- Setup: `https://docs.x402layer.cc/cloud/provide/node-setup`
- Requirements: `https://docs.x402layer.cc/cloud/provide/requirements`
- CLI reference: `https://docs.x402layer.cc/cloud/provide/cli`
- Staking to operate: `https://docs.x402layer.cc/cloud/provide/staking`
- Node repo: `https://github.com/Singularity-Layer/sgl-network-node`
