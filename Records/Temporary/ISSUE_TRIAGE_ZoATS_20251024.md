# ZoATS Pipeline Test - Issue Triage

**Date:** 2025-10-24  
**Test:** Stack Overflow Sr Director PM  
**Source:** Pipeline validation run (con_REVPs4hrFA44tr7Q)

---

## Issue Summary

**Total Issues Identified:** 4  
**Severity:** All non-blocking  
**Production Impact:** Low (fallbacks operational)

---

## Issue #1: LLM API Authentication Errors

**Severity:** ⚠️ MODERATE  
**Status:** Mitigated (fallback working)  
**Impact:** Evaluation uses fallback scoring instead of LLM-enhanced

### Details
- LLM API calls failing with auth errors
- Fallback scoring logic activated successfully
- All candidates received evaluations via fallback path

### Root Cause
Likely API key configuration or rate limiting

### Recommendation
1. **Immediate:** Verify API key configuration in ZoATS config
2. **Short-term:** Add API health check before pipeline runs
3. **Long-term:** Improve fallback scoring to match LLM quality

**Priority:** 🔴 HIGH (affects quality, but not functionality)

---

## Issue #2: Evaluation Logic Inconsistency

**Severity:** ⚠️ MODERATE  
**Status:** Data quality issue  
**Impact:** Confusing outputs (PASS with "not a fit" narrative)

### Details
All 5 candidates received:
- `decision: "PASS"`
- `confidence: "high"`
- `overall_narrative: "Not a fit" / "No compelling signals"`

This is contradictory and likely due to fallback scoring bugs.

### Example
```json
{
  "decision": "PASS",
  "confidence": "high",
  "overall_narrative": "No compelling signals for consulting role. Not a fit.",
  "concerns": [
    {"issue": "No direct consulting experience", "severity": "moderate"},
    {"issue": "Unclear analytical depth", "severity": "major"}
  ],
  "key_strengths": []
}
```

### Root Cause
Fallback evaluation logic not properly mapping concerns → decision

### Recommendation
1. **Immediate:** Review `gestalt_scorer.py` fallback logic
2. **Add validation:** Decision should align with narrative sentiment
3. **Fix logic:** Major concerns + no strengths = MAYBE or NO, not PASS

**Priority:** 🔴 HIGH (data integrity issue)

---

## Issue #3: UTF-8 Filename Handling

**Severity:** 🟡 LOW  
**Status:** Edge case  
**Impact:** One candidate not processed (María José Guerrero)

### Details
- File: `María José Guerrero resume.docx`
- Bash shell escaping issues with UTF-8 characters
- File exists but `cp` command failed

### Root Cause
Shell script using literal filenames instead of proper escaping

### Recommendation
1. **Immediate:** Use Python for file operations instead of bash
2. **Add:** Filename normalization in candidate_intake
3. **Test:** Add UTF-8 filename test cases

**Priority:** 🟡 MEDIUM (affects international candidates)

---

## Issue #4: Duplicate Candidate Detection

**Severity:** 🟢 MINOR  
**Status:** Expected behavior  
**Impact:** Same candidate processed twice (different filenames)

### Details
- Amanda Sachs processed twice:
  - `amanda-sachs.pdf` → `stack-overflow-sr-dir-pm-amanda-sachs-20251024-f1hgds`
  - `Amanda Sachs-GP Resume-July 17 v1.pdf` → `stack-overflow-sr-dir-pm-amanda-sachs-gp-july-17-v1-20251024-lj36ar`

### Root Cause
Filename-based candidate ID generation (expected)

### Recommendation
1. **Enhancement:** Add resume content hash deduplication
2. **Alternative:** Name + email matching in parsed fields
3. **UI:** Flag potential duplicates for human review

**Priority:** 🟢 LOW (enhancement, not bug)

---

## Production Readiness Assessment

### Blockers for Production Use
**None** - All issues are non-blocking

### Required Before Production
1. ✅ Pipeline stages functional
2. ⚠️ Fix evaluation logic inconsistency (#2)
3. ⚠️ Resolve LLM API authentication (#1)
4. ✅ Fallback scoring works (temporary solution)

### Recommended Before Production
- 🟡 UTF-8 filename handling (#3)
- 🟢 Duplicate detection (#4)
- Add monitoring/alerting
- Add retry logic for transient failures

---

## Next Steps

### Immediate (This Week)
1. **Debug LLM API auth** - Check config, test API calls
2. **Fix gestalt fallback logic** - Align decision with narrative
3. **Add validation** - Decision/narrative consistency check

### Short-term (Next Sprint)
4. **UTF-8 filename test** - Add to integration tests
5. **Duplicate detection** - Content-based deduplication
6. **Monitoring** - Add pipeline success metrics

### Long-term (Backlog)
7. **Improve fallback scoring** - Match LLM quality without API
8. **Add retry logic** - Transient failure handling
9. **Health checks** - Pre-flight API validation

---

## Test Coverage Validation

### What We Validated ✅
- End-to-end pipeline execution
- All stage transitions (intake → parse → eval → dossier)
- Fallback scoring mechanisms
- File structure generation
- Multiple candidate handling

### What We Didn't Test
- ❌ LLM-enhanced evaluation (API errors)
- ❌ Edge cases (malformed PDFs, empty resumes)
- ❌ Large batch processing (100+ candidates)
- ❌ Email integration (sending results)
- ❌ Concurrent pipeline runs

### Recommended Additional Tests
1. API health scenario (LLM working)
2. Error scenarios (corrupted files, missing fields)
3. Load testing (50-100 candidates)
4. Integration tests (email sender, rejection workflows)

---

## Conclusion

**Pipeline Status:** ✅ OPERATIONAL (with caveats)

The ZoATS pipeline is functional and can process candidates end-to-end. However, two moderate-priority issues (#1 and #2) should be resolved before production use to ensure evaluation quality and data integrity.

The fallback mechanisms work well, demonstrating system resilience, but should not be the primary path for production evaluations.

**Recommendation:** Fix issues #1 and #2, then run another validation test with LLM API working before declaring production-ready.

---

*Triage completed: 2025-10-24 15:51 ET*
