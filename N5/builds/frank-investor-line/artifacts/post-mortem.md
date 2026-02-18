---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: pulse:frank-investor-line:D3.1
---

# Post-Mortem: frank-investor-line

## Build Summary

Upgraded the Frank voice AI hotline from a generic Zo demo line to an investor intelligence system. Five drops across three waves.

## Test Results

### Schema Verification ✅
- `calls` table: `analysis` (JSON) and `caller_mode` (VARCHAR) columns present
- `call_questions` table: exists with id, call_id, question_text, normalized_question, answer_text, answer_quality, category, extracted_at
- `prefab_answers` table: exists with id, normalized_question, answer_text, occurrence_count, auto_generated, manually_approved, created_at, updated_at
- `question_stats` table: exists (view/materialized for aggregation)

### Synthetic Call Test ✅
- Inserted test call with INVESTOR mode and 4 investor questions
- Questions stored with categories: differentiation, business_model, fundraising, roadmap
- Answer quality tracked: 2 answered, 2 redirected
- Prefab trigger threshold (3 occurrences) correctly does not fire on first occurrence

### Pipeline Verification ✅
- `extractQuestions()`: Fire-and-forget after call save — uses `/zo/ask` with structured output
- `getPrefabAnswers()`: Queries prefab_answers, formats as FAQ block for system prompt injection
- `recordCallerMode()`: Vapi tool function that stores INVESTOR/USER in calls.caller_mode
- `sendRecapEmail()`: Includes sentiment analysis, call grade, key interests, concerns, follow-ups, notable quotes, question summary, and caller mode badge (💼/👤)
- System prompt: Loads zo-101-briefing.md + prefab FAQ + mode detection prompt dynamically at call start

### Mode Switching ✅
- First message asks caller to identify as investor or user
- `recordCallerMode` tool callable by Frank during conversation
- Investor mode: third-person phrasing about V, briefing + FAQ loaded
- User mode: practical second-person tone

## What Worked Well
- Drop isolation: Each drop had a clean scope — no conflicts between D1.2 (schema) and D2.1 (recap) and D2.2 (mode switch)
- D1.2's schema work set up D2.1 and D2.2 cleanly — good dependency ordering
- Fire-and-forget pattern for question extraction avoids blocking call saves

## What to Watch
- **Prefab answers are empty until 3+ real calls with repeated questions.** This is by design but means first few investor calls won't have FAQ injection.
- **Briefing is loaded from disk at call start.** Changes to zo-101-briefing.md take effect on next call (no hot reload needed, no restart needed).
- **Prompt size**: As prefab answers grow, monitor total system prompt length. Currently well within limits.
- **Test call left in DB**: test-integration-eee8f330 is synthetic — clean up before production reporting.

## Next Steps
- [ ] Make a real test call to verify end-to-end with Vapi
- [ ] Clean up synthetic test data after validation
- [ ] Monitor first 5 real investor calls for question extraction quality
- [ ] Review auto-generated prefab answers after threshold is hit
- [ ] Consider dashboard for investor call analytics (caller mode distribution, question frequency)
