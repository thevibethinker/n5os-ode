---
created: 2025-12-10
last_edited: 2025-12-10
version: 1.0
---

# Level Upper Analysis: Worker/Orchestrator System

## Task Complexity Assessment
**Complexity:** High - 8+ related scripts, 3 different patterns, overlapping responsibilities
**Quality Target:** Unified, maintainable system with clear separation of concerns

## 25% Checkpoint: Assumptions Validated

| Assumption | Status | Evidence |
|------------|--------|----------|
| Scripts are actively used | ✓ Validated | 10+ recent WORKER_ASSIGNMENT files |
| Should share patterns | ✓ Validated | Many do similar things differently |
| Consolidation desirable | ✓ Validated | Current state has duplication |

## Current Landscape

### Worker Spawning (3 scripts, overlapping)
| Script | Purpose | LLM-First? |
|--------|---------|------------|
| `spawn_worker.py` | Core worker spawning | ✓ Yes (v2) |
| `spawn_worker_v2.py` | Duplicate of spawn_worker.py | ✓ Yes |
| `n5_launch_worker.py` | CLI wrapper with wizard | ✗ No (wraps v1) |

**Issue:** n5_launch_worker.py wraps old spawn_worker.py and doesn't use the --context flag

### Build Orchestration (2 scripts, parallel)
| Script | Purpose | Storage |
|--------|---------|---------|
| `build_orchestrator.py` | Content Library specific | JSONL |
| `build_orchestrator_v2.py` | Generic, LLM-driven | SQLite |

**Issue:** v1 is hardcoded for one project, should be deprecated

### Conversation Orchestration (3 scripts, overlapping)
| Script | Purpose | Notes |
|--------|---------|-------|
| `conversation_orchestrator.py` | Spawn + monitor workers | Complex, has telemetry |
| `orchestrator.py` | CLI commands for workers | Simpler, different interface |
| `task_deconstructor.py` | Decompose tasks to workers | Analysis tool |

**Issue:** conversation_orchestrator.py duplicates spawn_worker functionality

### Supporting Scripts (Multiple)
- `context_bundle.py` - Context creation utilities
- `dependency_graph.py` - Visualize worker dependencies
- `phase_telemetry_validator.py` - Validate worker phases
- `principle_violation_detector.py` - Check for P15/P16/P19 violations
- `integration_test_runner.py` - Run tests against worker output

## 50% Checkpoint: What Would Make Me Wrong?

**Counter-argument 1:** "Different scripts serve different use cases"
- **Response:** True, but they should share a common core. spawn_worker.py should be the foundation that others build on.

**Counter-argument 2:** "Consolidation breaks existing workflows"
- **Response:** Need backwards compatibility. Old invocations should still work.

**Counter-argument 3:** "This is over-engineering"
- **Response:** Partially valid. Focus on high-impact consolidations only.

## Optimization Opportunities (Prioritized)

### Priority 1: Update n5_launch_worker.py to use spawn_worker.py v2
**Impact:** High
**Effort:** Low
**What:** n5_launch_worker.py should use --context JSON flag

### Priority 2: Deprecate build_orchestrator.py (v1)
**Impact:** Medium
**Effort:** Low
**What:** Mark as deprecated, update docs to use v2

### Priority 3: Consolidate orchestrator.py + conversation_orchestrator.py
**Impact:** Medium
**Effort:** Medium
**What:** Single orchestrator with CLI subcommands

### Priority 4: Create unified context_bundle pattern
**Impact:** Medium
**Effort:** Medium
**What:** All scripts use same context structure

### Priority 5: Streamline Prompts
**Impact:** Low
**Effort:** Low
**What:** Single "Worker" prompt that covers all use cases

## 75% Checkpoint: Evidence That Would Change Conclusion

1. If n5_launch_worker.py has unique features not in spawn_worker.py → Don't just replace
2. If conversation_orchestrator.py telemetry is critical → Preserve it in any consolidation
3. If V uses both old and new patterns → Provide migration path

## Recommended Actions

### Immediate (This Conversation)
1. ✓ Fixed spawn_worker.py (already done)
2. Update n5_launch_worker.py to use v2 --context pattern
3. Mark build_orchestrator.py (v1) as deprecated

### Follow-up (Future Conversation)  
4. Consolidate orchestrator scripts
5. Create unified worker management CLI

## Pattern to Extract

**Pattern Name:** "LLM-First Script Design"
**Description:** When building scripts that interact with LLM context, the LLM should provide semantic content via structured arguments (JSON), and the script should only handle mechanical operations (file I/O, timestamps, database updates).

**Anti-pattern:** Script trying to parse/extract semantic meaning from files with regex.


