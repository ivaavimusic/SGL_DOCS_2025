# Agent Pods API — `/pods/v1` (API-key surface)

The endpoints in `agent-pods.md` are the **dashboard's** surface: they expect a wallet
signature or a compute session, which is right for a human at a browser and awkward for a
program. `/pods/v1` is the same product behind **one API key**, meant for building on top of
pods rather than clicking them.

Use this reference when the caller holds an `x402c_…` key and no wallet. Use `agent-pods.md`
when signing with OWS.

- **Base:** `https://compute.x402layer.cc/pods/v1`
- **Auth:** `X-API-Key: x402c_…` on every route
- **Mint a key:** dashboard → Settings → API Keys

---

## Two rules that will cost you if you skip them

**Create is idempotent and the header is required.** `POST /pods` refuses without
`Idempotency-Key`, because the call provisions a machine and charges for it. Replaying the
same key returns the original response byte for byte instead of making a second pod; the same
key with a *different* body is a `409` with `details.code = idempotency_mismatch`, since that
is a bug in the caller and swallowing it would hide it.

Use an id you already have — an order number, a job id. A generated UUID protects a retry
inside one process; only a stable id protects a retry after that process dies.

**Delete is not instant.**

| Response | Meaning |
|---|---|
| `200` `destroyed` | the machine is confirmed gone |
| `202` `destroying` | accepted, provider would not delete yet, **may bill a few minutes more** |

A provider refuses to remove a machine that is still installing. Treating `202` as done is how
a pod keeps billing after you thought you deleted it. Poll `GET /pods/{id}` until `destroyed`.

---

## Create, then talk to it

```bash
POD=$(curl -s -X POST https://compute.x402layer.cc/pods/v1/pods \
  -H "X-API-Key: $SGL_API_KEY" \
  -H "Idempotency-Key: order-4471" \
  -H 'content-type: application/json' \
  -d '{"tier":"starter","name":"support agent","external_ref":"customer-42"}' | jq -r .pod.id)

# Booting takes a few minutes. status goes provisioning -> online.
curl -s "https://compute.x402layer.cc/pods/v1/pods/$POD" -H "X-API-Key: $SGL_API_KEY" | jq -r .pod.status
```

`external_ref` is **your** id. It comes back on every read and filters `GET /pods`, so you can
find a pod again from your own database without storing ours.

Once `online`, mint a pod key and use any OpenAI client. The model id is **`agent-pod`**:

```bash
KEY=$(curl -s -X POST "https://compute.x402layer.cc/pods/v1/pods/$POD/keys" \
  -H "X-API-Key: $SGL_API_KEY" -H 'content-type: application/json' -d '{}' | jq -r .key.secret)

curl -s -X POST "https://compute.x402layer.cc/pods/$POD/v1/chat/completions" \
  -H "Authorization: Bearer $KEY" -H 'content-type: application/json' \
  -d '{"model":"agent-pod","messages":[{"role":"user","content":"summarise today"}]}'
```

Streaming works (`"stream": true`, SSE). The pod key is returned **once**; it is not the same
thing as the account key and cannot manage pods.

---

## Routes

| Method | Path | Notes |
|---|---|---|
| `POST` | `/pods` | `Idempotency-Key` required. `201`, `status: provisioning` |
| `GET` | `/pods` | Newest first. `?external_ref=`, `?cursor=`, `?limit=` |
| `GET` `PATCH` `DELETE` | `/pods/{id}` | PATCH: `name`, `model`, `slug`, `auto_renew` |
| `POST` `GET` | `/pods/{id}/keys` | Pod endpoint keys; secret shown once |
| `DELETE` | `/pods/{id}/keys/{keyId}` | Takes effect immediately |
| `GET` | `/pods/{id}/usage` | AI spend and token counts |
| `POST` `GET` | `/pods/{id}/actions` | `restart`, `stop`, `redeploy`, `update`, `diagnose`, `logs` |
| `GET` `POST` | `/pods/{id}/tasks` | Scheduled tasks |
| `PATCH` `DELETE` | `/pods/{id}/tasks/{jobId}` | |
| `GET` `PATCH` | `/pods/{id}/wallet` | Cap field is `per_tx_cap_usd` |
| `GET` `PATCH` | `/pods/{id}/updates` | Who decides when this pod takes our updates |
| `POST` | `/pods/{id}/wallet/send` | Move funds. Needs `pods:wallet:write` |
| `POST` | `/pods/{id}/wallet/x402/pay` | Pay an x402 endpoint from the pod wallet |
| `GET` `POST` `DELETE` | `/pods/{id}/connectors` | MCP connectors |
| `GET` `PATCH` | `/pods/{id}/backups` | |
| `POST` | `/pods/{id}/chat-ticket` | Ticket for the streaming socket |
| `POST` `GET` | `/pods/{id}/channels/telegram/join-code` | POST mints, GET polls |
| `POST` | `/pods/{id}/channels/telegram/connect` | Attaches the group that claimed the code |
| `POST` | `/pods/{id}/channels/{channel}/pair` | Approves someone to DM the agent |
| `GET` | `/events` | Account event log, paged by `seq` |
| `POST` `GET` | `/webhooks` · `PATCH` `DELETE` `/webhooks/{id}` | |

### Actions are queued, not immediate

`POST /actions` returns **202**. The pod applies it on its next check-in, usually within a
minute. `diagnose` and `logs` write their output back through the heartbeat — read it from
`GET /actions` as `last_result`, and expect a minute or two, not a second.

Same for `tasks` and `connectors`: a `202` means the pod has been told, not that it is done.
`GET /tasks` reports what the pod itself says it has, so it lags the write by a heartbeat.

### Pairing: who may DM the agent

A stranger who finds the bot's username can DM it, and unlike a group that conversation is
private. So the agent refuses unknown people, shows them a short code, and waits. `POST
.../channels/{channel}/pair` with that `code` approves them.

The code must come from the agent, so this approves a pairing somebody already started — it
cannot add a person who never asked.

### Deciding when a pod takes an update

We ship updates to the pod's scripts, and by default a pod applies ours within six hours,
restarting its gateway for about forty seconds. That is fine for a pod you run for yourself.
It is not fine if you run pods for customers, because their agents all blink offline at a
moment you did not choose.

`PATCH /pods/{id}/updates` with `{"mode":"manual"}` and we keep answering that pod's version
poll with the version it already has, so it never updates itself. You apply the update when it
suits you:

```bash
curl -X POST ".../pods/v1/pods/$POD/actions" -H "X-API-Key: $KEY" \
  -H 'content-type: application/json' -d '{"action":"update"}'
```

`GET /pods/{id}/updates` tells you whether one is waiting, and `pod.update_available` fires in
the event log when a release arrives that a held pod has not taken.

**The hold expires after 30 days.** Security fixes ride these bundles, so a pod pinned
indefinitely stops being your scheduling choice and becomes an unpatched machine. The response
always names the date, and `hold_expired: true` says plainly when the window has passed.


---

## Scopes

Ordinary work needs `compute:read` / `compute:write`. Two powers are deliberately separate, so
a general key cannot use them:

| Scope | Grants |
|---|---|
| `pods:wallet:write` | Send from a pod wallet, pay x402 endpoints with it, raise its caps, set a backup passphrase |
| `pods:control:write` | Add/remove connectors, and a full-power control socket (pod files, skills, backups) |

Without `pods:control:write` a chat ticket is issued at **`chat`** scope: the socket accepts
conversation and nothing else. That is the intended default. Ask for the scope only when you
need the workspace, and expect a `403` naming it if you did not.

---

## Events and webhooks

**The log is the source of truth; webhooks are one way to read it.** A failed delivery is
gone, the log is not — so if you miss one, page `GET /events` and catch up.

Page by **`seq`**, never by timestamp. `seq` only goes up. Two events can share a millisecond,
and a timestamp cursor either skips one or repeats it forever.

```bash
curl -s "https://compute.x402layer.cc/pods/v1/events?after=41&limit=50" -H "X-API-Key: $SGL_API_KEY"
# { "events": [...], "next_after": 92, "has_more": true }
```

Types: `pod.created`, `pod.active`, `pod.destroyed`, `pod.destroy_failed`,
`pod.action.queued`, `pod.status.changed`, `pod.renewed`, `pod.renewal_failed`,
`pod.expiring`, `pod.backup.completed`, `pod.backup.failed`, `pod.update_available`.

### Verifying a delivery

HTTPS only. The signing secret is returned **once** at creation. Omit `event_types` for
everything; an empty array is refused, because subscribing to nothing is a webhook that
silently never fires.

```
x-sgl-signature: t=<unix>,v1=<hmac-sha256 of "<t>.<raw body>">
x-sgl-event-type: pod.status.changed
x-sgl-event-id: <uuid>
```

**Verify against the raw body.** Parsing and re-encoding JSON changes key order and spacing,
and the signature covers the bytes we sent — re-serialise and a genuine delivery will fail to
verify. Both SDKs ship a helper (`verifyPodWebhook`, `verify_pod_webhook`) that also enforces
the timestamp window; without that window, putting the timestamp inside the signature buys
nothing, because an old capture would still verify.

Failures back off (1, 5, 15, 60, 180, 360, 720 minutes) and then stop. When we give up,
`disabled_by_us_at` is set — deliberately distinct from `enabled: false`, which is you turning
it off. From the outside both look like silence.

---

## Errors and limits

```json
{ "error": { "code": "conflict", "message": "...", "details": { "code": "idempotency_mismatch" } } }
```

Branch on `code`, not the message: `invalid_request`, `unauthorized`, `forbidden`,
`not_found`, `conflict`, `limit_exceeded`, `capability_disabled`, `rate_limited`,
`not_implemented`, `internal`.

Every response carries **`x-request-id`**. Send your own and it is echoed; quote it in a
support message and it can be found in our logs.

| Limit | |
|---|---|
| Reads | 240/min per account |
| Writes | 60/min per account |
| **Creates** | **60/hour**, a separate bucket — this one provisions machines and charges |
| Body | 128 KB |
| Wallet moves | 30/hour, its own bucket |
| Webhooks | 10 per account |
| Event retention | 30 days |

---

## SDKs

Both published clients wrap this surface and are kept feature-equal:

```ts
import { PodsClient } from "@singularity-layer/grid";
const pods = new PodsClient({ apiKey: process.env.SGL_API_KEY! });
const pod = await pods.createPod({ tier: "starter", idempotencyKey: `order-${id}` });
await pods.waitForOnline(pod.id);
```

```python
from singularity_grid import PodsClient
pods = PodsClient(api_key=os.environ["SGL_API_KEY"])
pod = pods.create_pod(tier="starter", idempotency_key=f"order-{id}")
pods.wait_for_online(pod["id"])
```

`waitForDestroyed` / `wait_for_destroyed` exist for the same reason the `202` above does: they
hold until the machine is genuinely gone rather than until we accepted the request.
