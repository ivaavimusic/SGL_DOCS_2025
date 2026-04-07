# Webhooks and Payment Genuineness Verification

Use this reference when the user asks to configure seller webhooks, inspect events, debug delivery failures, or verify payment authenticity.

## Setup

Configure a webhook for an endpoint:

```bash
python {baseDir}/scripts/manage_webhook.py set <slug> <https_webhook_url>
```

Inspect/remove:

```bash
python {baseDir}/scripts/manage_webhook.py info <slug>
python {baseDir}/scripts/manage_webhook.py remove <slug>
```

Important: when a webhook is set or rotated, save the returned `signing_secret` immediately.

## Seller Webhook Headers

x402 Studio seller webhooks are HMAC-signed. Expect these headers on current deliveries:

- `X-X402-Signature`
- `X-X402-Timestamp`
- `X-X402-Event`
- `X-X402-Event-Id`

Event types currently include:

- `payment.succeeded`
- `credits.depleted`
- `credits.low`
- `credits.recharged`

## Signature Verification Model

Verification model:

- payload to sign: `<timestamp>.<raw_request_body>`
- algorithm: `HMAC-SHA256`
- secret: the webhook `signing_secret`

Python snippet:

```python
import hashlib
import hmac

def verify(secret: str, timestamp: str, raw_body: bytes, received_sig: str) -> bool:
    payload = timestamp.encode() + b"." + raw_body
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received_sig)
```

Do not parse and re-serialize JSON before hashing. Use the raw request body bytes.

## Backward Compatibility Warning

Some older receivers may still accept legacy raw-secret headers such as:

- `x-x402layer-secret`
- `x-x402-secret`
- `Authorization: Bearer <secret>`

That legacy model is not enough for current Studio seller webhook deliveries. Use signed webhook verification first and keep raw-secret-header fallback only if older clients still depend on it.

## Two Secret Hops

Do not confuse these two different secrets:

### 1) Studio → seller webhook receiver

- sender: x402 Studio
- secret: webhook `signing_secret`
- auth model: HMAC verification using the signed headers above

### 2) Seller webhook receiver → app settlement route

- sender: your own receiver / worker
- secret: your app-internal shared secret
- repo-specific example: worker sends `x-x402-secret`, app verifies with `X402_WEBHOOK_SECRET`

The Studio webhook signing secret is not the same thing as the app settlement secret.

## Secret Rotation Runbook

If webhook deliveries suddenly return `401` after previously working:

1. verify whether the Studio webhook `signing_secret` was rotated or drifted
2. rotate the webhook secret in Studio if needed
3. copy the newly returned `signing_secret` immediately
4. update the receiving worker/server to the exact new value
5. test again with one small payment

## Log Expectations

For debugging, it is safe and useful to log the presence or parsed values of:

- `x-x402-signature`
- `x-x402-timestamp`
- `x-x402-event`
- `x-x402-event-id`

Do not:

- log the signing secret itself
- log full signed payloads if they contain sensitive metadata unless that is absolutely necessary for a short-lived debug session

## Common Failure Mode

If Studio shows webhook delivery `401`, and a direct manual POST with the stored secret succeeds against the receiver, the receiver likely supports only legacy raw-secret auth while Studio is sending signed webhooks.

That mismatch is the first thing to check before blaming network or payload shape issues.

## Receipt Verification (PyJWT/JWKS)

For stronger authenticity checks, verify the receipt JWT (RS256/JWKS):

```bash
python {baseDir}/scripts/verify_webhook_payment.py \
  --body-file ./webhook.json \
  --signature 't=1700000000,v1=<hex>' \
  --secret '<YOUR_SIGNING_SECRET>' \
  --required-source-slug my-api \
  --require-receipt
```

Dependencies (already in `requirements.txt`):

```bash
pip install pyjwt[crypto] cryptography
```

## Cross-check Rules

When a receipt is present, compare:

- payload `data.tx_hash` == receipt `tx_hash`
- payload `data.source_slug` == receipt `source_slug`
- payload `data.amount` == receipt `amount`

Reject the request when:

- signature verification fails
- receipt is invalid or missing when required
- event fields and receipt fields do not match

## Minimal Test Flow

When integrating seller webhooks:

1. confirm whether the sender is Studio-signed or legacy raw-secret only
2. implement HMAC verification if Studio is the sender
3. keep legacy raw-secret fallback only if an older client still needs it
4. verify the exact secret source:
   - Studio webhook `signing_secret`
   - app settlement secret
5. test with:
   - one direct manual POST
   - one real Studio payment delivery
6. confirm the purchase row transitions from `pending` to `settled`
