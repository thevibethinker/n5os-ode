---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# MG-5 Follow-Up Email System: Architectural Redesign

**Conversation:** con_gThIJga4tEwotkyd  
**Date:** 2025-11-17  
**Duration:** ~45 minutes  
**Personas Used:** Debugger → Architect → Operator

## Problem Identified

The M→P (Meeting state transition) system was blocked because 5 of 11 meetings were stuck waiting for follow-up emails that were never being generated.

**Root Cause:** MG-5 (Follow-Up Email Generation) was using a Python-first architecture where the script tried to do semantic work (understanding meeting context, making judgment calls, generating content). This violated V's Division of Labor principle.

## Solution Delivered

Complete architectural redesign of MG-5 using LLM-first principles:
- Python handles mechanics (file operations, JSON updates)
- LLM handles semantics (understanding, judgment, content generation)

## Key Documents

1. **DIAGNOSTIC_COMPLETE.md** - Full diagnostic with blocker breakdown (45% follow-up emails, 18% intelligence blocks, etc.)
2. **ROOT_CAUSE_ARCHITECTURAL_MISMATCH.md** - Detailed explanation of Python vs LLM architectural issue
3. **MG5_V2_DESIGN.md** - Complete architectural specification for new system
4. **MG5_COMPARISON.md** - Side-by-side comparison of old vs new with testing plan
5. **CRITICAL_FINDING.md** - Manifest/file mismatch analysis
6. **ROOT_CAUSE_DEEP_DIVE.md** - Investigation notes

## Deliverables

### New Scheduled Task Created
- **Task ID:** 33d5378d-4ded-469b-b329-f6cd38692add
- **Schedule:** 5x daily (6am, 10am, 2pm, 6pm, 10pm ET)
- **Architecture:** LLM-first with clean mechanics/semantics separation
- **Status:** Active, ready for comparison testing

### Old Task Status
- **Task ID:** 740666e0-50d9-48a6-98a8-0bfe2ac1d577
- **Status:** Still running for comparison
- **To deprecate:** After 24-48 hours of validation

## Impact

- Unblocks M→P transitions for 5 meetings (45% of current backlog)
- Establishes architectural pattern for other MG tasks
- Enforces Division of Labor principle system-wide

## Next Steps

1. Monitor both tasks for 24-48 hours
2. Compare results (old likely produces nothing, new should generate semantic-driven emails)
3. Once validated, deprecate old task
4. Apply same architectural patterns to MG-2 (intelligence blocks status updates)

---

**Principle Enforced:** Division of Labor - Scripts handle mechanics, LLM handles semantics.

