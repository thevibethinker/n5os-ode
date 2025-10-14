# B31 Enhancement System Design & Implementation Thread

**Date:** 2025-10-13  
**Thread ID:** con_OG98iS3an1bv2pbR  
**Topic:** Enhanced B31 stakeholder research system with transcript-enriched aggregation  
**Status:** Phase 1 complete, Phase 2 ready for new thread

---

## Quick Start for New Thread

**Load these files:**
1. `file '/home/.z/workspaces/con_OG98iS3an1bv2pbR/FINAL_B31_SYSTEM_DESIGN.md'` - Complete architecture
2. `file '/home/.z/workspaces/con_OG98iS3an1bv2pbR/IMPLEMENTATION_HANDOFF.md'` - What's done vs needed

**Core ask:** "Implement Phase 2: Add transcript enrichment to aggregation script, create 3 category docs (Product/GTM/Fundraising), test with 4-5 meetings."

---

## What Was Decided

### Key Innovation: Lean B31 + Transcript-Enriched Aggregation

**Problem:** If B31 blocks are too detailed → context window explodes during meeting processing  
**Problem:** If B31 blocks are too lean → aggregation loses nuance  
**Solution:** Keep B31 lean, enrich during aggregation by selectively loading transcripts

### The Workflow

```
Meeting Processing:
  Transcript → B31 (lean 3-4 lines per insight) → Folder
  
Aggregation (Phase 2):
  Load B31s (4-5 meetings) → Identify patterns →
  FOR EACH pattern:
    Load relevant transcript → Extract quotes → Enrich pattern → Unload
  → Generate category doc with evidence
```

### Architecture Decisions

1. **Three category documents:** Product, GTM, Fundraising (not one big doc)
2. **Rolling window:** Process 4-5 meetings at a time (context window management)
3. **Table of contents:** Auto-generated from patterns (easy navigation)
4. **Credibility weighting:** PRIMARY/SECONDARY/SPECULATIVE sources per insight
5. **Evidence-first:** Direct quotes from transcripts, not summaries of summaries

---

## What Was Built (Phase 1) ✅

### 1. Enhanced Block Registry
**File:** `N5/prefs/block_type_registry.json`

**B08 additions:**
- Domain Authority section (tracks what each person is expert on)
- Insight track record (validation rate over time)
- Syncs to permanent CRM profiles

**B31 additions:**
- Signal strength ratings (●●●●○)
- Source credibility per insight
- Essential format (adequate length, not artificially terse)
- Categories: Product, GTM, Market Dynamics, Pain Points, Fundraising

### 2. B08 → CRM Sync Script
**File:** `N5/scripts/sync_b08_to_crm.py`

Bidirectional sync between meeting B08 blocks and permanent CRM profiles in `Knowledge/crm/individuals/`.

### 3. Basic Aggregation Script (v1.0)
**File:** `N5/scripts/aggregate_b31_insights.py`

- Extracts insights from B31 files
- Incremental aggregation (not batch)
- Handles old and new B31 formats
- **Missing:** Transcript enrichment (Phase 2 work)

### 4. Command Documentation
**File:** `N5/commands/aggregate-insights.md`

### 5. Sandbox Testing
**Location:** `N5/tests/b31_system_test/`
- 4 meetings tested
- Pattern detection validated
- Sample output generated

---

## What's Needed (Phase 2) 🚧

### Core Work: Transcript Enrichment

**Add to aggregation script:**

```python
def enrich_pattern_from_transcripts(
    pattern: Dict, 
    meeting_ids: List[str]
) -> Dict:
    """
    Enrich pattern with quotes from transcripts.
    
    Process (context window safe):
    1. For each meeting in pattern
    2. Load ONLY that transcript
    3. Search for relevant sections
    4. Extract 2-3 best quotes
    5. Unload transcript
    6. Return enriched pattern
    """
```

### Create 3 Category Templates

1. `Knowledge/market_intelligence/aggregated_insights_PRODUCT.md`
2. `Knowledge/market_intelligence/aggregated_insights_GTM.md`
3. `Knowledge/market_intelligence/aggregated_insights_FUNDRAISING.md`

**Each includes:**
- Table of contents (auto-generated)
- Strong Signals (≥3 PRIMARY sources)
- Emerging Signals (2 sources)
- Single-Source (monitor)
- Contradictions & Tensions
- Opportunity Map
- What's Missing / Next Conversations
- Change Log

### Test & Deploy

1. Select 4-5 GTM-focused meetings
2. Run enhanced aggregation
3. Validate output quality (quotes present, non-obvious patterns)
4. Backfill last 15-20 external meetings across all 3 categories

---

## Key Design Principles

1. **B31 = lean pointer** (not comprehensive)
2. **Enrichment = aggregation time** (not meeting processing)
3. **Never load all transcripts** (one at a time, then unload)
4. **Category split** (Product/GTM/Fundraising)
5. **Evidence-first** (direct quotes required)
6. **Primary sources > secondary** (credibility weighting)
7. **Table of contents** (navigation)
8. **Rolling window** (4-5 meetings max)

---

## Critical Files

**Design & handoff:**
- `/home/.z/workspaces/con_OG98iS3an1bv2pbR/FINAL_B31_SYSTEM_DESIGN.md`
- `/home/.z/workspaces/con_OG98iS3an1bv2pbR/IMPLEMENTATION_HANDOFF.md`

**Production files:**
- `N5/prefs/block_type_registry.json`
- `N5/scripts/sync_b08_to_crm.py`
- `N5/scripts/aggregate_b31_insights.py`
- `N5/commands/aggregate-insights.md`

**Test sandbox:**
- `N5/tests/b31_system_test/TEST_RESULTS.md`
- `N5/tests/b31_system_test/market_intelligence/aggregated_insights.md`

---

## Success Criteria

✅ Aggregated insights surface non-obvious patterns  
✅ Direct quotes from transcripts included  
✅ Context window < 50k tokens per batch  
✅ Category docs navigable  
✅ Insights actionable  
✅ Primary sources weighted properly  
✅ Synthesis value clear  

---

## Estimated Timeline

**Phase 2:** 2-3 hours
- Transcript enrichment: 60-90 min
- Category templates: 30 min
- Testing: 30-45 min
- Backfill: 30-45 min

---

**Exported:** 2025-10-13 05:05 AM ET  
**Ready for new thread implementation**
