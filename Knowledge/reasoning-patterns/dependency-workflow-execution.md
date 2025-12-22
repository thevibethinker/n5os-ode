---
created: 2025-12-17
last_edited: 2025-12-17
version: 1.0
provenance: agent_0dff3095-1068-4f53-a478-6f566f8164a0
title: "Dependency-Aware Workflow Execution"
type: reasoning_pattern
---

# Reasoning Pattern: Dependency-Aware Workflow Execution

**Summary:** Systematic approach for downstream workflows encountering missing prerequisites, focusing on discovery completion, dependency identification, and clear reporting rather than silent failure.

**Source:** MG-5 v2 Follow-Up Email Generation (2025-12-17)
**Validation:** 386 directory scan across full meeting tree
**Pattern ID:** DEP-WF-001

## Trigger

Downstream workflow (MG-5) attempts execution but finds prerequisite artifacts missing during discovery phase.

## Core Logic

1. **Discovery Phase** - Complete full scan regardless of blockers
2. **Prerequisite Audit** - Check for required files systematically
3. **Dependency Mapping** - Identify which upstream workflow creates missing artifacts
4. **Completion Report** - Document findings with clear status vs. silent failure
5. **Pattern Extraction** - Capture reasoning approach for future reuse

## Applications

- Meeting intelligence pipeline (MG-2 → MG-5)
- Warm intro generation (MG-4)
- Any downstream workflow with explicit prerequisites

## Stored Location

`/home/workspace/Knowledge/reasoning-patterns/dependency-workflow-execution.md`

---

This pattern should be applied whenever a workflow finds critical artifacts missing and needs to defer execution while providing clear signals about dependencies.

