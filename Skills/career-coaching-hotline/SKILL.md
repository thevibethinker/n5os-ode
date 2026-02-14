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
  port: 8848
  database: Datasets/career-hotline-calls/data.duckdb
---

## Quick Start

```bash
bun Skills/career-coaching-hotline/scripts/hotline-webhook.ts
```

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `CAREER_HOTLINE_VOICE_ID` | Yes | ElevenLabs voice ID |
| `VAPI_API_KEY` | Yes | Shared VAPI API key |
| `CAREER_HOTLINE_SECRET` | Yes | Webhook auth secret (set in VAPI dashboard) |
| `ZO_CLIENT_IDENTITY_TOKEN` | Yes | For /zo/ask SMS relay |
| `CAREER_HOTLINE_PORT` | No | Server port (default: 8848) |
| `CAREER_HOTLINE_BOOKING_LINK` | No | Careerspan booking URL |
| `CAREER_HOTLINE_VERBOSITY` | No | terse/normal/detailed (default: normal) |

## Architecture

Same webhook pattern as `Skills/zo-hotline/`:
- `assistant-request` → Returns full assistant config (prompt, voice, tools, transcriber)
- `tool-calls` → Executes career coaching tools
- `end-of-call-report` → Logs call to DuckDB, sends SMS to V

## Tools

| Tool | Purpose |
|------|---------|
| `assessCareerStage` | Process diagnostic answers → career stage + pain points |
| `getCareerRecommendations` | Stage-appropriate next steps and actions |
| `explainCareerConcept` | Pull career concepts from knowledge base |
| `requestCareerSession` | Book Careerspan coaching session |
| `lookupCaller` | Check phone number against Fillout intake form |
| `collectFeedback` | End-of-call feedback collection |

## Knowledge Base

26 files in `Knowledge/career-coaching-hotline/` organized by topic:
- `00-*` Philosophy
- `10-*` Resume
- `20-*` Cover Letters
- `30-*` LinkedIn
- `40-*` Job Search
- `50-*` Self Development
- `60-*` Assessment
- `70-*` Careerspan
- `80-*` Podcast Interviews

Concept resolution uses `concept-map.json` for fuzzy matching.

## Database

DuckDB at `Datasets/career-hotline-calls/data.duckdb`:
- `calls` — Call logs with duration, topics, stage
- `escalations` — Careerspan session requests
- `feedback` — End-of-call ratings
- `caller_lookup` — Fillout form submissions by phone
- `caller_insights` — Returning caller tracking

## CLI

```bash
bun Skills/career-coaching-hotline/scripts/call-logger.ts health
bun Skills/career-coaching-hotline/scripts/call-logger.ts analytics 30
bun Skills/career-coaching-hotline/scripts/call-logger.ts escalations
```
