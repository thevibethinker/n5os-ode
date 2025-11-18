# JSONL Registry Expunged - 2025-11-16

**Date:** 2025-11-16 09:37 ET  
**Reason:** Migrating to pipeline.db for all meeting tracking  
**Conversation:** con_SV4FJvpVsm8w9A9b

## What Was Removed

### Data Files
- `meeting_gdrive_registry.jsonl` (445 entries)
- `meeting_registry.jsonl`
- `meeting_registry_txlog.jsonl`
- `meeting_gdrive_registry.jsonl.backup`
- All backup copies from `/home/workspace/N5/data/backups/`

### Scripts Moved to .EXPUNGED
- `meeting_registry_manager.py`
- `meeting_registry_reconcile.py`
- `meeting_registry_reconcile_orphans.py`

## New Architecture

**Single Source of Truth:** `/home/workspace/N5/data/meeting_pipeline.db`

**Workflow:**
1. Firefly webhook → transcript to `Personal/Meetings/Inbox/{raw_folder}/`
2. Scheduled task "Generate meeting intelligence manifest" → Creates `{folder}_[M]/` with manifest
3. Scheduled task "Meeting Block Generation Process" → Generates blocks, marks `_[P]`
4. Scheduled task "Finalize Meeting Intelligence and Relocation" → **ADDS TO DATABASE** → Moves to `Personal/Meetings/{folder}/`

**Database Script:** `/home/workspace/N5/scripts/meeting_pipeline/add_to_database.py`

## Recovery

If needed, these files are preserved here and can be restored. However, the new system is the authoritative source going forward.

