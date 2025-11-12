# Light Cleanup Plan - FINAL
**Date:** 2025-11-04 13:43 ET

---

## Confirmed Duplicates

### 1. Asher Meeting (2025-08-26)
**Meeting ID:** `Asher King Abramson x Vrijen Attawar-transcript-2025-08-26T16-28-01.055Z`

**Keep:**
- `2025-08-26_asher-king-abramson_warmer-jobs-product-integration_partnership` (9 B*.md files)

**Delete:**
- `2025-08-26_asher-king-abramson_warmer-jobs-integration-discussion_partnership` (same meeting, different name)

**Also exists:**
- `Asher King Abramson x Vrijen Attawar-transcript-2025-08-26T16-28-01.055Z` (original transcript folder - keep for now or delete?)

---

### 2. Greenlight Meeting (2025-09-12)
**Meeting ID:** `Allie Cialeo and Vrijen Attawar + Logan Currie-transcript-2025-09-12T15-33-45.590Z`

**Keep:**
- `2025-09-12_greenlight_recruiting-discovery_sales` (has full B*.md files)

**Delete:**
- `2025-09-12_greenlight_talent-screening_sales` (duplicate with truncated Meeting ID)

---

### 3. Sept 22 Folders (EMPTY - artifacts)
All three Sept 22 folders have NO B26 files:
- `2025-09-22_ayush-jain_job-aggregation-automation-workflow_partnership` - EMPTY
- `2025-09-22_careerspan_kathy-pham-interview-planning_planning` - EMPTY  
- `2025-09-22_careerspan_podcast-production-gtm-planning_cofounder` - EMPTY

**Action:** Delete all three (they're empty placeholders/artifacts)

---

## Cleanup Actions

```bash
# Delete Asher duplicate
rm -rf "/home/workspace/Personal/Meetings/2025-08-26_asher-king-abramson_warmer-jobs-integration-discussion_partnership"

# Delete Greenlight duplicate
rm -rf "/home/workspace/Personal/Meetings/2025-09-12_greenlight_talent-screening_sales"

# Delete empty Sept 22 artifacts
rm -rf "/home/workspace/Personal/Meetings/2025-09-22_ayush-jain_job-aggregation-automation-workflow_partnership"
rm -rf "/home/workspace/Personal/Meetings/2025-09-22_careerspan_kathy-pham-interview-planning_planning"
rm -rf "/home/workspace/Personal/Meetings/2025-09-22_careerspan_podcast-production-gtm-planning_cofounder"

# Log cleanup
echo "{\"timestamp\": \"$(date -Iseconds)\", \"action\": \"cleanup_duplicates\", \"deleted\": 5}" >> /home/workspace/Personal/Meetings/rename_log.jsonl
```

---

## After Cleanup

**Result:**
- 2 true duplicates removed
- 3 empty artifacts removed
- All original transcript folders remain untouched
- 20 good standardized folders remain

**What about "unknown" folders?**
- Skip for now (you said something else will handle them)

---

## What to Rebuild?

**You asked:** "What needs to be fixed?"

**Answer:** The standardization system itself is NOT broken. It worked. The problem was:
1. **No idempotency** - same meeting got renamed twice because we didn't mark "already processed"
2. **LLM semantic variance** - two runs on same meeting generated different folder names

**Fix needed:**
1. Add `.standardized` marker file to prevent re-processing
2. Make standardization deterministic (check marker before renaming)
3. That's it - rest of system is fine

**Do you want me to:**
- A) Just do this cleanup (5 deletes) and call it done?
- B) Cleanup + add the idempotency fix so it doesn't happen again?

---

*Awaiting approval to execute*
