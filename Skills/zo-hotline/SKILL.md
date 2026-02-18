---
name: zo-hotline
description: Vibe Thinker Hotline — voice AI advisor for Zo Computer. Features Zoseph, a concise and characterful voice assistant with latency-optimized delivery, plus self-improving daily analysis.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: 3.0
  updated: 2026-02-14
---

# Vibe Thinker Hotline — Zoseph

Voice AI hotline for Zo Computer featuring "Zoseph" — a direct, personality-driven advisor who uses vibe thinking principles to help callers get unstuck.

## Overview

The Vibe Thinker Hotline provides:
- Concise, to-the-point AI productivity advice
- Vibe thinking protocol (expand → synthesize → threshold → crystallize)
- Level-appropriate recommendations for Zo usage
- Escalation to V for hands-on help
- Zero access to caller data or systems (read-only advisory)

**Phone:** +1 (857) 317-8492

## Setup

### Environment Variables

Set in [Settings → Advanced](/?t=settings&s=advanced):

| Variable | Required | Value |
|----------|----------|-------|
| `VAPI_API_KEY` | ✅ | Vapi Private API Key |
| `VAPI_HOTLINE_SECRET` | ⚠️ Recommended | Webhook auth secret — must match VAPI dashboard Bearer Token credential |
| `ZOSEPH_VERBOSITY` | Default: `terse` | `terse`, `normal`, or `detailed` |
| `VAPI_HOTLINE_PORT` | Default: `4243` | Webhook server port |

### Service

Registered as Zo user service `zo-hotline-webhook` on port 4243.

**Service ID:** `svc_EMlC6VztSCo`
**Public URL:** https://zo-hotline-webhook-va.zocomputer.io

## Architecture

- **scripts/hotline-webhook.ts** — Bun HTTP server handling VAPI webhooks, call logging, feedback collection
- **scripts/call_analysis_loop.py** — Daily LLM-powered analysis of call patterns, drop-offs, and caller insights
- **scripts/dropoff_analyzer.py** — LLM-powered classification of short/abandoned calls
- **scripts/call_analyzer.py** — Standalone call analytics and reporting
- **prompts/zoseph-system-prompt.md** — System prompt for Zoseph persona
- **config/hotline-assistant.json** — Reference configuration (webhook is source of truth)
- **IMPROVEMENT_PLAN.md** — Implementation plan and technical decisions

## Features

### Latency Optimization
- Smart endpointing with Deepgram transcriber
- ElevenLabs eleven_flash_v2_5 model (~75ms)
- Chunk streaming with 20-char minimum
- 0.3s response delay (reduced from 0.5s)
- Backchanneling enabled for natural conversation

### Verbosity Control
Set `ZOSEPH_VERBOSITY` environment variable:
- `terse` (default): 1-2 sentences max
- `normal`: 2-4 sentences
- `detailed`: Full explanations

### Zo/Zoho Disambiguation
Transcriber keyword boosting ensures "Zo" is recognized correctly instead of "Zoho".

### Voice Personality
ElevenLabs settings tuned for expressiveness:
- Stability: 0.45 (more variation)
- Style: 0.65 (more expressive)
- Voice: Custom (DwwuoY7Uz8AP8zrY5TAo)

## Usage

Callers reach the hotline and interact with Zoseph who:
1. Asks what they're working on (vibe thinking: expand)
2. Confirms understanding (synthesize)
3. Checks if enough context to advise (threshold)
4. Gives specific, actionable recommendations (crystallize)
5. Escalates to V when hands-on help is needed

### Self-Improving Call Analysis (v3)

A daily analysis loop studies call data and generates actionable insights using LLM semantic analysis (no regex heuristics).

**Scheduled Agent:** Runs daily at 6pm ET, covers previous day's conversations.

**What it does:**
1. **Substantive call analysis** (>2 min) — Extracts conversation patterns, topic frequency, satisfaction trends
2. **Drop-off diagnosis** (<1 min) — LLM classifies why callers hung up early (confusion, wrong number, technical issue, etc.)
3. **Caller profile building** — Extracts caller identity signals from transcripts (name, role, experience level, interests) and merges into `caller_insights`
4. **Caller insights** — Tracks returning callers by first name, merges topic history, averages satisfaction scores
5. **Zo team executive summary** — LLM-generated daily briefing with sections for Product team, GTM team, and Founders
6. **Daily report** — Writes markdown report to `Skills/zo-hotline/analysis/` and stores structured data in `daily_analysis` table

**Data tables:** `daily_analysis`, `caller_insights`, `feedback` (see `Datasets/zo-hotline-calls/schema.yaml`)

**Manual run:**
```bash
python3 Skills/zo-hotline/scripts/call_analysis_loop.py          # full run
python3 Skills/zo-hotline/scripts/call_analysis_loop.py --dry-run # preview only
python3 Skills/zo-hotline/scripts/dropoff_analyzer.py --dry-run   # drop-off analysis only
```

## Pulse Build Workflow

Future hotline improvement cycles can be orchestrated through Pulse. A template script pre-populates standard drops for the analyze-improve-deploy pattern.

### Starting a Hotline Improvement Build

```bash
python3 Skills/zo-hotline/scripts/hotline_build_init.py "description of improvement"
python3 Skills/zo-hotline/scripts/hotline_build_init.py "reduce greeting latency" --dry-run
```

### Standard Drops (Pre-populated)

| Drop | Name | Wave | Dependencies |
|------|------|------|-------------|
| D1.1 | Call Data Analysis Review | W1 | — |
| D1.2 | Improvement Identification | W1 | — |
| D2.1 | Implementation | W2 | D1.1, D1.2 |
| D2.2 | Testing & Validation | W2 | D2.1 |
| D2.3 | Deploy & Verify | W2 | D2.2 |

### Execution

```bash
# Check what's ready
python3 Skills/pulse/scripts/pulse_cc.py execute hotline-<slug>

# After completing a drop
python3 Skills/pulse/scripts/pulse_cc.py deposit hotline-<slug> D1.1 --status complete --summary "..."

# Finalize when done
python3 Skills/pulse/scripts/pulse_cc.py finalize hotline-<slug>
```

## Security Boundaries

- **Webhook authentication** via `X-Vapi-Secret` header (requires `VAPI_HOTLINE_SECRET` env var + VAPI dashboard credential)
- **Notification relay sanitization** — all `/zo/ask` calls use hardcoded SYSTEM NOTIFICATION RELAY framing that prevents prompt injection
- **Message length limiting** — notifications capped at 500 characters
- No Zo API access (beyond sanitized SMS relay)
- No caller data storage (except anonymous call logs)
- No system modification capability
- Pure advisory guidance only