---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
provenance: hotline-enhancement-v3
---

# Hotline Enhancement v3 — Build Plan

## Objective

Enhance the Vibe Thinker Hotline with four capabilities:

1. **Calendly event type creation guidance** — Create the actual 15-min event type in Calendly (V does this in UI) with specific constraints, and wire it into the webhook
2. **Self-improving call analysis loop** — Automated analysis of calls >2min for conversation patterns and <1min for drop-off diagnosis, feeding improvements back into the system
3. **Pulse integration for hotline builds** — Dedicated Pulse skill/script for orchestrating hotline improvement builds
4. **Optional caller identification + feedback** — End-of-call flow for collecting name/feedback and a satisfaction signal

## Success Criteria

- [ ] Calendly event type spec documented with exact settings; `ZO_HOTLINE_CALENDLY_LINK` env var updated with real link
- [ ] Analysis script processes call transcripts from DuckDB, categorizes patterns, and outputs actionable insights
- [ ] Drop-off analysis identifies why calls <1min end (no transcript? confusion? wrong number?)
- [ ] Scheduled agent runs analysis weekly and emails V a hotline report
- [ ] Webhook enhanced with optional end-of-call feedback collection
- [ ] Webhook topic extraction upgraded from hardcoded "general_advisory" to LLM-classified topics

## Phases

### Wave 1: Analysis Foundation + Calendly
Build the data analysis infrastructure and prepare Calendly.

- D1.1: Call Analysis Script (extract topics, patterns, quality signals from transcripts)
- D1.2: Drop-off Analyzer (diagnose why <1min calls end, classify reasons)
- D1.3: Calendly Event Type Spec + Webhook Wiring

### Wave 2: Feedback Loop + Automation
Wire analysis into ongoing improvement, add caller feedback.

- D2.1: Weekly Hotline Report Agent (scheduled analysis → email to V)
- D2.2: End-of-Call Feedback Enhancement (webhook changes for optional caller ID + satisfaction)
- D2.3: Topic Extraction Upgrade (replace hardcoded "general_advisory" with LLM classification in webhook)

## Architecture Decisions

- **Call analysis uses /zo/ask** for semantic extraction from transcripts (not regex — P22 language selection)
- **DuckDB remains the SSOT** for call data (P02)
- **Analysis outputs to `Knowledge/zo-hotline/analysis/`** for pattern accumulation
- **Weekly report is a scheduled agent**, not a cron job — fits existing N5 patterns
- **Feedback is optional** — Zoseph asks once at end, accepts "no" gracefully
