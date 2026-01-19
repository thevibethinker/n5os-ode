---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_K8CGjHBpHa9kAFAY
build_type: code_build
---

# Build: Voice Optimization Loop

**Slug:** `voice-optimization-loop`  
**Orchestrator Thread:** `[voice-optimization-loop] ORCH: Orchestrator`  
**Status:** Workers Ready  
**Started:** 2026-01-18  

---

## Overview

Build the feedback loop that learns from V's edits to Zo-generated content. When V improves a draft, Zo should:
1. Capture the before/after pair
2. Analyze what changed (semantic diff)
3. Extract actionable lessons
4. Store to semantic memory (scoped by content type)
5. Make lessons available to Writer persona
6. Sync existing voice primitives to semantic memory

---

## Wave Structure

```
Wave 1: Foundation (2 parallel workers)
├── W1.1: Capture Infrastructure — DB schema, capture script
└── W1.2: Primitives to Memory — Sync existing 419 primitives to semantic memory

Wave 2: Analysis (1 worker, depends on W1.1)
└── W2.1: Diff + Lesson Extraction — Semantic diff, lesson extraction

Wave 3: Integration (2 parallel workers, depends on W2.1)
├── W3.1: Storage Integration — Lessons → semantic memory + voice library
└── W3.2: Writer Integration — Retrieval script, prompt update
```

---

## Workers

| ID | Title | Wave | Depends On | Status |
|----|-------|------|------------|--------|
| W1.1 | Capture Infrastructure | 1 | — | Ready |
| W1.2 | Primitives to Memory | 1 | — | Ready |
| W2.1 | Diff + Lesson Extraction | 2 | W1.1 | Waiting |
| W3.1 | Storage Integration | 3 | W2.1 | Waiting |
| W3.2 | Writer Integration | 3 | W2.1 | Waiting |

---

## Execution Log

| Time | Event |
|------|-------|
| 2026-01-18 14:25 | Build initialized, Wave 1 briefs ready |

---

## How to Execute

1. **Launch Wave 1:** Open two new threads, paste W1.1 and W1.2 briefs
2. **Return here** when both complete (they'll write to `completions/`)
3. **I'll read completions** and prep Wave 2
4. Repeat until all waves done
5. **Final commit** by orchestrator

---

## Notes

- Workers do NOT commit — orchestrator commits atomically at end
- All output paths are in PLAN.md
- Worker briefs are in `workers/`
