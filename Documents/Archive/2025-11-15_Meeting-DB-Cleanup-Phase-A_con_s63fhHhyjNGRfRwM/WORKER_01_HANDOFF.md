---
created: 2025-11-15
last_edited: 2025-11-15
version: 1.0
---

# WORKER 01: Delete Empty Meeting Databases

**Spawned By**: Vibe Operator (con_wkDPnaagydefZ4QH)  
**Orchestrator Thread**: con_z6F09rhM12C9kJDZ  
**Phase**: A - Database Cleanup  
**Risk Level**: LOW  
**Estimated Time**: 10 minutes

---

## Mission

Delete 7 empty meeting databases that contain no data and serve no active purpose. These are confirmed empty via audit and represent technical debt from exploratory development.

---

## Context

From the meeting system audit (file `/home/.z/workspaces/con_z6F09rhM12C9kJDZ/MEETING_SYSTEM_AUDIT.md`):

**Empty Databases Identified**:
1. `/home/workspace/N5/data/meeting_db.sqlite` (8KB, empty)
2. `/home/workspace/N5/data/meetings_registry.db` (empty)
3. `/home/workspace/N5/data/meeting_processing.db` (empty)
4. `/home/workspace/N5/data/meeting_requests.db` (empty)
5. `/home/workspace/N5/registry/meeting_processing_registry.db` (empty)
6. `/home/workspace/N5/data/meeting_pipeline/meeting_queue.db` (empty)
7. Any other confirmed empty meeting-related .db/.sqlite files you discover

**Active/Critical Databases (DO NOT TOUCH)**:
- `/home/workspace/N5/data/meeting_pipeline.db` (180KB, 188 meetings) ✅
- `/home/workspace/N5/data/executables.db` (contains prompts/recipes) ✅
- Any database >10KB or with confirmed data ✅

---

## Your Task

### Step 1: Safety Verification (5 min)

For each target database:

```bash
# Verify it's empty
sqlite3 <db_path> "SELECT name FROM sqlite_master WHERE type='table';"

# Check file size
ls -lh <db_path>

# Check for any data
sqlite3 <db_path> ".tables" 
```

**Safety Rule**: Only delete if:
- File size ≤ 8KB AND
- No tables exist OR tables are empty AND
- Path matches audit list

### Step 2: Create Archive Backup (2 min)

```bash
# Create timestamped backup directory
mkdir -p /home/workspace/Archives/meeting-system-cleanup/phase-a-empty-dbs/$(date +%Y%m%d_%H%M%S)

# Copy all target files to archive
cp <each-empty-db> /home/workspace/Archives/meeting-system-cleanup/phase-a-empty-dbs/$(date +%Y%m%d_%H%M%S)/
```

### Step 3: Delete Empty Databases (2 min)

```bash
# Delete each confirmed empty database
rm <db_path>

# Verify deletion
ls -l <db_path> 2>&1  # Should return "No such file or directory"
```

### Step 4: Verification Scan (1 min)

```bash
# Scan for remaining empty meeting databases
find /home/workspace/N5/data -name "*.db" -o -name "*.sqlite" | while read db; do
  size=$(stat -c%s "$db")
  if [ $size -le 8192 ]; then
    echo "Small DB found: $db ($size bytes)"
    sqlite3 "$db" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>&1
  fi
done
```

---

## Success Criteria

✅ **MUST ACHIEVE**:
1. All 7 empty databases deleted
2. Archive backup created with timestamp
3. Active databases (`meeting_pipeline.db`) untouched
4. Verification scan shows no remaining empty meeting DBs

✅ **DELIVERABLES**:
1. List of deleted files with sizes
2. Archive backup location
3. Verification scan output
4. Confirmation that critical DBs are safe

---

## Safety Checks

### BEFORE DELETION:
- [ ] Verified database is empty (no tables OR all tables empty)
- [ ] File size ≤ 8KB
- [ ] Path matches audit list
- [ ] Created archive backup

### STOP IMMEDIATELY IF:
- ❌ Database has tables with data
- ❌ File size > 10KB
- ❌ Database is `meeting_pipeline.db` or `executables.db`
- ❌ Path is not in approved target list

### ROLLBACK PLAN:
```bash
# Restore from archive if needed
cp /home/workspace/Archives/meeting-system-cleanup/phase-a-empty-dbs/TIMESTAMP/* /home/workspace/N5/data/
```

---

## Reporting Back

### On Success:
Create file `/home/.z/workspaces/con_wkDPnaagydefZ4QH/PHASE_A_COMPLETE.md` with:

```markdown
# Phase A: Delete Empty Databases - COMPLETE ✅

**Worker**: [your-conversation-id]
**Date**: [timestamp]
**Duration**: [actual time]

## Deleted Databases
1. [path] - [size] - [verification status]
2. [path] - [size] - [verification status]
...

## Archive Location
/home/workspace/Archives/meeting-system-cleanup/phase-a-empty-dbs/[TIMESTAMP]/

## Verification
- Active databases safe: ✅
- No remaining empty DBs: ✅
- Archive backup created: ✅

## Next Action
Ready for Phase B (script consolidation)
```

### On Failure:
Create file `/home/.z/workspaces/con_wkDPnaagydefZ4QH/PHASE_A_FAILED.md` with:

```markdown
# Phase A: FAILED ❌

**Issue**: [description]
**Attempted**: [what you tried]
**Stopped At**: [which step]
**Rollback Status**: [restored or not needed]
**Recommendation**: [next steps]
```

---

## Approved Target List (from Audit)

```
/home/workspace/N5/data/meeting_db.sqlite
/home/workspace/N5/data/meetings_registry.db
/home/workspace/N5/data/meeting_processing.db
/home/workspace/N5/data/meeting_requests.db
/home/workspace/N5/registry/meeting_processing_registry.db
/home/workspace/N5/data/meeting_pipeline/meeting_queue.db
```

---

## DO NOT DELETE (Critical Infrastructure)

```
/home/workspace/N5/data/meeting_pipeline.db (180KB, 188 meetings)
/home/workspace/N5/data/executables.db (prompts/recipes)
Any database > 10KB
Any JSONL files (.jsonl)
```

---

**Status**: READY TO EXECUTE  
**Risk**: LOW  
**Expected Duration**: 10 minutes  
**Spawned By**: con_wkDPnaagydefZ4QH  
**Report Back To**: con_wkDPnaagydefZ4QH

---

**END OF WORKER 01 HANDOFF**

*Version 1.0 | 2025-11-15 | Vibe Operator*

