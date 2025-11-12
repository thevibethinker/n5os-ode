---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---

# Root Cause Analysis - Meeting Naming Disaster

## What Happened

**Time**: 2025-11-04 19:32 ET  
**Impact**: 18 meetings renamed to garbage names (`external_external`, `advisory_external`)  
**Data Loss**: NONE ✅ (all intelligence files intact)

## Root Causes

### 1. 🔴 **B26 Parser Completely Broken**

**Problem**: `extract_metadata_from_b26()` in name_normalizer.py returns empty data

**Evidence**:
```python
metadata = extract_metadata_from_b26(folder)
# Returns: {'date': None, 'stakeholders': [], 'meeting_type': None}
```

**Why**: The parser expects patterns that don't exist in actual B26 files:
- Looks for `## Stakeholders` (doesn't exist - format is `### Stakeholder Classification`)
- Looks for specific field names that don't match actual B26 format
- Regex patterns hardcoded for old B26 format

**Result**: Falls back to broken pattern matching → generates "external_external"

### 2. 🔴 **LLM Naming Not Actually Connected**

**Problem**: `llm_naming.py` has a placeholder that never actually invokes B99

**Evidence**:
```python
def call_b99_prompt(b26_content, b28_content):
    logging.info("LLM naming called (not yet connected to Zo API)")
    return None  # Always returns None!
```

**Why**: There's no actual implementation to invoke the B99 prompt as a tool

**Result**: Always falls back to broken B26 parser

### 3. 🟡 **Scheduled Task Ran Before Testing**

**Problem**: The meeting processor task ran at 19:32 before manual testing completed

**Why**: Task runs every 10 minutes - no pause during integration work

**Result**: Processed meetings with broken naming logic

## What Worked (Manual B99 Invocation)

**Process**:
1. Load file 'Intelligence/prompts/B99_folder_naming.md' into context
2. Read B26 + B28 for each folder
3. Manually apply B99 logic:
   - Parse attendees
   - Count external stakeholders
   - Determine if same org
   - Apply priority rules
   - Generate name
4. Execute renames

**Results**: 18/18 meetings correctly named ✅

## Fixes Needed

### Fix #1: Implement Real LLM Naming
Instead of parsing B26, the scheduled task AI should:
1. Load B99 prompt
2. Read B26 + B28 content
3. Apply B99 logic (I already have it in context)
4. Return generated name

**Key Insight**: The AI executor (me) should do the naming, not Python regex!

### Fix #2: Remove Broken B26 Parser
The `extract_metadata_from_b26()` function is unfixable - it's trying to parse free-form markdown with regex. Delete it.

### Fix #3: Add Idempotency Checks
Before renaming:
- Check if folder already has `.standardized` marker
- Skip if already renamed
- Only process folders with "unknown", "external_external", or obviously bad names

## Lessons Learned

1. **LLMs for semantics, scripts for mechanics**
   - ✅ LLM parses B26 naturally
   - ❌ Regex parsing fails on free-form markdown

2. **Test before deploying**
   - Should have paused scheduled task
   - Should have run dry-run on 1-2 meetings first

3. **The scheduled task AI has full context**
   - It can load prompts and apply logic
   - It doesn't need helper scripts for semantic work

---

**Status**: Disaster recovered, root causes identified, ready to fix properly
