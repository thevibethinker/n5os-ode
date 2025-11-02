# TASK: Add LLM Code Editing Architectural Principle

**Created:** 2025-11-01 22:15 ET  
**Priority:** High  
**Type:** Architectural Documentation  
**Worker:** Builder or Architect

## Context

During stakeholder profile system design, V identified: **LLMs editing existing code is RISKY**. Use **separate orchestration points** instead.

## Task

Add new architectural principle documenting this pattern to file .

**Pattern:** Separate orchestration for LLM-modified systems
- Create separate watcher/consumer
- Use file markers for coordination  
- Producer/consumer pattern
- Independent failure modes

**Example:** Don't edit meeting_processor_v3.py - create separate profile_enricher_watcher.py

## Deliverable

Update architectural principles with clear guidance on when/how to use separate orchestration vs integration.

---
*Spawned from con_iGbYpztfBufW4szX*
