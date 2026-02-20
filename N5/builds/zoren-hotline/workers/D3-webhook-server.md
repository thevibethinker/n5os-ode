---
created: 2026-02-20
last_edited: 2026-02-20
version: 1.0
provenance: con_gFL5uhApy1RZtlSJ
drop_id: D3
title: Webhook Server (Zoputer-Deployable)
status: pending
dependencies: [D1, D2]
---

# D3: Webhook Server

## Objective
Clone and adapt `hotline-webhook.ts` for Zøren. Must be deployable as a service on Zoputer.

## Inputs
- `Skills/zo-hotline/scripts/hotline-webhook.ts` (2384 lines — Zoseph webhook)
- D2 output (Zøren system prompt)
- D1 output (knowledge base path)

## Outputs
- `Skills/zoren-hotline/scripts/hotline-webhook.ts`
- `Skills/zoren-hotline/scripts/call-logger.ts`
- Supporting scripts
- `Skills/zoren-hotline/SKILL.md`

## Key Changes from Zoseph
- Knowledge base path: `Knowledge/foundermaxxing-hotline/`
- System prompt: `Skills/zoren-hotline/prompts/zoren-system-prompt.md`
- Caller profile DB: local to Zoputer deployment
- Identity resolution: phone → Stripe customer → email → Airtable member record
- Application state tracking in Airtable (prospect → applicant → approved → member)
- Stripe webhook handler for `checkout.session.completed` → member activation
- New AgentMail inbox for follow-up emails
- Adapted post-call follow-up for FounderMaxxing context
- Phone number collection validation (Stripe checkout phone matches caller)

## Deployment Notes
- Service runs on Zoputer, not V's Zo
- Port: TBD (check port registry on Zoputer)
- ENV vars needed: VAPI_HOTLINE_SECRET, ANTHROPIC_API_KEY, AGENTMAIL_API_KEY, STRIPE_SECRET_KEY, AIRTABLE_API_KEY

## Acceptance Criteria
- [ ] Server starts and handles VAPI webhook events
- [ ] Caller profiles stored and retrieved
- [ ] Stripe identity resolution working
- [ ] Airtable member status checked on incoming calls
- [ ] Post-call follow-up sends via AgentMail
- [ ] Application pathway creates Airtable records
- [ ] No references to V's primary Zo in code
