---
created: 2026-02-20
last_edited: 2026-02-20
build_slug: zoren-hotline
---

# Zøren Hotline — Build Status

## Overall: 6/7 Drops Complete (86%)

| Drop | Name | Status | Notes |
|------|------|--------|-------|
| D1 | Knowledge Base Fork | ✅ Complete | 102 files forked to `Knowledge/vibe-pill-hotline/`, 10 new Vibe Pill entries |
| D2 | Zøren System Prompt | ✅ Complete | 437-line prompt at `Skills/zoren-hotline/prompts/zoren-system-prompt.md` |
| D3 | Webhook Server | ✅ Complete | 2172-line server at `Skills/zoren-hotline/scripts/hotline-webhook.ts` (remediated) |
| D4 | Airtable + Stripe | ✅ Complete | Community Members expanded, Calls + Applications tables created, Stripe product configured |
| D5 | VAPI Assistant | ⏳ Blocked | **Needs V's input:** Twilio number, VAPI account, ElevenLabs voice selection |
| D6 | Call Analytics | ✅ Complete | DuckDB dataset at `Datasets/vibe-pill-calls/`, 6 tables, ingest pipeline ready |
| D7 | Landing Page Rebrand | ✅ Complete | `va.zo.space/vibe-pill` rebranded, 5 legacy routes deleted |

## D5 Blockers — What V Needs to Provide

1. **Twilio number** — Provision a San Francisco area code number (415/628), or confirm using existing number
2. **VAPI account** — Confirm VAPI API key is in Zo secrets, or provide it
3. **Voice selection** — Pick an ElevenLabs voice for Zøren (recommendation: a warm, slightly playful male voice)

Once V provides these, D5 can be completed in ~5 minutes.

## Git Branch
`feature/zoren-hotline` — 125 files committed, ready for merge after D5.
