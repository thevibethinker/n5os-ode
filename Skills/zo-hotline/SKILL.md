---
name: zo-hotline
description: Vibe Thinker Hotline — voice AI advisor for Zo Computer. Features Zoseph, a pathway-driven voice assistant with caller profiling, emotional detection, competitive intelligence, and self-improving daily analysis.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: 4.0
  updated: 2026-02-18
---

# Vibe Thinker Hotline — Zoseph v4

Voice AI hotline for Zo Computer featuring "Zoseph" — a direct, personality-driven advisor who routes callers through tailored pathways based on their intent and experience level.

## Overview

The Vibe Thinker Hotline provides:
- **3 caller pathways**: Explorer (new/curious), Builder (building something), Comparison (evaluating Zo vs alternatives)
- **Master Pattern**: Elicit → Mirror → Layer → Anchor across all interactions
- **Emotional detection**: Adapts tone based on caller signals (confusion, excitement, skepticism)
- **Caller profiles**: Returning callers recognized via hashed phone numbers, conversation history preserved
- **Competitive framework**: Honest concession-pivot responses for Claude, GPT, Cursor, Zapier, Notion
- **Self-improving analysis**: Daily messaging effectiveness tracking, call spotlights, pattern detection
- **98-entry knowledge index**: Voice-optimized reference files covering all Zo features, patterns, and use cases
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
| `DEEPGRAM_API_KEY` | ✅ | Deepgram transcription API key |
| `ANTHROPIC_API_KEY` | ✅ | Anthropic API key (for Claude Haiku 4.5) |

### Service

Registered as Zo user service `zo-hotline-webhook` on port 4243.

**Service ID:** `svc_EMlC6VztSCo`
**Public URL:** https://zo-hotline-webhook-va.zocomputer.io

## Architecture

- **scripts/hotline-webhook.ts** — Bun HTTP server: VAPI webhooks, caller profiles, knowledge index, call logging, spotlights, tool usage tracking
- **scripts/call_analysis_loop.py** — Daily LLM analysis: call patterns, drop-offs, messaging effectiveness, caller insights, executive summary
- **scripts/dropoff_analyzer.py** — LLM classification of short/abandoned calls
- **scripts/call_analyzer.py** — Standalone call analytics and reporting
- **prompts/zoseph-system-prompt.md** — System prompt v4.0 (2,231 words)
- **config/hotline-assistant.json** — Reference configuration (webhook is source of truth)
- **IMPROVEMENT_PLAN.md** — Full version history and technical decisions

### Knowledge Base (`Knowledge/zo-hotline/`)

| Folder | Contents |
|--------|----------|
| `00-knowledge-index.md` | 98-entry lookup table for explainConcept tool |
| `10-40` | Meta-OS framework (levels 1-3, V's tactics) |
| `50-use-case-inspiration/` | 12 community use cases, competitive landscape, gap analysis |
| `60-assessment/` | Diagnostic questions and scoring |
| `70-architectural-patterns/` | Webhook, dataset, email pipeline, persona routing patterns |
| `80-lessons-anti-patterns/` | Over-engineering, agent sprawl, skipping verification |
| `90-technical-advice/` | Rules vs personas, debugging agents, zo.space tips |
| `95-v-projects/` | N5OS Ode, Persona Optimization, Zo Substrate, etc. |
| `96-zo-platform/` | 41 voice-optimized platform docs (features, integrations, pricing) |
| `97-conversational-playbook/` | Pathways, proven phrases, danger zones, messaging cheat sheet, idealism talking points |

## Conversation Design (v4)

### Caller Pathways

**Explorer** — New/curious callers. Discovery questions → paint a specific future using one concrete use case. Lead with scheduled agents as the "aha" moment.

**Builder** — Active users building something. Technical calibration (1-5 scale), layered solutions (simple → advanced). Adapts language depth to stated level.

**Comparison** — Evaluating Zo vs alternatives. Concede competitor strengths honestly, pivot to autonomy + persistence. Idealism angle (open source, ownership) when caller shows affinity.

### Master Pattern (All Pathways)
1. **Elicit** — Pathway-specific discovery questions
2. **Mirror** — Reflect back what was heard before advising
3. **Layer** — Simple solution first, then advanced upgrade
4. **Anchor** — Paint a specific future ("Imagine tomorrow morning...")

### Emotional Detection
System prompt includes explicit instructions to detect and adapt:
- Surprise → lean in deeper
- Confusion → simplify, use analogies
- Skepticism → switch to Comparison pathway
- Overwhelm → offer the easy version
- Rapid-fire → match energy, be concise

### Additional Modes
- **Troubleshoot** — Specific errors or broken things
- **Compare** — Direct competitor comparison
- **Onboard** — First-15-minutes guided setup

## Caller Profiles

Returning callers identified via SHA-256 hashed phone numbers. Profile includes:
- Call count, first/last seen dates
- Topics discussed (deduplicated across calls)
- Assessed level (if diagnostic was run)

Injected into system prompt on `assistant-request` so Zoseph can personalize.

## Self-Improving Analysis (v4)

Daily analysis loop (6pm ET) now includes:

1. **Substantive call analysis** (>2 min) — Patterns, topics, satisfaction
2. **Drop-off diagnosis** (<1 min) — LLM classification
3. **Caller profile building** — Identity signals from transcripts
4. **Messaging effectiveness** — Correlates tool_usage.jsonl with call outcomes (which approaches → longer calls, higher satisfaction)
5. **Call spotlights** — Flags notable calls (returning callers, escalations, long calls, negative feedback)
6. **Executive summary** — Product / GTM / Founders sections

**Data tables:** `calls`, `escalations`, `feedback`, `daily_analysis`, `caller_insights`, `caller_profiles`, `call_spotlights`

## Latency Optimization

- Deepgram transcriber with 22 keyword boosts (Zo, competitors, concepts)
- ElevenLabs eleven_flash_v2_5 (~75ms)
- Chunk streaming: 20-char minimum
- Smart endpointing: 0.1s on punctuation, 0.8s without
- Silence timeout: 10s (reduced from 15s)
- Backchanneling enabled

## Security Boundaries

- Webhook authentication via `X-Vapi-Secret` header
- Notification relay sanitization (hardcoded framing prevents prompt injection)
- Message length limiting (500 chars)
- Phone numbers hashed (SHA-256), never stored in plaintext
- No Zo API access beyond sanitized SMS relay
- No caller data or system access — pure advisory