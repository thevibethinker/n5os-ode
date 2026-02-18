---
created: 2026-02-17
last_edited: 2026-02-18
version: 2
provenance: con_D22Ewo8OGuQrMBrx
spawn_mode: manual
status: pending
---
# D1: Webhook Infrastructure Upgrades

## Objective
Upgrade the Zo Hotline webhook with caller intelligence, knowledge retrieval optimization, call quality flagging, and latency improvements. This is the "make the plumbing smart" drop.

## Scope

### 1. Caller Profile System (Per-User Tracking)
- Create `caller_profiles` table in DuckDB:
  - phone_hash (SHA256 of phone — no raw PII stored)
  - first_name (if volunteered via feedback)
  - call_count, first_call_at, last_call_at
  - topics_discussed (cumulative, deduplicated)
  - level_assessed (most recent)
  - avg_satisfaction
  - preferred_style (terse/normal/detailed — inferred or stated)
  - notes (freeform, from standout analysis)
- On `assistant-request`: lookup caller by phone hash, inject context into system prompt:
  "Returning caller (3rd call). Previously interested in meeting intelligence. Rated 4/5 last time. Level 2."
- On `end-of-call-report`: update profile with new data

### 2. Knowledge Index Generation
- Generate `Knowledge/zo-hotline/00-knowledge-index.md` — a lightweight file listing every knowledge section with 1-line summaries
- Format: `| concept-key | file | 1-line summary |`
- The `explainConcept` tool reads this index FIRST to decide which file to fetch
- Reduces hallucination risk (Zoseph knows what it has before claiming knowledge)
- Script: `N5/scripts/generate_zo_knowledge_index.py` (runs on demand + via freshness agent)

### 3. Standout Call Flagging
- In end-of-call handler, add flag check (no LLM cost):
  - Duration < 30 seconds → flag: `dropped`
  - Duration > 5 minutes → flag: `high_engagement`
  - Satisfaction ≤ 2 → flag: `negative_feedback`
  - Escalation requested → flag: `escalation`
  - Repeat caller (3rd+ call) → flag: `returning`
- If ANY flag fires → trigger `/zo/ask` quick analysis:
  - Input: transcript excerpt + flag type
  - Output: 3-sentence "call spotlight"
  - Stored in `call_spotlights` table (call_id, flags, spotlight_text, created_at)
- Daily digest pulls spotlights into a "Notable Calls" section

### 4. Messaging Effectiveness Hooks
- Log which knowledge files were consulted per call (already partially done via tool-call logging)
- Add structured logging: `{call_id, tools_used: [{name, concept, file_path}], duration, satisfaction}`
- Daily analysis loop enhancement: extract Zoseph's approach per call from transcript, correlate with outcomes
- Surface in daily digest: "Messaging that landed" vs "Messaging that missed"

### 5. Latency Optimization (Original D1 Scope)
- Audit system prompt size (currently 1,925 words / 12.5KB)
- Trim without losing behavior — target 30% reduction
- Optimize VAPI config (endpointing, chunk plan, wait times)
- Profile Python subprocess overhead for DuckDB tool calls
- Benchmark before/after time-to-first-word

## Key Files
- `Skills/zo-hotline/scripts/hotline-webhook.ts` (main changes)
- `Skills/zo-hotline/prompts/zoseph-system-prompt.md` (trim)
- `Skills/zo-hotline/config/hotline-assistant.json` (reference update)
- `Knowledge/zo-hotline/00-knowledge-index.md` (new)
- `N5/scripts/generate_zo_knowledge_index.py` (new)

## Dependencies
- D5 complete (knowledge base must exist before indexing it) ✅

## Acceptance Criteria
- [ ] Caller profiles created and populated on calls
- [ ] Returning callers get personalized context in system prompt
- [ ] Knowledge index generated and integrated into explainConcept
- [ ] Standout call flagging operational (test with <30s and >5min calls)
- [ ] Messaging hooks logging tool usage per call
- [ ] System prompt measurably shorter
- [ ] Latency benchmarked before/after
