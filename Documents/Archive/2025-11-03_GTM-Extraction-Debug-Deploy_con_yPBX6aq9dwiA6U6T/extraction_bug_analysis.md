---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# GTM Extraction Pipeline Debug Analysis

## Problem Summary
Database has 40/63 records (63%) with empty insight fields despite being marked as "processed".

## Root Causes Identified

### 1. **Routing Bug (PRIMARY ISSUE)**
**Location:** `gtm_b31_processor.py` line 180

**Bug:**
```python
if '## Insight' in content:  # ← BUG HERE
    insights = parse_b31_format_new(content, ...)
```

**Why it fails:**
- Python substring check `'## Insight' in content` returns `True` for BOTH:
  - `"## Insight 1:"` (H2 header - intended match)
  - `"### Insight 1:"` (H3 header - false positive)
- Files with `### Insight N:` get routed to `parse_b31_format_new()`
- That parser splits on `r'\n## Insight \d+:'` (H2 only)
- Regex finds 0 matches, returns empty list
- Script marks file as "processed" with `insights_extracted=0`

**Impact:** 6 files with `### Insight N:` format extracted 0 insights

### 2. **Missing Format Handler**
**Parsers available:**
- `parse_b31_format_old()`: Handles `**N. Title**` (8 files)
- `parse_b31_format_3()`: Handles `### N. **Title**` (20 files)
- `parse_b31_format_new()`: Handles `## Insight N:` (3 files only!)

**Missing:** No parser for `### Insight N:` format (6 files)

### 3. **Silent Failure**
**Issue:** When parser returns empty list:
- No error logged
- File marked "processed_at=CURRENT_TIMESTAMP"
- `insights_extracted=0` written
- Looks like success in registry

**Result:** These files never get re-processed unless registry is manually reset.

### 4. **Format Fragmentation**
**Distribution across 209 B31 files:**
- 96 files: Empty/stub (< 100 bytes)
- 76 files: Narrative/unstructured (no insight blocks)
- 20 files: `### N. **Title**` format
- 8 files: `**N. Title**` format  
- 6 files: `### Insight N:` format
- 3 files: `## Insight N:` format

**Only 37 files** (18%) have structured insight blocks that current parsers can handle.

## Fixes Required

### Fix 1: Routing Logic (CRITICAL)
```python
# BEFORE (line 180):
if '## Insight' in content:

# AFTER:
if re.search(r'\n## Insight \d+:', content):
```

### Fix 2: Add H3 Insight Parser
Create `parse_b31_format_h3_insight()` to handle `### Insight N:` format.

### Fix 3: Better Error Logging
```python
if not insights:
    logger.warning(f"Zero insights extracted from {meeting_id} - format not recognized")
    # Optional: Log first 500 chars for manual review
```

### Fix 4: Format Detection Hierarchy
Update routing to check in order:
1. `r'\n## Insight \d+:'` → parse_b31_format_new()
2. `r'\n### Insight \d+:'` → parse_b31_format_h3_insight() [NEW]
3. `r'\n### \d+\. \*\*'` → parse_b31_format_3()
4. `r'\n\*\*\d+\.'` → parse_b31_format_old()
5. else → log "unrecognized format"

## Testing Plan
1. Create test file with each format
2. Verify routing sends to correct parser
3. Verify each parser extracts fields correctly
4. Test on actual files:
   - `/home/workspace/Personal/Meetings/2025-10-14_external-elaine-p/B31_STAKEHOLDER_RESEARCH.md` (H3 Insight format)
5. Re-process affected files after fix

## Files to Fix
- `/home/workspace/N5/scripts/gtm_b31_processor.py` (routing + new parser)
- `/home/workspace/N5/scripts/gtm_db_backfill.py` (if it has similar routing)
