# PHASE 3: Persona Integration - CORRECTED SPEC

**Time:** 2 hours  
**Dependencies:** Phase 2 complete ✅

## ISSUE IDENTIFIED

Original p3.md references principles P15-P33 that don't exist.
We only converted P0.1-P14 from operational_principles.md in Phase 2.

## CORRECTED MISSION

Add **existing** principle references to 8 personas (expanded from original 5).

## AVAILABLE PRINCIPLES

From Phase 2:
- P0.1: LLM-First for Analysis
- P1: Human-Readable First
- P2: Single Source of Truth
- P3: Voice Integration
- P4: Ontology-Weighted
- P5: Safety & Anti-Overwrite
- P6: Mirror Sync Hygiene
- P7: Idempotence & Dry-Run
- P8: Minimal Context
- P9: Copyable Blocks
- P10: Calendar & Time
- P11: Failure Modes
- P12: Testing Fresh Threads
- P13: Naming & Placement
- P14: Change Tracking
- P36: Orchestration Pattern
- P37: Refactor Pattern

## PERSONA ASSIGNMENTS (CORRECTED)

**Builder:**
- P1: Human-Readable First
- P5: Safety & Anti-Overwrite
- P7: Idempotence & Dry-Run
- P11: Failure Modes
- P36: Orchestration
- P37: Refactor

**Strategist:**
- P0.1: LLM-First
- P2: Single Source of Truth
- P8: Minimal Context
- P12: Testing Fresh Threads

**Teacher:**
- P1: Human-Readable First
- P8: Minimal Context
- P9: Copyable Blocks

**Writer:**
- P1: Human-Readable First
- P3: Voice Integration
- P8: Minimal Context

**Architect:**
- P2: Single Source of Truth
- P5: Safety & Anti-Overwrite
- P36: Orchestration
- P37: Refactor

**Debugger:**
- P5: Safety & Anti-Overwrite
- P7: Idempotence & Dry-Run
- P11: Failure Modes
- P12: Testing Fresh Threads

**Operator:**
- P6: Mirror Sync Hygiene
- P11: Failure Modes
- P13: Naming & Placement
- P14: Change Tracking
- P36: Orchestration

**Researcher:**
- P0.1: LLM-First
- P2: Single Source of Truth
- P4: Ontology-Weighted
- P8: Minimal Context

## FORMAT

Add to each persona:



## EXECUTION STEPS

1. list_personas to get all 8 IDs
2. For each persona:
   - Load relevant principle YAMLs
   - Create relevant_principles section
   - edit_persona to add section
3. Update BUILD_TRACKER phase3 to COMPLETE, phase4 to READY

## SUCCESS CRITERIA

- 8/8 personas have relevant_principles section
- Each principle has: name, trigger, pattern, reference
- All file references are correct
- BUILD_TRACKER updated

Launch: Load this corrected spec and execute
