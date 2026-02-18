---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
build_slug: career-hotline-monetization
---

# Plan: Career Coaching Hotline — Zozie Rename + Prepaid Credits Monetization

## Objective

Transform the Career Coaching Hotline from a free V-branded prototype to a monetizable Zozie-branded service with prepaid credit-based access. Three workstreams:

1. **WS1 — Zozie Identity**: Rename AI persona from "V" to "Zozie" (Z-O-Z-I-E), a female AI career coach modeled after V
2. **WS2 — Credit System**: Implement prepaid minute-pack monetization via Stripe, with 15 min free tier per phone number
3. **WS3 — Gating Logic**: Wire credit balance checks into the VAPI webhook so calls are gated by available minutes

## Open Questions

- [x] Pricing: $15/30min, $30/60min, $50/120min — **CONFIRMED**
- [x] Free tier: 15 min lifetime per phone number — **CONFIRMED**
- [ ] Landing/pricing page location — V will provide later (no blocker)

## Success Criteria

- [ ] System prompt says "Zozie" everywhere, no "V" self-references
- [ ] Webhook firstMessage, voicemailMessage, name all say Zozie
- [ ] V referenced only as founder/human coach for escalations
- [ ] Stripe products + payment links created for 3 tiers
- [ ] `caller_balances` table tracks minutes per phone number
- [ ] Stripe webhook on zo.space credits minutes on purchase
- [ ] VAPI webhook checks balance on assistant-request, gates if exhausted
- [ ] Zozie tells caller to buy more time when balance is zero
- [ ] End-of-call deducts actual minutes used from balance
- [ ] Integration tests updated and passing

## Phases

### Wave 1: Identity + Infrastructure (Parallel)

**Drops:**
- D1.1: Zozie system prompt rename — update system prompt, firstMessage, voicemailMessage, assistant name, all V→Zozie self-references. V stays as human founder for escalation. ⚡ PARALLEL
- D1.2: Stripe products + payment links — create 3 Stripe products (Starter 30m/$15, Standard 60m/$30, Deep Dive 120m/$50) with payment links. ⚡ PARALLEL
- D1.3: DuckDB schema — add `caller_balances` table (phone_number, total_minutes, used_minutes, free_tier_used, last_purchase), add `purchases` table for Stripe transaction log. ⚡ PARALLEL

**Gate:** All 3 drops complete. Stripe payment links live. DB schema in place.

### Wave 2: Credit Logic (Sequential)

**Drops:**
- D2.1: Stripe webhook on zo.space — API route at `/api/career-hotline-stripe` that receives checkout.session.completed events, extracts phone number + minutes purchased, credits the `caller_balances` table
- D2.2: Balance gating in VAPI webhook — on assistant-request, look up caller phone number, check balance (including 15 min free tier), gate call or proceed. On end-of-call-report, deduct actual minutes used. When balance exhausted mid-awareness, Zozie advises buying more time.

**Gate:** Full credit lifecycle works: purchase → credit → call → deduct.

### Wave 3: Testing + Polish

**Drops:**
- D3.1: Integration tests — update existing test suite with credit system tests (free tier, purchase, deduction, gating, Zozie identity verification)
- D3.2: Service restart + smoke test — restart the career-coaching-hotline service, verify health, run full integration suite

**Gate:** All tests passing. Service running.

## Affected Files

**Modified:**
- `N5/builds/career-coaching-hotline/artifacts/career-coach-system-prompt.md` — Zozie rename
- `Skills/career-coaching-hotline/scripts/hotline-webhook.ts` — balance gating + deduction + Zozie name
- `Skills/career-coaching-hotline/tests/integration-tests.ts` — new credit tests

**Created:**
- zo.space route: `/api/career-hotline-stripe` — Stripe webhook
- DuckDB tables: `caller_balances`, `purchases`

## Risks

- **Stripe webhook reliability**: Mitigated by idempotent event processing + event ID deduplication
- **Phone number format mismatch**: Mitigated by normalizing to E.164 in both webhook and VAPI
- **Mid-call cutoff**: NOT implementing hard cutoff — Zozie gets awareness of low balance but doesn't hang up
- **Free tier gaming**: Acceptable risk for now — phone numbers are reasonably unique identifiers
