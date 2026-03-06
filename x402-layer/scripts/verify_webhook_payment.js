#!/usr/bin/env node
/*
x402 Webhook Payment Verifier (Node + Singularity SDK)

Purpose:
- Verify webhook HMAC signature (X-X402-Signature)
- Optionally verify receipt JWT using x402sgl
- Cross-check payload fields against receipt claims

Install:
  npm install x402sgl

Usage:
  node verify_webhook_payment.js \
    --body-file ./webhook.json \
    --signature 't=1700000000,v1=<hex>' \
    --secret '<SIGNING_SECRET>' \
    --required-source-slug my-api \
    --receipt-token '<JWT>' \
    --require-receipt
*/

const crypto = require('crypto')
const fs = require('fs')

function parseArgs(argv) {
  const out = {
    bodyFile: null,
    body: null,
    signature: null,
    secret: null,
    receiptToken: null,
    requiredSourceSlug: null,
    expectedEvent: 'payment.succeeded',
    requireReceipt: false,
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--body-file') out.bodyFile = argv[++i]
    else if (arg === '--body') out.body = argv[++i]
    else if (arg === '--signature') out.signature = argv[++i]
    else if (arg === '--secret') out.secret = argv[++i]
    else if (arg === '--receipt-token') out.receiptToken = argv[++i]
    else if (arg === '--required-source-slug') out.requiredSourceSlug = argv[++i]
    else if (arg === '--expected-event') out.expectedEvent = argv[++i]
    else if (arg === '--require-receipt') out.requireReceipt = true
    else if (arg === '--help' || arg === '-h') {
      printHelp()
      process.exit(0)
    } else {
      throw new Error(`Unknown argument: ${arg}`)
    }
  }

  return out
}

function printHelp() {
  console.log(`x402 Webhook Payment Verifier

Usage:
  node verify_webhook_payment.js --body-file <path> --signature 't=...,v1=...' --secret <secret> [options]

Required:
  --body-file <path>            Path to raw webhook JSON body
  --signature <value>           X-X402-Signature header, format: t=<ts>,v1=<hex>
  --secret <secret>             Webhook signing_secret from create/manage webhook

Optional:
  --body <json>                 Raw JSON body string (instead of --body-file)
  --receipt-token <jwt>         Receipt JWT. If omitted, script tries body.data.receipt_token
  --required-source-slug <slug> Enforce source_slug when verifying receipt token
  --expected-event <event>      Default: payment.succeeded
  --require-receipt             Fail when receipt token is missing or invalid
  -h, --help                    Show this help

Install SDK:
  npm install x402sgl
`)
}

function parseSignature(headerValue) {
  if (!headerValue) {
    throw new Error('Missing --signature')
  }

  let timestamp = null
  const signatures = []

  for (const part of headerValue.split(',')) {
    const [kRaw, vRaw] = part.split('=')
    const k = (kRaw || '').trim()
    const v = (vRaw || '').trim()
    if (!k || !v) continue

    if (k === 't') timestamp = v
    if (k === 'v1') signatures.push(v)
  }

  if (!timestamp || signatures.length === 0) {
    throw new Error('Invalid --signature format. Expected: t=<timestamp>,v1=<hex>')
  }

  return { timestamp, signatures }
}

function verifyWebhookHmac(secret, timestamp, rawBody, receivedSigs) {
  const signedPayload = `${timestamp}.${rawBody}`
  const expected = crypto
    .createHmac('sha256', secret)
    .update(signedPayload, 'utf8')
    .digest('hex')

  for (const sig of receivedSigs) {
    try {
      const expectedBuf = Buffer.from(expected, 'hex')
      const sigBuf = Buffer.from(sig, 'hex')
      if (expectedBuf.length === sigBuf.length && crypto.timingSafeEqual(expectedBuf, sigBuf)) {
        return { ok: true, expected }
      }
    } catch {
      // Keep trying any additional signature candidates.
    }
  }

  return { ok: false, expected }
}

function firstDefined(...values) {
  for (const value of values) {
    if (value !== undefined && value !== null && value !== '') return value
  }
  return null
}

async function verifyReceiptToken(token, requiredSourceSlug) {
  let verifyX402ReceiptToken
  try {
    ;({ verifyX402ReceiptToken } = require('x402sgl'))
  } catch (err) {
    throw new Error('Missing dependency x402sgl. Run: npm install x402sgl')
  }

  return verifyX402ReceiptToken(token, requiredSourceSlug ? { requiredSourceSlug } : {})
}

async function main() {
  const args = parseArgs(process.argv.slice(2))

  if ((!args.bodyFile && !args.body) || !args.signature || !args.secret) {
    printHelp()
    process.exit(1)
  }

  const rawBody = args.body !== null ? args.body : fs.readFileSync(args.bodyFile, 'utf8')
  const parsedBody = JSON.parse(rawBody)

  const { timestamp, signatures } = parseSignature(args.signature)
  const hmacResult = verifyWebhookHmac(args.secret, timestamp, rawBody, signatures)

  if (!hmacResult.ok) {
    throw new Error('Invalid webhook signature')
  }

  if (args.expectedEvent && parsedBody.type !== args.expectedEvent) {
    throw new Error(`Unexpected event type. got=${parsedBody.type} expected=${args.expectedEvent}`)
  }

  const token = firstDefined(
    args.receiptToken,
    parsedBody?.data?.receipt_token,
    parsedBody?.receipt_token,
    parsedBody?.payment?.receipt_token
  )

  let receiptClaims = null
  if (token) {
    receiptClaims = await verifyReceiptToken(token, args.requiredSourceSlug)

    const payloadTx = parsedBody?.data?.tx_hash
    if (payloadTx && receiptClaims?.tx_hash && payloadTx !== receiptClaims.tx_hash) {
      throw new Error('Receipt tx_hash does not match webhook payload tx_hash')
    }

    const payloadSlug = parsedBody?.data?.source_slug
    if (payloadSlug && receiptClaims?.source_slug && payloadSlug !== receiptClaims.source_slug) {
      throw new Error('Receipt source_slug does not match webhook payload source_slug')
    }

    const payloadAmount = parsedBody?.data?.amount
    if (payloadAmount !== undefined && receiptClaims?.amount !== undefined) {
      const left = Number(payloadAmount)
      const right = Number(receiptClaims.amount)
      if (!Number.isNaN(left) && !Number.isNaN(right) && left !== right) {
        throw new Error('Receipt amount does not match webhook payload amount')
      }
    }
  } else if (args.requireReceipt) {
    throw new Error('Missing receipt token (--receipt-token or body.data.receipt_token)')
  }

  const result = {
    ok: true,
    verified: {
      webhook_signature: true,
      receipt_token: Boolean(receiptClaims),
    },
    event: parsedBody?.type || null,
    source_slug: firstDefined(parsedBody?.data?.source_slug, receiptClaims?.source_slug),
    tx_hash: firstDefined(parsedBody?.data?.tx_hash, receiptClaims?.tx_hash),
    amount: firstDefined(parsedBody?.data?.amount, receiptClaims?.amount),
    currency: firstDefined(parsedBody?.data?.currency, receiptClaims?.currency),
    receipt_claims: receiptClaims,
  }

  console.log(JSON.stringify(result, null, 2))
}

main().catch((err) => {
  console.error(JSON.stringify({ ok: false, error: err.message }, null, 2))
  process.exit(1)
})
