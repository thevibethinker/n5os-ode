# Architecture Correction: Remove Script-Based LLM Calls

**Date:** 2025-10-10  
**Status:** 🔄 READY FOR CORRECTION IN NEW THREAD  
**Previous Thread:** con_kf3FOpAIJeoe9JlO

---

## 🎯 Core Problem

The current implementation has Python scripts trying to "call Zo LLM" via subprocess/wrappers. This is fundamentally wrong because:

1. **I AM Zo** - The AI assistant should process content directly when invoked
2. **Scripts can't call me** - Circular dependency trying to subprocess to myself
3. **Unnecessary complexity** - Request/response files, wrappers, polling loops
4. **Wrong pattern** - Scripts should prepare data, Zo should process it

## ❌ What Was Built (Incorrectly)

### Files Created That Need Removal/Correction:

1. **`N5/scripts/utils/zo_llm.py`** ❌
   - Attempts to call Zo via subprocess
   - Creates request/response file system
   - Polling loop waiting for responses
   - **Action: DELETE THIS FILE**

2. **`N5/scripts/meeting_intelligence_orchestrator.py`** ⚠️
   - Imports `zo_llm` wrapper
   - Has `_call_llm()` method that tries to subprocess
   - **Action: SIMPLIFY - Make it data preparation only**

3. **Architecture pattern** ❌
   - Script → subprocess → Zo → response → script
   - **Should be:** Script → metadata → Zo invoked → Zo processes directly

---

## ✅ What Was Built (Correctly)

These components are good and should be kept:

1. **`N5/scripts/utils/stakeholder_classifier.py`** ✅
   - Pure Python classification logic
   - No LLM calls
   - Works perfectly
   - **Action: KEEP AS-IS**

2. **`N5/prefs/block_templates/{internal,external}/*.template.md`** ✅
   - Template files for both meeting types
   - Ready to be filled by Zo
   - **Action: KEEP AS-IS**

3. **`N5/scripts/meeting_auto_processor.py`** ✅ (mostly)
   - Detects transcripts
   - Classifies stakeholders
   - Creates processing requests
   - **Action: KEEP, remove any zo_llm imports if present**

4. **`N5/schemas/meeting-metadata.schema.json`** ✅
   - Updated with stakeholder fields
   - **Action: KEEP AS-IS**

---

## 🎯 Correct Architecture

### How It SHOULD Work:

```
┌─────────────────────────────────────────┐
│  1. Auto Processor (Python Script)      │
│     - Monitors Google Drive             │
│     - Downloads new transcripts         │
│     - Classifies stakeholders           │
│     - Creates processing request JSON   │
│     - NO LLM CALLS                      │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  2. Processing Request Queue            │
│     N5/inbox/meeting_requests/          │
│     {meeting-id}_request.json           │
│     Contains:                           │
│       - transcript_path                 │
│       - stakeholder_classification      │
│       - participants                    │
│       - meeting_id                      │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  3. Scheduled Task / Command            │
│     "Zo, process pending meetings"      │
│     OR                                  │
│     command 'meeting-process'           │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  4. Zo Processes Directly               │
│     - Read processing request           │
│     - Load transcript                   │
│     - Classify stakeholders             │
│     - Load appropriate templates        │
│     - Extract content (I do this)       │
│     - Fill templates                    │
│     - Save all blocks                   │
│     - Create metadata                   │
│     - Mark request as processed         │
└─────────────────────────────────────────┘
```

### Key Principle:
**Python scripts = data preparation**  
**Zo = content processing & LLM work**

---

## 🔧 Required Changes

### 1. Delete Unnecessary Files

```bash
rm N5/scripts/utils/zo_llm.py
rm -rf N5/inbox/llm_requests/
rm -rf N5/inbox/llm_responses/
```

### 2. Simplify Meeting Intelligence Orchestrator

**Current:** Tries to call LLM via subprocess  
**New:** Just prepares data structures, loads templates

**File:** `N5/scripts/meeting_intelligence_orchestrator.py`

**Changes needed:**
- Remove `from utils.zo_llm import call_zo_llm, extract_from_transcript`
- Remove `_call_llm()` method
- Remove all async LLM extraction methods
- Keep: `_load_templates()` method
- Keep: Template loading logic
- Keep: Data structure definitions

**New purpose:** Template manager and data structure provider, NOT LLM caller

### 3. Create Meeting Processing Command

**New file:** `N5/commands/meeting-process.md`

**Purpose:** Command that Zo executes to process meetings

**Structure:**
```markdown
# `meeting-process`

Process pending meeting transcripts with stakeholder-aware analysis.

## What This Does

1. Check N5/inbox/meeting_requests/ for pending requests
2. For each request:
   - Load transcript
   - Confirm stakeholder classification
   - Load appropriate templates (internal vs external)
   - Extract content for each block using LLM
   - Fill templates with extracted content
   - Save all blocks to meeting folder
   - Create _metadata.json
   - Mark request as processed

## Execution

When invoked via scheduled task or manually, Zo processes all pending
meeting requests directly using native LLM capabilities.

No Python subprocess calls required - Zo does all extraction natively.
```

### 4. Update Scheduled Task

**Current scheduled task instruction:**
```
[Check what the current instruction is]
```

**New scheduled task instruction:**
```
Execute command 'meeting-process' to process any pending meeting transcripts.

For each meeting in N5/inbox/meeting_requests/:
1. Load transcript and classification
2. Load appropriate templates based on stakeholder type
3. Extract all content using your LLM capabilities
4. Fill templates and save blocks
5. Mark as processed
```

---

## 📋 Step-by-Step Implementation Plan

### Phase 1: Cleanup (Delete Wrong Approach)
1. Delete `N5/scripts/utils/zo_llm.py`
2. Delete `N5/inbox/llm_requests/` directory
3. Delete `N5/inbox/llm_responses/` directory
4. Remove zo_llm imports from any scripts

### Phase 2: Simplify MIO
1. Open `N5/scripts/meeting_intelligence_orchestrator.py`
2. Remove all subprocess/LLM calling logic
3. Keep template loading functionality
4. Make it a pure data structure / template manager
5. Test that it still loads templates correctly

### Phase 3: Create Command-Based Workflow
1. Create `N5/commands/meeting-process.md`
2. Document how Zo should process meetings
3. Include template loading logic
4. Include extraction patterns for each block type

### Phase 4: Test End-to-End
1. Place test transcript in inbox
2. Run `command 'meeting-process'`
3. Verify Zo processes directly (no subprocess)
4. Check all blocks generated correctly
5. Validate metadata includes classification

### Phase 5: Update Documentation
1. Update `N5/docs/stakeholder-classification-quickstart.md`
2. Update implementation docs
3. Document new command-based approach

---

## 🧪 Test Cases for New Thread

### Test 1: Internal Meeting
**Transcript:** `N5/test/sample_internal_transcript.txt`  
**Expected classification:** Internal  
**Expected templates:** internal/  
**Expected blocks:** 7 (including debate-points.md, memo.md)

### Test 2: External Meeting
**Transcript:** `N5/test/sample_external_transcript.txt`  
**Expected classification:** External  
**Expected templates:** external/  
**Expected blocks:** 7 (including stakeholder-profile.md, follow-up-email.md)

### Test 3: Real Google Drive Meeting
**Source:** Actual transcript from Google Drive  
**Verify:** End-to-end flow with real data

---

## 📊 Current State Summary

### What's Working ✅
- Stakeholder classification logic (Python)
- Template files (both internal/external)
- Auto processor (detects & classifies)
- Processing request creation

### What's Wrong ❌
- zo_llm.py wrapper (unnecessary)
- MIO trying to subprocess to Zo
- Request/response file system
- Async polling loops

### What's Needed 🔄
- Delete wrapper files
- Simplify MIO to template manager only
- Create meeting-process command
- Update scheduled task
- Test with Zo processing directly

---

## 💡 Key Insights for New Thread

1. **Zo IS the LLM** - Don't try to subprocess to yourself
2. **Scripts prepare, Zo processes** - Clean separation of concerns
3. **Commands over complexity** - Simple command invocation beats subprocess wrappers
4. **Templates are data** - Scripts manage templates, Zo fills them
5. **Scheduled tasks invoke Zo** - Not scripts trying to call LLM

---

## 📁 Files to Review in New Thread

### Must Read First:
1. `file 'N5/docs/ARCHITECTURE_CORRECTION.md'` ← THIS FILE
2. `file 'N5/scripts/meeting_intelligence_orchestrator.py'` ← Needs simplification
3. `file 'N5/scripts/utils/zo_llm.py'` ← DELETE THIS
4. `file 'N5/scripts/meeting_auto_processor.py'` ← Check for zo_llm imports

### Reference (Keep As-Is):
1. `file 'N5/scripts/utils/stakeholder_classifier.py'` ← Working correctly
2. `file 'N5/prefs/block_templates/internal/'` ← Templates ready
3. `file 'N5/prefs/block_templates/external/'` ← Templates ready
4. `file 'N5/test/sample_internal_transcript.txt'` ← Test data
5. `file 'N5/test/sample_external_transcript.txt'` ← Test data

---

## 🎯 Success Criteria for Correction

After implementing in new thread, you should have:

✅ **No subprocess LLM calls** - Scripts don't try to call Zo  
✅ **Command-based processing** - `command 'meeting-process'` works  
✅ **Zo processes directly** - I extract content natively when invoked  
✅ **Simplified MIO** - Just template manager, no LLM logic  
✅ **End-to-end test passing** - Real transcript → processed blocks  
✅ **Scheduled task updated** - Invokes command, not scripts  

---

## 📝 User's Original Request (Context)

> "Can we go through and ensure that in all cases where you are using the 
> script-based approach to calling Zo, we have corrected it so that you are 
> calling Zo directly and make that standard operating procedure across the 
> platform? You have a bias towards generating Python scripts when they really 
> are not necessary and you can just directly invoke the LLM."

**Translation:** 
- Stop having Python scripts try to subprocess to Zo
- Zo should process content directly when invoked via commands
- Make this the standard pattern everywhere

---

## 🚀 Ready for New Thread

This document contains everything needed to correct the architecture in a clean, new thread.

**Next steps in new thread:**
1. Load this file: `file 'N5/docs/ARCHITECTURE_CORRECTION.md'`
2. Execute cleanup (delete zo_llm.py, etc.)
3. Simplify MIO
4. Create meeting-process command
5. Test end-to-end
6. Update docs

**Estimated time:** 30-45 minutes  
**Complexity:** Medium (mostly deletion + simplification)  
**Risk:** Low (keeping working components, removing broken ones)

---

**Created:** 2025-10-10 23:40 UTC  
**For new thread execution**  
**Status:** 🔄 Ready to implement
