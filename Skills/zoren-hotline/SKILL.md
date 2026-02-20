---
name: zoren-hotline
description: The Vibe Pill Hotline — Zøren voice AI concierge for V's AI workshop for founders. Handles inbound calls with 4 pathways (intake/screening, member support, FAQ, co-building), identity resolution (phone → Stripe → Airtable), membership application tracking, and post-call follow-up via AgentMail. Deployed on Zoputer.
compatibility: Created for Zo Computer (Zoputer deployment)
metadata:
  author: va.zo.computer
  version: 1.0
  updated: 2026-02-20
  brand: The Vibe Pill
  concierge: Zøren
  phone: (415) 340-8017
---

# Vibe Pill Hotline — Zøren v1

Voice AI hotline for The Vibe Pill community featuring "Zøren" — a direct, personality-driven concierge who routes callers through tailored pathways based on their intent and membership status.

## Overview

The Vibe Pill Hotline provides:
- **4 caller pathways**: Intake/Screening, Member Support, FAQ, Co-Building
- **Master Pattern**: Elicit → Mirror → Layer → Anchor
- **Identity resolution**: Phone → DuckDB → Airtable → Stripe lookup chain
- **Membership screening**: Conversational assessment for loyalty, engagement, and passion signals
- **Application pipeline**: Automatic Airtable record creation for qualified applicants
- **Stripe integration**: Payment link texting, checkout webhook for member activation
- **Post-call follow-up**: SMS via Zoputer, email via AgentMail (zoren@agentmail.to)
- **Call analytics**: DuckDB storage with pathway/outcome tracking
- **V notifications**: Real-time SMS alerts for call summaries, escalations, new members

**Phone:** (415) 340-8017
**AgentMail:** zoren@agentmail.to
**Deployment:** Zoputer (not V's primary Zo)

## Setup

### Environment Variables

Set on Zoputer in [Settings → Advanced](/?t=settings&s=advanced):

| Variable | Required | Value |
|----------|----------|-------|
| `VAPI_HOTLINE_SECRET` | ⚠️ Recommended | Webhook auth secret — must match VAPI dashboard |
| `ANTHROPIC_API_KEY` | ✅ | Anthropic API key (for Claude Haiku 4.5) |
| `AGENTMAIL_API_KEY` | ✅ | AgentMail API key for zoren@agentmail.to |
| `AIRTABLE_API_KEY` | ✅ | Airtable Personal Access Token |
| `STRIPE_SECRET_KEY` | ✅ | Stripe secret key for identity resolution |
| `ZOPUTER_API_KEY` | ✅ | Zoputer API key for SMS relay and notifications |
| `VAPI_VOICE_ID` | Default: `DwwuoY7Uz8AP8zrY5TAo` | ElevenLabs voice ID |
| `PORT` | Default: `4250` | Webhook server port |

### Service Registration

Register as a Zoputer user service:

```bash
# Check port registry first, then register
register_user_service(
  label="vibe-pill-hotline",
  protocol="http",
  local_port=4250,
  entrypoint="bun Skills/zoren-hotline/scripts/hotline-webhook.ts"
)
```

### Stripe Webhook

Configure in Stripe Dashboard → Webhooks:
- Endpoint URL: `https://<zoputer-service-url>/stripe`
- Events: `checkout.session.completed`
- Payment Links must have phone number collection enabled

## Architecture

### Scripts

- **scripts/hotline-webhook.ts** — Bun HTTP server: VAPI webhooks, Stripe webhooks, Airtable integration, identity resolution, call logging
- **scripts/call-logger.ts** — Call logging utilities and CLI analytics

### Knowledge Base (`Knowledge/vibe-pill-hotline/`)

| Folder | Contents |
|--------|----------|
| `00-knowledge-index.md` | Lookup table for explainConcept tool |
| `10-40` | Meta-OS framework (levels 1-3, V's tactics) |
| `50-use-case-inspiration/` | Community use cases, competitive landscape |
| `55-vibe-pill/` | Program overview, pricing, methodology, screening criteria |
| `60-assessment/` | Diagnostic questions and scoring |
| `70-architectural-patterns/` | Webhook, dataset, email pipeline patterns |
| `90-technical-advice/` | Rules vs personas, debugging agents |
| `95-v-projects/` | V's published projects |
| `96-zo-platform/` | Platform docs |
| `97-conversational-playbook/` | Pathways, proven phrases, messaging |

### System Prompt

`prompts/zoren-system-prompt.md` — Zøren persona, 4 pathways, voice rules, screening criteria, emotional detection, payment link sharing.

### Data Storage

- **DuckDB**: `Datasets/vibe-pill-calls/data.duckdb` — calls, member_profiles, applications, escalations, feedback, daily_analysis
- **Airtable**: Base `app4RseEJNYVUnH28` — Community Members (tblgEHq5Rk3C8SAA2), Calls (tblxf3kFkCDHRjsNr), Applications (tbl0yejg8syGjVRmh)

## Identity Resolution Flow

```
Inbound call → Phone number extracted
  ↓
DuckDB member_profiles lookup (phone)
  ↓
Airtable Community Members lookup (phone)
  ↓ (if no match)
Stripe customer search (phone)
  ↓
Merge results → MemberProfile
  ↓
Inject caller context into system prompt
```

## Membership State Machine

```
prospect → applicant → approved → member
                                    ↓
                                  churned
```

- **prospect**: First-time caller, unknown
- **applicant**: Qualified via screening, application created in Airtable
- **approved**: V approved the application
- **member**: Stripe checkout completed, fully activated
- **churned**: Subscription canceled

## API Endpoints

- `GET /` — Health check (text)
- `GET /health` — Health check (JSON)
- `POST /` — VAPI webhook (assistant-request, tool-calls, end-of-call-report, status-update)
- `POST /stripe` — Stripe webhook (checkout.session.completed)

## Caller Pathways

### Intake/Screening (Primary)
Conversational screen for 3 signals: loyalty (long-term thinking), engagement (collaborative energy), passion (genuine AI curiosity). Qualified callers get application created automatically.

### Member Support
Identity-resolved members greeted by name. Handles onboarding, build troubleshooting, session questions, account issues.

### FAQ
Direct answers about The Vibe Pill program, pricing (Founding 15 $100/mo, Standard $300/mo, Zo-to-Zo $150/mo), session format, V's background.

### Co-Building
Senior technical advisor mode. Elicit → Mirror → Layer → Anchor. Technical calibration (1-5), layered solutions.

## VAPI Debugging Protocol

**Read the Zoseph reference for the 3 known killers before editing:**
1. Keywords with spaces → VAPI silently rejects
2. Deepgram features on wrong model
3. analysisPlan nested format → use FLAT format

**Post-deploy verification:**
```bash
curl -s -X POST http://localhost:4250 \
  -H "Content-Type: application/json" \
  -d '{"message":{"type":"assistant-request","call":{"customer":{"number":"+15551234567"}}}}' \
  | python3 -c "import json,sys;d=json.load(sys.stdin);kw=d.get('assistant',{}).get('transcriber',{}).get('keywords',[]);bad=[k for k in kw if ' ' in k.split(':')[0]];print(f'Keywords: {len(kw)}, bad: {len(bad)}');ap=d.get('assistant',{}).get('analysisPlan',{});print('Format:','FLAT (ok)' if 'summaryPrompt' in ap else 'NESTED (bad)' if 'summaryPlan' in ap else 'missing')"
```
