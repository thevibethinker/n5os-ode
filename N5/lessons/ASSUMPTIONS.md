# Lessons System - Assumptions, Placeholders, and Stubs

**Created:** 2025-10-12  
**Last Updated:** 2025-10-12  
**Principle:** 21 (Document All Assumptions, Placeholders, and Stubs)

---

## Assumptions Made

### 1. Conversation Workspace Detection
**Assumption:** Can reliably auto-detect conversation workspace from environment or file system  
**Status:** Implemented, seems to work  
**Risk:** May fail in edge cases (no env var, multiple workspaces)  
**Mitigation:** Falls back to manual specification via CLI args

### 2. Significance Detection Criteria
**Assumption:** Current heuristics (error logs, versioned files, design docs) accurately identify significant threads  
**Status:** Basic implementation  
**Risk:** May miss important threads or flag too many  
**Mitigation:** Adjustable criteria, --force flag to override

### 3. JSONL Format
**Assumption:** JSONL (newline-delimited JSON) is appropriate for lesson storage  
**Status:** Implemented  
**Risk:** None, well-established format  
**Verification:** ✓ Working

### 4. Principle Numbering
**Assumption:** Principles 0-20 are current, no gaps  
**Status:** Verified during implementation  
**Risk:** If principles renumbered, mapping breaks  
**Mitigation:** principle_to_module dict in review script

### 5. Weekly Review Timing
**Assumption:** Sunday 19:00 is appropriate for weekly review  
**Status:** Scheduled task created  
**Risk:** User may prefer different time  
**Mitigation:** Easy to reschedule via Zo interface

---

## Placeholders

### 1. LLM Extraction Logic ✅ RESOLVED
**File:** `N5/scripts/n5_lessons_extract.py`  
**Function:** `extract_lessons_llm()` (lines ~110-135)  
**Previous status:** PLACEHOLDER - Returns empty list  
**Resolution:** Option A approach implemented
- I (the LLM) analyze conversation during conversation-end
- Extract lessons directly before script runs
- Write JSONL to pending/ directory
- Script now finds lessons already created
**Updated:** 2025-10-12 - Principle 16 applied (I AM the LLM, no external API)
**Implementation:** See file 'N5/commands/conversation-end.md' Phase 0

### 2. Conversation Summary
**File:** `N5/scripts/n5_lessons_extract.py`  
**Function:** `generate_conversation_summary()` (lines ~138-170)  
**Current behavior:** Basic file counting and name detection  
**What's needed:** 
- More sophisticated analysis of what happened in thread
- Extract key activities, decisions, errors
- Contextual summary for LLM extraction
**Status:** BASIC STUB - Works but limited  
**Priority:** Medium (current version adequate for now)

### 3. New Principle Creation
**File:** `N5/scripts/n5_lessons_review.py`  
**Function:** `approve_lesson()` (lines ~285-310)  
**Current behavior:** Warns "not yet implemented"  
**What's needed:**
- Interactive prompt for new principle details
- Determine which module to add to
- Format and insert new principle
- Update index
**Status:** STUB - Prints message only  
**Priority:** Low (can add manually for now)

### 4. Change Log Updates
**File:** `N5/scripts/n5_lessons_review.py`  
**Function:** `update_principle_with_lesson()` (lines ~255-283)  
**Current behavior:** Appends example but doesn't update change log section  
**What's needed:**
- Parse existing change log
- Add new entry with date and lesson reference
- Maintain chronological order
**Status:** PARTIAL - Adds example but not change log entry  
**Priority:** Medium

---

## Stubs / Simulations

### 1. Test Lesson Generator
**File:** `N5/scripts/test_lessons_system.py`  
**Purpose:** Creates mock lessons for testing  
**Status:** Complete simulation - not for production use  
**Note:** This is intentional test infrastructure

### 2. Extraction Prompt Template
**File:** `N5/lessons/schemas/extraction_prompt.txt`  
**Status:** Ready but unused (waiting for LLM integration)  
**Note:** Template is complete, just needs to be used by actual LLM call

---

## Known Limitations

### 1. Manual Principle-to-Module Mapping
**Location:** `n5_lessons_review.py` - `principle_to_module` dict  
**Issue:** Hardcoded mapping, must be updated if principles reorganized  
**Better approach:** Could parse module files to auto-detect which principles they contain  
**Priority:** Low (current approach works)

### 2. Single Thread Per File
**Location:** Lesson file naming convention  
**Issue:** One JSONL file per thread in pending, but may have multiple lessons  
**Impact:** Minimal - works fine, just could be more flexible  
**Priority:** Very low

### 3. No Lesson Deduplication
**Issue:** If same lesson extracted multiple times, no detection  
**Impact:** Could get duplicate entries in archive  
**Mitigation:** Review process allows rejection of duplicates  
**Priority:** Low

### 4. No Analytics/Reporting
**Issue:** No built-in way to analyze lessons over time  
**What's missing:**
- Trend analysis (most common mistakes)
- Principle coverage (which principles get most lessons)
- Time-series visualization
**Status:** Not implemented  
**Priority:** Low (future enhancement)

---

## Technical Debt

### 1. Extraction Integration ⚠️ HIGHEST PRIORITY
**Problem:** Extract lessons placeholder doesn't actually extract  
**Impact:** Core feature not working  
**Solution:** Implement actual LLM-based analysis (see Placeholder #1)  
**Estimated effort:** 1-2 hours  
**Blocker:** Need to understand correct pattern for LLM self-invocation

### 2. Error Handling in Review Script
**Problem:** Limited error handling for file I/O, JSON parsing  
**Impact:** Could crash on malformed lessons  
**Solution:** Add try-catch blocks, validation  
**Estimated effort:** 30 minutes  
**Priority:** Medium

### 3. Atomic File Operations
**Problem:** Lesson files written without atomic operations  
**Impact:** Could corrupt on interrupt  
**Solution:** Write to temp file, then atomic rename  
**Estimated effort:** 15 minutes  
**Priority:** Medium

---

## Questions / Unknowns

### 1. Scheduled Task Execution Context ❓
**Question:** When scheduled task runs, does it have access to me (the LLM)?  
**Status:** UNKNOWN - needs verification  
**Impact:** Critical for review workflow  
**Next step:** Test or consult documentation

### 2. Conversation Workspace Persistence ❓
**Question:** How long do conversation workspaces persist after thread closes?  
**Status:** UNKNOWN  
**Impact:** If cleaned up too fast, extraction may fail  
**Next step:** Document workspace lifecycle

### 3. Optimal Lesson Granularity ❓
**Question:** How many lessons per thread is ideal?  
**Status:** Unclear  
**Current guess:** 1-5 lessons per significant thread  
**Impact:** Affects extraction logic  
**Next step:** Empirical testing

---

## What's Actually Complete

✅ Directory structure  
✅ Schema definition  
✅ Significance detection (basic)  
✅ JSONL storage/validation  
✅ Review UI (full CRUD)  
✅ Principle update logic  
✅ Archive workflow  
✅ Scheduled task creation  
✅ Documentation  
✅ Command registration  
✅ Integration with conversation-end  

---

## What Needs LLM Integration

⚠️ **PRIMARY BLOCKER:** Actual lesson extraction from conversation content

**The gap:** `extract_lessons_llm()` needs to:
1. Analyze conversation workspace files
2. Identify techniques, strategies, patterns, troubleshooting
3. Generate structured lesson objects
4. Return JSON array

**The solution:** I (the LLM in conversation) should do this analysis directly, not call external API

**Why it was wrong:** I kept thinking "call LLM API" instead of "I AM the LLM"

**Correct approach:** (To be determined with user guidance)

---

## How to Track Future Changes

When adding features or fixing placeholders:

1. **Update this file** - Mark as complete, move from Placeholder to Complete
2. **Update principle modules** - If lesson learned
3. **Update README** - If user-facing change
4. **Update COMPLETE.md** - Final status document

---

**Principle Applied:** 21 (Document All Assumptions, Placeholders, and Stubs)  
**Status:** This manifest itself is now complete ✓
