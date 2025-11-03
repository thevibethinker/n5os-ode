# BUILD PLAN: Stakeholder Profile Auto-Creation (Phase 1)

**Created:** 2025-11-02 22:45 ET  
**Orchestrator:** Vibe Architect  
**Pattern:** Parallel track + sequential gates

## OBJECTIVE
Fix "only Edmund has a profile" problem with automatic profile creation.

## WORKERS

### WORKER 1: Database Schema (2h)
**Deliverable:** profiles.db with complete schema
**Files:** N5/scripts/create_profiles_db.py
**Dependencies:** None

### WORKER 2: Detection Engine (4h)  
**Deliverable:** scan_calendar_for_new_stakeholders() implementation
**Files:** auto_create_stakeholder_profiles.py
**Dependencies:** Worker 1 (needs DB for deduplication)

### WORKER 3: Profile Generator (3h)
**Deliverable:** create_stakeholder_profile_auto() implementation  
**Files:** auto_create_stakeholder_profiles.py
**Dependencies:** Worker 1 (needs DB)

### GATE 1: Integration
Workers 1-3 complete → Worker 4 begins

### WORKER 4: Orchestrator (2h)
**Deliverable:** main() + scheduled task
**Files:** auto_create_stakeholder_profiles.py + task creation
**Dependencies:** Gate 1

### GATE 2: Testing
Worker 4 complete → Worker 5 validates

### WORKER 5: Validation (2h)
**Deliverable:** Test script + documentation
**Files:** test_profile_creation.py, profile_auto_creation.md
**Dependencies:** Worker 4

## TIMELINE
- Day 1: Workers 1-3 parallel + Worker 4
- Day 2: Worker 5 + deploy
- Day 3: Monitor & iterate

Full spec in this file. Ready for Builder execution.

---
*Architect orchestration - con_iGbYpztfBufW4szX*
