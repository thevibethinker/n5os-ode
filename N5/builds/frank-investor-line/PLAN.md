---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: frank-investor-line
---

# Frank Investor Line v2 — Build Plan

## Objective
Upgrade the existing Vapi-powered phone line ("Frank") from a general-purpose voice assistant into an investor-focused intelligence system that:
1. **Speaks in V's voice** — third-person cadence, voice primitives, no marketing fluff
2. **Tracks every question** — DuckDB schema for caller questions, auto-generated prefab answers
3. **Delivers sentiment-rich recaps** — post-call emails with sentiment, concerns, follow-ups
4. **Detects investor vs. user callers** — mode switching that tailors tone and content

## Current State
- `Skills/vapi/` — working webhook + CLI on port 4242 (`vapi-webhook` service)
- `Datasets/vapi-calls/data.duckdb` — single `calls` table (id, phone_number, direction, timestamps, summary, transcript, cost, raw_data)
- `Skills/vapi/assets/zo-101-briefing.md` — static knowledge base loaded into Frank's system prompt
- System prompt is generic: "You are Assistant, V's assistant" — no investor differentiation
- Recap emails are basic markdown with transcript dump, no analysis

## Architecture Decisions
- **DuckDB stays** as the datastore (no migration to SQLite/Postgres — small scale, analytical queries, already in place)
- **Question extraction via /zo/ask** — LLM semantic extraction, not regex (P38: semantic over syntactic)
- **Prefab answers auto-generate** after a question is asked ≥3 times — LLM generates answer from briefing
- **Sentiment analysis via /zo/ask** — structured JSON output for grading, concerns, follow-ups
- **No new services** — all changes are within existing `webhook.ts` and new helper modules in `Skills/vapi/scripts/`

## Phase 1: Foundation (Parallel — no cross-dependencies)

**Drop D1.1: Briefing Rewrite + FAQ Foundation** `[manual]` `[Stream 1]`
- Rewrite `zo-101-briefing.md` in V's third-person investor voice
- Structure as: Thesis → Why It Matters → What V Built → How to Get Started → Investor FAQ
- Inject 3-5 voice primitives from V's documented patterns
- Add structured FAQ section (seed 8-10 common investor questions with natural answers)
- Sensitive questions (valuation, cap table) redirect to "book a call with V"
- Output: Updated `Skills/vapi/assets/zo-101-briefing.md`

**Drop D1.2: Question Tracking Schema + Extraction Logic** `[auto]` `[Stream 2]`
- Add DuckDB tables: `call_questions` (per-question rows with category, answer_quality, normalized form) and `prefab_answers` (auto-generated FAQ entries)
- Build `extractQuestions()` — post-call LLM extraction via `/zo/ask` that parses transcript into structured questions
- Build `generatePrefabAnswer()` — triggers when a normalized question reaches ≥3 occurrences
- Build `getPrefabAnswers()` — returns formatted FAQ section for prompt injection
- Fire-and-forget pattern: extraction runs after `insertCall()`, doesn't block
- Add `calls.analysis` JSON column for storing structured analysis data
- Output: Schema migration script + helper functions in `Skills/vapi/scripts/question-tracker.ts`

## Phase 2: Intelligence Layer (Depends on Phase 1 outputs)

**Drop D2.1: Sentiment + Insight Recap Emails** `[auto]` `[Stream 1]` `[depends: D1.2]`
- Replace basic `sendRecapEmail()` with intelligence-grade analysis
- Call `/zo/ask` with structured output for: sentiment (1-10), grade (A-F), top concerns, follow-up actions, interest level
- Build rich email template: Call Details → Sentiment & Grade → Key Concerns → Follow-Up Actions → Question Summary → Full Transcript
- Pull question data from `call_questions` table for the question summary section
- Store analysis JSON in `calls.analysis` column
- Graceful fallback to basic email if LLM analysis fails
- Output: Updated `sendRecapEmail()` in `webhook.ts`

**Drop D2.2: Persona Tuning + Investor vs. User Mode** `[auto]` `[Stream 2]` `[depends: D1.1]`
- Add mode detection to Frank's opening: "Are you calling as an investor or a Zo user?"
- Store mode in new `calls.caller_mode` column (INVESTOR/USER/UNKNOWN)
- In investor mode: load refreshed briefing + prefab FAQ, speak third-person, use voice primitives
- In user mode: practical second-person tone, skip investor context
- Inject `getPrefabAnswers()` output into system prompt as "Investor FAQ" section
- Pass caller mode through to recap email (D2.1)
- Output: Updated assistant-request handler in `webhook.ts`, mode migration, runbook doc

## Phase 3: Validation (Depends on all Phase 2 outputs)

**Drop D3.1: Integration Test + Runbook** `[manual]` `[Stream 1]` `[depends: D2.1, D2.2]`
- Simulate end-to-end call flow: intake → question extraction → prefab generation → sentiment recap
- Verify all schema objects exist and migrations are idempotent
- Verify mode switching stores correctly and appears in recap
- Produce runbook covering: voice protocol, question tracking workflow, prefab maintenance, recap oversight, troubleshooting
- Produce post-mortem with test results and future work ideas
- Output: `artifacts/runbook.md`, `artifacts/post-mortem.md`, `Skills/vapi/assets/runbook-inventory.md`

## Open Questions
- [x] Keep DuckDB or migrate? → **Keep DuckDB** (small scale, analytical, already in place)
- [x] New service or extend existing? → **Extend existing** webhook.ts on port 4242
- [ ] Should Frank's opening always ask investor/user, or only for unknown numbers?
- [ ] Should prefab answers require V's approval before injecting, or auto-inject immediately?
- [ ] What's the max number of prefab answers to inject into the system prompt before truncating?
- [ ] Should the recap email go to V only, or also to a shared inbox for team review?
- [ ] Which ElevenLabs voice ID should be used for the investor persona, or keep the same voice?
- [ ] Should we add a DuckDB dashboard (zo.space page) for question analytics in a follow-up build?

## Success Criteria
- [ ] Briefing reflects V's voice + investor thesis + voice primitives
- [ ] Database tracks questions; prefab answers spawn after ≥3 occurrences; "needs context" flags set when responses weak
- [ ] Recap email contains sentiment, insights, top questions, prefab references
- [ ] Frank asks "Investor vs. user?" and tailors tone accordingly while staying third-person in investor mode
- [ ] All changes captured in `Skills/vapi/`, with no new services or ports
- [ ] Runbook documents the full system for future tuning

## Risk Notes
- **Prompt size**: Briefing + prefab FAQ + call history could exceed context window. D2.2 should monitor prompt length and truncate prefabs if needed.
- **LLM latency**: Question extraction and sentiment analysis add post-call processing time. Fire-and-forget pattern (D1.2) mitigates this for call flow; recap email (D2.1) may take a few extra seconds.
- **Voice primitive drift**: Manual D1.1 ensures V reviews the tone before it goes live.
