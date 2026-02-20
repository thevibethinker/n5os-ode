---
created: 2026-02-20
last_edited: 2026-02-20
version: 1.0
provenance: con_gFL5uhApy1RZtlSJ
drop_id: D5
title: VAPI Assistant Configuration
status: pending
dependencies: [D2, D3]
---

# D5: VAPI Assistant Configuration

## Objective
Set up new VAPI assistant for Zøren with the new SF Twilio number.

## Inputs
- Zøren system prompt (D2)
- Webhook URL from deployed service (D3)
- New Twilio phone number (V provisioning)

## Outputs
- VAPI assistant: "Zøren — FounderMaxxing"
- Twilio number → VAPI routing configured
- Tool definitions for Zøren
- Voice selection (ElevenLabs male voice)

## Needs from V
- New Twilio number
- ElevenLabs voice preference (or selection from options)
- VAPI account access (same account as Zoseph? or new?)

## Acceptance Criteria
- [ ] VAPI assistant created
- [ ] Twilio number connected
- [ ] Inbound calls route to Zøren
- [ ] All tools registered and functional
- [ ] Voice sounds authoritative, modern, male
- [ ] Test call succeeds end-to-end
