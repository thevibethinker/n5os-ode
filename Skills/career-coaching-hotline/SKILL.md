---
name: career-coaching-hotline
description: >
  VAPI webhook server for the Careerspan Career Coaching Hotline. Handles voice AI calls
  with career-specific tools (assessCareerStage, getCareerRecommendations, explainCareerConcept,
  requestCareerSession, lookupCaller, collectFeedback). Logs calls to DuckDB, sends SMS
  notifications, and serves as the core runtime for V's career coaching voice agent.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  build: career-coaching-hotline
  version: 1.0
  deployed: 2026-02-14
---

# Careerspan Career Coaching Hotline

Free voice AI career coaching hotline powered by VAPI, built on a decade of V's coaching expertise. Callers get personalized career guidance from an AI that speaks with V's voice, methodology, and philosophy.

**Phone:** TBD — V needs to provision in VAPI (see `references/vapi-setup.md`)

## Overview

The Career Coaching Hotline provides:
- Personalized career coaching via voice AI, using V's methodology
- Diagnostic career stage assessment (5 stages: groundwork → materials → outreach → performance → transition)
- Knowledge base access (26 files across 9 categories of career coaching content)
- Pre-call intake matching via Fillout form (caller context before they speak)
- Escalation to real Careerspan coaching sessions
- Returning caller recognition and continuity
- Zero access to caller PII or systems (read-only advisory)

## Setup

### Service

Registered as Zo user service `career-coaching-hotline` on port 8848.

**Service ID:** `svc_JKqkUI_p4bQ`
**Public URL:** https://career-coaching-hotline-va.zocomputer.io

### Environment Variables

Set in [Settings → Advanced](/?t=settings&s=advanced):

| Variable | Required | Status |
|----------|----------|--------|
| `CAREER_HOTLINE_VOICE_ID` | ✅ | Set in Zo secrets |
| `VAPI_API_KEY` | ✅ | Shared with zo-hotline |
| `CAREER_HOTLINE_SECRET` | ✅ | **V needs to create** — see `references/vapi-setup.md` |
| `ZO_CLIENT_IDENTITY_TOKEN` | ✅ | Auto-available |
| `CAREER_HOTLINE_PORT` | Default 8848 | Set in service config |
| `CAREER_HOTLINE_BOOKING_LINK` | Default: mycareerspan.com/book | Update when booking page ready |
| `CAREER_HOTLINE_VERBOSITY` | Default: normal | terse/normal/detailed |

Full checklist: `references/env-vars.md`

### V's Setup Steps (Manual)

1. **VAPI Assistant** — Create in VAPI dashboard, point webhook to service URL. Guide: `references/vapi-setup.md`
2. **Fillout Form** — Create intake form, configure webhook. Guide: `references/fillout-setup.md`
3. **Webhook Secret** — Generate and set in both VAPI + Zo secrets
4. **Phone Number** — Provision in VAPI and assign to assistant

## Architecture

```
Caller → VAPI (voice + transcription) → Webhook Server (8848)
                                              ↓
                              assistant-request → Returns full config
                              tool-calls → Executes 6 career tools
                              end-of-call-report → Logs + SMS
                                              ↓
                              DuckDB (call logs, caller data, feedback)
```

### Scripts

- **scripts/hotline-webhook.ts** — Main VAPI webhook server (904 lines). Handles assistant config, tool execution, call logging, SMS notifications.
- **scripts/intake-webhook.ts** — Fillout form webhook receiver (492 lines). Processes pre-call intake submissions, stores in DuckDB for caller matching.
- **scripts/caller-lookup.ts** — Shared module for phone number normalization and caller data lookup.
- **scripts/call-logger.ts** — CLI tool for call analytics, health checks, and escalation tracking.
- **scripts/call_analysis_loop.py** — Daily LLM-powered call analysis (planned).
- **scripts/init_db.py** — Database initialization script.

### Config

- **config/hotline-assistant.json** — Reference VAPI assistant configuration. The webhook server is the source of truth — this file is for documentation only.

### Tests

- **tests/integration-tests.ts** — Full integration test suite (51 tests, all passing).

## Tools

| Tool | Purpose |
|------|---------|
| `assessCareerStage` | Process diagnostic answers → career stage + pain points |
| `getCareerRecommendations` | Stage-appropriate next steps and actions |
| `explainCareerConcept` | Pull career concepts from knowledge base (fuzzy matching via concept-map) |
| `requestCareerSession` | Book a Careerspan coaching session (logs escalation + sends SMS) |
| `lookupCaller` | Check phone number against Fillout intake data |
| `collectFeedback` | End-of-call satisfaction rating and feedback |

Tool specifications: `N5/builds/career-coaching-hotline/artifacts/tool-specs.json`

## Knowledge Base

26 files in `Knowledge/career-coaching-hotline/` organized by topic:

| Prefix | Category | Files |
|--------|----------|-------|
| `00-*` | Philosophy | V's coaching philosophy and approach |
| `10-*` | Resume | Resume writing, ATS optimization, formatting |
| `20-*` | Cover Letters | Cover letter strategy and templates |
| `30-*` | LinkedIn | Profile optimization, networking, content |
| `40-*` | Job Search | Search strategy, applications, networking |
| `50-*` | Self Development | Career growth, skill building, mindset |
| `60-*` | Assessment | Career stage diagnostics, self-evaluation |
| `70-*` | Careerspan | Service overview, value proposition |
| `80-*` | Podcast Interviews | V's public insights and perspectives |

Concept resolution uses `N5/builds/career-coaching-hotline/artifacts/concept-map.json` for fuzzy topic matching.

## Database

DuckDB at `Datasets/career-hotline-calls/data.duckdb`:

| Table | Purpose |
|-------|---------|
| `calls` | Call logs with duration, topics, career stage, satisfaction |
| `escalations` | Careerspan session booking requests |
| `feedback` | End-of-call ratings and comments |
| `caller_lookup` | Fillout form submissions indexed by phone number |
| `caller_insights` | Returning caller tracking and merged history |
| `daily_analysis` | Daily call analysis results (planned) |

## CLI

```bash
# Health check
bun Skills/career-coaching-hotline/scripts/call-logger.ts health

# Call analytics (last N days)
bun Skills/career-coaching-hotline/scripts/call-logger.ts analytics 30

# View escalations
bun Skills/career-coaching-hotline/scripts/call-logger.ts escalations

# Run integration tests
bun Skills/career-coaching-hotline/tests/integration-tests.ts
```

## Voice Personality

ElevenLabs settings tuned for V's coaching delivery:
- Model: `eleven_flash_v2_5` (~75ms latency)
- Stability: 0.45 (more variation, more natural)
- Style: 0.65 (expressive, warm)
- Chunk streaming with 20-char minimum
- Backchanneling enabled for natural conversation flow

## Latency Optimization

- Deepgram transcriber with career-specific keyword boosting
- Smart endpointing (punctuation: 0.1s, no-punctuation: 0.8s)
- 0.1s response delay
- Chunk plan with punctuation boundaries

## Security Boundaries

- **Webhook authentication** via `X-Vapi-Secret` header (requires `CAREER_HOTLINE_SECRET`)
- **SMS notification relay** via `/zo/ask` with sanitized framing
- **Message length limiting** on notifications (500 char cap)
- No direct Zo API access beyond sanitized SMS relay
- No caller PII stored beyond anonymous call logs and voluntary intake data
- No system modification capability
- Pure advisory guidance only

## Build Provenance

Built via Pulse orchestration: `N5/builds/career-coaching-hotline/`

| Wave | Drops | Content |
|------|-------|---------|
| W1 | D1.1, D1.2 | Source extraction, knowledge base creation |
| W2 | D2.1, D2.2, D2.3 | System prompt, value prop tree, diagnostic flow |
| W3 | D3.1, D3.2, D3.3 | Webhook server, intake webhook, integration tests |
| W4 | D4.1, D4.2 | Caller lookup, DuckDB schema + test validation |
| W5 | D5.1 | Service deployment, documentation |

All 51 integration tests passing. See `N5/builds/career-coaching-hotline/artifacts/test-results.md`.
