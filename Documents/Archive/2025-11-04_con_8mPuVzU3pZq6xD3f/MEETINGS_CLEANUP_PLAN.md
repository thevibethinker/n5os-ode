# Personal/Meetings Cleanup Plan

**Date:** 2025-11-04
**Status:** Ready for approval

---

## Current State Analysis

### Files to Clean Up

#### 1. Implementation Documentation (Out of Date - System is Built)
- ✅ `FIXES_COMPLETE.md` - Documents Nov 4 fixes
- ✅ `IMPLEMENTATION_COMPLETE.md` - Documents pipeline implementation
- ✅ `HUEY_IMPLEMENTATION_COMPLETE.md` - Documents Huey setup
- ✅ `GDRIVE_FIX_SUMMARY.md` - Documents GDrive fix
- ✅ `IMPORT_STATUS.md` - Documents import status

**Action:** Archive to `Knowledge/architectural/meetings-pipeline/` (historical reference)

#### 2. Temporary Backup Directories
- ✅ `BACKUP_20251104_122007/` - Contains only Inbox subdirectory (empty now)
- ✅ `CURRENT_BACKUP_20251104/` - Contains 47 old .transcript.md files (superseded by current ones)

**Action:** Delete (content superseded by production files in meeting folders)

#### 3. Bulk Import Working Directory
- ✅ `BULK_IMPORT_20251104/` - Contains scripts & reports from bulk import process
  - convert_transcripts.py
  - deduplicate.py, deduplicate_fixed.py
  - fix_missing_extensions.py
  - DEDUPLICATION_REPORT.md
  - PHASE1_COMPLETE.md

**Action:** Archive scripts to `N5/scripts/archive/bulk-import-2025-11/` (may be useful for future bulk imports)
**Action:** Archive reports with implementation docs

#### 4. Sync Artifacts (Junk)
- ✅ `.DS_Store` - Mac filesystem metadata
- ✅ `.sync-conflict-20251103-000747-RY3QBDJ.DS_Store` - Syncthing conflict file

**Action:** Delete (unnecessary metadata)

#### 5. Daily Prep File
- ✅ `daily-meeting-prep-2025-11-01.md` - Dated prep file from Nov 1

**Action:** Move to `Personal/Planning/` or delete if obsolete

#### 6. Inbox Directory
- Contains 194+ transcripts waiting to be processed
- Has duplicate Acquisition War Room files with different naming conventions

**Action:** Keep as-is (working directory for pipeline), but clean duplicates

---

## Cleanup Actions

### Phase 1: Archive Implementation Docs
```bash
mkdir -p /home/workspace/Knowledge/architectural/meetings-pipeline
mv /home/workspace/Personal/Meetings/FIXES_COMPLETE.md \
   /home/workspace/Personal/Meetings/IMPLEMENTATION_COMPLETE.md \
   /home/workspace/Personal/Meetings/HUEY_IMPLEMENTATION_COMPLETE.md \
   /home/workspace/Personal/Meetings/GDRIVE_FIX_SUMMARY.md \
   /home/workspace/Personal/Meetings/IMPORT_STATUS.md \
   /home/workspace/Knowledge/architectural/meetings-pipeline/
```

### Phase 2: Archive Bulk Import Scripts
```bash
mkdir -p /home/workspace/N5/scripts/archive/bulk-import-2025-11
mv /home/workspace/Personal/Meetings/BULK_IMPORT_20251104/*.py \
   /home/workspace/N5/scripts/archive/bulk-import-2025-11/
mv /home/workspace/Personal/Meetings/BULK_IMPORT_20251104/*.md \
   /home/workspace/Knowledge/architectural/meetings-pipeline/
```

### Phase 3: Delete Backup Directories
```bash
rm -rf /home/workspace/Personal/Meetings/BACKUP_20251104_122007
rm -rf /home/workspace/Personal/Meetings/CURRENT_BACKUP_20251104
rm -rf /home/workspace/Personal/Meetings/BULK_IMPORT_20251104
```

### Phase 4: Delete Sync Artifacts
```bash
rm /home/workspace/Personal/Meetings/.DS_Store
rm /home/workspace/Personal/Meetings/.sync-conflict-*
```

### Phase 5: Move Daily Prep
```bash
# Check if file is still relevant or should be deleted
# If relevant: mv to Personal/Planning/
# If obsolete: delete
```

### Phase 6: Clean Inbox Duplicates
```bash
# Deduplicate Acquisition War Room files in Inbox
# Keep only canonical versions with proper naming
```

---

## What Stays in Personal/Meetings

After cleanup:
1. Meeting folders (named like `2025-10-09_Alex-Caveny_advisory-coaching`)
2. Inbox/ (working directory for pipeline)
3. .stignore (Syncthing configuration)
4. .n5protected (protection marker)
5. .stfolder (Syncthing metadata - required)
6. .stversions/ (Syncthing versions - if needed)

---

## Safety Notes

⚠️ This directory is protected. All operations will be:
1. Non-destructive to meeting data
2. Archiving (not deleting) implementation docs
3. Removing only temporary/obsolete files
4. Preserving pipeline infrastructure

---

**Ready to execute?**
