---
created: 2025-11-05
version: 1.0
---

# Vestigial Meeting Code Archive

**Date:** 2025-11-05  
**Reason:** Superseded by Prompt Tool architecture

## Files Archived

1. `block_selector.py.backup-20251103` - Old backup
2. `drive_download_wrapper.sh.VESTIGIAL_20251105` - Bridge attempt (architecturally unsound)
3. `drive_ingestion.py.VESTIGIAL_20251105` - Phase 1 skeleton, Phase 2 never completed
4. `drive_ingestion.py.backup-phase1` - Early version
5. `gdrive_fetch_wrapper.py.BROKEN` - Old approach #1
6. `gdrive_fetcher_v2.py.BROKEN` - Old approach #2
7. `gdrive_transcript_fetcher.py.BROKEN` - Old approach #3
8. `gdrive_transcript_fetcher.py.backup` - Backup of #3
9. `transcript_processor_v3.py.backup` - Old processor

## Why Archived

These files represent failed attempts to build Python-based Drive ingestion.

**Problem:** Python scripts cannot directly call `use_app_google_drive` (Zo AI tool).

**Solution:** Prompt Tool architecture at `Prompts/drive_meeting_ingestion.md` enables full AI orchestration.

## Production Architecture (Nov 2025)

**Ingestion:** Prompt Tool (`Prompts/drive_meeting_ingestion.md`)  
**Normalization:** `semantic_filename.py` (strips milliseconds)  
**Registry:** `N5/data/meeting_gdrive_registry.jsonl`  
**Safeguards:**
- `detect_duplicates.py` - Hourly scan
- `rate_limit_check.py` - Auto-pause if runaway
- `queue_manager.py` - Schema validation + size limits

## Can These Be Deleted?

Yes, but kept for historical reference. If disk space needed, delete entire `.archive_20251105/` directory.

---

**Last updated:** 2025-11-05
