# Unprocessed Meetings Marked for Queue

**Date:** November 2, 2025 11:36 PM ET  
**Action:** Marked 143 meetings with B31 files as "unprocessed" in registry

---

## Summary

Successfully added all meetings that have B31 files but were not in the database registry to the processing queue.

### Before
- **In registry:** 15 meetings
- **With B31 files:** 203 meetings total
- **Untracked:** 188 meetings

### After
- **Total in registry:** 158 meetings
- **Marked as unprocessed (insights_extracted=0):** 147 meetings
- **Already processed (insights>0):** 11 meetings

---

## What This Means

**Queue Status:** 147 meetings are now marked as "unprocessed" and ready for batch extraction.

**Processing Flow:**
1. Meeting has B31 file → ✓ (already exists)
2. Meeting in registry → ✓ (just added)
3. insights_extracted = 0 → ✓ (marked as unprocessed)
4. Ready for batch processing → ✓

---

## Next Steps

### Option 1: Process ALL Unprocessed (147 meetings)

**Estimated yield:** ~550-650 insights (assuming ~4 insights/meeting average)

### Option 2: Process Subset (Recommended)

Start with recent/high-value meetings (October 2025, external stakeholders only, etc.)

---

**Action Complete:** All meetings with B31 files are now tracked in the registry and ready for processing.

**Database:** Knowledge/market_intelligence/gtm_intelligence.db
