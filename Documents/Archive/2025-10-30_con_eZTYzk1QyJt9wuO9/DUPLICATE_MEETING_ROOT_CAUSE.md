# Duplicate Meeting Requests - Root Cause Analysis
**Date:** 2025-10-30 07:51 ET  
**Issue:** 5 duplicate request.json files created for Oct 29 meetings

---

## Root Cause

**Deduplication state loss during scheduled task execution**

### Timeline
1. **2025-10-30 04:38:44 EDT**: Scheduled task runs with `dedup_gdrive_ids: 0`
2. Task scans Google Drive, finds 14 files
3. **With empty dedup set**, creates 12 new request files (should have been 0)
4. Some of these 12 were duplicates of existing requests from earlier successful runs

### Why Dedup State Was Lost

**Script:** `/home/workspace/N5/scripts/meeting_transcript_scan.py`
**Line 202-205:** Dedup loading logic

```python
existing_gdrive_ids = set()
existing_gdrive_ids.add("mock_gdrive_id_5_duplicate") # MOCK DATA POLLUTION
existing_gdrive_ids.update(load_gdrive_ids_from_json_files(INBOX_PATH))
existing_gdrive_ids.update(load_gdrive_ids_from_json_files(PROCESSED_PATH))
existing_gdrive_ids.update(load_gdrive_ids_from_json_files(COMPLETED_PATH))
existing_gdrive_ids.update(load_gdrive_ids_from_metadata_files(RECORDS_PATH))
```

**Problem**: This script loads gdrive_ids from:
- `N5/inbox/meeting_requests/*.json` (INBOX_PATH)
- `N5/inbox/meeting_requests/processed/*.json` (PROCESSED_PATH)  
- `N5/inbox/meeting_requests/completed/*.json` (COMPLETED_PATH)
- `Personal/Meetings/*/_metadata.json` (RECORDS_PATH)

**At 04:38, one or more of these directories was empty or failed to load, resulting in dedup_gdrive_ids: 0**

### Why Duplicates Have Different meeting_ids

**Lines 121-132:** `generate_meeting_id()` function

The meeting_id is generated from **parsed filename**, not gdrive_id:
- Same gdrive_id with different filename → different meeting_id
- Example:
  - `"Alex x Vrijen - Wisdom Partners.docx"` → `2025-10-29_external-alex-x-vrijen-wisdom-partners-coaching`
  - `"Alex.docx"` (same gdrive_id) → `2025-10-29_external-alex`

---

## Duplicates Created

| Original | Duplicate | gdrive_id |
|----------|-----------|-----------|
| 2025-10-29_external-alex-x-vrijen-wisdom-partners-coaching | 2025-10-29_external-alex | 1pjMiHTyw47xQulTyGO-AScQrVLcLV3NO |
| 2025-10-29_external-mihir-makwana-x-vrijen | 2025-10-29_external-mihir-makwana | 1IKoUI6pmfRharCMR5OMlLXi_TqQBNWPY |
| 2025-10-29_internal-daily-team-stand-up-02 | 2025-10-29_internal-daily-team-stand-up-143858 | 1jQGY_eDyoAfSjHWiJ3LN_qL99jtHeTZa |
| 2025-10-29_internal-daily-team-stand-up-143753 | 2025-10-29_internal-daily-team-stand-up | 1C2SifCEwPDdslKpdiZD2YNGMWyc17Kzu |
| 2025-10-29_internal-daily-team-stand-up-143925 | 2025-10-29_internal-internal-team | 1EsraiV5Bko-crA8Yh0vU0uZAHW1QJ2wM |

**All duplicates deleted: 2025-10-30 07:50 ET**

---

## The Fix

### Immediate (Applied)
✅ Delete 5 duplicate request files

### Short-term (In Progress)
1. **Add persistent dedup registry** - Don't rely on file scanning alone
2. **Gdrive_id as primary key** - Check gdrive_id BEFORE generating meeting_id
3. **Remove mock data pollution** - Clean up test code from production script

### Long-term (P29: Mock Data Discipline)
1. Rename demo/mock scripts with `.DEMO` suffix
2. Add n5_safety.py checks to CI/CD
3. Extend SESSION_STATE with Development artifact tracking
4. Never commit test/mock data in production code paths

---

**Resolution Status:** Root cause identified, duplicates cleaned, fix in progress

*Analysis complete: 2025-10-30 07:52 ET*
