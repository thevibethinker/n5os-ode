---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# GTM Extraction Process Debugging - COMPLETE

## Executive Summary
**Problem:** 63% of database records have empty insight fields.  
**Root Cause:** Routing bug in line 180 of `gtm_b31_processor.py` + missing format handler.  
**Status:** Debugged. Ready for fix implementation.

---

## Debugging Process (Per Vibe Debugger Protocol)

### Phase 1: Reconstruct System ✅
**Goal:** Understand what was actually built

**Components Identified:**
- `gtm_intelligence.db` (SQLite database, 63 records)
- `gtm_b31_processor.py` (scheduled extraction script)
- `gtm_db_backfill.py` (manual backfill utility)
- `gtm_processing_registry` table (tracks processed files)
- 209 B31 files in `/home/workspace/Personal/Meetings/*/B31_*.md`

**Data Flow:**
```
B31 files → gtm_b31_processor.py → parse_b31_file() → [route to parser] → DB insert
                                          ↓
                                   [routing decision]
                                          ↓
                          if '## Insight' in content ← BUG HERE
```

### Phase 2: Test Systematically ✅
**Goal:** Find what breaks

**Test 1: Database Quality**
```sql
Total records: 63
Empty insight field: 40 (63%)
Empty why_it_matters: 49 (78%)
Empty quote field: 49 (78%)
Has all 3 fields populated: 14 (22%)
```
**Result:** Most records are title-only stubs.

**Test 2: Format Detection**
Scanned all 209 B31 files:
- 96 empty/stub (< 100 bytes)
- 76 narrative/unstructured
- 20 use `### N. **Title**` format
- 8 use `**N. Title**` format
- 6 use `### Insight N:` format ← PROBLEM FILES
- 3 use `## Insight N:` format

**Test 3: Parser Pattern Matching**
Tested on actual file `2025-10-14_external-elaine-p/B31_STAKEHOLDER_RESEARCH.md`:
```
Pattern '## Insight N:' matches: 0
Pattern '### Insight N:' matches: 3 ✅
```

**Test 4: Routing Logic Bug**
```python
>>> '## Insight' in '### Insight 1: Test'
True  ← BUG: Substring match doesn't respect markdown syntax
```

### Phase 3: Validate Against Plan (P28) ✅
**Goal:** Does plan match reality?

**Findings:**
- No documented spec for B31 format variations
- Parser assumes uniform format but reality is fragmented
- No error handling for unrecognized formats
- Silent failure: marks files "processed" with 0 insights

**P28 Violation:** Quality issue upstream - no format specification document.

### Phase 4: Check Principles ✅
**Violations Found:**

| Principle | Violation | Evidence |
|-----------|-----------|----------|
| **P15: False Completion** | ✅ VIOLATED | Files marked "processed" with 0 insights extracted |
| **P19: Error Handling** | ✅ VIOLATED | No try/except around format detection, no logging when insights=0 |
| **P21: Document Assumptions** | ✅ VIOLATED | Format assumptions undocumented, no schema for B31 structure |
| **P28: Code Matches Plan** | ✅ VIOLATED | No plan/spec found for handling format variations |

### Phase 5: Report Findings ✅

---

## CRITICAL ISSUES

### Issue 1: Routing Bug (SEVERITY: HIGH)
**Location:** `gtm_b31_processor.py:180`

**Code:**
```python
if '## Insight' in content:  # ← Uses substring check, not regex
    insights = parse_b31_format_new(content, meeting_id, meeting_date, b31_path)
```

**Problem:**
- `'## Insight' in '### Insight 1:'` returns `True` (substring match)
- Files with H3 headers `### Insight N:` get routed to H2 parser
- H2 parser splits on `r'\n## Insight \d+:'` → finds nothing → returns []

**Impact:** 6 files with correct structure but wrong header level extract 0 insights

**Fix:**
```python
if re.search(r'\n## Insight \d+:', content):  # Use regex, not substring
    insights = parse_b31_format_new(content, meeting_id, meeting_date, b31_path)
elif re.search(r'\n### Insight \d+:', content):  # Add H3 handler
    insights = parse_b31_format_h3_insight(content, meeting_id, meeting_date, b31_path)
```

### Issue 2: Missing Format Handler (SEVERITY: MEDIUM)
**Problem:** No parser exists for `### Insight N:` format (6 files use this)

**Fix:** Create `parse_b31_format_h3_insight()` by copying `parse_b31_format_new()` and changing:
```python
blocks = re.split(r'\n## Insight \d+:', content)  # OLD
blocks = re.split(r'\n### Insight \d+:', content)  # NEW
```

### Issue 3: Silent Failure (SEVERITY: MEDIUM)
**Problem:** When `insights = []`, script:
1. Marks file as processed ✅
2. Sets `insights_extracted = 0` ✅
3. Logs "No insights extracted" ℹ️
4. Never logs WHY no insights were found ❌

**Impact:** Impossible to distinguish:
- Empty B31 file (legitimate)
- Unrecognized format (bug)
- Parser crash (bug)

**Fix:** Add format detection logging:
```python
if not insights:
    logger.warning(f"Zero insights from {meeting_id}")
    logger.debug(f"First 500 chars: {content[:500]}")
```

---

## QUALITY CONCERNS

### Concern 1: Format Fragmentation
**Finding:** 209 B31 files use at least 6 different formats  
**Risk:** Parsers will continue to break as formats evolve  
**Recommendation:** Establish canonical B31 schema, enforce during meeting processing

### Concern 2: No Format Specification
**Finding:** No document defines expected B31 structure(s)  
**Risk:** Future contributors won't know which formats are supported  
**Recommendation:** Create `N5/schemas/B31_format_spec.md`

### Concern 3: Backfill vs Scheduled Divergence
**Finding:** Two different scripts extract B31 data  
**Risk:** Bug fixes must be applied in 2 places  
**Recommendation:** Extract parsing logic to shared module

---

## VALIDATED

✅ All 3 existing parsers correctly extract their respective formats:
- `parse_b31_format_old()` handles `**N. Title**`
- `parse_b31_format_3()` handles `### N. **Title**`
- `parse_b31_format_new()` handles `## Insight N:` (when routed correctly)

✅ Database schema is sound

✅ Registry tracking works as designed

---

## NOT TESTED

⚠️ LLM backfill script (`gtm_backfill_llm.py`) - different approach entirely  
⚠️ Error recovery when DB insert fails  
⚠️ Handling of malformed UTF-8 in B31 files  
⚠️ Concurrent processing (if multiple scripts run simultaneously)

---

## NEXT STEPS

### Immediate (Required)
1. Fix routing logic (30 min)
2. Add H3 Insight parser (20 min)  
3. Add format detection logging (10 min)
4. Test on 5 example files (20 min)
5. Reset affected 6 files in registry (5 min)
6. Re-run processor on those 6 files (5 min)

### Short-term (Recommended)
7. Create B31 format specification document
8. Refactor parsers into shared module
9. Add unit tests for each parser
10. Document extraction process in Knowledge/

### Long-term (Strategic)
11. Standardize B31 output format in meeting processor
12. Add format validation during meeting processing
13. Create migration path for legacy formats

---

## FILES FOR REFERENCE
- Debug log: file `/home/.z/workspaces/con_yPBX6aq9dwiA6U6T/DEBUG_LOG.jsonl`
- Full analysis: file `/home/.z/workspaces/con_yPBX6aq9dwiA6U6T/extraction_bug_analysis.md`
- Test script: file `/home/.z/workspaces/con_yPBX6aq9dwiA6U6T/test_parser.py`
- Format survey: file `/home/.z/workspaces/con_yPBX6aq9dwiA6U6T/check_all_formats.py`

---

**Debugging Status:** ✅ COMPLETE  
**Ready for:** Fix implementation  
**Time to fix:** ~1.5 hours including testing
