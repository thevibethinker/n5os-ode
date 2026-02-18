---
created: 2026-02-17
version: 1.0
provenance: con_3BuG4GkgO8ROXcds
spawn_mode: manual
status: pending
---
# D1: Latency Optimization

## Objective
Reduce Zoseph's time-to-first-word and overall response latency.

## Scope
- Audit and trim system prompt (target: 50% reduction without losing behavior)
- Optimize VAPI voice/endpointing config
- Reduce tool call overhead (Python subprocess for DuckDB)
- Trim recent call context injection
- Benchmark before/after

## Key Files
- Skills/zo-hotline/scripts/hotline-webhook.ts
- Skills/zo-hotline/prompts/zoseph-system-prompt.md
- Skills/zo-hotline/config/hotline-assistant.json

## Acceptance Criteria
- Measurably shorter system prompt
- Documented VAPI config changes with rationale
- Before/after latency benchmarks (if measurable)
