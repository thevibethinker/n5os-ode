# Phase 2 Fix Implementation Plan

**Date:** 2025-10-13 22:40 ET  
**Thread:** con_VlqH7nqYbBLQjkoL  
**Status:** Pre-implementation  

---

## Current State Assessment

### What's Actually Working ✅
- Script already has docx handling (lines 88-138)
- python-docx installed and functioning
- Transcripts load successfully (tested with Krista: 29,574 chars)
- B31 files exist in correct locations (`N5/records/meetings/*/B31_STAKEHOLDER_RESEARCH.md`)
- Registry tracking system operational
- GTM doc exists with 39 insights (v1.0)

### What Needs Fixing 🔧
1. **Sofia Meeting:** Incorrectly included in GTM aggregation (should remove)
2. **Quote Enrichment:** Krista + Rajesh have abbreviated quotes from B31, not fuller transcript quotes
3. **Version Bump:** Need to create v1.1 with fixes

---

## Strategic Decisions (from User)

1. **Insight Numbering:** Option C (restart per category - clearer structure)
2. **New Pattern Detection:** Option B (flag for manual review - maintains quality)
3. **Version Bump:** Increment per operation (1.0 → 1.1 for fixes)
4. **Transcript Format:** Option A (handle both .docx and .txt automatically)

---

## Implementation Steps (P7 Dry-Run First)

### Step 1: Analyze Current GTM Doc ✅ COMPLETE
- **Status:** Reviewed aggregated_insights_GTM.md
- **Findings:**
  - 39 insights across 5 categories
  - Krista has 3 insights with abbreviated quotes
  - Rajesh has 3 insights with abbreviated quotes
  - Sofia included (error documented)
  
### Step 2: Create Quote Enrichment Script
- **File:** `/home/.z/workspaces/con_VlqH7nqYbBLQjkoL/enrich_quotes.py`
- **Purpose:** Extract fuller quotes from transcripts for Krista + Rajesh insights
- **Method:**
  1. Load GTM doc
  2. Find Krista + Rajesh insights
  3. Load their transcripts (using existing `load_transcript` function)
  4. Search for fuller context around existing quotes
  5. Generate enriched versions

**Dry-run:** Print proposed changes without writing

### Step 3: Manual Review of Enriched Quotes
- Review proposed replacements
- Verify quotes are accurate and in context
- Confirm 1000-char context window appropriate

### Step 4: Remove Sofia Meeting
- Remove Sofia insights from GTM doc
- Update registry to mark as error
- Document removal in changelog

### Step 5: Generate GTM v1.1
- Apply quote enrichments
- Remove Sofia content
- Update header (version, meeting count, timestamp)
- Update registry with v1.1

### Step 6: State Verification (P18)
- [ ] File exists
- [ ] File size > 0
- [ ] Valid markdown structure
- [ ] All Krista + Rajesh insights have fuller quotes
- [ ] Sofia insights removed
- [ ] Registry updated correctly
- [ ] Version number incremented

---

## Compliance Checklist

### Safety (P5, P7, P11, P19)
- [ ] **P5:** Backup original GTM v1.0 before modification
- [ ] **P7:** Dry-run mode for all operations
- [ ] **P11:** Error handling for transcript loading failures
- [ ] **P19:** Explicit try-catch for all file operations

### Quality (P15, P16, P18, P21)
- [ ] **P15:** Define "complete" = all 6 steps done + verified
- [ ] **P16:** Only use actual transcript quotes, no invention
- [ ] **P18:** Verify all writes succeeded
- [ ] **P21:** Document any assumptions made

---

## Expected Outputs

1. **GTM v1.1:** `Knowledge/market_intelligence/aggregated_insights_GTM.md`
   - Sofia removed
   - Krista + Rajesh quotes enriched
   - Version incremented
   - ~30-32 KB (reduced from 34.5 KB due to Sofia removal)

2. **Registry Update:** `Knowledge/market_intelligence/.processed_meetings.json`
   - doc_version: "1.1"
   - total_meetings: 4 (was 5)
   - Sofia marked with error note
   - last_run updated

3. **Backup:** `aggregated_insights_GTM_v1.0_backup.md`

4. **Change Log:** Documentation of what changed

---

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Quotes not found in transcript | Error handling + fallback to original |
| Registry corruption | Backup before modification |
| Incomplete removal of Sofia | Search all sections, verify count |
| Version number mismatch | Atomic update of all version references |

---

## Success Criteria

**GTM v1.1 is complete when:**
1. All Sofia insights removed (count reduced from 39)
2. All Krista insights have fuller transcript quotes
3. All Rajesh insights have fuller transcript quotes
4. Registry shows 4 meetings (not 5)
5. Version numbers consistent across doc + registry
6. Backup of v1.0 exists
7. All P18 verification checks pass

---

**Status:** Ready for Step 2 (quote enrichment script)  
**Next:** Create enrichment script with dry-run mode
