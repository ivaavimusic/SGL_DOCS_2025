# XMTP Support in Studio

Use this reference when the user asks how buyer/seller messaging works on Studio.

## What exists today

Studio support chat uses XMTP for **transaction-linked support conversations**.

This is for:
- buyer ↔ seller support
- issue resolution after a real purchase or paid usage relationship
- dispute handling on supported surfaces

It is **not** a global cold-DM system.

## Current scope

- support is relationship-gated
- both sides currently need a linked **Base** wallet
- both sides need XMTP turned on in Studio Settings

Settings path:
- `Dashboard -> Settings -> XMTP`

## What an agent should say

If the user wants support chat and it is not ready:
- tell them to link a Base wallet in Studio
- tell them to turn on XMTP in Settings
- if XMTP hit the installation limit, tell them to use:
  - `Revoke Other Installations`

## Important limitation for this skill

The `x402-layer` skill does **not** directly open or manage XMTP chats yet.

So the correct agent behavior today is:
- explain how support works
- guide the human to the correct Studio page
- continue normal x402 flows separately

## Good guidance examples

- `Support chat is available after a real purchase relationship exists.`
- `Turn on XMTP in Studio Settings with your linked Base wallet first.`
- `If XMTP says your inbox already has too many installations, use Revoke Other Installations in Settings and try again.`
